"""Creator-system beta readiness aggregate."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .creator_release_gate import build_creator_release_gate
from .creator_run import repo_root, validate_creator_run, validate_creator_templates
from .startup_yc_promotion import (
    build_startup_yc_network_absorption_review,
    check_startup_yc_validation_evidence_shape,
)


SCHEMA_VERSION = "adaptive_creator_loop.creator_system_beta_check.v1"


def build_creator_system_beta_check(
    *,
    startup_run_dir: str | Path | None = None,
    validation_plan_path: str | Path | None = None,
    generated_summary_path: str | Path | None = None,
    product_runtime_review_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build the local beta readiness packet without approving publication."""

    root = repo_root()
    startup_run = Path(startup_run_dir) if startup_run_dir else _default_startup_run(root)
    validation_plan = (
        Path(validation_plan_path)
        if validation_plan_path
        else _default_validation_plan(root)
    )
    validation_dir = validation_plan.parent
    raw_evidence_path = validation_dir / "shape_only_multi_seed_evidence.json"
    saved_suite_path = validation_dir / "validation_suite_blocked.json"
    saved_network_review_path = validation_dir / "network_absorption_review_blocked.json"

    template_check = validate_creator_templates()
    smoke = validate_creator_run(startup_run).to_dict()
    raw_evidence_check = check_startup_yc_validation_evidence_shape(
        raw_evidence_path,
        evidence_kind="multi_seed",
    )
    network_review = build_startup_yc_network_absorption_review(
        validation_plan,
        validation_suite_path=saved_suite_path,
    )
    release_gate = build_creator_release_gate(
        validation_plan_path=validation_plan,
        generated_summary_path=generated_summary_path,
        startup_network_review_path=saved_network_review_path,
        product_runtime_review_path=product_runtime_review_path,
    )

    checks = [
        _check_template_result(template_check),
        _check_strict_startup_smoke(smoke),
        _check_raw_evidence(raw_evidence_check),
        _check_network_review(network_review),
        _check_release_gate(
            release_gate,
            generated_summary_path=generated_summary_path,
            product_runtime_review_path=product_runtime_review_path,
        ),
    ]
    blocking_checks = [
        f"{check['name']}:{blocker}"
        for check in checks
        if check["status"] != "pass"
        for blocker in check["blocking_checks"]
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": "blocked" if blocking_checks else "pass",
        "network_absorbable": False,
        "claim_boundary": (
            "Technical beta readiness proves local creator-run usability only; "
            "it does not approve network absorption or product runtime publication."
        ),
        "checks": checks,
        "blocking_checks": blocking_checks,
        "input_provenance": [
            _provenance("startup_run_dir", startup_run),
            _provenance("validation_plan", validation_plan),
            _provenance("raw_validation_evidence", raw_evidence_path),
            _provenance("saved_validation_suite", saved_suite_path),
            _provenance("saved_network_review", saved_network_review_path),
            _provenance("generated_summary", generated_summary_path),
            _provenance("product_runtime_review", product_runtime_review_path),
        ],
        "next_actions": _next_actions(blocking_checks),
    }


def _check_template_result(result: dict[str, Any]) -> dict[str, Any]:
    blocking = list(result.get("blocking_checks") or [])
    if result.get("verdict") != "pass":
        blocking.append(f"template_verdict:{result.get('verdict')}")
    return _check(
        "creator_run_templates",
        blocking=blocking,
        detail={
            "verdict": result.get("verdict"),
            "status_counts": result.get("status_counts", {}),
        },
    )


def _check_strict_startup_smoke(smoke: dict[str, Any]) -> dict[str, Any]:
    blocking = list(smoke.get("blocking_checks") or [])
    if smoke.get("verdict") != "ready_for_swarm_packet":
        blocking.append(f"smoke_verdict:{smoke.get('verdict')}")
    if smoke.get("evidence_tier") != "transfer_supported":
        blocking.append(f"evidence_tier:{smoke.get('evidence_tier')}")
    if smoke.get("evidence_mode") != "saved":
        blocking.append(f"evidence_mode:{smoke.get('evidence_mode')}")
    if smoke.get("warning_checks"):
        blocking.append("startup_smoke_warnings_present")
    return _check(
        "startup_yc_strict_smoke",
        blocking=blocking,
        detail={
            "verdict": smoke.get("verdict"),
            "evidence_tier": smoke.get("evidence_tier"),
            "evidence_mode": smoke.get("evidence_mode"),
            "status_counts": smoke.get("status_counts", {}),
        },
    )


