"""Startup YC promotion gate checks.

This module keeps Startup YC network absorption conservative: validation plans
can document future gates, but the checker blocks stronger claims until the
plan explicitly removes prohibitions and records every required gate as passed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "adaptive_creator_loop.startup_yc_promotion_gate_check.v1"
MULTI_SEED_SCHEMA_VERSION = "adaptive_creator_loop.startup_yc_multi_seed_check.v1"
HELDOUT_SCHEMA_VERSION = "adaptive_creator_loop.startup_yc_heldout_check.v1"
REVIEW_GATES_SCHEMA_VERSION = "adaptive_creator_loop.startup_yc_review_gates_check.v1"
PROMOTION_EVIDENCE_SCHEMA_VERSION = (
    "adaptive_creator_loop.startup_yc_promotion_evidence_check.v1"
)
VALIDATION_SUITE_SCHEMA_VERSION = (
    "adaptive_creator_loop.startup_yc_validation_suite.v1"
)
VALIDATION_EVIDENCE_CHECK_SCHEMA_VERSION = (
    "adaptive_creator_loop.startup_yc_validation_evidence_check.v1"
)
VALIDATION_EVIDENCE_SCHEMA_PATH = (
    "docs/creator_system/schemas/startup-yc-validation-evidence.schema.json"
)

_REVIEW_GATE_REQUIREMENTS = {
    "human_operator_calibration": ("reviewer", "evidence_ref", "calibration_notes"),
    "privacy_review": ("reviewer", "evidence_ref", "privacy_lane_decision"),
    "rollback_review": ("reviewer", "evidence_ref", "rollback_rule"),
    "publication_approval": ("reviewer", "evidence_ref", "publication_decision"),
}

_VALIDATION_EVIDENCE_KINDS = {
    "multi_seed",
    "heldout",
    "review_gates",
    "promotion_evidence_bundle",
}


def check_startup_yc_validation_evidence_shape(
    evidence_path: str | Path,
    *,
    evidence_kind: str,
) -> dict[str, Any]:
    """Check raw Startup YC validation evidence before it becomes gate output."""

    path = Path(evidence_path)
    blocking_checks: list[str] = []
    if evidence_kind not in _VALIDATION_EVIDENCE_KINDS:
        blocking_checks.append(f"unknown_evidence_kind:{evidence_kind}")

    evidence_present = path.exists()
    payload: dict[str, Any] = {}
    if not evidence_present:
        blocking_checks.append(f"missing_evidence:{path}")
    else:
        payload = _load_json(path)

    if payload:
        if evidence_kind == "multi_seed":
            blocking_checks.extend(_validate_multi_seed_evidence_payload(payload))
        elif evidence_kind == "heldout":
            blocking_checks.extend(_validate_heldout_evidence_payload(payload))
        elif evidence_kind == "review_gates":
            blocking_checks.extend(_validate_review_gate_evidence_payload(payload))
        elif evidence_kind == "promotion_evidence_bundle":
            blocking_checks.extend(_validate_promotion_evidence_bundle_payload(payload))

    blocking_checks = _dedupe(blocking_checks)
    return {
        "schema_version": VALIDATION_EVIDENCE_CHECK_SCHEMA_VERSION,
        "schema_path": VALIDATION_EVIDENCE_SCHEMA_PATH,
        "evidence_path": str(path),
        "evidence_kind": evidence_kind,
        "evidence_present": evidence_present,
        "verdict": "blocked" if blocking_checks else "passed",
        "blocking_checks": blocking_checks,
        "next_actions": _validation_evidence_next_actions(
            evidence_kind=evidence_kind,
            blocked=bool(blocking_checks),
        ),
    }


def check_startup_yc_promotion_gates(
    validation_plan_path: str | Path,
    *,
    requested_claim: str = "network_absorbable",
) -> dict[str, Any]:
    """Return a machine-readable promotion verdict for Startup YC."""

    plan_path = Path(validation_plan_path)
    plan = _load_json(plan_path)
    required_gates = _list_str(plan.get("required_promotion_gates"))
    gate_values = plan.get("gate_status")
    gate_status = {
        gate: isinstance(gate_values, dict) and gate_values.get(gate) is True
        for gate in required_gates
    }
    missing_gates = [gate for gate in required_gates if gate_status.get(gate) is not True]
    prohibited_claims = set(_list_str(plan.get("prohibited_claims")))
    blocking_checks = [
        f"missing_gate:{gate}"
        for gate in missing_gates
    ]
    if requested_claim in prohibited_claims:
        blocking_checks.append(f"prohibited_claim:{requested_claim}")
    if (
        requested_claim == "network_absorbable"
        and _nested(plan, "publication_boundary", "network_publication_allowed")
        is not True
    ):
        blocking_checks.append("publication_boundary:network_publication_allowed")

    evidence_paths = _evidence_paths(plan_path, plan)
    missing_evidence_paths = [
        item["path"] for item in evidence_paths if item["present"] is False
    ]
    blocking_checks.extend(
        f"missing_evidence:{path}" for path in missing_evidence_paths
    )
    verdict = "blocked" if blocking_checks else "approved"
    return {
        "schema_version": SCHEMA_VERSION,
        "plan_path": str(plan_path),
        "plan_id": plan.get("plan_id"),
        "domain": plan.get("domain"),
        "current_claim": plan.get("current_claim"),
        "requested_claim": requested_claim,
        "verdict": verdict,
        "network_absorbable": verdict == "approved"
        and requested_claim == "network_absorbable",
        "gate_status": gate_status,
        "missing_gates": missing_gates,
        "blocking_checks": _dedupe(blocking_checks),
        "evidence_paths": evidence_paths,
        "next_actions": _next_actions(missing_gates, requested_claim),
    }


def check_startup_yc_multi_seed_validation(
    validation_plan_path: str | Path,
    *,
    evidence_path: str | Path | None = None,
) -> dict[str, Any]:
    """Check Startup YC multi-seed evidence without granting network absorption."""

    plan_path = Path(validation_plan_path)
    plan = _load_json(plan_path)
    multi_seed_plan = plan.get("minimum_multi_seed_plan")
    if not isinstance(multi_seed_plan, dict):
        multi_seed_plan = {}

    required_tracks = _list_str(multi_seed_plan.get("tracks"))
    minimum_seeds_per_track = _int_value(
        multi_seed_plan.get("minimum_seeds_per_track"), default=0
    )
    required_min_delta = _float_value(
        multi_seed_plan.get("required_min_delta"), default=0.0
    )
    evidence_reference = (
        str(evidence_path) if evidence_path else plan.get("multi_seed_evidence_path")
    )
    blocking_checks: list[str] = []
    rows: list[dict[str, Any]] = []
    evidence_present = False
    evidence_file: Path | None = None
    evidence_display_path = (
        evidence_reference if isinstance(evidence_reference, str) else None
    )

    if not isinstance(evidence_reference, str) or not evidence_reference.strip():
        blocking_checks.append("missing_evidence_path:multi_seed_evidence_path")
    else:
        evidence_file = _resolve_related_path(plan_path, evidence_reference)
        evidence_present = evidence_file.exists()
        if not evidence_present:
            blocking_checks.append(f"missing_evidence:{evidence_reference}")
        else:
            rows = _load_multi_seed_rows(evidence_file)

    row_failures, eligible_counts = _evaluate_multi_seed_rows(
        rows,
        required_tracks=required_tracks,
        required_min_delta=required_min_delta,
    )
    blocking_checks.extend(
        f"row_failure:{failure['seed_id']}:{failure['reason']}"
        for failure in row_failures
    )

    missing_tracks = [
        track for track in required_tracks if eligible_counts.get(track, 0) == 0
    ]
    underfilled_tracks = [
        {
            "track": track,
            "count": eligible_counts.get(track, 0),
            "minimum": minimum_seeds_per_track,
        }
        for track in required_tracks
        if eligible_counts.get(track, 0) < minimum_seeds_per_track
    ]
    blocking_checks.extend(f"missing_track:{track}" for track in missing_tracks)
    blocking_checks.extend(
        f"underfilled_track:{item['track']}:{item['count']}/{item['minimum']}"
        for item in underfilled_tracks
    )

    blocking_checks = _dedupe(blocking_checks)
    gate_passed = not blocking_checks and bool(required_tracks)
    return {
        "schema_version": MULTI_SEED_SCHEMA_VERSION,
        "plan_path": str(plan_path),
        "plan_id": plan.get("plan_id"),
        "domain": plan.get("domain"),
        "current_claim": plan.get("current_claim"),
        "evidence_path": evidence_display_path,
        "evidence_present": evidence_present,
        "required_tracks": required_tracks,
        "minimum_seeds_per_track": minimum_seeds_per_track,
        "required_min_delta": required_min_delta,
        "track_counts": {
            track: eligible_counts.get(track, 0) for track in required_tracks
        },
        "missing_tracks": missing_tracks,
        "underfilled_tracks": underfilled_tracks,
        "row_failures": row_failures,
        "verdict": "passed" if gate_passed else "blocked",
        "gate_passed": gate_passed,
        "network_absorbable": False,
        "provenance": _input_provenance(evidence_file, evidence_display_path),
        "blocking_checks": blocking_checks,
        "next_actions": _multi_seed_next_actions(
            gate_passed=gate_passed,
            required_tracks=required_tracks,
            minimum_seeds_per_track=minimum_seeds_per_track,
        ),
    }


def check_startup_yc_heldout_validation(
    validation_plan_path: str | Path,
    *,
    evidence_path: str | Path | None = None,
) -> dict[str, Any]:
    """Check held-out Startup YC founder-advice evidence."""

    plan_path = Path(validation_plan_path)
    plan = _load_json(plan_path)
    blocking_checks: list[str] = []
    case_failures: list[dict[str, Any]] = []
    cases = _load_heldout_cases(plan_path, plan, blocking_checks)

    evidence_reference = (
        str(evidence_path) if evidence_path else plan.get("held_out_evidence_path")
    )
    evidence_rows: list[dict[str, Any]] = []
    evidence_present = False
    evidence_file: Path | None = None
    evidence_display_path = (
        evidence_reference if isinstance(evidence_reference, str) else None
    )
    if not isinstance(evidence_reference, str) or not evidence_reference.strip():
        blocking_checks.append("missing_evidence_path:held_out_evidence_path")
    else:
        evidence_file = _resolve_related_path(plan_path, evidence_reference)
        evidence_present = evidence_file.exists()
        if not evidence_present:
            blocking_checks.append(f"missing_evidence:{evidence_reference}")
        else:
            evidence_rows = _load_rows(evidence_file)

    case_failures.extend(_evaluate_heldout_rows(cases, evidence_rows))
    blocking_checks.extend(
        f"case_failure:{failure['case_id']}:{failure['reason']}"
        for failure in case_failures
    )
    blocking_checks = _dedupe(blocking_checks)
    passed_case_ids = {
        row.get("case_id")
        for row in evidence_rows
        if isinstance(row.get("case_id"), str)
        and all(row.get(field) is True for field in _HELDOUT_PASS_FIELDS)
    }
    required_case_ids = [str(case.get("case_id")) for case in cases]
    gate_passed = not blocking_checks and bool(required_case_ids)

    return {
        "schema_version": HELDOUT_SCHEMA_VERSION,
        "plan_path": str(plan_path),
        "plan_id": plan.get("plan_id"),
        "domain": plan.get("domain"),
        "current_claim": plan.get("current_claim"),
        "evidence_path": evidence_display_path,
        "evidence_present": evidence_present,
        "case_count": len(required_case_ids),
        "passed_case_count": len(passed_case_ids.intersection(required_case_ids)),
        "missing_cases": [
            case_id for case_id in required_case_ids if case_id not in passed_case_ids
        ],
        "case_failures": case_failures,
        "verdict": "passed" if gate_passed else "blocked",
        "gate_passed": gate_passed,
        "network_absorbable": False,
        "provenance": _input_provenance(evidence_file, evidence_display_path),
        "blocking_checks": blocking_checks,
        "next_actions": _heldout_next_actions(gate_passed=gate_passed),
    }


def check_startup_yc_review_gates(
    validation_plan_path: str | Path,
    *,
    evidence_path: str | Path | None = None,
) -> dict[str, Any]:
    """Check human review gates without granting network absorption."""

    plan_path = Path(validation_plan_path)
    plan = _load_json(plan_path)
    required_gates = [
        gate
        for gate in _list_str(plan.get("required_promotion_gates"))
        if gate in _REVIEW_GATE_REQUIREMENTS
    ]
    evidence_reference = (
        str(evidence_path) if evidence_path else plan.get("review_gate_evidence_path")
    )
    evidence_present = False
    evidence_file: Path | None = None
    evidence_rows: list[dict[str, Any]] = []
    evidence_display_path = (
        evidence_reference if isinstance(evidence_reference, str) else None
    )
    blocking_checks: list[str] = []

    if not isinstance(evidence_reference, str) or not evidence_reference.strip():
        blocking_checks.append("missing_evidence_path:review_gate_evidence_path")
    else:
        evidence_file = _resolve_related_path(plan_path, evidence_reference)
        evidence_present = evidence_file.exists()
        if not evidence_present:
            blocking_checks.append(f"missing_evidence:{evidence_reference}")
        else:
            evidence_rows = _load_review_gate_rows(evidence_file)

    gate_failures, gate_status = _evaluate_review_gate_rows(
        required_gates,
        evidence_rows,
    )
    blocking_checks.extend(
        f"gate_failure:{failure['gate']}:{failure['reason']}"
        for failure in gate_failures
    )
    blocking_checks = _dedupe(blocking_checks)
    gate_passed = not blocking_checks and bool(required_gates)

    return {
        "schema_version": REVIEW_GATES_SCHEMA_VERSION,
        "plan_path": str(plan_path),
        "plan_id": plan.get("plan_id"),
        "domain": plan.get("domain"),
        "current_claim": plan.get("current_claim"),
        "evidence_path": evidence_display_path,
        "evidence_present": evidence_present,
        "required_gates": required_gates,
        "gate_status": gate_status,
        "missing_gates": [
            gate for gate in required_gates if gate_status.get(gate) is not True
        ],
        "gate_failures": gate_failures,
        "verdict": "passed" if gate_passed else "blocked",
        "gate_passed": gate_passed,
        "network_absorbable": False,
        "provenance": _input_provenance(evidence_file, evidence_display_path),
        "blocking_checks": blocking_checks,
        "next_actions": _review_gates_next_actions(gate_passed=gate_passed),
    }


def check_startup_yc_promotion_evidence(
    validation_plan_path: str | Path,
    *,
    evidence_bundle_path: str | Path | None = None,
) -> dict[str, Any]:
    """Check that saved gate evidence outputs coherently support the plan."""

    plan_path = Path(validation_plan_path)
    plan = _load_json(plan_path)
    required_gates = _list_str(plan.get("required_promotion_gates"))
    bundle_reference = (
        str(evidence_bundle_path)
        if evidence_bundle_path
        else plan.get("promotion_evidence_bundle_path")
    )
    blocking_checks: list[str] = []
    bundle_present = False
    bundle_file: Path | None = None
    bundle: dict[str, Any] = {}
    bundle_display_path = bundle_reference if isinstance(bundle_reference, str) else None

    if not isinstance(bundle_reference, str) or not bundle_reference.strip():
        blocking_checks.append("missing_evidence_path:promotion_evidence_bundle_path")
    else:
        bundle_file = _resolve_related_path(plan_path, bundle_reference)
        bundle_present = bundle_file.exists()
        if not bundle_present:
            blocking_checks.append(f"missing_evidence:{bundle_reference}")
        else:
            bundle = _load_json(bundle_file)

    gate_support, evidence_checks = _evaluate_promotion_evidence_bundle(
        plan_path,
        bundle,
        required_gates,
        blocking_checks,
    )
    blocking_checks = _dedupe(blocking_checks)
    all_supported = bool(required_gates) and all(
        gate_support.get(gate) is True for gate in required_gates
    )
    return {
        "schema_version": PROMOTION_EVIDENCE_SCHEMA_VERSION,
        "plan_path": str(plan_path),
        "plan_id": plan.get("plan_id"),
        "domain": plan.get("domain"),
        "current_claim": plan.get("current_claim"),
        "evidence_bundle_path": bundle_display_path,
        "evidence_bundle_present": bundle_present,
        "required_gates": required_gates,
        "gate_support": gate_support,
        "missing_gates": [
            gate for gate in required_gates if gate_support.get(gate) is not True
        ],
        "evidence_checks": evidence_checks,
        "verdict": "passed" if all_supported and not blocking_checks else "blocked",
        "all_required_gates_supported": all_supported and not blocking_checks,
        "network_absorbable": False,
        "provenance": _input_provenance(bundle_file, bundle_display_path),
        "blocking_checks": blocking_checks,
        "next_actions": _promotion_evidence_next_actions(
            all_supported=all_supported and not blocking_checks
        ),
    }


def run_startup_yc_validation_suite(
    validation_plan_path: str | Path,
    *,
    multi_seed_evidence_path: str | Path | None = None,
    heldout_evidence_path: str | Path | None = None,
    review_gate_evidence_path: str | Path | None = None,
    promotion_evidence_bundle_path: str | Path | None = None,
    requested_claim: str = "network_absorbable",
) -> dict[str, Any]:
    """Run all Startup YC validation checks as one read-only suite."""

    plan_path = Path(validation_plan_path)
    plan = _load_json(plan_path)
    subchecks = {
        "promotion_gates": check_startup_yc_promotion_gates(
            plan_path,
            requested_claim=requested_claim,
        ),
        "multi_seed_validation": check_startup_yc_multi_seed_validation(
            plan_path,
            evidence_path=multi_seed_evidence_path,
        ),
        "held_out_founder_advice_pass": check_startup_yc_heldout_validation(
            plan_path,
            evidence_path=heldout_evidence_path,
        ),
        "review_gates": check_startup_yc_review_gates(
            plan_path,
            evidence_path=review_gate_evidence_path,
        ),
        "promotion_evidence_bundle": check_startup_yc_promotion_evidence(
            plan_path,
            evidence_bundle_path=promotion_evidence_bundle_path,
        ),
    }
    blocking_checks = _suite_blocking_checks(subchecks)
    required_subchecks_passed = all(
        subchecks[key]["verdict"] == "passed"
        for key in (
            "multi_seed_validation",
            "held_out_founder_advice_pass",
            "review_gates",
            "promotion_evidence_bundle",
        )
    )
    final_promotion_ready = (
        required_subchecks_passed and subchecks["promotion_gates"]["verdict"] == "approved"
    )
    return {
        "schema_version": VALIDATION_SUITE_SCHEMA_VERSION,
        "plan_path": str(plan_path),
        "plan_id": plan.get("plan_id"),
        "domain": plan.get("domain"),
        "current_claim": plan.get("current_claim"),
        "requested_claim": requested_claim,
        "verdict": "passed" if final_promotion_ready else "blocked",
        "required_subchecks_passed": required_subchecks_passed,
        "final_promotion_ready": final_promotion_ready,
        "network_absorbable": False,
        "subchecks": subchecks,
        "blocking_checks": blocking_checks,
        "next_actions": _validation_suite_next_actions(
            required_subchecks_passed=required_subchecks_passed,
            final_promotion_ready=final_promotion_ready,
        ),
    }


def _evidence_paths(plan_path: Path, plan: dict[str, Any]) -> list[dict[str, Any]]:
    base = plan_path.parent
    path_fields = (
        ("held_out_cases", "held_out_cases_path"),
        ("operator_calibration", "operator_calibration_checklist_path"),
        ("privacy_rollback_publication", "privacy_rollback_publication_review_path"),
    )
    evidence: list[dict[str, Any]] = []
    for kind, field in path_fields:
        relative_path = plan.get(field)
        if not isinstance(relative_path, str) or not relative_path.strip():
            continue
        path = base / relative_path
        evidence.append(
            {
                "kind": kind,
                "path": relative_path,
                "present": path.exists(),
                "claim_boundary": "presence only; gate still needs explicit pass evidence",
            }
        )
    return evidence


def _load_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix == ".jsonl":
        rows = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            rows = data.get("rows", [])
        else:
            rows = data
    if not isinstance(rows, list):
        raise ValueError(f"{path} must contain a list or an object with rows")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"{path} rows must be JSON objects")
    return rows


def _load_multi_seed_rows(path: Path) -> list[dict[str, Any]]:
    return _load_rows(path)


def _load_review_gate_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix == ".jsonl":
        return _load_rows(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("gates"), dict):
        return [
            {"gate": gate, **details}
            for gate, details in data["gates"].items()
            if isinstance(details, dict)
        ]
    if isinstance(data, dict) and isinstance(data.get("rows"), list):
        rows = data["rows"]
    else:
        rows = data
    if not isinstance(rows, list):
        raise ValueError(f"{path} must contain review rows or a gates object")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"{path} rows must be JSON objects")
    return rows


_HELDOUT_PASS_FIELDS = (
    "passed",
    "operator_moves_covered",
    "reject_claims_avoided",
    "success_gate_met",
    "privacy_lane_respected",
)


def _load_heldout_cases(
    plan_path: Path,
    plan: dict[str, Any],
    blocking_checks: list[str],
) -> list[dict[str, Any]]:
    cases_reference = plan.get("held_out_cases_path")
    if not isinstance(cases_reference, str) or not cases_reference.strip():
        blocking_checks.append("missing_cases_path:held_out_cases_path")
        return []
    cases_file = _resolve_related_path(plan_path, cases_reference)
    if not cases_file.exists():
        blocking_checks.append(f"missing_cases:{cases_reference}")
        return []
    return _load_rows(cases_file)


def _evaluate_heldout_rows(
    cases: list[dict[str, Any]],
    evidence_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    required_case_ids = [str(case.get("case_id")) for case in cases]
    required_case_id_set = set(required_case_ids)
    evidence_by_case = {
        str(row.get("case_id")): row
        for row in evidence_rows
        if isinstance(row.get("case_id"), str)
    }

    for case_id in required_case_ids:
        row = evidence_by_case.get(case_id)
        if row is None:
            failures.append({"case_id": case_id, "reason": "missing_evidence"})
            continue
        for field in _HELDOUT_PASS_FIELDS:
            if row.get(field) is not True:
                failures.append({"case_id": case_id, "reason": f"{field}_failed"})

    for row in evidence_rows:
        case_id = str(row.get("case_id") or "unknown")
        if case_id not in required_case_id_set:
            failures.append({"case_id": case_id, "reason": "unknown_case"})

    return failures


def _evaluate_review_gate_rows(
    required_gates: list[str],
    evidence_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, bool]]:
    failures: list[dict[str, Any]] = []
    gate_status = {gate: False for gate in required_gates}
    required_gate_set = set(required_gates)
    rows_by_gate = {
        str(row.get("gate")): row
        for row in evidence_rows
        if isinstance(row.get("gate"), str)
    }

    for gate in required_gates:
        row = rows_by_gate.get(gate)
        if row is None:
            failures.append({"gate": gate, "reason": "missing_evidence"})
            continue
        row_reasons: list[str] = []
        if row.get("passed") is not True:
            row_reasons.append("passed_flag_missing")
        for field in _REVIEW_GATE_REQUIREMENTS[gate]:
            if not isinstance(row.get(field), str) or not row.get(field, "").strip():
                row_reasons.append(f"{field}_missing")
        if gate == "publication_approval":
            if row.get("network_publication_allowed") is not True:
                row_reasons.append("network_publication_not_allowed")
            if row.get("approved_claim") != "network_absorbable":
                row_reasons.append("approved_claim_missing")
        if row_reasons:
            failures.extend({"gate": gate, "reason": reason} for reason in row_reasons)
        else:
            gate_status[gate] = True

    for row in evidence_rows:
        gate = str(row.get("gate") or "unknown")
        if gate not in required_gate_set:
            failures.append({"gate": gate, "reason": "unknown_gate"})

    return failures, gate_status


def _evaluate_promotion_evidence_bundle(
    plan_path: Path,
    bundle: dict[str, Any],
    required_gates: list[str],
    blocking_checks: list[str],
) -> tuple[dict[str, bool], list[dict[str, Any]]]:
    gate_support = {gate: False for gate in required_gates}
    evidence_checks: list[dict[str, Any]] = []
    checks = bundle.get("checks") if isinstance(bundle, dict) else None
    if not isinstance(checks, dict):
        blocking_checks.append("missing_bundle_checks")
        return gate_support, evidence_checks

    multi_seed = _load_bundle_check(plan_path, checks, "multi_seed_validation")
    evidence_checks.append(multi_seed)
    if _check_output_passes(
        multi_seed,
        expected_schema=MULTI_SEED_SCHEMA_VERSION,
        plan_path=plan_path,
        blocking_checks=blocking_checks,
    ):
        gate_support["multi_seed_validation"] = True

    heldout = _load_bundle_check(plan_path, checks, "held_out_founder_advice_pass")
    evidence_checks.append(heldout)
    if _check_output_passes(
        heldout,
        expected_schema=HELDOUT_SCHEMA_VERSION,
        plan_path=plan_path,
        blocking_checks=blocking_checks,
    ):
        gate_support["held_out_founder_advice_pass"] = True

    review = _load_bundle_check(plan_path, checks, "review_gates")
    evidence_checks.append(review)
    if _check_output_passes(
        review,
        expected_schema=REVIEW_GATES_SCHEMA_VERSION,
        plan_path=plan_path,
        blocking_checks=blocking_checks,
    ):
        output = review.get("output")
        gate_status = output.get("gate_status") if isinstance(output, dict) else None
        if isinstance(gate_status, dict):
            for gate in _REVIEW_GATE_REQUIREMENTS:
                gate_support[gate] = gate_status.get(gate) is True
                if gate in required_gates and gate_status.get(gate) is not True:
                    blocking_checks.append(f"unsupported_gate:{gate}")

    return gate_support, evidence_checks


def _suite_blocking_checks(subchecks: dict[str, dict[str, Any]]) -> list[str]:
    blocking_checks: list[str] = []
    for name, result in subchecks.items():
        verdict = result.get("verdict")
        if verdict not in ("passed", "approved"):
            blocking_checks.append(f"subcheck_blocked:{name}")
        blocking_checks.extend(
            f"{name}:{check}"
            for check in _list_str(result.get("blocking_checks"))
        )
    return _dedupe(blocking_checks)


def _load_bundle_check(
    plan_path: Path,
    checks: dict[str, Any],
    key: str,
) -> dict[str, Any]:
    reference = checks.get(key)
    result: dict[str, Any] = {
        "key": key,
        "path": reference if isinstance(reference, str) else None,
        "present": False,
        "schema_ok": False,
        "plan_match": False,
        "gate_passed": False,
    }
    if not isinstance(reference, str) or not reference.strip():
        result["error"] = "missing_check_path"
        return result
    output_path = _resolve_related_path(plan_path, reference)
    result["present"] = output_path.exists()
    if not result["present"]:
        result["error"] = "missing_check_output"
        return result
    output = _load_json(output_path)
    result["output"] = output
    return result


def _check_output_passes(
    check: dict[str, Any],
    *,
    expected_schema: str,
    plan_path: Path,
    blocking_checks: list[str],
) -> bool:
    key = str(check.get("key"))
    if check.get("present") is not True:
        blocking_checks.append(f"missing_check_output:{key}")
        return False
    output = check.get("output")
    if not isinstance(output, dict):
        blocking_checks.append(f"invalid_check_output:{key}")
        return False
    schema_ok = output.get("schema_version") == expected_schema
    plan_match = output.get("plan_path") == str(plan_path)
    gate_passed = output.get("gate_passed") is True
    provenance_ok = _check_output_provenance(
        output,
        key=key,
        plan_path=plan_path,
        blocking_checks=blocking_checks,
    )
    check["schema_ok"] = schema_ok
    check["plan_match"] = plan_match
    check["gate_passed"] = gate_passed
    check["provenance_ok"] = provenance_ok
    if not schema_ok:
        blocking_checks.append(f"schema_mismatch:{key}")
    if not plan_match:
        blocking_checks.append(f"plan_mismatch:{key}")
    if not gate_passed:
        blocking_checks.append(f"gate_not_passed:{key}")
    return schema_ok and plan_match and gate_passed and provenance_ok


def _check_output_provenance(
    output: dict[str, Any],
    *,
    key: str,
    plan_path: Path,
    blocking_checks: list[str],
) -> bool:
    provenance = output.get("provenance")
    if not isinstance(provenance, dict):
        blocking_checks.append(f"missing_provenance:{key}")
        return False
    input_hashes = provenance.get("input_hashes")
    if not isinstance(input_hashes, dict) or not input_hashes:
        blocking_checks.append(f"missing_provenance_hash:{key}")
        return False

    provenance_ok = True
    for reference, expected_digest in input_hashes.items():
        if not isinstance(reference, str) or not isinstance(expected_digest, str):
            blocking_checks.append(f"invalid_provenance_hash:{key}")
            provenance_ok = False
            continue
        input_path = _resolve_related_path(plan_path, reference)
        if not input_path.exists():
            blocking_checks.append(f"missing_provenance_input:{key}")
            provenance_ok = False
            continue
        if _file_sha256(input_path) != expected_digest:
            blocking_checks.append(f"provenance_mismatch:{key}")
            provenance_ok = False
    return provenance_ok


def _evaluate_multi_seed_rows(
    rows: list[dict[str, Any]],
    *,
    required_tracks: list[str],
    required_min_delta: float,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    required_track_set = set(required_tracks)
    failures: list[dict[str, Any]] = []
    eligible_counts = {track: 0 for track in required_tracks}

    for index, row in enumerate(rows):
        seed_id = str(row.get("seed_id") or f"row_{index + 1}")
        track = str(row.get("track") or "")
        baseline_score = row.get("baseline_score")
        candidate_score = row.get("candidate_score")
        baseline_value = _number_value(baseline_score)
        candidate_value = _number_value(candidate_score)
        delta = (
            candidate_value - baseline_value
            if baseline_value is not None and candidate_value is not None
            else None
        )
        row_reasons: list[str] = []
        if track not in required_track_set:
            row_reasons.append("unknown_track")
        if not row.get("seed_id"):
            row_reasons.append("missing_seed_id")
        if delta is None:
            row_reasons.append("invalid_score")
        elif delta < required_min_delta:
            row_reasons.append("negative_delta")
        if row.get("constraints_passed") is not True:
            row_reasons.append("constraints_failed")
        if row.get("held_out_passed") is not True:
            row_reasons.append("held_out_failed")

        if row_reasons:
            failures.extend(
                {
                    "seed_id": seed_id,
                    "track": track or None,
                    "reason": reason,
                }
                for reason in row_reasons
            )
        elif track in eligible_counts:
            eligible_counts[track] += 1

    return failures, eligible_counts


def _validate_multi_seed_evidence_payload(payload: dict[str, Any]) -> list[str]:
    rows = payload.get("rows")
    failures = _validate_non_empty_rows(rows, "multi_seed")
    if failures or not isinstance(rows, list):
        return failures
    required_fields = {
        "seed_id": str,
        "track": str,
        "baseline_score": (int, float),
        "candidate_score": (int, float),
        "constraints_passed": bool,
        "held_out_passed": bool,
    }
    return failures + _validate_row_fields(rows, required_fields)


def _validate_heldout_evidence_payload(payload: dict[str, Any]) -> list[str]:
    rows = payload.get("rows")
    failures = _validate_non_empty_rows(rows, "heldout")
    if failures or not isinstance(rows, list):
        return failures
    required_fields = {
        "case_id": str,
        "passed": bool,
        "operator_moves_covered": bool,
        "reject_claims_avoided": bool,
        "success_gate_met": bool,
        "privacy_lane_respected": bool,
    }
    return failures + _validate_row_fields(rows, required_fields)


def _validate_review_gate_evidence_payload(payload: dict[str, Any]) -> list[str]:
    gates = payload.get("gates")
    if not isinstance(gates, dict):
        return ["missing_gates_object"]
    failures: list[str] = []
    for gate, fields in _REVIEW_GATE_REQUIREMENTS.items():
        value = gates.get(gate)
        if not isinstance(value, dict):
            failures.append(f"missing_gate:{gate}")
            continue
        if value.get("passed") is not True:
            failures.append(f"gate_field_invalid:{gate}:passed")
        for field in fields:
            if not isinstance(value.get(field), str) or not value.get(field, "").strip():
                failures.append(f"gate_field_invalid:{gate}:{field}")
        if gate == "publication_approval":
            if value.get("approved_claim") != "network_absorbable":
                failures.append("gate_field_invalid:publication_approval:approved_claim")
            if not isinstance(value.get("network_publication_allowed"), bool):
                failures.append(
                    "gate_field_invalid:publication_approval:network_publication_allowed"
                )
    return failures


def _validate_promotion_evidence_bundle_payload(payload: dict[str, Any]) -> list[str]:
    checks = payload.get("checks")
    if not isinstance(checks, dict):
        return ["missing_checks_object"]
    failures: list[str] = []
    for key in (
        "multi_seed_validation",
        "held_out_founder_advice_pass",
        "review_gates",
    ):
        if not isinstance(checks.get(key), str) or not checks.get(key, "").strip():
            failures.append(f"missing_check_path:{key}")
    return failures


def _validate_non_empty_rows(value: Any, kind: str) -> list[str]:
    if not isinstance(value, list):
        return [f"missing_rows:{kind}"]
    if not value:
        return [f"empty_rows:{kind}"]
    if not all(isinstance(row, dict) for row in value):
        return [f"invalid_rows:{kind}"]
    return []


def _validate_row_fields(
    rows: list[dict[str, Any]],
    required_fields: dict[str, type | tuple[type, ...]],
) -> list[str]:
    failures: list[str] = []
    for index, row in enumerate(rows):
        row_id = str(row.get("seed_id") or row.get("case_id") or f"row_{index + 1}")
        for field, expected_type in required_fields.items():
            value = row.get(field)
            if isinstance(value, bool) and expected_type in ((int, float), int, float):
                failures.append(f"row_field_invalid:{row_id}:{field}")
            elif not isinstance(value, expected_type):
                failures.append(f"row_field_invalid:{row_id}:{field}")
            elif isinstance(value, str) and not value.strip():
                failures.append(f"row_field_invalid:{row_id}:{field}")
    return failures


def _next_actions(missing_gates: list[str], requested_claim: str) -> list[str]:
    actions = [
        "Keep Startup YC at transfer_supported until promotion gates pass.",
    ]
    if requested_claim == "network_absorbable":
        actions.append(
            "Do not publish or network-absorb this packet without multi-seed validation, human/operator calibration, privacy review, rollback review, and publication approval."
        )
    if missing_gates:
        actions.append("Complete and record explicit pass evidence for: " + ", ".join(missing_gates) + ".")
    return actions


def _multi_seed_next_actions(
    *,
    gate_passed: bool,
    required_tracks: list[str],
    minimum_seeds_per_track: int,
) -> list[str]:
    if gate_passed:
        return [
            "Record this as multi_seed_validation evidence only.",
            "Keep Startup YC below network_absorbable until calibration, privacy, rollback, and publication gates also pass.",
        ]
    return [
        "Collect complete Startup YC multi-seed evidence before considering network absorption.",
        "Each required track needs at least "
        f"{minimum_seeds_per_track} eligible seeds: {', '.join(required_tracks)}.",
        "Every row must pass held-out constraints and meet the minimum delta.",
    ]


def _heldout_next_actions(*, gate_passed: bool) -> list[str]:
    if gate_passed:
        return [
            "Record this as held_out_founder_advice_pass evidence only.",
            "Keep Startup YC below network_absorbable until multi-seed, calibration, privacy, rollback, and publication gates also pass.",
        ]
    return [
        "Evaluate every held-out founder-advice case before promotion.",
        "Each case needs explicit pass flags for operator moves, rejected claims, success gate, and privacy lane.",
        "Keep Startup YC at transfer_supported while held-out evidence is absent or incomplete.",
    ]


def _review_gates_next_actions(*, gate_passed: bool) -> list[str]:
    if gate_passed:
        return [
            "Record this as human review gate evidence only.",
            "Keep Startup YC below network_absorbable until promotion-gate status explicitly records every required gate as passed.",
        ]
    return [
        "Collect structured evidence for human/operator calibration, privacy review, rollback review, and publication approval.",
        "Publication approval must explicitly name network_absorbable and set network_publication_allowed=true.",
        "Keep Startup YC at transfer_supported while review evidence is absent or incomplete.",
    ]


def _promotion_evidence_next_actions(*, all_supported: bool) -> list[str]:
    if all_supported:
        return [
            "Treat this as coherent promotion evidence, not final promotion.",
            "Run startup-yc-promotion-gate-check after the validation plan records explicit gate_status values.",
            "Keep Startup YC below network_absorbable until the plan removes prohibited claims and publication boundary blocks.",
        ]
    return [
        "Regenerate or repair the individual gate check outputs before final promotion review.",
        "Every bundled check must match the validation plan path, expected schema, and gate_passed=true.",
        "Do not infer network absorption from partial or stale saved evidence.",
    ]


def _validation_evidence_next_actions(
    *,
    evidence_kind: str,
    blocked: bool,
) -> list[str]:
    if not blocked:
        return [
            f"Use this {evidence_kind} packet as raw input for its Startup YC gate command.",
            "Keep final promotion blocked until gate outputs, bundle checks, and review gates pass.",
        ]
    return [
        "Repair the raw Startup YC evidence shape before running gate checks.",
        "Use startup-yc-validation-evidence.schema.json as the packet contract.",
        "Do not convert malformed raw evidence into promotion support.",
    ]


def _validation_suite_next_actions(
    *,
    required_subchecks_passed: bool,
    final_promotion_ready: bool,
) -> list[str]:
    if final_promotion_ready:
        return [
            "Treat this as validation-suite readiness only.",
            "Complete any external governance process before publication or network absorption.",
        ]
    if required_subchecks_passed:
        return [
            "Saved evidence subchecks are coherent, but final promotion is still blocked by the validation plan.",
            "Update gate_status, prohibited claims, and publication boundary only after explicit human approval.",
            "Do not claim network_absorbable from subcheck evidence alone.",
        ]
    return [
        "Repair blocked validation subchecks before final promotion review.",
        "Run the individual Startup YC gate commands to regenerate fresh evidence.",
        "Keep Startup YC at transfer_supported while suite blockers remain.",
    ]


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _input_provenance(path: Path | None, display_path: str | None) -> dict[str, Any]:
    provenance: dict[str, Any] = {
        "source": "startup_yc_operator_validation_v1",
        "input_hashes": {},
        "missing_inputs": [],
    }
    if path is None or display_path is None:
        return provenance
    if not path.exists():
        provenance["missing_inputs"] = [display_path]
        return provenance
    provenance["input_hashes"] = {display_path: _file_sha256(path)}
    return provenance


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_related_path(base_path: Path, related_path: str) -> Path:
    path = Path(related_path)
    if path.is_absolute():
        return path
    return base_path.parent / path


def _list_str(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]


def _int_value(value: Any, *, default: int) -> int:
    return value if isinstance(value, int) else default


def _float_value(value: Any, *, default: float) -> float:
    return float(value) if isinstance(value, int | float) else default


def _number_value(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    return float(value) if isinstance(value, int | float) else None


def _nested(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
