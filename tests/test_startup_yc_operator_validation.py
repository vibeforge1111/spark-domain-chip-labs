from __future__ import annotations

import json
import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

from chip_labs.startup_yc_promotion import (
    check_startup_yc_heldout_validation,
    check_startup_yc_multi_seed_validation,
    check_startup_yc_promotion_evidence,
    check_startup_yc_promotion_gates,
    check_startup_yc_review_gates,
    check_startup_yc_validation_evidence_shape,
    run_startup_yc_validation_suite,
)


FIXTURE_DIR = Path("docs/creator_system/examples/startup-yc-operator-validation")
SHAPE_ONLY_MULTI_SEED_EVIDENCE = FIXTURE_DIR / "shape_only_multi_seed_evidence.json"
GATE_CHECK_SCHEMA = Path(
    "docs/creator_system/schemas/startup-yc-gate-check-result.schema.json"
)
VALIDATION_EVIDENCE_SCHEMA = Path(
    "docs/creator_system/schemas/startup-yc-validation-evidence.schema.json"
)
VALIDATION_EVIDENCE_CHECK_RESULT_SCHEMA = Path(
    "docs/creator_system/schemas/startup-yc-validation-evidence-check-result.schema.json"
)
VALIDATION_SUITE_SCHEMA = Path(
    "docs/creator_system/schemas/startup-yc-validation-suite.schema.json"
)


def test_startup_yc_validation_plan_blocks_network_absorption() -> None:
    plan = _load_plan()

    assert plan["current_claim"] == "transfer_supported"
    assert "network_absorbable" in plan["prohibited_claims"]
    assert plan["publication_boundary"]["network_publication_allowed"] is False
    assert set(plan["required_promotion_gates"]) == {
        "multi_seed_validation",
        "held_out_founder_advice_pass",
        "human_operator_calibration",
        "privacy_review",
        "rollback_review",
        "publication_approval",
    }
    assert plan["minimum_multi_seed_plan"]["minimum_seeds_per_track"] >= 5
    assert plan["minimum_multi_seed_plan"]["negative_row_policy"] == (
        "block_network_absorption"
    )


def test_startup_yc_held_out_cases_cover_operator_traps() -> None:
    plan = _load_plan()
    cases = _load_jsonl(FIXTURE_DIR / plan["held_out_cases_path"])
    case_kinds = {case["case_kind"] for case in cases}

    assert len(cases) >= 5
    assert {
        "demand_reality",
        "vanity_metric_trap",
        "narrow_wedge",
        "finance_default_alive",
        "privacy_boundary",
    }.issubset(case_kinds)
    assert any(
        "traction_from_vanity_metrics" in case["reject_claims"]
        for case in cases
        if case["case_kind"] == "vanity_metric_trap"
    )
    assert all(case["promotion_tier_ceiling"] == "transfer_supported" for case in cases)
    assert all(case["expected_operator_moves"] for case in cases)
    assert all(case["success_gate"] for case in cases)


def test_startup_yc_review_docs_keep_required_gates_visible() -> None:
    plan = _load_plan()
    calibration = (FIXTURE_DIR / plan["operator_calibration_checklist_path"]).read_text(
        encoding="utf-8"
    )
    publication = (
        FIXTURE_DIR / plan["privacy_rollback_publication_review_path"]
    ).read_text(encoding="utf-8")

    for required_text in (
        "Multi-seed validation",
        "Held-out founder advice",
        "Operator calibration",
        "Privacy review",
        "Rollback review",
        "Publication approval",
    ):
        assert required_text in calibration
    assert "workspace-only" in publication
    assert "network_absorbable" in publication
    assert "private founder/customer details" in publication


def test_startup_yc_promotion_gate_check_blocks_network_absorption() -> None:
    result = check_startup_yc_promotion_gates(FIXTURE_DIR / "validation_plan.json")

    assert result["schema_version"] == (
        "adaptive_creator_loop.startup_yc_promotion_gate_check.v1"
    )
    assert result["verdict"] == "blocked"
    assert result["network_absorbable"] is False
    assert result["requested_claim"] == "network_absorbable"
    assert "prohibited_claim:network_absorbable" in result["blocking_checks"]
    assert "publication_boundary:network_publication_allowed" in result[
        "blocking_checks"
    ]
    assert result["missing_gates"] == _load_plan()["required_promotion_gates"]
    assert all(item["present"] is True for item in result["evidence_paths"])


def test_startup_yc_multi_seed_check_blocks_without_evidence() -> None:
    result = check_startup_yc_multi_seed_validation(FIXTURE_DIR / "validation_plan.json")

    assert result["schema_version"] == (
        "adaptive_creator_loop.startup_yc_multi_seed_check.v1"
    )
    assert result["verdict"] == "blocked"
    assert result["gate_passed"] is False
    assert result["network_absorbable"] is False
    assert "missing_evidence_path:multi_seed_evidence_path" in result[
        "blocking_checks"
    ]
    assert result["underfilled_tracks"]


