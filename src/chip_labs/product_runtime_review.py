"""Product runtime review packets for creator-system release gates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PACKET_SCHEMA_VERSION = "adaptive_creator_loop.product_runtime_review_packet.v1"
CHECK_SCHEMA_VERSION = "adaptive_creator_loop.product_runtime_review_check.v1"
REQUIRED_SURFACES = (
    "builder",
    "telegram",
    "spawner",
    "canvas",
    "kanban",
)


def load_product_runtime_review_packet(path: str | Path) -> dict[str, Any]:
    packet_path = Path(path)
    data = json.loads(packet_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{packet_path} must contain a JSON object")
    return data


def build_open_product_runtime_review_packet(
    *,
    review_id: str,
    requested_release: str = "network_absorption",
) -> dict[str, Any]:
    """Build an open product runtime review packet with every surface blocked."""

    return {
        "schema_version": PACKET_SCHEMA_VERSION,
        "review_id": review_id,
        "requested_release": requested_release,
        "network_absorbable": False,
        "product_runtime_controls_wired": False,
        "surfaces": {
            surface: {
                "status": "missing",
                "reviewer": None,
                "evidence_ref": None,
                "runtime_wiring_reviewed": False,
                "read_only_adapter_preserved": False,
                "blocked_states_visible": False,
                "evidence_mode_preserved": False,
                "creator_controls_enabled": False,
                "network_publication_allowed": False,
                "rollback_plan_ref": None,
            }
            for surface in REQUIRED_SURFACES
        },
        "claim_boundary": (
            "Product runtime review evidence is required before exposing creator "
            "controls, but this packet does not wire product surfaces or approve "
            "network_absorbable."
        ),
        "next_actions": [
            "Review Builder, Telegram, Spawner, Canvas, and Kanban runtime branches separately.",
            "Keep creator controls disabled until every surface has rollback and blocked-state evidence.",
        ],
    }


def check_product_runtime_review_packet(packet: dict[str, Any]) -> dict[str, Any]:
    """Check product runtime review evidence without wiring product controls."""

    blocking_checks: list[str] = []
    if packet.get("schema_version") != PACKET_SCHEMA_VERSION:
        blocking_checks.append("schema_version")
    if packet.get("network_absorbable") is not False:
        blocking_checks.append("network_absorbable_must_be_false")
    if packet.get("product_runtime_controls_wired") is not False:
        blocking_checks.append("product_runtime_controls_must_not_be_wired_here")

    surfaces = packet.get("surfaces")
    if not isinstance(surfaces, dict):
        surfaces = {}
        blocking_checks.append("surfaces_missing")

    surface_status: dict[str, bool] = {}
    for surface in REQUIRED_SURFACES:
        row = surfaces.get(surface)
        failures = _surface_failures(surface, row)
        surface_status[surface] = not failures
        blocking_checks.extend(
            f"surface_failure:{surface}:{failure}" for failure in failures
        )

    blocking_checks = _dedupe(blocking_checks)
    verdict = "pass" if not blocking_checks else "blocked"
    return {
        "schema_version": CHECK_SCHEMA_VERSION,
        "review_id": packet.get("review_id"),
        "requested_release": packet.get("requested_release") or "network_absorption",
        "verdict": verdict,
        "surface_status": surface_status,
        "missing_surfaces": [
            surface for surface, passed in surface_status.items() if not passed
        ],
        "blocking_checks": blocking_checks,
        "network_absorbable": False,
        "claim_boundary": (
            "Passing product runtime review is not network absorption; it is one "
            "phase in the stronger-release gate bundle."
        ),
        "next_actions": _next_actions(verdict),
    }


def _surface_failures(surface: str, row: Any) -> list[str]:
    if not isinstance(row, dict):
        return ["missing"]
    failures: list[str] = []
    if row.get("status") != "passed":
        failures.append("not_passed")
    for field in ("reviewer", "evidence_ref", "rollback_plan_ref"):
        if not isinstance(row.get(field), str) or not row[field].strip():
            failures.append(f"{field}_missing")
    required_true_fields = (
        "runtime_wiring_reviewed",
        "read_only_adapter_preserved",
        "blocked_states_visible",
        "evidence_mode_preserved",
        "network_publication_allowed",
    )
    for field in required_true_fields:
        if row.get(field) is not True:
            failures.append(f"{field}_not_true")
    if row.get("creator_controls_enabled") is not False:
        failures.append("creator_controls_enabled_must_be_false_in_methodology_repo")
    if surface not in REQUIRED_SURFACES:
        failures.append("unknown_surface")
    return failures


def _next_actions(verdict: str) -> list[str]:
    if verdict == "pass":
        return [
            "Attach this as product runtime review evidence in creator-release-gate.",
            "Do not treat this packet as network absorption or product deployment by itself.",
        ]
    return [
        "Collect named reviewer, evidence reference, blocked-state, evidence-mode, and rollback evidence for every product surface.",
        "Keep product runtime controls disabled until product-repo reviews pass.",
    ]


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))
