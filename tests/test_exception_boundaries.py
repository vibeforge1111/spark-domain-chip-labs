"""Regression tests for recoverable exception boundaries."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from chip_labs.chip_factory import gap_analyzer
from chip_labs.chip_factory.gap_analyzer import GapFix, _fix_has_skill_file, improve_chip
from chip_labs.chip_factory.scaffold import scaffold_chip
from chip_labs.hooks import _write_cache


def _valid_brief(**overrides: Any) -> dict[str, Any]:
    brief: dict[str, Any] = {
        "domain_id": "test-domain",
        "domain_name": "Test Domain",
        "primary_metric": "accuracy",
        "mutation_axes": [{"name": "tone", "values": ["plain"]}],
    }
    brief.update(overrides)
    return brief


def test_fix_has_skill_file_falls_back_on_expected_io_failure(monkeypatch, tmp_path: Path) -> None:
    import chip_labs.intelligence_serving.intelligence_server as server

    def raise_io_error(_chip_path: Path) -> None:
        raise OSError("cannot build skill")

    monkeypatch.setattr(server, "build_skill", raise_io_error)

    chip_path = tmp_path / "domain-chip-demo"
    chip_path.mkdir()

    assert _fix_has_skill_file(chip_path) is True
    assert (chip_path / "chip_skill.md").exists()


def test_fix_has_skill_file_surfaces_unexpected_builder_errors(monkeypatch, tmp_path: Path) -> None:
    import chip_labs.intelligence_serving.intelligence_server as server

    def raise_runtime_error(_chip_path: Path) -> None:
        raise RuntimeError("builder bug")

    monkeypatch.setattr(server, "build_skill", raise_runtime_error)

    with pytest.raises(RuntimeError, match="builder bug"):
        chip_path = tmp_path / "domain-chip-demo"
        chip_path.mkdir()
        _fix_has_skill_file(chip_path)


def test_improve_chip_marks_expected_fix_io_failure_without_swallowing_bugs(
    monkeypatch,
    tmp_path: Path,
) -> None:
    def score(_chip_path: Path) -> dict[str, Any]:
        return {"total_score": 0, "passed_checks": [], "failed_checks": [], "dimensions": []}

    def fail_with_io(_chip_path: Path) -> bool:
        raise OSError("readonly")

    monkeypatch.setattr(gap_analyzer, "score_chip", score)
    monkeypatch.setattr(gap_analyzer, "_persist_score", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        gap_analyzer,
        "analyze_gaps",
        lambda _result: [
            GapFix(
                check_id="io_fix",
                dimension="docs",
                description="io fix",
                points_recoverable=1,
                auto_fixable=True,
                fix_fn=fail_with_io,
                fix_description="expected IO failure",
            )
        ],
    )

    result = improve_chip(tmp_path, target_score=10, max_iterations=1)

    assert result["fixes_applied"][0]["succeeded"] is False


def test_improve_chip_surfaces_unexpected_fix_errors(monkeypatch, tmp_path: Path) -> None:
    def score(_chip_path: Path) -> dict[str, Any]:
        return {"total_score": 0, "passed_checks": [], "failed_checks": [], "dimensions": []}

    def fail_with_bug(_chip_path: Path) -> bool:
        raise RuntimeError("fix bug")

    monkeypatch.setattr(gap_analyzer, "score_chip", score)
    monkeypatch.setattr(gap_analyzer, "_persist_score", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        gap_analyzer,
        "analyze_gaps",
        lambda _result: [
            GapFix(
                check_id="bug_fix",
                dimension="docs",
                description="bug fix",
                points_recoverable=1,
                auto_fixable=True,
                fix_fn=fail_with_bug,
            )
        ],
    )

    with pytest.raises(RuntimeError, match="fix bug"):
        improve_chip(tmp_path, target_score=10, max_iterations=1)


def test_scaffold_chip_keeps_optional_dspy_io_failure_nonfatal(monkeypatch, tmp_path: Path) -> None:
    import chip_labs.dspy_slot as dspy_slot

    def raise_io_error(_chip_path: Path, _slot_type: str) -> None:
        raise OSError("cannot write optional slot")

    monkeypatch.setattr(dspy_slot, "scaffold_dspy_slot", raise_io_error)

    chip_dir = scaffold_chip(_valid_brief(dspy_enabled=True), output_dir=tmp_path)

    assert chip_dir.exists()


def test_scaffold_chip_surfaces_unexpected_dspy_errors(monkeypatch, tmp_path: Path) -> None:
    import chip_labs.dspy_slot as dspy_slot

    def raise_runtime_error(_chip_path: Path, _slot_type: str) -> None:
        raise RuntimeError("dspy bug")

    monkeypatch.setattr(dspy_slot, "scaffold_dspy_slot", raise_runtime_error)

    with pytest.raises(RuntimeError, match="dspy bug"):
        scaffold_chip(_valid_brief(dspy_enabled=True), output_dir=tmp_path)


@dataclass
class _CacheChip:
    chip_path: Path
    chip_name: str = "test-chip"
    domain: str = "testing"
    version: str = "0.1.0"
    capabilities: list[str] = field(default_factory=list)
    quality_score: float = 0.0
    quality_verdict: str = "scaffold"


def test_write_cache_treats_missing_intelligence_as_recoverable(tmp_path: Path) -> None:
    cache_file = tmp_path / "cache.json"

    _write_cache(cache_file, [_CacheChip(chip_path=tmp_path / "domain-chip-test")])

    assert cache_file.exists()


def test_write_cache_surfaces_unexpected_intelligence_errors(tmp_path: Path) -> None:
    class BrokenChip(_CacheChip):
        @property
        def intelligence(self) -> Any:
            raise RuntimeError("intelligence bug")

    with pytest.raises(RuntimeError, match="intelligence bug"):
        _write_cache(tmp_path / "cache.json", [BrokenChip(chip_path=tmp_path)])
