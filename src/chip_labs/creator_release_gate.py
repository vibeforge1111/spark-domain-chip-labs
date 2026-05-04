"""Release gate aggregation for stronger creator-system claims."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .creator_generator import validate_multi_seed_generator_summary
from .startup_yc_promotion import build_startup_yc_network_absorption_review


SCHEMA_VERSION = "adaptive_creator_loop.creator_release_gate.v1"
DEFAULT_REQUIRED_PRODUCT_SURFACES = (
    "builder",
    "telegram",
    "spawner",
    "canvas",
    "kanban",
)


def build_creator_release_gate(
    *,
    validation_plan_path: str | Path,
    generated_summary_path: str | Path | None = None,
    startup_network_review_path: str | Path | None = None,
    product_runtime_review_path: str | Path | None = None,
    requested_release: str = "network_absorption",
) -> dict[str, Any]:
    """Aggregate phase gates for a stronger creator-system release."""

    plan_path = Path(validation_plan_path)
    phase_status = [
        _generated_multi_seed_phase(generated_summary_path),
        _startup_network_review_phase(
            validation_plan_path=plan_path,
            startup_network_review_path=startup_network_review_path,
        ),
        _product_runtime_phase(product_runtime_review_path),
    ]
    blocking_checks = [
        f"{phase['phase']}:{blocker}"
        for phase in phase_status
        if phase["passed"] is not True
        for blocker in phase["blocking_checks"]
    ]
    verdict = "review_ready" if not blocking_checks else "blocked"
    return {
        "schema_version": SCHEMA_VERSION,
        "requested_release": requested_release,
        "verdict": verdict,
        "network_absorbable": False,
        "claim_boundary": (
            "This release gate aggregates promotion evidence only; it does not "
            "approve network_absorbable or product runtime publication."
        ),
        "phase_status": phase_status,
        "blocking_checks": blocking_checks,
        "input_provenance": [
            _provenance("validation_plan", plan_path),
            _provenance("generated_summary", generated_summary_path),
            _provenance("startup_network_review", startup_network_review_path),
            _provenance("product_runtime_review", product_runtime_review_path),
        ],
        "next_actions": _next_actions(phase_status),
    }


def _generated_multi_seed_phase(
    generated_summary_path: str | Path | None,
) -> dict[str, Any]:
    phase = "generated_multi_seed_validation"
    if generated_summary_path is None:
        return _phase(
            phase,
            passed=False,
            evidence_ref=None,
            evidence_mode="missing",
            blocking_checks=["missing_generated_multi_seed_summary"],
            detail={
                "required_command": (
                    "generated-multi-seed-run followed by "
                    "generated-multi-seed-summary-check --fail-on-blocked"
                )
            },
        )

    path = Path(generated_summary_path)
    if not path.exists():
        return _phase(
            phase,
            passed=False,
            evidence_ref=str(path),
            evidence_mode="missing",
            blocking_checks=["generated_multi_seed_summary_not_found"],
        )

    check = validate_multi_seed_generator_summary(path)
    blocking_checks = list(check.get("blocking_checks") or [])
    if check.get("verdict") != "pass":
        blocking_checks.append(f"summary_check_verdict:{check.get('verdict')}")
    return _phase(
        phase,
        passed=not blocking_checks,
        evidence_ref=str(path),
        evidence_mode=str(check.get("evidence_mode") or "recomputed"),
        blocking_checks=_dedupe(blocking_checks),
        detail={
            "summary_check_schema_version": check.get("schema_version"),
            "row_count": check.get("row_count"),
            "failed_seed_ids": check.get("failed_seed_ids", []),
            "network_absorbable": check.get("network_absorbable"),
        },
    )


def _startup_network_review_phase(
    *,
    validation_plan_path: Path,
    startup_network_review_path: str | Path | None,
) -> dict[str, Any]:
    phase = "startup_yc_network_absorption_review"
    if startup_network_review_path is None:
        review = build_startup_yc_network_absorption_review(validation_plan_path)
        evidence_ref: str | None = str(validation_plan_path)
        evidence_mode = "fresh_run"
    else:
        path = Path(startup_network_review_path)
        evidence_ref = str(path)
        if not path.exists():
            return _phase(
                phase,
                passed=False,
                evidence_ref=evidence_ref,
                evidence_mode="missing",
                blocking_checks=["startup_network_review_not_found"],
            )
        review = _load_json(path)
        evidence_mode = "saved"

    blocking_checks = list(review.get("blocking_checks") or [])
    if review.get("verdict") != "review_ready":
        blocking_checks.append(f"network_review_verdict:{review.get('verdict')}")
    if review.get("network_absorbable") is not False:
        blocking_checks.append("network_review_claimed_absorbable")
    return _phase(
        phase,
        passed=not blocking_checks,
        evidence_ref=evidence_ref,
        evidence_mode=evidence_mode,
        blocking_checks=_dedupe(blocking_checks),
        detail={
            "review_schema_version": review.get("schema_version"),
            "review_verdict": review.get("verdict"),
            "network_absorbable": review.get("network_absorbable"),
        },
    )


def _product_runtime_phase(
    product_runtime_review_path: str | Path | None,
) -> dict[str, Any]:
    phase = "product_runtime_integration_review"
    if product_runtime_review_path is None:
        return _phase(
            phase,
            passed=False,
            evidence_ref=None,
            evidence_mode="missing",
            blocking_checks=["missing_product_runtime_review"],
            detail={"required_surfaces": list(DEFAULT_REQUIRED_PRODUCT_SURFACES)},
        )

    path = Path(product_runtime_review_path)
    if not path.exists():
        return _phase(
            phase,
            passed=False,
            evidence_ref=str(path),
            evidence_mode="missing",
            blocking_checks=["product_runtime_review_not_found"],
        )

    packet = _load_json(path)
    surfaces = packet.get("surfaces")
    if not isinstance(surfaces, dict):
        surfaces = {}
    blocking_checks: list[str] = []
    for surface in DEFAULT_REQUIRED_PRODUCT_SURFACES:
        row = surfaces.get(surface)
        if not isinstance(row, dict):
            blocking_checks.append(f"surface_missing:{surface}")
            continue
        if row.get("runtime_wiring_reviewed") is not True:
            blocking_checks.append(f"surface_not_reviewed:{surface}")
        if row.get("network_publication_allowed") is not True:
            blocking_checks.append(f"surface_publication_not_allowed:{surface}")
        if not isinstance(row.get("rollback_plan_ref"), str) or not row[
            "rollback_plan_ref"
        ].strip():
            blocking_checks.append(f"surface_missing_rollback:{surface}")
    if packet.get("network_absorbable") is not False:
        blocking_checks.append("product_review_claimed_absorbable")
    return _phase(
        phase,
        passed=not blocking_checks,
        evidence_ref=str(path),
        evidence_mode="saved",
        blocking_checks=_dedupe(blocking_checks),
        detail={
            "review_schema_version": packet.get("schema_version"),
            "review_id": packet.get("review_id"),
            "surface_count": len(surfaces),
            "network_absorbable": packet.get("network_absorbable"),
        },
    )


def _phase(
    phase: str,
    *,
    passed: bool,
    evidence_ref: str | None,
    evidence_mode: str,
    blocking_checks: list[str],
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "phase": phase,
        "passed": passed,
        "evidence_ref": evidence_ref,
        "evidence_mode": evidence_mode,
        "blocking_checks": _dedupe(blocking_checks),
        "detail": detail or {},
    }


def _next_actions(phase_status: list[dict[str, Any]]) -> list[str]:
    blocked = [phase for phase in phase_status if phase["passed"] is not True]
    if not blocked:
        return [
            "Treat this packet as review-ready evidence only.",
            "Run a human release review before any network or product publication.",
        ]
    actions: list[str] = []
    for phase in blocked:
        if phase["phase"] == "generated_multi_seed_validation":
            actions.append(
                "Run and recompute-check the generated multi-domain multi-seed matrix."
            )
        elif phase["phase"] == "startup_yc_network_absorption_review":
            actions.append(
                "Resolve Startup YC validation-suite, provenance, and publication blockers."
            )
        elif phase["phase"] == "product_runtime_integration_review":
            actions.append(
                "Add explicit Builder, Telegram, Spawner, Canvas, and Kanban runtime review evidence before exposing creator controls."
            )
    return _dedupe(actions)


def _provenance(label: str, path_value: str | Path | None) -> dict[str, Any]:
    if path_value is None:
        return {
            "label": label,
            "path": None,
            "present": False,
            "sha256": None,
        }
    path = Path(path_value)
    return {
        "label": label,
        "path": str(path),
        "present": path.exists(),
        "sha256": _sha256(path) if path.exists() else None,
    }


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))
