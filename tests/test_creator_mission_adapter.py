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


def _smoke(
    verdict: str = "ready_for_swarm_packet",
    evidence_mode: str = "saved",
) -> dict[str, object]:
    blocked = verdict == "blocked"
    return {
        "schema_version": "adaptive_creator_loop.smoke_result.v1",
        "run_dir": "runs/demo",
        "verdict": verdict,
        "evidence_tier": "transfer_supported",
        "evidence_mode": evidence_mode,
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


def _generated_multi_seed_summary(verdict: str = "candidate_review") -> dict[str, object]:
    blocked = verdict == "blocked"
    return {
        "schema_version": "adaptive_creator_loop.generated_multi_seed_validation.v1",
        "matrix": {
            "domain_family_count": 6,
            "variants_per_domain": 3,
            "seed_count": 2,
            "completed_run_count": 36,
        },
        "verdict": verdict,
        "evidence_tier": "candidate_review",
        "evidence_mode": "recomputed",
        "network_absorbable": False,
        "aggregate_hidden_failures": False,
        "passed_run_count": 35 if blocked else 36,
        "blocked_run_count": 1 if blocked else 0,
        "failed_seed_ids": ["doctor_security_variant_2_seed_2"] if blocked else [],
        "blocking_checks": ["unsafe_promotion_trap"] if blocked else [],
        "warning_checks": [],
        "claim_boundary": (
            "generated multi-seed factory proof only; does not approve network absorption"
        ),
        "rows": [],
        "next_actions": [],
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
    assert status["canonical"]["evidence_mode"] == "saved"
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
    assert status["surface_adapters"]["builder"]["evidence_mode"] == "saved"
    assert "Evidence mode: `saved`." in status["surface_adapters"]["telegram"]["text"]
    assert status["surface_adapters"]["spawner"]["may_execute"] is False
    assert status["surface_adapters"]["spawner"]["evidence_mode"] == "saved"
    assert status["surface_adapters"]["canvas"]["may_edit_artifacts"] is False
    assert status["surface_adapters"]["kanban"]["may_change_verdict"] is False
    canvas = status["surface_adapters"]["canvas"]
    mission_node = next(node for node in canvas["nodes"] if node["id"] == "creator_mission")
    assert mission_node["evidence_mode"] == "saved"
    node_ids = {node["id"] for node in canvas["nodes"]}
    assert {
        edge["from"] for edge in canvas["edges"] if edge["from"] != "creator_mission"
    }.issubset(node_ids)
    assert status["surface_adapters"]["kanban"]["columns"]["review_required"][0][
        "evidence_mode"
    ] == "saved"


def test_creator_mission_status_propagates_recomputed_evidence_mode() -> None:
    status = build_creator_mission_status(
        mission_id="mission-recomputed",
        smoke=_smoke(evidence_mode="recomputed"),
    )

    assert status["canonical"]["evidence_mode"] == "recomputed"
    assert status["surface_adapters"]["builder"]["evidence_mode"] == "recomputed"
    assert status["surface_adapters"]["spawner"]["evidence_mode"] == "recomputed"
    assert "Evidence mode: `recomputed`." in status["surface_adapters"]["telegram"]["text"]
    mission_node = next(
        node
        for node in status["surface_adapters"]["canvas"]["nodes"]
        if node["id"] == "creator_mission"
    )
    assert mission_node["evidence_mode"] == "recomputed"
    assert status["surface_adapters"]["kanban"]["columns"]["review_required"][0][
        "evidence_mode"
    ] == "recomputed"


def test_creator_mission_status_projects_generated_multi_seed_evidence() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(CREATOR_MISSION_SCHEMA.read_text(encoding="utf-8"))
    status = build_creator_mission_status(
        mission_id="mission-generated-matrix",
        smoke=_smoke(evidence_mode="recomputed"),
        generated_multi_seed=_generated_multi_seed_summary(),
    )

    jsonschema.Draft202012Validator(schema).validate(status)
    source = next(
        summary
        for summary in status["source_packets"]
        if summary["packet"] == "generated_multi_seed"
    )
    assert source["state"] == "ready"
    assert source["run_count"] == 36
    assert source["passed_run_count"] == 36
    assert source["aggregate_hidden_failures"] is False
    assert source["network_absorbable"] is False
    assert "Generated multi-seed: `36/36` rows passed." in status[
        "surface_adapters"
    ]["telegram"]["text"]
    assert status["surface_adapters"]["builder"]["generated_multi_seed"] == {
        "state": "ready",
        "verdict": "candidate_review",
        "run_count": 36,
        "passed_run_count": 36,
        "blocked_run_count": 0,
        "failed_seed_ids": [],
        "aggregate_hidden_failures": False,
        "evidence_mode": "recomputed",
        "network_absorbable": False,
    }
    assert status["surface_adapters"]["spawner"]["may_execute"] is False
    assert "generated_multi_seed" in {
        edge["from"] for edge in status["surface_adapters"]["canvas"]["edges"]
    }
    kanban_card = status["surface_adapters"]["kanban"]["columns"]["review_required"][0]
    assert kanban_card["generated_multi_seed"]["run_count"] == 36


def test_creator_mission_status_blocks_failed_generated_multi_seed_evidence() -> None:
    status = build_creator_mission_status(
        mission_id="mission-generated-matrix-blocked",
        smoke=_smoke(evidence_mode="recomputed"),
        generated_multi_seed=_generated_multi_seed_summary("blocked"),
    )

    assert status["canonical"]["stage_status"] == "blocked"
    assert "generated_multi_seed" in {blocker["source"] for blocker in status["blockers"]}
    assert status["surface_adapters"]["builder"]["generated_multi_seed"][
        "failed_seed_ids"
    ] == ["doctor_security_variant_2_seed_2"]
    assert "Generated multi-seed: `35/36` rows passed." in status[
        "surface_adapters"
    ]["telegram"]["text"]


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
    generated_multi_seed_path = tmp_path / "generated-multi-seed.json"
    output_path = tmp_path / "mission.json"
    smoke_path.write_text(json.dumps(_smoke(), indent=2) + "\n", encoding="utf-8")
    generated_multi_seed_path.write_text(
        json.dumps(_generated_multi_seed_summary(), indent=2) + "\n",
        encoding="utf-8",
    )

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
            "--generated-multi-seed",
            str(generated_multi_seed_path),
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
    generated_multi_seed_summary = next(
        summary
        for summary in payload["source_packets"]
        if summary["packet"] == "generated_multi_seed"
    )
    assert generated_multi_seed_summary["present"] is True
    assert generated_multi_seed_summary["run_count"] == 36
    assert "Generated multi-seed: `36/36` rows passed." in payload[
        "surface_adapters"
    ]["telegram"]["text"]


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
    assert saved["canonical"]["evidence_mode"] == "saved"
    assert saved["publication"]["publish_mode"] == "swarm_shared"
    assert saved["publication"]["swarm_shared_allowed"] is False
    assert saved["publication"]["network_absorbable"] is False
    assert saved["surface_adapters"]["builder"]["may_mutate_state"] is False
    assert saved["surface_adapters"]["builder"]["evidence_mode"] == "saved"
    assert "Evidence mode: `saved`." in saved["surface_adapters"]["telegram"]["text"]
    assert saved["surface_adapters"]["telegram"]["may_request_secret_paste"] is False
    assert saved["surface_adapters"]["spawner"]["may_execute"] is False
    assert saved["surface_adapters"]["spawner"]["evidence_mode"] == "saved"
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
    mission_node = next(node for node in canvas["nodes"] if node["id"] == "creator_mission")
    assert mission_node["evidence_mode"] == "saved"
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
    kanban_cards = [
        card
        for cards in saved["surface_adapters"]["kanban"]["columns"].values()
        for card in cards
    ]
    kanban_card = next(
        card
        for card in kanban_cards
        if card["mission_id"] == "startup-yc-product-readonly"
    )
    assert kanban_card["evidence_mode"] == "saved"


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

    missing_canvas_mode = json.loads(json.dumps(saved))
    mission_node = next(
        node
        for node in missing_canvas_mode["surface_adapters"]["canvas"]["nodes"]
        if node["id"] == "creator_mission"
    )
    del mission_node["evidence_mode"]
    assert list(validator.iter_errors(missing_canvas_mode))

    missing_kanban_mode = json.loads(json.dumps(saved))
    kanban_card = next(
        card
        for cards in missing_kanban_mode["surface_adapters"]["kanban"]["columns"].values()
        for card in cards
    )
    del kanban_card["evidence_mode"]
    assert list(validator.iter_errors(missing_kanban_mode))
