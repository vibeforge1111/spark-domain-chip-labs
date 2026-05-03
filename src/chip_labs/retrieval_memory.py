"""Local retrieval-memory promotion checks for creator-system proof fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CLAIM_BOUNDARY = (
    "local retrieval-memory contract only; no production memory runtime or "
    "network-shareable recall claim"
)

ALLOWED_LANES = {
    "local_workspace",
    "private_user",
    "network_shareable",
}

RESIDUE_SOURCE_KINDS = {
    "conversation_residue",
    "tool_stdout",
    "route_state",
    "workflow_debris",
}


def load_retrieval_memory_packet(path: str | Path) -> dict[str, Any]:
    packet_path = Path(path)
    data = json.loads(packet_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{packet_path} must contain a JSON object")
    return data


def check_retrieval_memory_packet(packet: dict[str, Any]) -> dict[str, Any]:
    entries = packet.get("entries")
    checks: list[dict[str, Any]] = []
    if not isinstance(entries, list) or not entries:
        _append_check(
            checks,
            "entries_present",
            False,
            "Packet includes memory entries.",
            "Packet must include at least one memory entry.",
            paths=[],
        )
        entries = []
    else:
        _append_check(
            checks,
            "entries_present",
            True,
            "Packet includes memory entries.",
            "Packet must include at least one memory entry.",
            paths=[],
        )

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            _append_check(
                checks,
                f"entry:{index}:shape",
                False,
                "Entry is an object.",
                "Each memory entry must be a JSON object.",
                paths=[],
            )
            continue
        _check_entry(index, entry, checks)

    blocking_checks = [
        check["name"] for check in checks if check["status"] == "fail"
    ]
    verdict = "blocked" if blocking_checks else "pass"
    return {
        "schema_version": "adaptive_creator_loop.retrieval_memory_check.v1",
        "verdict": verdict,
        "calibration_verdict": "blocked" if blocking_checks else "pass",
        "claim_boundary": CLAIM_BOUNDARY,
        "status_counts": _status_counts(checks),
        "blocking_checks": blocking_checks,
        "checks": checks,
        "promotion": {
            "allowed": verdict == "pass",
            "network_absorbable": False,
            "reason": (
                "Local memory retrieval contract is coherent."
                if verdict == "pass"
                else "Do not promote retrieved context until blockers are repaired."
            ),
        },
        "next_actions": _next_actions(blocking_checks),
    }


def _check_entry(
    index: int,
    entry: dict[str, Any],
    checks: list[dict[str, Any]],
) -> None:
    prefix = f"entry:{index}"
    lane = str(entry.get("memory_lane") or "")
    source_kind = str(entry.get("source_kind") or "")
    promotion_allowed = entry.get("promotion_allowed") is True
    contradicted_by = entry.get("contradicted_by")
    source_refs = entry.get("source_refs")
    provenance = entry.get("provenance")
    review = entry.get("review")

    _append_check(
        checks,
        f"{prefix}:lane",
        lane in ALLOWED_LANES,
        f"Memory lane `{lane}` is supported.",
        f"Memory lane must be one of {', '.join(sorted(ALLOWED_LANES))}.",
        paths=[],
    )
    _append_check(
        checks,
        f"{prefix}:provenance",
        isinstance(provenance, dict)
        and bool(provenance.get("source_path"))
        and bool(provenance.get("captured_at")),
        "Entry includes source provenance.",
        "Entry must include provenance.source_path and provenance.captured_at.",
        paths=[],
    )
    _append_check(
        checks,
        f"{prefix}:source_refs",
        isinstance(source_refs, list) and bool(source_refs),
        "Entry includes exact source refs.",
        "Retrieved summaries need exact source refs before promotion.",
        paths=[],
    )
    _append_check(
        checks,
        f"{prefix}:provenance_source_ref",
        isinstance(provenance, dict)
        and isinstance(source_refs, list)
        and provenance.get("source_path") in source_refs,
        "Provenance source path is present in exact source refs.",
        "provenance.source_path must be one of the exact source_refs.",
        paths=list(source_refs or []),
    )
    _append_check(
        checks,
        f"{prefix}:residue_boundary",
        not (source_kind in RESIDUE_SOURCE_KINDS and promotion_allowed),
        "Workflow residue is not promoted as memory truth.",
        f"`{source_kind}` cannot be promoted as durable memory truth.",
        paths=list(source_refs or []),
    )
    _append_check(
        checks,
        f"{prefix}:freshness",
        not (
            entry.get("freshness") == "stale"
            and promotion_allowed
            and entry.get("revalidated") is not True
        ),
        "Stale memory is revalidated before promotion.",
        "Stale memory must be revalidated before promotion.",
        paths=list(source_refs or []),
    )
    _append_check(
        checks,
        f"{prefix}:contradiction",
        not (bool(contradicted_by) and promotion_allowed),
        "Contradicted memory is blocked from promotion.",
        "Contradicted memory must be quarantined or rewritten before promotion.",
        paths=list(contradicted_by or []),
    )
    _append_check(
        checks,
        f"{prefix}:network_review",
        not (
            lane == "network_shareable"
            and promotion_allowed
            and not (isinstance(review, dict) and review.get("approved") is True)
        ),
        "Network-shareable memory has explicit review.",
        "Network-shareable memory requires explicit review approval.",
        paths=[],
    )


def _append_check(
    checks: list[dict[str, Any]],
    name: str,
    condition: bool,
    pass_message: str,
    fail_message: str,
    *,
    paths: list[str],
) -> None:
    checks.append(
        {
            "name": name,
            "status": "pass" if condition else "fail",
            "message": pass_message if condition else fail_message,
            "paths": paths,
        }
    )


def _status_counts(checks: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"pass": 0, "warn": 0, "fail": 0}
    for check in checks:
        counts[check["status"]] += 1
    return counts


def _next_actions(blocking_checks: list[str]) -> list[str]:
    if not blocking_checks:
        return ["Use retrieved context locally with the declared privacy lane."]
    return [
        "Keep retrieved context out of durable memory and prompts until blockers are repaired.",
        "Prefer exact source artifacts over summaries or conversational residue.",
    ]
