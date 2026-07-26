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
    _prepare_hook_command,
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

    def test_rejects_shell_hook_command_from_manifest(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "domain-chip-cmd"
        chip_dir.mkdir()
        input_path = tmp_path / "input.json"
        output_path = tmp_path / "output.json"

        with pytest.raises(ValueError, match="python or python3"):
            _prepare_hook_command(
                "cmd.exe /c calc",
                "evaluate",
                input_path,
                output_path,
                chip_path=chip_dir,
            )

    @pytest.mark.parametrize(
        "executable",
        ["/tmp/python", "./python3", r"C:\\untrusted\\python.exe"],
    )
    def test_rejects_path_prefixed_python_executable_from_manifest(
        self,
        tmp_path: Path,
        executable: str,
    ) -> None:
        chip_dir = tmp_path / "domain-chip-cmd"
        chip_dir.mkdir()

        with pytest.raises(ValueError, match="bare python executable"):
            _prepare_hook_command(
                [executable, "eval.py"],
                "evaluate",
                tmp_path / "input.json",
                tmp_path / "output.json",
                chip_path=chip_dir,
            )

    def test_rejects_hook_script_outside_chip_dir(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "domain-chip-cmd"
        chip_dir.mkdir()
        outside = tmp_path / "outside.py"
        outside.write_text("print('outside')\n", encoding="utf-8")

        with pytest.raises(ValueError, match="inside the chip directory"):
            _prepare_hook_command(
                ["python", str(outside)],
                "evaluate",
                tmp_path / "input.json",
                tmp_path / "output.json",
                chip_path=chip_dir,
            )

    def test_accepts_local_python_hook_command(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "domain-chip-cmd"
        chip_dir.mkdir()

        resolved, use_stdin = _prepare_hook_command(
            ["python", "eval.py"],
            "evaluate",
            tmp_path / "input.json",
            tmp_path / "output.json",
            chip_path=chip_dir,
        )

        assert resolved[:2] == ["python", "eval.py"]
        assert use_stdin is True

    def test_failed_hook_result_does_not_expose_raw_stderr(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "domain-chip-cmd"
        chip_dir.mkdir()
        (chip_dir / "fail.py").write_text(
            "import sys\nsys.stderr.write('sensitive path /private/keyfile')\nraise SystemExit(7)\n",
            encoding="utf-8",
        )
        chip = ChipHandle(
            chip_path=chip_dir,
            chip_name="domain-chip-cmd",
            domain="testing",
            version="1.0.0",
            commands={"evaluate": ["python3", "fail.py"]},
        )

        result = execute_hook(chip, "evaluate", {})

        assert result.success is False
        assert result.result["returncode"] == 7
        assert result.result["stderr_present"] is True
        assert "stderr" not in result.result
        assert "keyfile" not in json.dumps(result.result)

    def test_reads_file_hook_output_before_temporary_directory_cleanup(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "domain-chip-cmd"
        chip_dir.mkdir()
        (chip_dir / "file_output.py").write_text(
            "import argparse, json\n"
            "parser = argparse.ArgumentParser()\n"
            "parser.add_argument('--input')\n"
            "parser.add_argument('--output')\n"
            "args = parser.parse_args()\n"
            "with open(args.output, 'w', encoding='utf-8') as handle:\n"
            "    json.dump({'source': 'file', 'ok': True}, handle)\n",
            encoding="utf-8",
        )
        chip = ChipHandle(
            chip_path=chip_dir,
            chip_name="domain-chip-cmd",
            domain="testing",
            version="1.0.0",
            commands={
                "evaluate": [
                    "python3",
                    "file_output.py",
                    "--input",
                    "{input}",
                    "--output",
                    "{output}",
                ]
            },
        )

        result = execute_hook(chip, "evaluate", {})

        assert result.success is True
        assert result.result == {"source": "file", "ok": True}


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

    def test_includes_current_workspace_chip_for_default_search(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "spark-domain-chip-labs"
        chip_dir.mkdir()
        (chip_dir / "spark-chip.json").write_text(
            json.dumps(
                {
                    "chip_name": "domain-chip-labs",
                    "domain": "chip-research",
                    "version": "0.1.0",
                    "capabilities": ["evaluate"],
                    "commands": {},
                    "frontier": {},
                }
            ),
            encoding="utf-8",
        )

        with patch("chip_labs.chip_runtime.discover_chips", return_value=[]):
            with patch("chip_labs.chip_runtime.score_chip_v3", return_value=FakeEvalResult(55.0)):
                with patch("chip_labs.chip_runtime.Path.cwd", return_value=chip_dir):
                    handles = load_portfolio(min_score=0)

        assert len(handles) == 1
        assert handles[0].chip_name == "domain-chip-labs"
        assert handles[0].chip_path == chip_dir

    def test_explicit_search_dir_does_not_include_current_workspace_chip(self, tmp_path: Path) -> None:
        chip_dir = tmp_path / "spark-domain-chip-labs"
        chip_dir.mkdir()
        (chip_dir / "spark-chip.json").write_text(
            json.dumps(
                {
                    "chip_name": "domain-chip-labs",
                    "domain": "chip-research",
                    "version": "0.1.0",
                }
            ),
            encoding="utf-8",
        )

        with patch("chip_labs.chip_runtime.discover_chips", return_value=[]):
            with patch("chip_labs.chip_runtime.Path.cwd", return_value=chip_dir):
                handles = load_portfolio(tmp_path, min_score=0)

        assert handles == []

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
