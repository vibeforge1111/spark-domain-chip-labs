from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from chip_labs.tool_operation import (
    CLAIM_BOUNDARY,
    check_tool_operation,
    default_tool_operation_manifest,
    identify_operation,
    load_tool_operation_packet,
)


FIXTURE_DIR = Path("docs/creator_system/examples/tool-operation")


def _smoke_result(verdict: str = "ready_for_swarm_packet") -> dict[str, object]:
    blocked = verdict == "blocked"
    return {
        "schema_version": "adaptive_creator_loop.smoke_result.v1",
        "verdict": verdict,
        "status_counts": {"pass": 3, "warn": 0, "fail": 1 if blocked else 0},
        "automation": {"blocked": blocked, "ci_exit_code": 1 if blocked else 0},
        "checks": [],
    }


def test_tool_operation_manifest_lists_safe_creator_commands() -> None:
    manifest = default_tool_operation_manifest()

    assert manifest["schema_version"] == "tool_operation.manifest.v1"
    assert manifest["claim_boundary"] == CLAIM_BOUNDARY
    assert "creator-run-smoke" in manifest["supported_operations"]
    assert "git push" in manifest["protected_command_markers"]


def test_identify_operation_detects_creator_run_smoke() -> None:
    command = "python -m chip_labs.cli creator-run-smoke runs/demo --recompute"

    assert identify_operation(command) == "creator-run-smoke"


def test_tool_operation_check_passes_with_parsed_postconditions() -> None:
    result = check_tool_operation({
        "command": "python -m chip_labs.cli creator-run-smoke runs/demo --recompute",
        "exit_code": 0,
        "result": _smoke_result(),
    })

    assert result["verdict"] == "pass"
    assert result["allowed"] is True
    assert result["blocking_checks"] == []


def test_tool_operation_pass_fixture_is_executable() -> None:
    result = check_tool_operation(
        load_tool_operation_packet(FIXTURE_DIR / "creator_run_smoke_pass.json")
    )
    saved = json.loads(
        (FIXTURE_DIR / "creator_run_smoke_pass.check.json").read_text(encoding="utf-8")
    )

    assert result == saved
    assert saved["verdict"] == "pass"
    assert saved["allowed"] is True
    assert saved["blocking_checks"] == []


def test_tool_operation_check_rejects_stdout_only_success() -> None:
    result = check_tool_operation({
        "command": "python -m chip_labs.cli creator-run-smoke runs/demo",
        "exit_code": 0,
        "stdout": json.dumps(_smoke_result()),
    })

    assert result["verdict"] == "blocked"
    assert "parsed_result" in result["blocking_checks"]


def test_tool_operation_check_requires_rollback_note_for_failed_operation() -> None:
    result = check_tool_operation({
        "command": "python -m chip_labs.cli creator-run-smoke runs/demo --fail-on-blocked",
        "exit_code": 1,
        "result": _smoke_result("blocked"),
    })

    assert result["verdict"] == "blocked"
    assert "rollback_note" in result["blocking_checks"]
    assert result["rollback_report"]["required"] is True
    assert result["rollback_report"]["provided"] is False


def test_tool_operation_check_rejects_protected_and_secret_workflows() -> None:
    protected = check_tool_operation({
        "command": "git push origin main",
        "exit_code": 0,
        "result": {"schema_version": "unknown"},
    })
    secret = check_tool_operation({
        "command": "python -m chip_labs.cli creator-run-smoke runs/demo",
        "operator_request": "Ask the operator to paste token into docs.",
        "exit_code": 0,
        "result": _smoke_result(),
    })

    assert "protected_command" in protected["blocking_checks"]
    assert "secret_boundary" in secret["blocking_checks"]


def test_tool_operation_check_blocks_missing_expected_postconditions() -> None:
    result = check_tool_operation({
        "command": "python -m chip_labs.cli creator-run-smoke runs/demo",
        "exit_code": 0,
        "expected_postconditions": {
            "verdict": "ready_for_swarm_packet",
            "missing_paths_empty": True,
            "blocking_checks_empty": True,
            "automation_blocked": False,
        },
        "result": {
            **_smoke_result("prototype"),
            "missing_paths": ["reports/baseline.json"],
            "blocking_checks": [],
        },
        "rollback_note": "Keep the mission in scaffold state until missing reports exist.",
    })

    assert result["verdict"] == "blocked"
    assert "expected_verdict" in result["blocking_checks"]
    assert "expected_no_missing_paths" in result["blocking_checks"]
    assert result["rollback_report"]["required"] is True
    assert result["rollback_report"]["provided"] is True


def test_tool_operation_replay_fixtures_are_executable() -> None:
    expected_blockers = {
        "creator_run_smoke_pass.json": set(),
        "blocked_smoke_with_rollback.json": {"success_value"},
        "stale_evidence_recompute.json": {"success_value"},
        "missing_artifacts_expected_swarm.json": {
            "expected_verdict",
            "expected_no_missing_paths",
        },
        "unsafe_secret_request.json": {"secret_boundary"},
    }

    for fixture_name, blockers in expected_blockers.items():
        result = check_tool_operation(load_tool_operation_packet(FIXTURE_DIR / fixture_name))

        assert result["verdict"] == ("pass" if not blockers else "blocked")
        assert blockers.issubset(set(result["blocking_checks"]))
        assert result["rollback_report"]["required"] is bool(blockers)
        assert result["rollback_report"]["provided"] is bool(blockers)


def test_cli_tool_operation_check_outputs_packet(tmp_path: Path) -> None:
    input_path = tmp_path / "operation.json"
    output_path = tmp_path / "check.json"
    input_path.write_text(
        json.dumps({
            "command": "python -m chip_labs.cli creator-run-smoke runs/demo --recompute",
            "exit_code": 0,
            "result": _smoke_result(),
        }),
        encoding="utf-8",
    )
    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "tool-operation-check",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ],
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "tool_operation.check_result.v1"
    assert payload["verdict"] == "pass"
