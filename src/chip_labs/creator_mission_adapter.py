"""Read-only creator mission adapter for product surfaces.

This module turns canonical creator-system packets into one product-safe status
object. It does not execute tools, publish packets, or mutate product surfaces.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "adaptive_creator_loop.creator_mission_status.v1"
CLAIM_BOUNDARY = (
    "read-only product adapter over canonical creator-system outputs; product "
    "surfaces must not invent verdicts, evidence tiers, or publication state"
)
SURFACES = ("builder", "telegram", "spawner", "canvas", "kanban")
NETWORK_REQUIRED_GATES = (
    "multi_seed_validation",
    "human_operator_calibration",
    "privacy_review",
    "rollback_review",
    "publication_approval",
)


def load_json_packet(path: str | Path) -> dict[str, Any]:
    packet_path = Path(path)
    data = json.loads(packet_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{packet_path} must contain a JSON object")
    return data


def build_creator_mission_status(
    *,
    smoke: dict[str, Any],
    mission_id: str = "creator-mission-local",
    publish_mode: str = "local_only",
    doctor: dict[str, Any] | None = None,
    tool_operation: dict[str, Any] | None = None,
    artifact_quality: dict[str, Any] | None = None,
    content_route: dict[str, Any] | None = None,
    retrieval_memory: dict[str, Any] | None = None,
    startup_validation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a read-only mission status from canonical packet outputs."""

    packets = {
        "smoke": smoke,
        "doctor": doctor,
        "tool_operation": tool_operation,
        "artifact_quality": artifact_quality,
        "content_route": content_route,
        "retrieval_memory": retrieval_memory,
        "startup_validation": startup_validation,
    }
    packet_summaries = _packet_summaries(packets)
    blocking_sources = [
        summary for summary in packet_summaries if summary["state"] == "blocked"
    ]
    warning_sources = [
        summary for summary in packet_summaries if summary["warning_count"] > 0
    ]
    smoke_verdict = str(smoke.get("verdict") or "unknown")
    evidence_tier = str(smoke.get("evidence_tier") or "prototype")
    stage_status = _stage_status(smoke_verdict, bool(blocking_sources))
    publication = _publication_gate(
        publish_mode=publish_mode,
        evidence_tier=evidence_tier,
        startup_validation=startup_validation,
    )
    blockers = _blockers(packet_summaries, publication)
    next_actions = _next_actions(smoke, doctor, publication, blockers)
    mission = {
        "schema_version": SCHEMA_VERSION,
        "mission_id": mission_id,
        "read_only": True,
        "claim_boundary": CLAIM_BOUNDARY,
        "canonical": {
            "verdict": smoke_verdict,
            "stage_status": stage_status,
            "evidence_tier": evidence_tier,
            "automation_blocked": bool(_nested(smoke, "automation", "blocked")),
            "blocking_checks": list(smoke.get("blocking_checks") or []),
            "warning_checks": list(smoke.get("warning_checks") or []),
            "missing_paths": list(smoke.get("missing_paths") or []),
            "recommended_next_command": _nested(
                smoke, "automation", "recommended_next_command"
            ),
        },
        "publication": publication,
        "source_packets": packet_summaries,
        "blockers": blockers,
        "warnings": [summary["packet"] for summary in warning_sources],
        "next_actions": next_actions,
    }
    mission["surface_adapters"] = _surface_adapters(mission)
    return mission


