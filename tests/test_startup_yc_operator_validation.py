from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from chip_labs.startup_yc_promotion import (
    check_startup_yc_heldout_validation,
    check_startup_yc_multi_seed_validation,
    check_startup_yc_promotion_gates,
    check_startup_yc_review_gates,
)


FIXTURE_DIR = Path("docs/creator_system/examples/startup-yc-operator-validation")


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


def _load_plan() -> dict[str, object]:
    return json.loads((FIXTURE_DIR / "validation_plan.json").read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
