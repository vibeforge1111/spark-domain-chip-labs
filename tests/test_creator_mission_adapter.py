from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from chip_labs.creator_mission_adapter import build_creator_mission_status


STARTUP_VALIDATION = Path(
    "docs/creator_system/examples/startup-yc-operator-validation/validation_plan.json"
)
PRODUCT_SURFACE_FIXTURE = Path(
    "docs/creator_system/examples/product-surface-readonly"
)
CREATOR_MISSION_SCHEMA = Path(
    "docs/creator_system/schemas/creator-mission-status.schema.json"
)
ARTIFACT_QUALITY_REPORT = Path(
    "docs/creator_system/examples/artifact-quality/good_design_pr.report.json"
)
TOOL_OPERATION_CHECK = Path(
    "docs/creator_system/examples/tool-operation/creator_run_smoke_pass.check.json"
)
MIROFISH_CONTENT_ROUTE = Path(
    "docs/creator_system/examples/mirofish-content/route-invoke.json"
)
RETRIEVAL_MEMORY_CHECK = Path(
    "docs/creator_system/examples/retrieval-memory/correct_prior_decision.check.json"
)


def _smoke(verdict: str = "ready_for_swarm_packet") -> dict[str, object]:
    blocked = verdict == "blocked"
    return {
        "schema_version": "adaptive_creator_loop.smoke_result.v1",
        "run_dir": "runs/demo",
        "verdict": verdict,
        "evidence_tier": "transfer_supported",
        "evidence_mode": "saved",
        "status_counts": {"pass": 68, "warn": 0, "fail": 0 if not blocked else 1},
        "blocking_checks": [] if not blocked else ["candidate_delta"],
        "warning_checks": [],
        "automation": {
            "blocked": blocked,
            "ci_exit_code": 1 if blocked else 0,
            "recommended_next_command": "Review provenance, privacy, rollback, and claim boundaries before publication.",
        },
        "checks": [],
        "missing_paths": [],
        "next_actions": [
            "Review provenance, trap status, rollback, and privacy boundary before network publication."
        ],
    }


def test_creator_mission_status_emits_read_only_surface_adapters() -> None:
    status = build_creator_mission_status(
        mission_id="mission-1",
        smoke=_smoke(),
        startup_validation=json.loads(STARTUP_VALIDATION.read_text(encoding="utf-8")),
    )

    assert status["schema_version"] == "adaptive_creator_loop.creator_mission_status.v1"
    assert status["read_only"] is True
    assert status["canonical"]["verdict"] == "ready_for_swarm_packet"
    assert status["canonical"]["stage_status"] == "review_required"
    assert status["publication"]["network_absorbable"] is False
    assert status["publication"]["swarm_shared_allowed"] is False
    assert set(status["surface_adapters"]) == {
        "builder",
        "telegram",
        "spawner",
        "canvas",
        "kanban",
    }
    assert status["surface_adapters"]["builder"]["may_mutate_state"] is False
    assert status["surface_adapters"]["spawner"]["may_execute"] is False
    assert status["surface_adapters"]["canvas"]["may_edit_artifacts"] is False
    assert status["surface_adapters"]["kanban"]["may_change_verdict"] is False
    canvas = status["surface_adapters"]["canvas"]
    node_ids = {node["id"] for node in canvas["nodes"]}
    assert {
        edge["from"] for edge in canvas["edges"] if edge["from"] != "creator_mission"
    }.issubset(node_ids)


def test_creator_mission_status_preserves_blockers_from_canonical_packets() -> None:
    status = build_creator_mission_status(
        smoke=_smoke("blocked"),
        doctor={
            "schema_version": "adaptive_creator_loop.doctor_result.v1",
            "verdict": "blocked",
            "repair_steps": [
                {
                    "action": "Regenerate benchmark reports, then rerun smoke.",
                }
            ],
            "smoke": {},
        },
    )

    assert status["canonical"]["stage_status"] == "blocked"
    assert status["blockers"][0]["source"] == "smoke"
    assert "Regenerate benchmark reports" in status["next_actions"][0]
    assert status["surface_adapters"]["kanban"]["columns"]["blocked"]