def _packet_summaries(packets: dict[str, dict[str, Any] | None]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for name, packet in packets.items():
        if packet is None:
            summaries.append({
                "packet": name,
                "present": False,
                "state": "missing",
                "verdict": None,
                "blocking_checks": [],
                "warning_count": 0,
                "claim_boundary": None,
            })
            continue
        blocking_checks = list(packet.get("blocking_checks") or [])
        state = _packet_state(packet)
        summaries.append({
            "packet": name,
            "present": True,
            "state": state,
            "verdict": packet.get("verdict"),
            "blocking_checks": blocking_checks,
            "warning_count": len(packet.get("warning_checks") or []),
            "claim_boundary": packet.get("claim_boundary"),
        })
    return summaries


def _packet_state(packet: dict[str, Any]) -> str:
    verdict = str(packet.get("verdict") or "").lower()
    if verdict in {"blocked", "fail", "failed"}:
        return "blocked"
    if packet.get("allowed") is False:
        return "blocked"
    if _nested(packet, "automation", "blocked") is True:
        return "blocked"
    if packet.get("blocking_checks"):
        return "blocked"
    return "ready"


def _stage_status(smoke_verdict: str, blocked: bool) -> str:
    if blocked or smoke_verdict == "blocked":
        return "blocked"
    if smoke_verdict == "ready_for_swarm_packet":
        return "review_required"
    if smoke_verdict in {"prototype", "ready_for_baseline"}:
        return smoke_verdict
    return "unknown"


def _publication_gate(
    *,
    publish_mode: str,
    evidence_tier: str,
    startup_validation: dict[str, Any] | None,
) -> dict[str, Any]:
    requested_network = publish_mode == "swarm_shared" or evidence_tier == "network_absorbable"
    gates = _startup_gate_status(startup_validation)
    missing_gates = [
        gate for gate in NETWORK_REQUIRED_GATES
        if gates.get(gate) is not True
    ]
    network_absorbable = requested_network and not missing_gates
    return {
        "publish_mode": publish_mode,
        "local_display_allowed": True,
        "github_pr_allowed": publish_mode == "github_pr",
        "swarm_shared_allowed": False,
        "network_absorbable": False,
        "requested_network_absorption": requested_network,
        "blocked_reason": (
            "Network absorption requires multi-seed validation, human/operator "
            "calibration, privacy review, rollback review, and publication approval."
            if requested_network and missing_gates
            else None
        ),
        "required_gates": list(NETWORK_REQUIRED_GATES),
        "missing_gates": missing_gates if requested_network else list(NETWORK_REQUIRED_GATES),
        "gate_status": gates,
        "unsafe_claim_blocked": not network_absorbable,
    }


def _startup_gate_status(startup_validation: dict[str, Any] | None) -> dict[str, bool]:
    if not startup_validation:
        return {gate: False for gate in NETWORK_REQUIRED_GATES}
    gate_values = startup_validation.get("gate_status")
    if isinstance(gate_values, dict):
        return {
            gate: gate_values.get(gate) is True
            for gate in NETWORK_REQUIRED_GATES
        }
    required_gates = startup_validation.get("required_promotion_gates")
    if not isinstance(required_gates, list):
        return {gate: False for gate in NETWORK_REQUIRED_GATES}
    return {gate: False for gate in NETWORK_REQUIRED_GATES}


def _blockers(
    packet_summaries: list[dict[str, Any]],
    publication: dict[str, Any],
) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    for summary in packet_summaries:
        if summary["state"] != "blocked":
            continue
        blockers.append({
            "source": summary["packet"],
            "blocking_checks": summary["blocking_checks"],
            "message": f"{summary['packet']} reports blocked state.",
        })
    if publication["requested_network_absorption"] and publication["missing_gates"]:
        blockers.append({
            "source": "publication_gate",
            "blocking_checks": publication["missing_gates"],
            "message": publication["blocked_reason"],
        })
    return blockers


def _next_actions(
    smoke: dict[str, Any],
    doctor: dict[str, Any] | None,
    publication: dict[str, Any],
    blockers: list[dict[str, Any]],
) -> list[str]:
    actions: list[str] = []
    if blockers:
        doctor_steps = doctor.get("repair_steps") if isinstance(doctor, dict) else None
        if isinstance(doctor_steps, list) and doctor_steps:
            actions.extend(
                str(step.get("action"))
                for step in doctor_steps
                if isinstance(step, dict) and step.get("action")
            )
        recommended = _nested(smoke, "automation", "recommended_next_command")
        if recommended:
            actions.append(str(recommended))
    else:
        actions.extend(str(action) for action in smoke.get("next_actions") or [])
    if publication["requested_network_absorption"]:
        actions.append(
            "Keep publication local until network absorption gates are explicitly approved."
        )
    return _dedupe(actions)


def _surface_adapters(mission: dict[str, Any]) -> dict[str, Any]:
    canonical = mission["canonical"]
    publication = mission["publication"]
    blockers = mission["blockers"]
    return {
        "builder": {
            "packet_kind": "builder_creator_readonly_handoff",
            "mission_id": mission["mission_id"],
            "read_only": True,
            "verdict": canonical["verdict"],
            "stage_status": canonical["stage_status"],
            "evidence_tier": canonical["evidence_tier"],
            "blocking_checks": canonical["blocking_checks"],
            "missing_paths": canonical["missing_paths"],
            "recommended_next_command": canonical["recommended_next_command"],
            "may_mutate_state": False,
        },
        "telegram": {
            "packet_kind": "telegram_creator_status_summary",
            "mission_id": mission["mission_id"],
            "text": _telegram_text(mission),
            "show_publication_warning": bool(publication["missing_gates"]),
            "may_request_secret_paste": False,
        },
        "spawner": {
            "packet_kind": "spawner_creator_trace_readonly",
            "mission_id": mission["mission_id"],
            "stage_status": canonical["stage_status"],
            "blockers": blockers,
            "publication": publication,
            "may_execute": False,
        },
        "canvas": {
            "packet_kind": "canvas_creator_graph_readonly",
            "mission_id": mission["mission_id"],
            "nodes": _canvas_nodes(mission),
            "edges": _canvas_edges(mission),
            "may_edit_artifacts": False,
        },
        "kanban": {
            "packet_kind": "kanban_creator_columns_readonly",
            "mission_id": mission["mission_id"],
            "columns": _kanban_columns(mission),
            "may_change_verdict": False,
        },
    }


def _telegram_text(mission: dict[str, Any]) -> str:
    canonical = mission["canonical"]
    parts = [
        f"Creator mission `{mission['mission_id']}` is `{canonical['stage_status']}`.",
        f"Canonical verdict: `{canonical['verdict']}`.",
        f"Evidence tier: `{canonical['evidence_tier']}`.",
    ]
    if mission["blockers"]:
        parts.append("Blocked by: " + ", ".join(blocker["source"] for blocker in mission["blockers"]))
    if mission["publication"]["missing_gates"]:
        parts.append("Network absorption is not approved.")
    return " ".join(parts)


def _canvas_nodes(mission: dict[str, Any]) -> list[dict[str, Any]]:
    canonical = mission["canonical"]
    packet_nodes = [
        {
            "id": summary["packet"],
            "label": summary["packet"],
            "status": summary["state"],
            "source": "canonical_packet",
        }
        for summary in mission["source_packets"]
        if summary["present"]
    ]
    return [
        {
            "id": "creator_mission",
            "label": "Creator Mission",
            "status": canonical["stage_status"],
            "source": "adapter",
        },
        *packet_nodes,
        {
            "id": "publication_gate",
            "label": "Publication Gate",
            "status": "blocked" if mission["publication"]["missing_gates"] else "ready",
            "source": "adapter",
        },
    ]


def _canvas_edges(mission: dict[str, Any]) -> list[dict[str, str]]:
    edges = [
        {"from": summary["packet"], "to": "creator_mission"}
        for summary in mission["source_packets"]
        if summary["present"]
    ]
    edges.append({"from": "creator_mission", "to": "publication_gate"})
    return edges


def _kanban_columns(mission: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    canonical = mission["canonical"]
    card = {
        "mission_id": mission["mission_id"],
        "title": "Creator mission status",
        "verdict": canonical["verdict"],
        "evidence_tier": canonical["evidence_tier"],
        "blocked": bool(mission["blockers"]),
    }
    columns = {
        "prototype": [],
        "ready_for_baseline": [],
        "review_required": [],
        "blocked": [],
    }
    target = "blocked" if mission["blockers"] else canonical["stage_status"]
    if target not in columns:
        target = "prototype"
    columns[target].append(card)
    return columns


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
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
