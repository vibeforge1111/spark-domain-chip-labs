"""Startup YC promotion gate checks.

This module keeps Startup YC network absorption conservative: validation plans
can document future gates, but the checker blocks stronger claims until the
plan explicitly removes prohibitions and records every required gate as passed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "adaptive_creator_loop.startup_yc_promotion_gate_check.v1"
MULTI_SEED_SCHEMA_VERSION = "adaptive_creator_loop.startup_yc_multi_seed_check.v1"


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
        "blocking_checks": blocking_checks,
        "next_actions": _multi_seed_next_actions(
            gate_passed=gate_passed,
            required_tracks=required_tracks,
            minimum_seeds_per_track=minimum_seeds_per_track,
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


def _load_multi_seed_rows(path: Path) -> list[dict[str, Any]]:
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


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


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
