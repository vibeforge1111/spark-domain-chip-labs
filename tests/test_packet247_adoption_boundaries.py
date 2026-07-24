from __future__ import annotations

import io
import json
from pathlib import Path
from unittest.mock import patch

from chip_labs import hooks
from chip_labs.chip_factory.gap_analyzer import _fix_commands_defined
from chip_labs.creator_mission_adapter import _generated_multi_seed_summary
from chip_labs.intelligence_serving.chip_advisor import _classify_guidance
from chip_labs.intelligence_serving.chip_mcp_server import ChipMCPServer
from chip_labs.intelligence_serving.intelligence_server import _atomic_write_text
from chip_labs.quality_rubric import _check_evidence_separation
from chip_labs.transfer import TransferPattern, apply_pattern


def _pattern(pattern_type: str, implementation: dict[str, object]) -> TransferPattern:
    return TransferPattern(
        pattern_id=f"packet247-{pattern_type}",
        source_chip="domain-chip-source",
        pattern_type=pattern_type,
        description="Packet 247 proof",
        implementation=implementation,
        evidence_strength=0.9,
        applicable_categories=["all"],
    )


def test_transfer_reports_only_real_changes_and_does_not_pad_trials(
    tmp_path: Path,
) -> None:
    chip = tmp_path / "domain-chip-target"
    chip.mkdir()
    project = {
        "project_name": "target",
        "candidate_trials": [],
    }
    (chip / "spark-researcher.project.json").write_text(
        json.dumps(project),
        encoding="utf-8",
    )
    pattern = _pattern("research_pipeline", {"has_baseline": True})

    assert apply_pattern(chip, pattern) is True
    updated = json.loads(
        (chip / "spark-researcher.project.json").read_text(encoding="utf-8")
    )
    assert [row["candidate_id"] for row in updated["candidate_trials"]] == [
        "global-baseline"
    ]
    assert apply_pattern(chip, pattern) is False
    assert not list(chip.rglob("*.tmp"))


def test_concrete_evidence_lanes_override_keyword_gaming(tmp_path: Path) -> None:
    chip = tmp_path / "domain-chip-evidence"
    lane = chip / "research" / "research_grounded"
    lane.mkdir(parents=True)
    (lane / "source.md").write_text("bounded source", encoding="utf-8")
    (chip / "README.md").write_text(
        "benchmark_grounded exploratory_frontier realworld_validated",
        encoding="utf-8",
    )

    checks = _check_evidence_separation(chip)

    assert checks == {
        "has_research_grounded": True,
        "has_benchmark_grounded": False,
        "has_exploratory_frontier": False,
        "has_realworld_validated": False,
    }


def test_domain_hint_remains_authoritative_without_cwd(tmp_path: Path) -> None:
    chip = type(
        "Chip",
        (),
        {
            "chip_name": "startup",
            "domain": "startup",
            "quality_score": 90,
            "intelligence": None,
        },
    )()
    captured: list[str] = []

    with (
        patch.dict(hooks.os.environ, {hooks.DOMAIN_HINT_ENV: "startup"}, clear=False),
        patch.object(hooks, "_load_portfolio_safe", return_value=[chip]),
        patch.object(hooks, "_select_session_chips", return_value=[]),
        patch.object(
            hooks,
            "_build_context_text",
            side_effect=lambda portfolio, query, max_chips: captured.append(query)
            or "Startup context",
        ),
    ):
        result = hooks.handle_session_start({"cwd": ""})

    assert result["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert captured == ["startup"]


def test_list_commands_are_normalized_before_evaluate_fix(tmp_path: Path) -> None:
    project_path = tmp_path / "spark-researcher.project.json"
    project_path.write_text(
        json.dumps({"commands": [{"name": "suggest", "kind": "chip-suggest"}]}),
        encoding="utf-8",
    )

    assert _fix_commands_defined(tmp_path) is True

    commands = json.loads(project_path.read_text(encoding="utf-8"))["commands"]
    assert commands["suggest"]["kind"] == "chip-suggest"
    assert commands["evaluate"] == {"kind": "chip-evaluate"}


def test_broken_mcp_output_pipe_stops_cleanly() -> None:
    class BrokenOutput:
        def write(self, value: str) -> None:
            raise BrokenPipeError

        def flush(self) -> None:
            raise AssertionError("flush should not run after a broken write")

    server = ChipMCPServer()
    server.run(
        stdin=io.StringIO(
            '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n'
        ),
        stdout=BrokenOutput(),
        stderr=io.StringIO(),
    )


def test_zero_run_count_does_not_fall_through() -> None:
    summary = _generated_multi_seed_summary(
        {
            "run_count": 0,
            "matrix": {"completed_run_count": 7, "target_run_count": 9},
            "rows": [{}, {}],
        }
    )

    assert summary["run_count"] == 0


def test_adjacent_punctuation_keeps_warning_classification() -> None:
    assert _classify_guidance(
        "send provider headers",
        "Avoid: leaking provider headers",
    ) == "warns"


def test_atomic_intelligence_write_leaves_no_partial_file(tmp_path: Path) -> None:
    output = tmp_path / "chip_context.json"
    _atomic_write_text(output, '{"version": 1}')
    _atomic_write_text(output, '{"version": 2}')

    assert output.read_text(encoding="utf-8") == '{"version": 2}'
    assert list(tmp_path.iterdir()) == [output]
