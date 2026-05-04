from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from chip_labs.creator_generator import run_multi_seed_generator_validation
from chip_labs.creator_release_gate import build_creator_release_gate
from chip_labs.product_runtime_review import (
    REQUIRED_SURFACES,
    build_open_product_runtime_review_packet,
)


SCHEMA = Path("docs/creator_system/schemas/creator-release-gate.schema.json")
VALIDATION_PLAN = Path(
    "docs/creator_system/examples/startup-yc-operator-validation/validation_plan.json"
)
PRODUCT_READ_ONLY_REVIEW = Path(
    "docs/creator_system/examples/product-runtime-review/review-complete-read-only.json"
)


def _brief() -> dict[str, object]:
    return {
        "domain_id": "release-gate-demo",
        "domain_name": "Release Gate Demo",
        "goal": "Prove release gates keep generated proof separate from publication.",
        "known_limits": ["No product runtime surface is approved."],
        "unsafe_claims": ["Treat local candidate review as network absorption."],
    }


def _validate_schema(payload: dict[str, object]) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)


def _complete_product_runtime_review(path: Path) -> None:
    packet = build_open_product_runtime_review_packet(review_id="release-product-review")
    packet["surfaces"] = {
        surface: {
            "status": "passed",
            "reviewer": f"{surface}-reviewer",
            "evidence_ref": f"product-runtime/{surface}.md",
            "runtime_wiring_reviewed": True,
            "read_only_adapter_preserved": True,
            "blocked_states_visible": True,
            "evidence_mode_preserved": True,
            "creator_controls_enabled": False,
            "network_publication_allowed": True,
            "rollback_plan_ref": f"rollback/{surface}.md",
        }
        for surface in REQUIRED_SURFACES
    }
    path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")


def test_creator_release_gate_blocks_missing_phase_evidence() -> None:
    gate = build_creator_release_gate(validation_plan_path=VALIDATION_PLAN)

    _validate_schema(gate)
    assert gate["schema_version"] == "adaptive_creator_loop.creator_release_gate.v1"
    assert gate["verdict"] == "blocked"
    assert gate["network_absorbable"] is False
    assert "does not approve network_absorbable" in gate["claim_boundary"]
    assert (
        "generated_multi_seed_validation:missing_generated_multi_seed_summary"
        in gate["blocking_checks"]
    )
    assert (
        "product_runtime_integration_review:missing_product_runtime_review"
        in gate["blocking_checks"]
    )
    assert any(
        str(item["label"]) == "validation_plan" and item["present"] is True
        for item in gate["input_provenance"]
    )


def test_creator_release_gate_accepts_generated_matrix_but_preserves_other_blockers(
    tmp_path: Path,
) -> None:
    summary = run_multi_seed_generator_validation(
        tmp_path / "generated",
        [_brief()],
        seeds=(1,),
        variants_per_domain=1,
    )
    summary_path = tmp_path / "generated" / "multi_seed_validation_summary.json"

    gate = build_creator_release_gate(
        validation_plan_path=VALIDATION_PLAN,
        generated_summary_path=summary_path,
    )

    _validate_schema(gate)
    assert summary["passed_run_count"] == 1
    generated_phase = next(
        phase
        for phase in gate["phase_status"]
        if phase["phase"] == "generated_multi_seed_validation"
    )
    assert generated_phase["passed"] is True
    assert generated_phase["detail"]["row_count"] == 1
    assert gate["verdict"] == "blocked"
    assert gate["network_absorbable"] is False
    assert any(
        blocker.startswith("startup_yc_network_absorption_review:")
        for blocker in gate["blocking_checks"]
    )


def test_creator_release_gate_accepts_complete_product_review_as_one_phase(
    tmp_path: Path,
) -> None:
    product_review_path = tmp_path / "product-runtime-review.json"
    _complete_product_runtime_review(product_review_path)

    gate = build_creator_release_gate(
        validation_plan_path=VALIDATION_PLAN,
        product_runtime_review_path=product_review_path,
    )

    _validate_schema(gate)
    product_phase = next(
        phase
        for phase in gate["phase_status"]
        if phase["phase"] == "product_runtime_integration_review"
    )
    assert product_phase["passed"] is True
    assert product_phase["detail"]["network_absorbable"] is False
    assert gate["verdict"] == "blocked"
    assert gate["network_absorbable"] is False


def test_creator_release_gate_accepts_saved_product_review_but_keeps_release_blocked() -> None:
    gate = build_creator_release_gate(
        validation_plan_path=VALIDATION_PLAN,
        product_runtime_review_path=PRODUCT_READ_ONLY_REVIEW,
    )

    _validate_schema(gate)
    product_phase = next(
        phase
        for phase in gate["phase_status"]
        if phase["phase"] == "product_runtime_integration_review"
    )
    assert product_phase["passed"] is True
    assert gate["verdict"] == "blocked"
    assert gate["network_absorbable"] is False
    assert any(
        blocker.startswith("generated_multi_seed_validation:")
        for blocker in gate["blocking_checks"]
    )
    assert any(
        blocker.startswith("startup_yc_network_absorption_review:")
        for blocker in gate["blocking_checks"]
    )


def test_creator_release_gate_schema_rejects_absorbable_claim() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    gate = build_creator_release_gate(validation_plan_path=VALIDATION_PLAN)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    _validate_schema(gate)
    unsafe = json.loads(json.dumps(gate))
    unsafe["network_absorbable"] = True
    assert list(jsonschema.Draft202012Validator(schema).iter_errors(unsafe))


def test_cli_creator_release_gate_fails_on_blocked(tmp_path: Path) -> None:
    output_path = tmp_path / "creator-release-gate.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "creator-release-gate",
            "--validation-plan",
            str(VALIDATION_PLAN),
            "--output",
            str(output_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    _validate_schema(payload)
    assert payload["verdict"] == "blocked"
    assert payload["network_absorbable"] is False
