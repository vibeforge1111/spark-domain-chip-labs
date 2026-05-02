from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from chip_labs.startup_yc_promotion import check_startup_yc_promotion_gates


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


def _load_plan() -> dict[str, object]:
    return json.loads((FIXTURE_DIR / "validation_plan.json").read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
