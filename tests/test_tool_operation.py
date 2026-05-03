from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from chip_labs.tool_operation import (
    CLAIM_BOUNDARY,
    check_tool_operation,
    default_tool_operation_manifest,
    identify_operation,
    load_tool_operation_packet,
)


FIXTURE_DIR = Path("docs/creator_system/examples/tool-operation")
MANIFEST_SCHEMA = Path("docs/creator_system/schemas/tool-operation-manifest.schema.json")
PACKET_SCHEMA = Path("docs/creator_system/schemas/tool-operation-packet.schema.json")
CHECK_SCHEMA = Path("docs/creator_system/schemas/tool-operation-check.schema.json")


def _smoke_result(
    verdict: str = "ready_for_swarm_packet",
    *,
    evidence_mode: str = "saved",
) -> dict[str, object]:
    blocked = verdict == "blocked"
    return {
        "schema_version": "adaptive_creator_loop.smoke_result.v1",
        "verdict": verdict,
        "evidence_mode": evidence_mode,
        "status_counts": {"pass": 3, "warn": 0, "fail": 1 if blocked else 0},
        "automation": {"blocked": blocked, "ci_exit_code": 1 if blocked else 0},
        "checks": [],
    }


def _content_multi_seed_result(
    *,
    seed_count: int = 3,
    stable_top_candidate_ids: list[str] | None = None,
) -> dict[str, object]:
    stable = stable_top_candidate_ids if stable_top_candidate_ids is not None else ["candidate-1"]
    return {
        "packet_kind": "mirofish_content_multi_seed_result",
        "verdict": "candidate_review",
        "calibration_verdict": "pass",
        "seed_count": seed_count,
        "seed_results": [
            {
                "seed": seed,
                "verdict": "ranked",
                "calibration_verdict": "pass",
                "top_candidate_id": stable[0] if stable else None,
                "blocking_checks": [],
            }
            for seed in range(1, seed_count + 1)
        ],
        "blocking_checks": [],
        "stable_top_candidate_ids": stable,
        "network_absorbable": False,
    }


def _doctor_adversarial_sweep_result(
    *,
    case_count: int = 5,
    failed_case_ids: list[str] | None = None,
) -> dict[str, object]:
    failed = failed_case_ids or []
    return {
        "schema_version": "adaptive_creator_loop.doctor_adversarial_sweep.v1",
        "verdict": "pass" if not failed else "blocked",
        "case_count": case_count,
        "passed_case_count": case_count - len(failed),
        "failed_case_ids": failed,
        "schema_families": [
            "adapter_map",
            "candidate_report",
            "absorption_summary",
            "swarm_packet",
            "evidence_ladder",
        ],
        "network_absorbable": False,
        "rows": [],
    }


def test_tool_operation_manifest_lists_safe_creator_commands() -> None:
    manifest = default_tool_operation_manifest()

    assert manifest["schema_version"] == "tool_operation.manifest.v1"
    assert manifest["claim_boundary"] == CLAIM_BOUNDARY
    assert "creator-run-smoke" in manifest["supported_operations"]
    assert "creator-run-doctor-adversarial-sweep" in manifest["supported_operations"]
    assert "mirofish-content-multi-seed" in manifest["supported_operations"]
    assert "git push" in manifest["protected_command_markers"]


def test_identify_operation_detects_creator_run_smoke() -> None:
    command = "python -m chip_labs.cli creator-run-smoke runs/demo --recompute"

    assert identify_operation(command) == "creator-run-smoke"


def test_identify_operation_prefers_doctor_adversarial_sweep() -> None:
    command = "python -m chip_labs.cli creator-run-doctor-adversarial-sweep runs/demo"

    assert identify_operation(command) == "creator-run-doctor-adversarial-sweep"