def test_blocked_creator_mission_status_stays_blocked_across_product_views() -> None:
    status = build_creator_mission_status(
        mission_id="blocked-product-view",
        publish_mode="swarm_shared",
        smoke=_smoke("blocked"),
        doctor={
            "schema_version": "adaptive_creator_loop.doctor_result.v1",
            "verdict": "blocked",
            "repair_steps": [
                {"action": "Regenerate stale evidence and rerun recompute smoke."}
            ],
            "smoke": {},
        },
        startup_validation=json.loads(STARTUP_VALIDATION.read_text(encoding="utf-8")),
    )

    assert status["canonical"]["stage_status"] == "blocked"
    assert status["publication"]["requested_network_absorption"] is True
    assert status["publication"]["swarm_shared_allowed"] is False
    assert status["publication"]["network_absorbable"] is False
    assert {blocker["source"] for blocker in status["blockers"]} == {
        "doctor",
        "smoke",
        "publication_gate",
    }

    builder = status["surface_adapters"]["builder"]
    telegram = status["surface_adapters"]["telegram"]
    spawner = status["surface_adapters"]["spawner"]
    canvas = status["surface_adapters"]["canvas"]
    kanban = status["surface_adapters"]["kanban"]

    assert builder["stage_status"] == "blocked"
    assert builder["may_mutate_state"] is False
    assert "Network absorption is not approved" in telegram["text"]
    assert telegram["may_request_secret_paste"] is False
    assert spawner["may_execute"] is False
    assert {blocker["source"] for blocker in spawner["blockers"]} == {
        "doctor",
        "smoke",
        "publication_gate",
    }
    assert canvas["may_edit_artifacts"] is False
    assert any(
        node["id"] == "creator_mission" and node["status"] == "blocked"
        for node in canvas["nodes"]
    )
    assert kanban["may_change_verdict"] is False
    assert kanban["columns"]["blocked"][0]["blocked"] is True


def test_creator_mission_status_blocks_swarm_publication_request() -> None:
    status = build_creator_mission_status(
        smoke=_smoke(),
        publish_mode="swarm_shared",
        startup_validation=json.loads(STARTUP_VALIDATION.read_text(encoding="utf-8")),
    )

    assert status["publication"]["requested_network_absorption"] is True
    assert status["publication"]["swarm_shared_allowed"] is False
    assert "publication_gate" in {blocker["source"] for blocker in status["blockers"]}
    assert "publication approval" in status["publication"]["blocked_reason"]
    assert "Network absorption is not approved" in status["surface_adapters"]["telegram"]["text"]


