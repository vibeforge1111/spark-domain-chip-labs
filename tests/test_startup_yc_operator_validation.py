from __future__ import annotations

import json
from pathlib import Path


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


def _load_plan() -> dict[str, object]:
    return json.loads((FIXTURE_DIR / "validation_plan.json").read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