def test_tool_operation_check_passes_with_parsed_postconditions() -> None:
    result = check_tool_operation({
        "command": "python -m chip_labs.cli creator-run-smoke runs/demo --recompute",
        "exit_code": 0,
        "expected_postconditions": {
            "verdict": "ready_for_swarm_packet",
            "blocking_checks_empty": True,
            "automation_blocked": False,
        },
        "result": _smoke_result(evidence_mode="recomputed"),
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


def test_tool_operation_check_requires_expected_postconditions_for_success() -> None:
    result = check_tool_operation({
        "command": "python -m chip_labs.cli creator-run-smoke runs/demo",
        "exit_code": 0,
        "result": _smoke_result(),
        "rollback_note": "Add expected postconditions before updating mission state.",
    })

    assert result["verdict"] == "blocked"
    assert "expected_postconditions_present" in result["blocking_checks"]


def test_tool_operation_check_rejects_recompute_mode_mismatch() -> None:
    result = check_tool_operation({
        "command": "python -m chip_labs.cli creator-run-smoke runs/demo --recompute",
        "exit_code": 0,
        "result": _smoke_result(evidence_mode="saved"),
        "rollback_note": "Rerun with --recompute and record the recomputed smoke packet.",
    })

    assert result["verdict"] == "blocked"
    assert "evidence_mode" in result["blocking_checks"]


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


def test_tool_operation_check_passes_content_multi_seed_postconditions() -> None:
    result = check_tool_operation({
        "command": (
            "python -m chip_labs.cli mirofish-content-multi-seed "
            "--task title --candidate A --candidate B --seed 1 --seed 2 --seed 3"
        ),
        "exit_code": 0,
        "expected_postconditions": {
            "verdict": "candidate_review",
            "blocking_checks_empty": True,
            "calibration_verdict": "pass",
            "network_absorbable": False,
            "minimum_seed_count": 3,
            "stable_top_candidate_required": True,
        },
        "result": _content_multi_seed_result(),
    })

    assert result["verdict"] == "pass"
    assert result["operation_key"] == "mirofish-content-multi-seed"
    assert result["blocking_checks"] == []


def test_tool_operation_check_blocks_unstable_content_multi_seed() -> None:
    result = check_tool_operation({
        "command": (
            "python -m chip_labs.cli mirofish-content-multi-seed "
            "--task title --candidate A --candidate B --seed 1"
        ),
        "exit_code": 0,
        "expected_postconditions": {
            "verdict": "candidate_review",
            "blocking_checks_empty": True,
            "calibration_verdict": "pass",
            "network_absorbable": False,
            "minimum_seed_count": 3,
            "stable_top_candidate_required": True,
        },
        "result": _content_multi_seed_result(seed_count=1, stable_top_candidate_ids=[]),
        "rollback_note": "Do not update mission state until seeded content simulation is stable.",
    })

    assert result["verdict"] == "blocked"
    assert "expected_minimum_seed_count" in result["blocking_checks"]
    assert "expected_stable_top_candidate" in result["blocking_checks"]


def test_tool_operation_check_passes_doctor_adversarial_sweep_postconditions() -> None:
    result = check_tool_operation({
        "command": (
            "python -m chip_labs.cli creator-run-doctor-adversarial-sweep "
            "runs/demo --manifest docs/creator_system/examples/doctor-security/"
            "adversarial_schema_sweep.json --fail-on-blocked"
        ),
        "exit_code": 0,
        "expected_postconditions": {
            "verdict": "pass",
            "network_absorbable": False,
            "minimum_case_count": 5,
            "failed_case_ids_empty": True,
            "schema_families_include": [
                "adapter_map",
                "candidate_report",
                "absorption_summary",
                "swarm_packet",
                "evidence_ladder",
            ],
        },
        "result": _doctor_adversarial_sweep_result(),
    })

    assert result["verdict"] == "pass"
    assert result["operation_key"] == "creator-run-doctor-adversarial-sweep"
    assert result["blocking_checks"] == []


def test_tool_operation_check_blocks_incomplete_doctor_adversarial_sweep() -> None:
    result = check_tool_operation({
        "command": "python -m chip_labs.cli creator-run-doctor-adversarial-sweep runs/demo",
        "exit_code": 0,
        "expected_postconditions": {
            "verdict": "pass",
            "network_absorbable": False,
            "minimum_case_count": 5,
            "failed_case_ids_empty": True,
            "schema_families_include": ["adapter_map", "swarm_packet", "evidence_ladder"],
        },
        "result": {
            **_doctor_adversarial_sweep_result(
                case_count=4,
                failed_case_ids=["swarm-packet-tier-escalation"],
            ),
            "schema_families": ["adapter_map", "swarm_packet"],
        },
        "rollback_note": "Do not trust doctor-sweep state until all schema families pass.",
    })

    assert result["verdict"] == "blocked"
    assert "success_value" in result["blocking_checks"]
    assert "expected_minimum_case_count" in result["blocking_checks"]
    assert "expected_no_failed_case_ids" in result["blocking_checks"]
    assert "expected_schema_families" in result["blocking_checks"]


def test_tool_operation_replay_fixtures_are_executable() -> None:
    expected_blockers = {
        "creator_run_smoke_pass.json": set(),
        "mirofish_content_multi_seed_pass.json": set(),
        "doctor_adversarial_sweep_pass.json": set(),
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
            "expected_postconditions": {
                "verdict": "ready_for_swarm_packet",
                "blocking_checks_empty": True,
                "automation_blocked": False,
            },
            "result": _smoke_result(evidence_mode="recomputed"),
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


def test_tool_operation_schemas_validate_fixture_suite() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    manifest_schema = json.loads(MANIFEST_SCHEMA.read_text(encoding="utf-8"))
    packet_schema = json.loads(PACKET_SCHEMA.read_text(encoding="utf-8"))
    check_schema = json.loads(CHECK_SCHEMA.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator(manifest_schema).validate(
        default_tool_operation_manifest()
    )
    for fixture_path in sorted(FIXTURE_DIR.glob("*.json")):
        if fixture_path.name.endswith(".check.json"):
            packet = json.loads(fixture_path.read_text(encoding="utf-8"))
        else:
            packet = load_tool_operation_packet(fixture_path)
            jsonschema.Draft202012Validator(packet_schema).validate(packet)
            packet = check_tool_operation(packet)
        jsonschema.Draft202012Validator(check_schema).validate(packet)


def test_tool_operation_schemas_reject_unsafe_shapes() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    packet_schema = json.loads(PACKET_SCHEMA.read_text(encoding="utf-8"))
    check_schema = json.loads(CHECK_SCHEMA.read_text(encoding="utf-8"))
    packet = load_tool_operation_packet(FIXTURE_DIR / "creator_run_smoke_pass.json")
    check = check_tool_operation(packet)

    packet["expected_postconditions"]["network_absorbable"] = True
    check["verdict"] = "blocked"
    check["allowed"] = True

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(packet_schema).validate(packet)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(check_schema).validate(check)
