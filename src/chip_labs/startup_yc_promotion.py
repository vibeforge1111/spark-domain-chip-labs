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


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _list_str(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]


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
