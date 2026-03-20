"""Tests for chip_labs.chip_runtime."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from chip_labs.chip_runtime import (
    ChipHandle,
    HookResult,
    execute_hook,
    load_chip,
    load_portfolio,
    score_gate,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_manifest(name="domain-chip-test", domain="testing",
                   version="1.0.0", capabilities=None,
                   commands=None, frontier=None):
    """Return a minimal spark-chip.json dict."""
    return {
        "name": name,
        "domain": domain,
        "version": version,
        "capabilities": capabilities or ["evaluate", "suggest"],
        "commands": commands or {},
        "frontier": frontier or {},
    }


class FakeEvalResult:
    """Minimal stand-in for DeepEvalResult."""
    def __init__(self, total_score=55.0, verdict="alpha"):
        self.total_score = total_score
        self.verdict = verdict


@pytest.fixture
def mock_chip_dir(tmp_path):
    """Create a minimal chip directory with manifest."""
    chip_dir = tmp_path / "domain-chip-test"
    chip_dir.mkdir()
    manifest = _make_manifest()
    (chip_dir / "spark-chip.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    return chip_dir


# ---------------------------------------------------------------------------
# TestLoadChip
# ---------------------------------------------------------------------------

class TestLoadChip:
    def test_loads_manifest_fields(self, mock_chip_dir: Path) -> None:
        with patch("chip_labs.chip_runtime.score_chip_v3", return_value=FakeEvalResult(72.0, "beta")):
            handle = load_chip(mock_chip_dir)

        assert handle.chip_name == "domain-chip-test"
        assert handle.domain == "testing"
        assert handle.version == "1.0.0"
        assert handle.quality_score == 72.0
        assert handle.quality_verdict == "beta"

    def test_raises_on_missing_manifest(self, tmp_path: Path) -> None:
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        with pytest.raises(FileNotFoundError):
            load_chip(empty_dir)

    def test_capabilities_from_manifest(self, mock_chip_dir: Path) -> None:
        with patch("chip_labs.chip_runtime.score_chip_v3", return_value=FakeEvalResult()):
            handle = load_chip(mock_chip_dir)
        assert "evaluate" in handle.capabilities
        assert "suggest" in handle.capabilities

    def test_commands_from_manifest(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "domain-chip-cmd"
        chip_dir.mkdir()
        manifest = _make_manifest(commands={"evaluate": ["python", "eval.py"]})
        (chip_dir / "spark-chip.json").write_text(json.dumps(manifest), encoding="utf-8")

        with patch("chip_labs.chip_runtime.score_chip_v3", return_value=FakeEvalResult()):
            handle = load_chip(chip_dir)
        assert handle.commands["evaluate"] == ["python", "eval.py"]


# ---------------------------------------------------------------------------
# TestLoadPortfolio
# ---------------------------------------------------------------------------

class TestLoadPortfolio:
    def test_loads_discovered_chips(self, tmp_path: Path) -> None:
        for name in ("domain-chip-a", "domain-chip-b"):
            d = tmp_path / name
            d.mkdir()
            (d / "spark-chip.json").write_text(
                json.dumps(_make_manifest(name=name)), encoding="utf-8"
            )

        descriptors = [
            {"name": "domain-chip-a", "path": str(tmp_path / "domain-chip-a")},
            {"name": "domain-chip-b", "path": str(tmp_path / "domain-chip-b")},
        ]

        with patch("chip_labs.chip_runtime.discover_chips", return_value=descriptors):
            with patch("chip_labs.chip_runtime.score_chip_v3", return_value=FakeEvalResult(55.0)):
                handles = load_portfolio(tmp_path, min_score=0)

        assert len(handles) == 2

    def test_filters_by_min_score(self, tmp_path: Path) -> None:
        d = tmp_path / "domain-chip-low"
        d.mkdir()
        (d / "spark-chip.json").write_text(
            json.dumps(_make_manifest(name="low")), encoding="utf-8"
        )

        descriptors = [{"name": "low", "path": str(d)}]

        with patch("chip_labs.chip_runtime.discover_chips", return_value=descriptors):
            with patch("chip_labs.chip_runtime.score_chip_v3", return_value=FakeEvalResult(20.0, "scaffold")):
                handles = load_portfolio(tmp_path, min_score=35)

        assert len(handles) == 0

    def test_skips_broken_chips(self, tmp_path: Path) -> None:
        bad_dir = tmp_path / "domain-chip-broken"
        bad_dir.mkdir()  # No manifest

        descriptors = [{"name": "broken", "path": str(bad_dir)}]

        with patch("chip_labs.chip_runtime.discover_chips", return_value=descriptors):
            handles = load_portfolio(tmp_path, min_score=0)

        assert len(handles) == 0


# ---------------------------------------------------------------------------
# TestScoreGate
# ---------------------------------------------------------------------------

class TestScoreGate:
    def test_passes_above_threshold(self) -> None:
        chip = ChipHandle(chip_path=Path("/m"), chip_name="t", domain="t",
                          version="0.1", quality_score=60.0)
        assert score_gate(chip, min_score=35) is True

    def test_fails_below_threshold(self) -> None:
        chip = ChipHandle(chip_path=Path("/m"), chip_name="t", domain="t",
                          version="0.1", quality_score=20.0)
        assert score_gate(chip, min_score=35) is False

    def test_exact_threshold(self) -> None:
        chip = ChipHandle(chip_path=Path("/m"), chip_name="t", domain="t",
                          version="0.1", quality_score=35.0)
        assert score_gate(chip, min_score=35) is True


# ---------------------------------------------------------------------------
# TestExecuteHook
# ---------------------------------------------------------------------------

class TestExecuteHook:
    def test_intelligence_fallback(self, tmp_path: Path) -> None:
        chip = ChipHandle(
            chip_path=tmp_path, chip_name="test-chip", domain="testing",
            version="0.1", quality_score=60.0,
        )

        with patch("chip_labs.chip_runtime.serve_context", return_value={"context": "test"}):
            result = execute_hook(chip, "evaluate")

        assert result.success is True
        assert result.execution_mode == "intelligence_fallback"
        assert result.hook_name == "evaluate"
        assert result.duration_ms >= 0

    def test_confidence_from_quality(self, tmp_path: Path) -> None:
        chip = ChipHandle(
            chip_path=tmp_path, chip_name="t", domain="t",
            version="0.1", quality_score=75.0,
        )

        with patch("chip_labs.chip_runtime.serve_context", return_value={}):
            result = execute_hook(chip, "suggest")

        assert result.confidence == 0.75

    def test_fallback_on_error(self, tmp_path: Path) -> None:
        chip = ChipHandle(
            chip_path=tmp_path, chip_name="t", domain="t",
            version="0.1", quality_score=50.0,
        )

        with patch("chip_labs.chip_runtime.serve_context", side_effect=RuntimeError("fail")):
            result = execute_hook(chip, "evaluate")

        assert result.success is False
        assert "error" in result.result


# ---------------------------------------------------------------------------
# TestHookResult
# ---------------------------------------------------------------------------

class TestHookResult:
    def test_default_values(self) -> None:
        hr = HookResult(hook_name="test", chip_name="c", success=True)
        assert hr.result == {}
        assert hr.confidence == 0.0
        assert hr.execution_mode == "unknown"
        assert hr.duration_ms == 0