def test_startup_yc_shape_only_fixture_does_not_pass_multi_seed_gate() -> None:
    result = check_startup_yc_multi_seed_validation(
        FIXTURE_DIR / "validation_plan.json",
        evidence_path=SHAPE_ONLY_MULTI_SEED_EVIDENCE.resolve(),
    )

    assert result["verdict"] == "blocked"
    assert result["gate_passed"] is False
    assert result["network_absorbable"] is False
    assert result["track_counts"]["gtm"] == 1
    assert "missing_track:finance" in result["blocking_checks"]
    assert "underfilled_track:gtm:1/5" in result["blocking_checks"]


def test_startup_yc_multi_seed_check_passes_only_the_multi_seed_gate(
    tmp_path: Path,
) -> None:
    plan = _load_plan()
    tracks = plan["minimum_multi_seed_plan"]["tracks"]
    rows = [
        {
            "seed_id": f"{track}-{index}",
            "track": track,
            "baseline_score": 0.5,
            "candidate_score": 0.6,
            "constraints_passed": True,
            "held_out_passed": True,
        }
        for track in tracks
        for index in range(1, 6)
    ]
    evidence_path = tmp_path / "multi_seed_evidence.json"
    evidence_path.write_text(json.dumps({"rows": rows}, indent=2), encoding="utf-8")

    result = check_startup_yc_multi_seed_validation(
        FIXTURE_DIR / "validation_plan.json",
        evidence_path=evidence_path,
    )

    assert result["verdict"] == "passed"
    assert result["gate_passed"] is True
    assert result["network_absorbable"] is False
    assert result["blocking_checks"] == []
    assert result["track_counts"] == {track: 5 for track in tracks}


def test_startup_yc_multi_seed_check_blocks_negative_rows(tmp_path: Path) -> None:
    evidence_path = tmp_path / "multi_seed_evidence.json"
    evidence_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "seed_id": "gtm-negative-1",
                        "track": "gtm",
                        "baseline_score": 0.7,
                        "candidate_score": 0.5,
                        "constraints_passed": True,
                        "held_out_passed": True,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = check_startup_yc_multi_seed_validation(
        FIXTURE_DIR / "validation_plan.json",
        evidence_path=evidence_path,
    )

    assert result["verdict"] == "blocked"
    assert result["gate_passed"] is False
    assert {
        "seed_id": "gtm-negative-1",
        "track": "gtm",
        "reason": "negative_delta",
    } in result["row_failures"]
    assert "row_failure:gtm-negative-1:negative_delta" in result["blocking_checks"]


def test_startup_yc_heldout_check_blocks_without_evidence() -> None:
    result = check_startup_yc_heldout_validation(FIXTURE_DIR / "validation_plan.json")

    assert result["schema_version"] == (
        "adaptive_creator_loop.startup_yc_heldout_check.v1"
    )
    assert result["verdict"] == "blocked"
    assert result["gate_passed"] is False
    assert result["network_absorbable"] is False
    assert result["case_count"] >= 5
    assert "missing_evidence_path:held_out_evidence_path" in result[
        "blocking_checks"
    ]
    assert result["missing_cases"]


def test_startup_yc_heldout_check_passes_only_the_heldout_gate(
    tmp_path: Path,
) -> None:
    plan = _load_plan()
    cases = _load_jsonl(FIXTURE_DIR / plan["held_out_cases_path"])
    rows = [
        {
            "case_id": case["case_id"],
            "passed": True,
            "operator_moves_covered": True,
            "reject_claims_avoided": True,
            "success_gate_met": True,
            "privacy_lane_respected": True,
        }
        for case in cases
    ]
    evidence_path = tmp_path / "heldout_evidence.json"
    evidence_path.write_text(json.dumps({"rows": rows}, indent=2), encoding="utf-8")

    result = check_startup_yc_heldout_validation(
        FIXTURE_DIR / "validation_plan.json",
        evidence_path=evidence_path,
    )

    assert result["verdict"] == "passed"
    assert result["gate_passed"] is True
    assert result["network_absorbable"] is False
    assert result["blocking_checks"] == []
    assert result["passed_case_count"] == len(cases)


