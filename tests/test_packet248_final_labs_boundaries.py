from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import pytest

from chip_labs.chip_factory.gap_analyzer import (
    _fix_candidate_trials,
    _fix_multiple_metrics,
)
from chip_labs.chip_factory.scaffold import _parse_simple_yaml
from chip_labs.cli import cmd_portfolio_v3
from chip_labs.intelligence_serving import chip_runtime
from chip_labs.intelligence_serving.chip_runtime import ChipHandle, _execute_subprocess
from chip_labs.lab_hooks import evaluate as evaluate_module
from chip_labs.mirofish.discovery import _build_alias_map
from chip_labs.transfer import TransferPattern, apply_pattern
from chip_labs.transfer_surface import transfer


def test_failed_transfer_is_bounded_and_not_counted(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pattern = TransferPattern(
        pattern_id="failure-proof",
        source_chip="source",
        pattern_type="failure-proof",
        description="failure proof",
        implementation={},
        evidence_strength=1.0,
        applicable_categories=["all"],
    )

    def fail(target: Path, source: TransferPattern) -> bool:
        raise ValueError("secret transfer detail")

    monkeypatch.setitem(transfer._PATTERN_APPLIERS, "failure-proof", fail)
    with caplog.at_level("WARNING"):
        assert apply_pattern(tmp_path, pattern) is False

    assert pattern.times_applied == 0
    assert pattern.times_successful == 0
    assert "ValueError" in caplog.text
    assert "secret transfer detail" not in caplog.text


def test_subprocess_failure_returns_type_without_exception_payload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chip = ChipHandle(
        chip_path=tmp_path,
        chip_name="bounded",
        domain="test",
        version="1",
        commands={"evaluate": ["python", "-m", "bounded.evaluate"]},
    )

    def time_out(*args: object, **kwargs: object) -> None:
        raise subprocess.TimeoutExpired("secret command", 30)

    monkeypatch.setattr(chip_runtime.subprocess, "run", time_out)
    result = _execute_subprocess(chip, "evaluate", {})

    assert result.success is False
    assert result.result == {
        "error": "hook_execution_failed",
        "error_type": "TimeoutExpired",
    }


def test_candidate_and_metric_fixes_preserve_declared_shapes(tmp_path: Path) -> None:
    (tmp_path / "spark-chip.json").write_text(
        json.dumps(
            {
                "frontier": {
                    "allowed_mutations": {
                        "mode": ["safe", "fast"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    project_path = tmp_path / "spark-researcher.project.json"
    project_path.write_text(
        json.dumps(
            {
                "candidate_trials": [{"name": "baseline", "mutations": {}}],
                "metrics": {"quality_score": {}},
            }
        ),
        encoding="utf-8",
    )

    assert _fix_candidate_trials(tmp_path) is True
    assert _fix_multiple_metrics(tmp_path) is True

    project = json.loads(project_path.read_text(encoding="utf-8"))
    assert [row["mutations"] for row in project["candidate_trials"]] == [
        {},
        {"mode": "safe"},
        {"mode": "fast"},
    ]
    assert set(project["metrics"]) == {"quality_score", "relevance", "consistency"}


def test_simple_yaml_parses_third_level_mapping() -> None:
    parsed = _parse_simple_yaml(
        """
frontier:
  allowed_mutations:
    mode: [safe, fast]
    depth: deep
"""
    )

    assert parsed["frontier"]["allowed_mutations"] == {
        "mode": ["safe", "fast"],
        "depth": "deep",
    }


def test_duplicate_domain_id_never_creates_self_alias() -> None:
    aliases = _build_alias_map(
        [
            {"domain_id": "same", "label": "First", "duplicate_aliases": []},
            {"domain_id": "same", "label": "Second", "duplicate_aliases": []},
        ]
    )

    assert aliases == {}


def test_lab_state_cache_key_changes_with_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[str] = []

    def capture(repo: str, search: str, state_key: str) -> dict[str, str]:
        captured.append(state_key)
        return {"state_key": state_key}

    monkeypatch.setattr(evaluate_module, "_cached_lab_state", capture)
    evaluate_module._lab_state(tmp_path)
    packets = tmp_path / "research" / "packets"
    packets.mkdir(parents=True)
    (packets / "new.json").write_text("{}", encoding="utf-8")
    evaluate_module._lab_state(tmp_path)

    assert captured[0] != captured[1]


def test_empty_portfolio_prints_explicit_ranking_state(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "chip_labs.deep_eval.score_portfolio_v3",
        lambda search_dir: {
            "summary": {
                "chip_count": 0,
                "average_score": 0,
                "verdicts": {},
                "ranking": [],
            },
            "chips": {},
        },
    )

    cmd_portfolio_v3(argparse.Namespace(search_dir=tmp_path, output=None))

    assert "Ranking: no domain chips discovered" in capsys.readouterr().out