def _check_raw_evidence(result: dict[str, Any]) -> dict[str, Any]:
    blocking = list(result.get("blocking_checks") or [])
    if result.get("verdict") != "passed":
        blocking.append(f"raw_evidence_verdict:{result.get('verdict')}")
    if result.get("evidence_present") is not True:
        blocking.append("raw_evidence_missing")
    return _check(
        "startup_yc_raw_evidence_shape",
        blocking=blocking,
        detail={
            "verdict": result.get("verdict"),
            "evidence_kind": result.get("evidence_kind"),
            "evidence_present": result.get("evidence_present"),
        },
    )


def _check_network_review(review: dict[str, Any]) -> dict[str, Any]:
    blocking: list[str] = []
    if review.get("verdict") != "blocked":
        blocking.append(f"network_review_verdict:{review.get('verdict')}")
    if review.get("network_absorbable") is not False:
        blocking.append("network_review_claimed_absorbable")
    if "external_provenance:missing" not in list(review.get("blocking_checks") or []):
        blocking.append("network_review_missing_external_provenance_blocker")
    return _check(
        "startup_yc_network_absorption_boundary",
        blocking=blocking,
        detail={
            "verdict": review.get("verdict"),
            "network_absorbable": review.get("network_absorbable"),
            "blocking_check_count": len(review.get("blocking_checks") or []),
        },
    )


def _check_release_gate(
    release_gate: dict[str, Any],
    *,
    generated_summary_path: str | Path | None,
    product_runtime_review_path: str | Path | None,
) -> dict[str, Any]:
    blocking: list[str] = []
    if release_gate.get("verdict") != "blocked":
        blocking.append(f"release_gate_verdict:{release_gate.get('verdict')}")
    if release_gate.get("network_absorbable") is not False:
        blocking.append("release_gate_claimed_absorbable")

    phases = {
        str(phase.get("phase")): phase
        for phase in release_gate.get("phase_status", [])
        if isinstance(phase, dict)
    }
    generated_phase = phases.get("generated_multi_seed_validation", {})
    startup_phase = phases.get("startup_yc_network_absorption_review", {})
    product_phase = phases.get("product_runtime_integration_review", {})
    if generated_summary_path is None:
        if "missing_generated_multi_seed_summary" not in list(
            generated_phase.get("blocking_checks") or []
        ):
            blocking.append("release_gate_missing_generated_summary_blocker")
    elif generated_phase.get("passed") is not True:
        blocking.append("release_gate_generated_summary_not_passing")
    if startup_phase.get("passed") is not False:
        blocking.append("release_gate_startup_phase_not_blocked")
    if product_runtime_review_path is None:
        if product_phase.get("passed") is not False:
            blocking.append("release_gate_product_phase_not_blocked")
    elif product_phase.get("passed") is not True:
        blocking.append("release_gate_product_phase_not_blocked")

    return _check(
        "stronger_release_gate_boundary",
        blocking=blocking,
        detail={
            "verdict": release_gate.get("verdict"),
            "network_absorbable": release_gate.get("network_absorbable"),
            "generated_phase_passed": generated_phase.get("passed"),
            "startup_phase_passed": startup_phase.get("passed"),
            "product_phase_passed": product_phase.get("passed"),
        },
    )


def _check(
    name: str,
    *,
    blocking: list[str],
    detail: dict[str, Any],
) -> dict[str, Any]:
    blocking_checks = _dedupe(blocking)
    return {
        "name": name,
        "status": "fail" if blocking_checks else "pass",
        "blocking_checks": blocking_checks,
        "detail": detail,
    }


def _provenance(label: str, path_value: str | Path | None) -> dict[str, Any]:
    if path_value is None:
        return {
            "label": label,
            "path": None,
            "present": False,
            "sha256": None,
        }
    path = Path(path_value)
    present = path.exists()
    return {
        "label": label,
        "path": str(path),
        "present": present,
        "sha256": _sha256(path) if present and path.is_file() else None,
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _next_actions(blocking_checks: list[str]) -> list[str]:
    if not blocking_checks:
        return [
            "Use this repo as a local creator-system technical beta.",
            "Keep network absorption blocked until the full promotion bundle passes.",
        ]
    return [
        "Repair the failed beta readiness checks before handing this repo to users.",
        "Do not publish creator outputs or enable product runtime controls from a blocked beta check.",
    ]


def _default_startup_run(root: Path) -> Path:
    return root / "docs" / "creator_system" / "examples" / "startup-yc-creator-run"


def _default_validation_plan(root: Path) -> Path:
    return (
        root
        / "docs"
        / "creator_system"
        / "examples"
        / "startup-yc-operator-validation"
        / "validation_plan.json"
    )