def test_startup_yc_heldout_check_blocks_failed_claim_rejection(
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "heldout_evidence.json"
    evidence_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "case_id": "vanity-growth-trap",
                        "passed": False,
                        "operator_moves_covered": True,
                        "reject_claims_avoided": False,
                        "success_gate_met": False,
                        "privacy_lane_respected": True,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = check_startup_yc_heldout_validation(
        FIXTURE_DIR / "validation_plan.json",
        evidence_path=evidence_path,
    )

    assert result["verdict"] == "blocked"
    assert result["gate_passed"] is False
    assert {
        "case_id": "vanity-growth-trap",
        "reason": "reject_claims_avoided_failed",
    } in result["case_failures"]
    assert "case_failure:vanity-growth-trap:reject_claims_avoided_failed" in result[
        "blocking_checks"
    ]


def test_startup_yc_review_gates_check_blocks_without_evidence() -> None:
    result = check_startup_yc_review_gates(FIXTURE_DIR / "validation_plan.json")

    assert result["schema_version"] == (
        "adaptive_creator_loop.startup_yc_review_gates_check.v1"
    )
    assert result["verdict"] == "blocked"
    assert result["gate_passed"] is False
    assert result["network_absorbable"] is False
    assert set(result["missing_gates"]) == {
        "human_operator_calibration",
        "privacy_review",
        "rollback_review",
        "publication_approval",
    }
    assert "missing_evidence_path:review_gate_evidence_path" in result[
        "blocking_checks"
    ]


def test_startup_yc_review_gates_check_passes_only_review_gates(
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "review_gate_evidence.json"
    evidence_path.write_text(
        json.dumps(
            {
                "gates": {
                    "human_operator_calibration": {
                        "passed": True,
                        "reviewer": "operator",
                        "evidence_ref": "calibration-review-1",
                        "calibration_notes": "Reviewed held-out advice quality.",
                    },
                    "privacy_review": {
                        "passed": True,
                        "reviewer": "operator",
                        "evidence_ref": "privacy-review-1",
                        "privacy_lane_decision": "No private founder details leave local lane.",
                    },
                    "rollback_review": {
                        "passed": True,
                        "reviewer": "operator",
                        "evidence_ref": "rollback-review-1",
                        "rollback_rule": "Revoke promotion on stale or negative evidence.",
                    },
                    "publication_approval": {
                        "passed": True,
                        "reviewer": "operator",
                        "evidence_ref": "publication-review-1",
                        "publication_decision": "Approved for network_absorbable only after all gates pass.",
                        "approved_claim": "network_absorbable",
                        "network_publication_allowed": True,
                    },
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = check_startup_yc_review_gates(
        FIXTURE_DIR / "validation_plan.json",
        evidence_path=evidence_path,
    )

    assert result["verdict"] == "passed"
    assert result["gate_passed"] is True
    assert result["network_absorbable"] is False
    assert result["blocking_checks"] == []
    assert all(result["gate_status"].values())


def test_startup_yc_review_gates_check_blocks_unsafe_publication(
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "review_gate_evidence.json"
    evidence_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "gate": "publication_approval",
                        "passed": True,
                        "reviewer": "operator",
                        "evidence_ref": "publication-review-1",
                        "publication_decision": "Do not publish.",
                        "approved_claim": "transfer_supported",
                        "network_publication_allowed": False,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = check_startup_yc_review_gates(
        FIXTURE_DIR / "validation_plan.json",
        evidence_path=evidence_path,
    )

    assert result["verdict"] == "blocked"
    assert "gate_failure:publication_approval:network_publication_not_allowed" in result[
        "blocking_checks"
    ]
    assert "gate_failure:publication_approval:approved_claim_missing" in result[
        "blocking_checks"
    ]


def test_startup_yc_promotion_evidence_check_blocks_without_bundle() -> None:
    result = check_startup_yc_promotion_evidence(FIXTURE_DIR / "validation_plan.json")

    assert result["schema_version"] == (
        "adaptive_creator_loop.startup_yc_promotion_evidence_check.v1"
    )
    assert result["verdict"] == "blocked"
    assert result["all_required_gates_supported"] is False
    assert result["network_absorbable"] is False
    assert "missing_evidence_path:promotion_evidence_bundle_path" in result[
        "blocking_checks"
    ]
    assert result["missing_gates"] == _load_plan()["required_promotion_gates"]


def test_startup_yc_promotion_evidence_check_passes_only_evidence_support(
    tmp_path: Path,
) -> None:
    plan_path = FIXTURE_DIR / "validation_plan.json"
    (
        multi_seed_evidence_path,
        heldout_evidence_path,
        review_gate_evidence_path,
    ) = _write_raw_validation_evidence(tmp_path)
    multi_seed_output_path = _write_gate_output(
        tmp_path / "multi-seed.json",
        "adaptive_creator_loop.startup_yc_multi_seed_check.v1",
        plan_path,
        gate_passed=True,
        evidence_path=multi_seed_evidence_path,
    )
    heldout_output_path = _write_gate_output(
        tmp_path / "heldout.json",
        "adaptive_creator_loop.startup_yc_heldout_check.v1",
        plan_path,
        gate_passed=True,
        evidence_path=heldout_evidence_path,
    )
    review_output_path = _write_gate_output(
        tmp_path / "review-gates.json",
        "adaptive_creator_loop.startup_yc_review_gates_check.v1",
        plan_path,
        gate_passed=True,
        evidence_path=review_gate_evidence_path,
        gate_status={
            "human_operator_calibration": True,
            "privacy_review": True,
            "rollback_review": True,
            "publication_approval": True,
        },
    )
    bundle_path = tmp_path / "promotion-evidence-bundle.json"
    bundle_path.write_text(
        json.dumps(
                {
                    "checks": {
                        "multi_seed_validation": str(multi_seed_output_path),
                        "held_out_founder_advice_pass": str(heldout_output_path),
                        "review_gates": str(review_output_path),
                    }
                },
                indent=2,
        ),
        encoding="utf-8",
    )

    result = check_startup_yc_promotion_evidence(
        plan_path,
        evidence_bundle_path=bundle_path,
    )

    assert result["verdict"] == "passed"
    assert result["all_required_gates_supported"] is True
    assert result["network_absorbable"] is False
    assert result["missing_gates"] == []
    assert result["blocking_checks"] == []
    assert all(result["gate_support"].values())


def test_startup_yc_promotion_evidence_blocks_stale_gate_provenance(
    tmp_path: Path,
) -> None:
    plan_path = FIXTURE_DIR / "validation_plan.json"
    (
        multi_seed_evidence_path,
        heldout_evidence_path,
        review_gate_evidence_path,
    ) = _write_raw_validation_evidence(tmp_path)
    multi_seed_output_path = _write_gate_output(
        tmp_path / "multi-seed.json",
        "adaptive_creator_loop.startup_yc_multi_seed_check.v1",
        plan_path,
        gate_passed=True,
        evidence_path=multi_seed_evidence_path,
    )
    heldout_output_path = _write_gate_output(
        tmp_path / "heldout.json",
        "adaptive_creator_loop.startup_yc_heldout_check.v1",
        plan_path,
        gate_passed=True,
        evidence_path=heldout_evidence_path,
    )
    review_output_path = _write_gate_output(
        tmp_path / "review-gates.json",
        "adaptive_creator_loop.startup_yc_review_gates_check.v1",
        plan_path,
        gate_passed=True,
        evidence_path=review_gate_evidence_path,
        gate_status={
            "human_operator_calibration": True,
            "privacy_review": True,
            "rollback_review": True,
            "publication_approval": True,
        },
    )
    bundle_path = tmp_path / "promotion-evidence-bundle.json"
    bundle_path.write_text(
        json.dumps(
            {
                "checks": {
                    "multi_seed_validation": str(multi_seed_output_path),
                    "held_out_founder_advice_pass": str(heldout_output_path),
                    "review_gates": str(review_output_path),
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    multi_seed_evidence_path.write_text(
        json.dumps({"rows": []}, indent=2),
        encoding="utf-8",
    )

    result = check_startup_yc_promotion_evidence(
        plan_path,
        evidence_bundle_path=bundle_path,
    )

    assert result["verdict"] == "blocked"
    assert "provenance_mismatch:multi_seed_validation" in result["blocking_checks"]
    assert result["gate_support"]["multi_seed_validation"] is False


def test_startup_yc_promotion_evidence_check_blocks_stale_plan_output(
    tmp_path: Path,
) -> None:
    multi_seed_path = _write_gate_output(
        tmp_path / "multi-seed.json",
        "adaptive_creator_loop.startup_yc_multi_seed_check.v1",
        Path("other-plan.json"),
        gate_passed=True,
    )
    bundle_path = tmp_path / "promotion-evidence-bundle.json"
    bundle_path.write_text(
        json.dumps(
            {
                "checks": {
                    "multi_seed_validation": str(multi_seed_path),
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = check_startup_yc_promotion_evidence(
        FIXTURE_DIR / "validation_plan.json",
        evidence_bundle_path=bundle_path,
    )

    assert result["verdict"] == "blocked"
    assert "plan_mismatch:multi_seed_validation" in result["blocking_checks"]
    assert "missing_check_output:held_out_founder_advice_pass" in result[
        "blocking_checks"
    ]
    assert "missing_check_output:review_gates" in result["blocking_checks"]


def test_startup_yc_validation_suite_blocks_without_evidence() -> None:
    result = run_startup_yc_validation_suite(FIXTURE_DIR / "validation_plan.json")

    assert result["schema_version"] == (
        "adaptive_creator_loop.startup_yc_validation_suite.v1"
    )
    assert result["verdict"] == "blocked"
    assert result["required_subchecks_passed"] is False
    assert result["final_promotion_ready"] is False
    assert result["network_absorbable"] is False
    assert "subcheck_blocked:promotion_gates" in result["blocking_checks"]
    assert "subcheck_blocked:multi_seed_validation" in result["blocking_checks"]
    assert "subcheck_blocked:held_out_founder_advice_pass" in result[
        "blocking_checks"
    ]
    assert "subcheck_blocked:review_gates" in result["blocking_checks"]
    assert "subcheck_blocked:promotion_evidence_bundle" in result["blocking_checks"]


def test_saved_startup_yc_validation_suite_fixture_matches_current_blockers() -> None:
    saved = json.loads(
        (FIXTURE_DIR / "validation_suite_blocked.json").read_text(encoding="utf-8")
    )
    current = run_startup_yc_validation_suite(FIXTURE_DIR / "validation_plan.json")

    assert saved["schema_version"] == current["schema_version"]
    assert saved["plan_id"] == current["plan_id"]
    assert saved["current_claim"] == "transfer_supported"
    assert saved["requested_claim"] == "network_absorbable"
    assert saved["verdict"] == current["verdict"] == "blocked"
    assert saved["required_subchecks_passed"] is False
    assert saved["final_promotion_ready"] is False
    assert saved["network_absorbable"] is False
    assert saved["blocking_checks"] == current["blocking_checks"]
    assert {
        name: result["verdict"]
        for name, result in saved["subchecks"].items()
    } == {
        name: result["verdict"]
        for name, result in current["subchecks"].items()
    }


def test_startup_yc_validation_suite_schema_blocks_network_absorption() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    referencing = pytest.importorskip("referencing")
    schema = json.loads(VALIDATION_SUITE_SCHEMA.read_text(encoding="utf-8"))
    gate_schema = json.loads(GATE_CHECK_SCHEMA.read_text(encoding="utf-8"))
    saved = json.loads(
        (FIXTURE_DIR / "validation_suite_blocked.json").read_text(encoding="utf-8")
    )
    registry = referencing.Registry().with_resource(
        gate_schema["$id"],
        referencing.Resource.from_contents(gate_schema),
    )
    validator = jsonschema.Draft202012Validator(schema, registry=registry)

    validator.validate(saved)

    unsafe = json.loads(json.dumps(saved))
    unsafe["network_absorbable"] = True
    assert list(validator.iter_errors(unsafe))

    malformed_subcheck = json.loads(json.dumps(saved))
    del malformed_subcheck["subchecks"]["multi_seed_validation"]["provenance"]
    assert list(validator.iter_errors(malformed_subcheck))


def test_startup_yc_gate_check_schema_blocks_network_absorption(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(GATE_CHECK_SCHEMA.read_text(encoding="utf-8"))
    plan_path = FIXTURE_DIR / "validation_plan.json"
    (
        multi_seed_evidence_path,
        heldout_evidence_path,
        review_gate_evidence_path,
    ) = _write_raw_validation_evidence(tmp_path)
    multi_seed_path = _write_gate_output(
        tmp_path / "multi-seed.json",
        "adaptive_creator_loop.startup_yc_multi_seed_check.v1",
        plan_path,
        gate_passed=True,
        evidence_path=multi_seed_evidence_path,
    )
    heldout_path = _write_gate_output(
        tmp_path / "heldout.json",
        "adaptive_creator_loop.startup_yc_heldout_check.v1",
        plan_path,
        gate_passed=True,
        evidence_path=heldout_evidence_path,
    )
    review_path = _write_gate_output(
        tmp_path / "review-gates.json",
        "adaptive_creator_loop.startup_yc_review_gates_check.v1",
        plan_path,
        gate_passed=True,
        evidence_path=review_gate_evidence_path,
        gate_status={
            "human_operator_calibration": True,
            "privacy_review": True,
            "rollback_review": True,
            "publication_approval": True,
        },
    )
    bundle_path = tmp_path / "promotion-evidence-bundle.json"
    bundle_path.write_text(
        json.dumps(
            {
                "checks": {
                    "multi_seed_validation": str(multi_seed_path),
                    "held_out_founder_advice_pass": str(heldout_path),
                    "review_gates": str(review_path),
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    payloads = [
        check_startup_yc_promotion_gates(plan_path),
        check_startup_yc_multi_seed_validation(plan_path),
        check_startup_yc_multi_seed_validation(
            plan_path,
            evidence_path=multi_seed_evidence_path,
        ),
        check_startup_yc_heldout_validation(plan_path),
        check_startup_yc_heldout_validation(
            plan_path,
            evidence_path=heldout_evidence_path,
        ),
        check_startup_yc_review_gates(plan_path),
        check_startup_yc_review_gates(
            plan_path,
            evidence_path=review_gate_evidence_path,
        ),
        check_startup_yc_promotion_evidence(plan_path),
        check_startup_yc_promotion_evidence(
            plan_path,
            evidence_bundle_path=bundle_path,
        ),
    ]
    validator = jsonschema.Draft202012Validator(schema)

    for payload in payloads:
        validator.validate(payload)
        unsafe = json.loads(json.dumps(payload))
        unsafe["network_absorbable"] = True
        assert list(validator.iter_errors(unsafe))


def test_startup_yc_validation_evidence_schema_checks_raw_inputs(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(VALIDATION_EVIDENCE_SCHEMA.read_text(encoding="utf-8"))
    (
        multi_seed_evidence_path,
        heldout_evidence_path,
        review_gate_evidence_path,
    ) = _write_raw_validation_evidence(tmp_path)
    bundle_path = tmp_path / "promotion-evidence-bundle.json"
    bundle_path.write_text(
        json.dumps(
            {
                "checks": {
                    "multi_seed_validation": "multi-seed-output.json",
                    "held_out_founder_advice_pass": "heldout-output.json",
                    "review_gates": "review-output.json",
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    validator = jsonschema.Draft202012Validator(schema)

    for path in (
        multi_seed_evidence_path,
        heldout_evidence_path,
        review_gate_evidence_path,
        bundle_path,
    ):
        validator.validate(json.loads(path.read_text(encoding="utf-8")))

    malformed_heldout = json.loads(heldout_evidence_path.read_text(encoding="utf-8"))
    del malformed_heldout["rows"][0]["privacy_lane_respected"]
    assert list(validator.iter_errors(malformed_heldout))


def test_startup_yc_validation_evidence_check_result_schema_blocks_network_absorption(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        VALIDATION_EVIDENCE_CHECK_RESULT_SCHEMA.read_text(encoding="utf-8")
    )
    multi_seed_evidence_path, _, _ = _write_raw_validation_evidence(tmp_path)
    payload = check_startup_yc_validation_evidence_shape(
        multi_seed_evidence_path,
        evidence_kind="multi_seed",
    )
    validator = jsonschema.Draft202012Validator(schema)

    validator.validate(payload)

    unsafe = json.loads(json.dumps(payload))
    unsafe["network_absorbable"] = True
    assert list(validator.iter_errors(unsafe))

    missing_provenance = json.loads(json.dumps(payload))
    del missing_provenance["provenance"]
    assert list(validator.iter_errors(missing_provenance))


def test_startup_yc_validation_evidence_shape_check_blocks_malformed_raw_input(
    tmp_path: Path,
) -> None:
    (
        multi_seed_evidence_path,
        heldout_evidence_path,
        review_gate_evidence_path,
    ) = _write_raw_validation_evidence(tmp_path)
    bundle_path = tmp_path / "promotion-evidence-bundle.json"
    bundle_path.write_text(
        json.dumps(
            {
                "checks": {
                    "multi_seed_validation": "multi-seed-output.json",
                    "held_out_founder_advice_pass": "heldout-output.json",
                    "review_gates": "review-output.json",
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    for evidence_kind, evidence_path in (
        ("multi_seed", multi_seed_evidence_path),
        ("heldout", heldout_evidence_path),
        ("review_gates", review_gate_evidence_path),
        ("promotion_evidence_bundle", bundle_path),
    ):
        result = check_startup_yc_validation_evidence_shape(
            evidence_path,
            evidence_kind=evidence_kind,
        )
        assert result["verdict"] == "passed"
        assert result["schema_path"].endswith(
            "startup-yc-validation-evidence.schema.json"
        )
        assert result["provenance"]["input_hashes"] == {
            str(evidence_path): hashlib.sha256(evidence_path.read_bytes()).hexdigest()
        }

    malformed = json.loads(heldout_evidence_path.read_text(encoding="utf-8"))
    del malformed["rows"][0]["privacy_lane_respected"]
    malformed_path = tmp_path / "malformed-heldout-evidence.json"
    malformed_path.write_text(json.dumps(malformed, indent=2), encoding="utf-8")

    result = check_startup_yc_validation_evidence_shape(
        malformed_path,
        evidence_kind="heldout",
    )

    assert result["verdict"] == "blocked"
    assert "row_field_invalid:urgent-pain-or-politeness:privacy_lane_respected" in (
        result["blocking_checks"]
    )


def test_startup_yc_validation_suite_keeps_final_promotion_blocked(
    tmp_path: Path,
) -> None:
    plan_path = FIXTURE_DIR / "validation_plan.json"
    (
        multi_seed_evidence_path,
        heldout_evidence_path,
        review_gate_evidence_path,
    ) = _write_raw_validation_evidence(tmp_path)
    multi_seed_path = _write_gate_output(
        tmp_path / "multi-seed.json",
        "adaptive_creator_loop.startup_yc_multi_seed_check.v1",
        plan_path,
        gate_passed=True,
        evidence_path=multi_seed_evidence_path,
    )
    heldout_path = _write_gate_output(
        tmp_path / "heldout.json",
        "adaptive_creator_loop.startup_yc_heldout_check.v1",
        plan_path,
        gate_passed=True,
        evidence_path=heldout_evidence_path,
    )
    review_path = _write_gate_output(
        tmp_path / "review-gates.json",
        "adaptive_creator_loop.startup_yc_review_gates_check.v1",
        plan_path,
        gate_passed=True,
        evidence_path=review_gate_evidence_path,
        gate_status={
            "human_operator_calibration": True,
            "privacy_review": True,
            "rollback_review": True,
            "publication_approval": True,
        },
    )
    bundle_path = tmp_path / "promotion-evidence-bundle.json"
    bundle_path.write_text(
        json.dumps(
            {
                "checks": {
                    "multi_seed_validation": str(multi_seed_path),
                    "held_out_founder_advice_pass": str(heldout_path),
                    "review_gates": str(review_path),
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = run_startup_yc_validation_suite(
        plan_path,
        multi_seed_evidence_path=multi_seed_evidence_path,
        heldout_evidence_path=heldout_evidence_path,
        review_gate_evidence_path=review_gate_evidence_path,
        promotion_evidence_bundle_path=bundle_path,
    )

    assert result["verdict"] == "blocked"
    assert result["required_subchecks_passed"] is True
    assert result["final_promotion_ready"] is False
    assert result["network_absorbable"] is False
    assert result["subchecks"]["promotion_gates"]["verdict"] == "blocked"
    assert "promotion_gates:prohibited_claim:network_absorbable" in result[
        "blocking_checks"
    ]


def test_cli_startup_yc_promotion_gate_check_fails_on_blocked(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "startup-yc-promotion-gates.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "startup-yc-promotion-gate-check",
            "--validation-plan",
            str(FIXTURE_DIR / "validation_plan.json"),
            "--output",
            str(output_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.returncode == 1
    assert payload["verdict"] == "blocked"
    assert payload["network_absorbable"] is False


def test_cli_startup_yc_validation_evidence_check_fails_on_malformed_input(
    tmp_path: Path,
) -> None:
    _, heldout_evidence_path, _ = _write_raw_validation_evidence(tmp_path)
    malformed = json.loads(heldout_evidence_path.read_text(encoding="utf-8"))
    del malformed["rows"][0]["privacy_lane_respected"]
    malformed_path = tmp_path / "malformed-heldout-evidence.json"
    malformed_path.write_text(json.dumps(malformed, indent=2), encoding="utf-8")
    output_path = tmp_path / "validation-evidence-shape.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "startup-yc-validation-evidence-check",
            "--evidence",
            str(malformed_path),
            "--evidence-kind",
            "heldout",
            "--output",
            str(output_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.returncode == 1
    assert payload["verdict"] == "blocked"
    assert payload["evidence_kind"] == "heldout"


def test_cli_startup_yc_validation_evidence_check_output_matches_result_schema(
    tmp_path: Path,
) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        VALIDATION_EVIDENCE_CHECK_RESULT_SCHEMA.read_text(encoding="utf-8")
    )
    multi_seed_evidence_path, _, _ = _write_raw_validation_evidence(tmp_path)
    output_path = tmp_path / "validation-evidence-shape.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "startup-yc-validation-evidence-check",
            "--evidence",
            str(multi_seed_evidence_path),
            "--evidence-kind",
            "multi_seed",
            "--output",
            str(output_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.returncode == 0
    assert payload["verdict"] == "passed"
    jsonschema.Draft202012Validator(schema).validate(payload)


def test_cli_startup_yc_multi_seed_check_fails_on_blocked(tmp_path: Path) -> None:
    output_path = tmp_path / "startup-yc-multi-seed.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "startup-yc-multi-seed-check",
            "--validation-plan",
            str(FIXTURE_DIR / "validation_plan.json"),
            "--output",
            str(output_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.returncode == 1
    assert payload["verdict"] == "blocked"
    assert payload["network_absorbable"] is False


def test_cli_startup_yc_heldout_check_fails_on_blocked(tmp_path: Path) -> None:
    output_path = tmp_path / "startup-yc-heldout.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "startup-yc-heldout-check",
            "--validation-plan",
            str(FIXTURE_DIR / "validation_plan.json"),
            "--output",
            str(output_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.returncode == 1
    assert payload["verdict"] == "blocked"
    assert payload["network_absorbable"] is False


def test_cli_startup_yc_review_gates_check_fails_on_blocked(tmp_path: Path) -> None:
    output_path = tmp_path / "startup-yc-review-gates.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "startup-yc-review-gates-check",
            "--validation-plan",
            str(FIXTURE_DIR / "validation_plan.json"),
            "--output",
            str(output_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.returncode == 1
    assert payload["verdict"] == "blocked"
    assert payload["network_absorbable"] is False


def test_cli_startup_yc_promotion_evidence_check_fails_on_blocked(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "startup-yc-promotion-evidence.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "startup-yc-promotion-evidence-check",
            "--validation-plan",
            str(FIXTURE_DIR / "validation_plan.json"),
            "--output",
            str(output_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.returncode == 1
    assert payload["verdict"] == "blocked"
    assert payload["network_absorbable"] is False


def test_cli_startup_yc_gate_outputs_bundle_with_provenance(
    tmp_path: Path,
) -> None:
    plan_path = FIXTURE_DIR / "validation_plan.json"
    (
        multi_seed_evidence_path,
        heldout_evidence_path,
        review_gate_evidence_path,
    ) = _write_raw_validation_evidence(tmp_path)
    multi_seed_output = tmp_path / "multi-seed-output.json"
    heldout_output = tmp_path / "heldout-output.json"
    review_output = tmp_path / "review-output.json"

    for command, evidence_path, output_path in (
        ("startup-yc-multi-seed-check", multi_seed_evidence_path, multi_seed_output),
        ("startup-yc-heldout-check", heldout_evidence_path, heldout_output),
        ("startup-yc-review-gates-check", review_gate_evidence_path, review_output),
    ):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "chip_labs.cli",
                command,
                "--validation-plan",
                str(plan_path),
                "--evidence",
                str(evidence_path),
                "--output",
                str(output_path),
                "--fail-on-blocked",
            ],
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        assert result.returncode == 0
        assert payload["gate_passed"] is True
        assert payload["network_absorbable"] is False
        assert payload["provenance"]["input_hashes"]

    bundle_path = tmp_path / "promotion-evidence-bundle.json"
    bundle_path.write_text(
        json.dumps(
            {
                "checks": {
                    "multi_seed_validation": str(multi_seed_output),
                    "held_out_founder_advice_pass": str(heldout_output),
                    "review_gates": str(review_output),
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    promotion_output = tmp_path / "promotion-output.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "startup-yc-promotion-evidence-check",
            "--validation-plan",
            str(plan_path),
            "--evidence-bundle",
            str(bundle_path),
            "--output",
            str(promotion_output),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(promotion_output.read_text(encoding="utf-8"))
    assert result.returncode == 0
    assert payload["all_required_gates_supported"] is True
    assert payload["network_absorbable"] is False

    heldout_evidence_path.write_text(
        json.dumps({"rows": []}, indent=2),
        encoding="utf-8",
    )
    stale_output = tmp_path / "stale-promotion-output.json"
    stale_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "startup-yc-promotion-evidence-check",
            "--validation-plan",
            str(plan_path),
            "--evidence-bundle",
            str(bundle_path),
            "--output",
            str(stale_output),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )
    stale_payload = json.loads(stale_output.read_text(encoding="utf-8"))
    assert stale_result.returncode == 1
    assert "provenance_mismatch:held_out_founder_advice_pass" in stale_payload[
        "blocking_checks"
    ]


def test_cli_startup_yc_validation_suite_fails_on_blocked(tmp_path: Path) -> None:
    output_path = tmp_path / "startup-yc-validation-suite.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "startup-yc-validation-suite",
            "--validation-plan",
            str(FIXTURE_DIR / "validation_plan.json"),
            "--output",
            str(output_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.returncode == 1
    assert payload["verdict"] == "blocked"
    assert payload["network_absorbable"] is False


def _load_plan() -> dict[str, object]:
    return json.loads((FIXTURE_DIR / "validation_plan.json").read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_gate_output(
    path: Path,
    schema_version: str,
    plan_path: Path,
    *,
    gate_passed: bool,
    evidence_path: Path | None = None,
    gate_status: dict[str, bool] | None = None,
) -> Path:
    payload: dict[str, object] = {
        "schema_version": schema_version,
        "plan_path": str(plan_path),
        "gate_passed": gate_passed,
        "network_absorbable": False,
    }
    if evidence_path is not None:
        payload["evidence_path"] = str(evidence_path)
        payload["provenance"] = {
            "source": "startup_yc_operator_validation_v1",
            "input_hashes": {
                str(evidence_path): hashlib.sha256(
                    evidence_path.read_bytes()
                ).hexdigest()
            },
            "missing_inputs": [],
        }
    if gate_status is not None:
        payload["gate_status"] = gate_status
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _write_raw_validation_evidence(tmp_path: Path) -> tuple[Path, Path, Path]:
    plan = _load_plan()
    tracks = plan["minimum_multi_seed_plan"]["tracks"]
    multi_seed_evidence_path = tmp_path / "multi-seed-evidence.json"
    multi_seed_evidence_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "seed_id": f"{track}-{index}",
                        "track": track,
                        "baseline_score": 0.4,
                        "candidate_score": 0.6,
                        "constraints_passed": True,
                        "held_out_passed": True,
                    }
                    for track in tracks
                    for index in range(1, 6)
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    cases = _load_jsonl(FIXTURE_DIR / plan["held_out_cases_path"])
    heldout_evidence_path = tmp_path / "heldout-evidence.json"
    heldout_evidence_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "case_id": case["case_id"],
                        "passed": True,
                        "operator_moves_covered": True,
                        "reject_claims_avoided": True,
                        "success_gate_met": True,
                        "privacy_lane_respected": True,
                    }
                    for case in cases
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    review_gate_evidence_path = tmp_path / "review-gate-evidence.json"
    review_gate_evidence_path.write_text(
        json.dumps(
            {
                "gates": {
                    "human_operator_calibration": {
                        "passed": True,
                        "reviewer": "operator",
                        "evidence_ref": "calibration-review-1",
                        "calibration_notes": "Reviewed held-out advice quality.",
                    },
                    "privacy_review": {
                        "passed": True,
                        "reviewer": "operator",
                        "evidence_ref": "privacy-review-1",
                        "privacy_lane_decision": "No private founder details leave local lane.",
                    },
                    "rollback_review": {
                        "passed": True,
                        "reviewer": "operator",
                        "evidence_ref": "rollback-review-1",
                        "rollback_rule": "Revoke promotion on stale or negative evidence.",
                    },
                    "publication_approval": {
                        "passed": True,
                        "reviewer": "operator",
                        "evidence_ref": "publication-review-1",
                        "publication_decision": "Approved for network_absorbable only after all gates pass.",
                        "approved_claim": "network_absorbable",
                        "network_publication_allowed": True,
                    },
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return multi_seed_evidence_path, heldout_evidence_path, review_gate_evidence_path
