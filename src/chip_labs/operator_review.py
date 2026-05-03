"""Generic operator-review packets for generated creator systems."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PACKET_SCHEMA_VERSION = "adaptive_creator_loop.operator_review_packet.v1"
CHECK_SCHEMA_VERSION = "adaptive_creator_loop.operator_review_check.v1"
REQUIRED_REVIEW_GATES = (
    "human_operator_calibration",
    "privacy_review",
    "rollback_review",
    "publication_approval",
)


def load_operator_review_packet(path: str | Path) -> dict[str, Any]:
    packet_path = Path(path)
    data = json.loads(packet_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{packet_path} must contain a JSON object")
    return data


def build_operator_review_packet(
    *,
    review_id: str,
    creator_run_id: str,
    domain: str,
    evidence_tier: str,
    known_limits: list[str] | None = None,
    forbidden_claims: list[str] | None = None,
    requested_claim: str = "network_absorbable",
) -> dict[str, Any]:
    """Build an open review packet for a generated creator run."""

    forbidden = list(forbidden_claims or [])
    if requested_claim not in forbidden:
        forbidden.append(requested_claim)
    return {
        "schema_version": PACKET_SCHEMA_VERSION,
        "review_id": review_id,
        "creator_run_id": creator_run_id,
        "domain": domain,
        "requested_claim": requested_claim,
        "evidence_tier": evidence_tier,
        "network_absorbable": False,
        "gate_status": {gate: False for gate in REQUIRED_REVIEW_GATES},
        "gates": {
            "human_operator_calibration": {
                "status": "missing",
                "reviewer": None,
                "evidence_ref": None,
                "calibration_notes": "Open: human/operator calibration is not complete.",
            },
            "privacy_review": {
                "status": "missing",
                "reviewer": None,
                "evidence_ref": None,
                "privacy_boundary": "workspace_only",
                "privacy_decision": "Open: privacy review is not complete.",
            },
            "rollback_review": {
                "status": "missing",
                "reviewer": None,
                "evidence_ref": None,
                "rollback_rule": "Open: rollback review is not complete.",
            },
            "publication_approval": {
                "status": "missing",
                "reviewer": None,
                "evidence_ref": None,
                "approved_claim": None,
                "network_publication_allowed": False,
                "publication_decision": "Open: publication approval is not complete.",
            },
        },
        "known_limits": list(known_limits or []),
        "forbidden_claims": forbidden,
        "claim_boundary": (
            "Operator review evidence is one promotion gate family only; it does "
            "not approve network_absorbable without multi-seed validation, privacy, "
            "rollback, and publication gates in the full promotion bundle."
        ),
        "next_actions": [
            "Collect named reviewer evidence for every review gate.",
            "Keep network_absorbable false until the full promotion gate bundle passes.",
        ],
    }


def check_operator_review_packet(packet: dict[str, Any]) -> dict[str, Any]:
    """Check a generic operator-review packet without approving absorption."""

    blocking_checks: list[str] = []
    if packet.get("schema_version") != PACKET_SCHEMA_VERSION:
        blocking_checks.append("schema_version")
    requested_claim = str(packet.get("requested_claim") or "network_absorbable")
    if packet.get("network_absorbable") is not False:
        blocking_checks.append("network_absorbable_must_be_false")

    forbidden_claims = packet.get("forbidden_claims")
    if not isinstance(forbidden_claims, list) or requested_claim not in {
        str(claim) for claim in forbidden_claims
    }:
        blocking_checks.append(f"forbidden_claim_missing:{requested_claim}")

    gates = packet.get("gates")
    if not isinstance(gates, dict):
        gates = {}
        blocking_checks.append("gates_missing")

    gate_status: dict[str, bool] = {}
    for gate in REQUIRED_REVIEW_GATES:
        row = gates.get(gate)
        gate_failures = _gate_failures(gate, row, requested_claim=requested_claim)
        gate_status[gate] = not gate_failures
        blocking_checks.extend(f"gate_failure:{gate}:{failure}" for failure in gate_failures)

    verdict = "pass" if not blocking_checks else "blocked"
    return {
        "schema_version": CHECK_SCHEMA_VERSION,
        "review_id": packet.get("review_id"),
        "creator_run_id": packet.get("creator_run_id"),
        "domain": packet.get("domain"),
        "requested_claim": requested_claim,
        "verdict": verdict,
        "gate_status": gate_status,
        "missing_gates": [
            gate for gate, passed in gate_status.items()
            if not passed
        ],
        "blocking_checks": blocking_checks,
        "network_absorbable": False,
        "claim_boundary": (
            "Passing operator review gates is not sufficient for network absorption; "
            "the full promotion gate bundle must still pass."
        ),
        "next_actions": _next_actions(verdict),
    }


def _gate_failures(
    gate: str,
    row: Any,
    *,
    requested_claim: str,
) -> list[str]:
    if not isinstance(row, dict):
        return ["missing"]
    failures: list[str] = []
    if row.get("status") != "passed":
        failures.append("not_passed")
    for field in ("reviewer", "evidence_ref"):
        if not isinstance(row.get(field), str) or not row[field].strip():
            failures.append(f"{field}_missing")
    if gate == "human_operator_calibration":
        _require_text(row, "calibration_notes", failures)
    elif gate == "privacy_review":
        _require_text(row, "privacy_decision", failures)
        _require_text(row, "privacy_boundary", failures)
    elif gate == "rollback_review":
        _require_text(row, "rollback_rule", failures)
    elif gate == "publication_approval":
        _require_text(row, "publication_decision", failures)
        if row.get("approved_claim") != requested_claim:
            failures.append("approved_claim_missing")
        if row.get("network_publication_allowed") is not True:
            failures.append("network_publication_not_allowed")
    return failures


def _require_text(row: dict[str, Any], field: str, failures: list[str]) -> None:
    if not isinstance(row.get(field), str) or not row[field].strip():
        failures.append(f"{field}_missing")


def _next_actions(verdict: str) -> list[str]:
    if verdict == "pass":
        return [
            "Record this as operator-review evidence only.",
            "Keep network_absorbable false until multi-seed, privacy, rollback, and publication checks pass in the full promotion bundle.",
        ]
    return [
        "Collect named reviewer, evidence reference, calibration, privacy, rollback, and publication decision fields.",
        "Do not use incomplete review evidence to upgrade generated creator systems.",
    ]