def test_cli_creator_mission_status_outputs_read_only_packet(tmp_path: Path) -> None:
    smoke_path = tmp_path / "smoke.json"
    output_path = tmp_path / "mission.json"
    smoke_path.write_text(json.dumps(_smoke(), indent=2) + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "creator-mission-status",
            "--smoke",
            str(smoke_path),
            "--startup-validation",
            str(STARTUP_VALIDATION),
            "--tool-operation",
            str(TOOL_OPERATION_CHECK),
            "--artifact-quality",
            str(ARTIFACT_QUALITY_REPORT),
            "--content-route",
            str(MIROFISH_CONTENT_ROUTE),
            "--retrieval-memory",
            str(RETRIEVAL_MEMORY_CHECK),
            "--mission-id",
            "mission-cli",
            "--output",
            str(output_path),
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["mission_id"] == "mission-cli"
    assert payload["surface_adapters"]["telegram"]["may_request_secret_paste"] is False
    tool_operation_summary = next(
        summary
        for summary in payload["source_packets"]
        if summary["packet"] == "tool_operation"
    )
    assert tool_operation_summary["present"] is True
    assert tool_operation_summary["state"] == "ready"
    content_route_summary = next(
        summary
        for summary in payload["source_packets"]
        if summary["packet"] == "content_route"
    )
    assert content_route_summary["present"] is True
    assert content_route_summary["state"] == "ready"
    artifact_quality_summary = next(
        summary
        for summary in payload["source_packets"]
        if summary["packet"] == "artifact_quality"
    )
    assert artifact_quality_summary["present"] is True
    assert artifact_quality_summary["state"] == "ready"
    retrieval_memory_summary = next(
        summary
        for summary in payload["source_packets"]
        if summary["packet"] == "retrieval_memory"
    )
    assert retrieval_memory_summary["present"] is True
    assert retrieval_memory_summary["state"] == "ready"


def test_product_surface_fixture_matches_current_adapter_output() -> None:
    smoke = json.loads((PRODUCT_SURFACE_FIXTURE / "startup-yc-smoke.json").read_text(encoding="utf-8"))
    doctor = json.loads((PRODUCT_SURFACE_FIXTURE / "startup-yc-doctor.json").read_text(encoding="utf-8"))
    startup_validation = json.loads(STARTUP_VALIDATION.read_text(encoding="utf-8"))
    tool_operation = json.loads(TOOL_OPERATION_CHECK.read_text(encoding="utf-8"))
    artifact_quality = json.loads(ARTIFACT_QUALITY_REPORT.read_text(encoding="utf-8"))
    content_route = json.loads(MIROFISH_CONTENT_ROUTE.read_text(encoding="utf-8"))
    retrieval_memory = json.loads(RETRIEVAL_MEMORY_CHECK.read_text(encoding="utf-8"))
    saved = json.loads(
        (PRODUCT_SURFACE_FIXTURE / "startup-yc-mission-status.json").read_text(encoding="utf-8")
    )

    rebuilt = build_creator_mission_status(
        mission_id="startup-yc-product-readonly",
        publish_mode="swarm_shared",
        smoke=smoke,
        doctor=doctor,
        tool_operation=tool_operation,
        artifact_quality=artifact_quality,
        content_route=content_route,
        retrieval_memory=retrieval_memory,
        startup_validation=startup_validation,
    )

    assert rebuilt == saved
    assert saved["read_only"] is True
    assert saved["canonical"]["verdict"] == "ready_for_swarm_packet"
    assert saved["canonical"]["stage_status"] == "review_required"
    assert saved["canonical"]["evidence_tier"] == "transfer_supported"
    assert saved["publication"]["publish_mode"] == "swarm_shared"
    assert saved["publication"]["swarm_shared_allowed"] is False
    assert saved["publication"]["network_absorbable"] is False
    assert saved["surface_adapters"]["builder"]["may_mutate_state"] is False
    assert saved["surface_adapters"]["telegram"]["may_request_secret_paste"] is False
    assert saved["surface_adapters"]["spawner"]["may_execute"] is False
    assert saved["surface_adapters"]["canvas"]["may_edit_artifacts"] is False
    assert saved["surface_adapters"]["kanban"]["may_change_verdict"] is False
    tool_operation_summary = next(
        summary
        for summary in saved["source_packets"]
        if summary["packet"] == "tool_operation"
    )
    assert tool_operation_summary == {
        "packet": "tool_operation",
        "present": True,
        "state": "ready",
        "verdict": "pass",
        "blocking_checks": [],
        "warning_count": 0,
        "claim_boundary": "tool_operation local postcondition check only",
    }
    artifact_quality_summary = next(
        summary
        for summary in saved["source_packets"]
        if summary["packet"] == "artifact_quality"
    )
    assert artifact_quality_summary == {
        "packet": "artifact_quality",
        "present": True,
        "state": "ready",
        "verdict": "review_ready",
        "blocking_checks": [],
        "warning_count": 0,
        "claim_boundary": "artifact_quality local review only",
    }
    content_route_summary = next(
        summary for summary in saved["source_packets"] if summary["packet"] == "content_route"
    )
    assert content_route_summary == {
        "packet": "content_route",
        "present": True,
        "state": "ready",
        "verdict": "invoke",
        "blocking_checks": [],
        "warning_count": 0,
        "claim_boundary": "candidate_review local simulator protocol only",
    }
    retrieval_memory_summary = next(
        summary
        for summary in saved["source_packets"]
        if summary["packet"] == "retrieval_memory"
    )
    assert retrieval_memory_summary == {
        "packet": "retrieval_memory",
        "present": True,
        "state": "ready",
        "verdict": "pass",
        "blocking_checks": [],
        "warning_count": 0,
        "claim_boundary": (
            "local retrieval-memory contract only; no production memory runtime or "
            "network-shareable recall claim"
        ),
    }
    canvas = saved["surface_adapters"]["canvas"]
    node_ids = {node["id"] for node in canvas["nodes"]}
    assert "tool_operation" in node_ids
    assert "artifact_quality" in node_ids
    assert "content_route" in node_ids
    assert "retrieval_memory" in node_ids
    assert {"from": "tool_operation", "to": "creator_mission"} in canvas["edges"]
    assert {"from": "artifact_quality", "to": "creator_mission"} in canvas["edges"]
    assert {"from": "content_route", "to": "creator_mission"} in canvas["edges"]
    assert {"from": "retrieval_memory", "to": "creator_mission"} in canvas["edges"]
    assert {
        edge["from"] for edge in canvas["edges"] if edge["from"] != "creator_mission"
    }.issubset(node_ids)


def test_creator_mission_status_schema_enforces_read_only_boundaries() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(CREATOR_MISSION_SCHEMA.read_text(encoding="utf-8"))
    saved = json.loads(
        (PRODUCT_SURFACE_FIXTURE / "startup-yc-mission-status.json").read_text(encoding="utf-8")
    )
    validator = jsonschema.Draft202012Validator(schema)

    validator.validate(saved)

    unsafe_network = json.loads(json.dumps(saved))
    unsafe_network["publication"]["network_absorbable"] = True
    assert list(validator.iter_errors(unsafe_network))

    unsafe_canvas = json.loads(json.dumps(saved))
    unsafe_canvas["surface_adapters"]["canvas"]["may_edit_artifacts"] = True
    assert list(validator.iter_errors(unsafe_canvas))

    unsafe_telegram = json.loads(json.dumps(saved))
    unsafe_telegram["surface_adapters"]["telegram"]["may_request_secret_paste"] = True
    assert list(validator.iter_errors(unsafe_telegram))
