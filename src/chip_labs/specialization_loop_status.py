"""Specialization-loop status guardrails owned by Domain Chip Labs."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any


SCHEMA_VERSION = "adaptive_creator_loop.specialization_loop_status.v1"
CHECK_SCHEMA_VERSION = "adaptive_creator_loop.specialization_loop_status_check.v1"
INSIGHT_SCHEMA_VERSION = "adaptive_creator_loop.specialization_loop_insight_packet.v1"
INSIGHT_CHECK_SCHEMA_VERSION = "adaptive_creator_loop.specialization_loop_insight_check.v1"
DOMAIN_CHIP_OWNER_REPO = "spark-domain-chip-labs"
OWNERSHIP_SCOPE = "specialization_loop_status_contract"
DECISIONS = {"improved", "held_steady", "regressed", "unproven"}
REQUIRED_IMPROVEMENT_PROOFS = ("baseline", "candidate", "comparison")
OPTIONAL_PASS_PROOFS = ("held_out", "trap")
INSIGHT_PACKET_KIND = "local_private_specialization_insight"
INSIGHT_SHARE_STATES = {"local_only", "private_workspace", "review_candidate"}
INSIGHT_EVIDENCE_TIERS = {
    "prototype",
    "benchmark_signal",
    "focused_pattern",
    "candidate_review",
    "transfer_supported",
}
INSIGHT_REQUIRED_FALSE_FLAGS = (
    "network_absorbable",
    "network_publication_allowed",
    "memory_promotion_allowed",
    "product_runtime_wiring_allowed",
)
CLAIM_BOUNDARY = (
    "Domain Chip Labs status only: improved requires baseline, candidate, "
    "comparison, held-out, and trap proof; missing proof means unproven."
)
INSIGHT_CLAIM_BOUNDARY = (
    "Local/private specialization insight only: may summarize reusable lessons "
    "from a canonical status packet, but cannot approve network absorption, "
    "publication, memory promotion, or product runtime wiring."
)


def build_specialization_loop_status(
    *,
    loop_id: str,
    path_id: str,
    domain_chip_id: str,
    domain_chip_name: str,
    benchmark_pack_id: str,
    stage: str,
    status: str,
    evidence_state: str,
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    comparison: dict[str, Any],
    held_out: dict[str, Any],
    trap: dict[str, Any],
    decision: str,
    next_move: str,
    path_manifest_ref: str = "specialization-path/path.manifest.json",
    domain_chip_manifest_ref: str = "domain-chip/chip.manifest.json",
    benchmark_manifest_ref: str = "benchmark/benchmark_pack.manifest.json",
    benchmark_pack_version: str = "v1",
    workspace_links: list[dict[str, Any]] | None = None,
    raw_artifact_refs: list[dict[str, Any]] | None = None,
    updated_at: str | None = None,
) -> dict[str, Any]:
    """Build a canonical specialization-loop status packet."""

    return {
        "schema_version": SCHEMA_VERSION,
        "loop_id": loop_id,
        "path": {
            "path_id": path_id,
            "manifest_ref": path_manifest_ref,
        },
        "domain_chip": {
            "chip_id": domain_chip_id,
            "name": domain_chip_name,
            "owner_repo": DOMAIN_CHIP_OWNER_REPO,
            "ownership_scope": OWNERSHIP_SCOPE,
            "manifest_ref": domain_chip_manifest_ref,
        },
        "benchmark_pack": {
            "pack_id": benchmark_pack_id,
            "manifest_ref": benchmark_manifest_ref,
            "version": benchmark_pack_version,
        },
        "stage": stage,
        "status": status,
        "evidence_state": evidence_state,
        "baseline": baseline,
        "candidate": candidate,
        "comparison": comparison,
        "held_out": held_out,
        "trap": trap,
        "decision": decision,
        "claim_boundary": CLAIM_BOUNDARY,
        "next_move": next_move,
        "workspace_links": workspace_links or [],
        "raw_artifact_refs": raw_artifact_refs or [],
        "updated_at": updated_at or _utc_now(),
    }


def check_specialization_loop_status(packet: dict[str, Any]) -> dict[str, Any]:
    """Return a dependency-free guardrail check for a status packet."""

    blocking_checks = _base_blockers(packet)
    decision = str(packet.get("decision") or "")
    improvement_blockers = improvement_proof_blockers(packet)
    if decision == "improved":
        blocking_checks.extend(improvement_blockers)
    effective_decision = (
        "unproven" if decision == "improved" and improvement_blockers else decision
    )
    blocking_checks = _dedupe(blocking_checks)
    return {
        "schema_version": CHECK_SCHEMA_VERSION,
        "loop_id": packet.get("loop_id"),
        "decision": decision,
        "effective_decision": (
            effective_decision if effective_decision in DECISIONS else "unproven"
        ),
        "improved_claim_allowed": decision == "improved" and not improvement_blockers,
        "blocking_checks": blocking_checks,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def build_specialization_loop_insight_packet(
    *,
    packet_id: str,
    loop_id: str,
    source_status_ref: str,
    source_status_sha256: str,
    source_decision: str,
    source_improved_claim_allowed: bool,
    evidence_tier: str,
    insight_title: str,
    insight_summary: str,
    reusable_lesson: str,
    applies_to: list[str],
    does_not_apply_to: list[str],
    proof_refs: list[dict[str, Any]],
    share_state: str = "private_workspace",
    privacy_reviewed: bool = False,
    next_actions: list[str] | None = None,
    updated_at: str | None = None,
) -> dict[str, Any]:
    """Build a local/private insight packet linked to a canonical status packet."""

    return {
        "schema_version": INSIGHT_SCHEMA_VERSION,
        "packet_id": packet_id,
        "packet_kind": INSIGHT_PACKET_KIND,
        "loop_id": loop_id,
        "source_status": {
            "schema_version": SCHEMA_VERSION,
            "artifact_ref": source_status_ref,
            "sha256": source_status_sha256,
            "decision": source_decision,
            "improved_claim_allowed": source_improved_claim_allowed,
        },
        "share_state": share_state,
        "evidence_tier": evidence_tier,
        "insight": {
            "title": insight_title,
            "summary": insight_summary,
            "reusable_lesson": reusable_lesson,
            "applies_to": applies_to,
            "does_not_apply_to": does_not_apply_to,
        },
        "proof_refs": proof_refs,
        "privacy": {
            "reviewed": privacy_reviewed,
            "raw_prompt_exported": False,
            "provider_output_exported": False,
            "chat_or_user_id_exported": False,
            "memory_body_exported": False,
            "artifact_body_exported": False,
            "secret_value_exported": False,
        },
        "promotion": {
            "network_absorbable": False,
            "network_publication_allowed": False,
            "memory_promotion_allowed": False,
            "product_runtime_wiring_allowed": False,
            "allowed_next_lanes": [
                "local_only",
                "private_workspace",
                "review_candidate",
            ],
            "forbidden_claims": [
                "network_absorbable",
                "network_publication_allowed",
                "memory_promotion_allowed",
                "product_runtime_wiring_allowed",
            ],
            "required_before_network_absorption": [
                "multi-seed validation",
                "human/operator calibration",
                "privacy review",
                "rollback review",
                "publication approval",
                "product runtime review",
                "publication authority",
            ],
        },
        "claim_boundary": INSIGHT_CLAIM_BOUNDARY,
        "next_actions": next_actions
        or [
            "Keep the insight in local/private lanes until promotion gates pass.",
            "Review privacy, rollback, calibration, and publication authority before network absorption.",
        ],
        "updated_at": updated_at or _utc_now(),
    }


def check_specialization_loop_insight_packet(
    packet: dict[str, Any],
    *,
    status_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Check a local/private insight packet without approving promotion."""

    blocking_checks = _insight_blockers(packet, status_packet=status_packet)
    verdict = "pass" if not blocking_checks else "blocked"
    return {
        "schema_version": INSIGHT_CHECK_SCHEMA_VERSION,
        "packet_id": packet.get("packet_id"),
        "loop_id": packet.get("loop_id"),
        "verdict": verdict,
        "local_private_safe": verdict == "pass",
        "network_absorbable": False,
        "blocking_checks": blocking_checks,
        "claim_boundary": INSIGHT_CLAIM_BOUNDARY,
        "next_actions": _insight_next_actions(blocking_checks),
    }


def improvement_proof_blockers(packet: dict[str, Any]) -> list[str]:
    """List proof gaps that prevent an `improved` specialization-loop claim."""

    blockers: list[str] = []
    for field in REQUIRED_IMPROVEMENT_PROOFS:
        proof = packet.get(field)
        allowed = {"present", "pass"} if field != "comparison" else {"pass"}
        if not _proof_has_allowed_status(proof, allowed, require_artifact_ref=True):
            blockers.append(f"{field}_proof_missing")

    for field in OPTIONAL_PASS_PROOFS:
        proof = packet.get(field)
        if not _proof_has_allowed_status(
            proof,
            {"pass", "not_required"},
            require_artifact_ref=_proof_status(proof) != "not_required",
        ):
            blockers.append(f"{field}_proof_missing")

    if packet.get("evidence_state") != "complete":
        blockers.append("evidence_state_not_complete")
    return _dedupe(blockers)


def _insight_blockers(
    packet: dict[str, Any],
    *,
    status_packet: dict[str, Any] | None,
) -> list[str]:
    blockers: list[str] = []
    if packet.get("schema_version") != INSIGHT_SCHEMA_VERSION:
        blockers.append("schema_version")
    if packet.get("packet_kind") != INSIGHT_PACKET_KIND:
        blockers.append("packet_kind")
    if not str(packet.get("packet_id") or "").strip():
        blockers.append("packet_id")
    if not str(packet.get("loop_id") or "").strip():
        blockers.append("loop_id")
    if packet.get("share_state") not in INSIGHT_SHARE_STATES:
        blockers.append("share_state")
    if packet.get("evidence_tier") not in INSIGHT_EVIDENCE_TIERS:
        blockers.append("evidence_tier")

    source_status = packet.get("source_status")
    if not isinstance(source_status, dict):
        blockers.append("source_status")
    else:
        blockers.extend(_source_status_blockers(source_status))

    insight = packet.get("insight")
    if not isinstance(insight, dict):
        blockers.append("insight")
    else:
        for field in (
            "title",
            "summary",
            "reusable_lesson",
        ):
            if not str(insight.get(field) or "").strip():
                blockers.append(f"insight_{field}")
        for field in ("applies_to", "does_not_apply_to"):
            values = insight.get(field)
            if not isinstance(values, list) or not any(
                str(value).strip() for value in values
            ):
                blockers.append(f"insight_{field}")

    proof_refs = packet.get("proof_refs")
    if not isinstance(proof_refs, list) or not proof_refs:
        blockers.append("proof_refs")
    else:
        for index, proof_ref in enumerate(proof_refs):
            blockers.extend(_proof_ref_blockers(index, proof_ref))

    privacy = packet.get("privacy")
    if not isinstance(privacy, dict):
        blockers.append("privacy")
    else:
        if (
            packet.get("share_state") == "review_candidate"
            and privacy.get("reviewed") is not True
        ):
            blockers.append("privacy_review_required_for_review_candidate")
        for field in (
            "raw_prompt_exported",
            "provider_output_exported",
            "chat_or_user_id_exported",
            "memory_body_exported",
            "artifact_body_exported",
            "secret_value_exported",
        ):
            if privacy.get(field) is not False:
                blockers.append(f"privacy_{field}_must_be_false")

    promotion = packet.get("promotion")
    if not isinstance(promotion, dict):
        blockers.append("promotion")
    else:
        for field in INSIGHT_REQUIRED_FALSE_FLAGS:
            if promotion.get(field) is not False:
                blockers.append(f"promotion_{field}_must_be_false")
        allowed_next_lanes = promotion.get("allowed_next_lanes")
        if not isinstance(allowed_next_lanes, list) or not allowed_next_lanes:
            blockers.append("promotion_allowed_next_lanes")
        elif not set(allowed_next_lanes).issubset(INSIGHT_SHARE_STATES):
            blockers.append("promotion_allowed_next_lanes_not_local_private")
        forbidden_claims = promotion.get("forbidden_claims")
        if (
            not isinstance(forbidden_claims, list)
            or "network_absorbable" not in forbidden_claims
        ):
            blockers.append("promotion_forbidden_claims_missing_network_absorbable")
        required = promotion.get("required_before_network_absorption")
        if not isinstance(required, list) or not required:
            blockers.append("promotion_required_before_network_absorption")

    if status_packet is not None:
        blockers.extend(_status_alignment_blockers(packet, status_packet))

    return _dedupe(blockers)


def _source_status_blockers(source_status: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if source_status.get("schema_version") != SCHEMA_VERSION:
        blockers.append("source_status_schema_version")
    if not str(source_status.get("artifact_ref") or "").strip():
        blockers.append("source_status_artifact_ref")
    if not _looks_like_sha256(source_status.get("sha256")):
        blockers.append("source_status_sha256")
    decision = source_status.get("decision")
    if decision not in DECISIONS:
        blockers.append("source_status_decision")
    if (
        decision == "improved"
        and source_status.get("improved_claim_allowed") is not True
    ):
        blockers.append("source_status_improved_claim_not_allowed")
    return blockers


def _proof_ref_blockers(index: int, proof_ref: Any) -> list[str]:
    if not isinstance(proof_ref, dict):
        return [f"proof_ref:{index}:shape"]
    blockers: list[str] = []
    for field in ("label", "artifact_ref", "evidence_role"):
        if not str(proof_ref.get(field) or "").strip():
            blockers.append(f"proof_ref:{index}:{field}")
    if not _looks_like_sha256(proof_ref.get("sha256")):
        blockers.append(f"proof_ref:{index}:sha256")
    return blockers


def _status_alignment_blockers(
    packet: dict[str, Any],
    status_packet: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if status_packet.get("loop_id") != packet.get("loop_id"):
        blockers.append("source_status_loop_id_mismatch")
    source_status = packet.get("source_status")
    if not isinstance(source_status, dict):
        return blockers
    if source_status.get("decision") != status_packet.get("decision"):
        blockers.append("source_status_decision_mismatch")
    status_check = check_specialization_loop_status(status_packet)
    if (
        source_status.get("decision") == "improved"
        and not status_check["improved_claim_allowed"]
    ):
        blockers.append("source_status_canonical_improved_claim_blocked")
    return blockers


def _insight_next_actions(blocking_checks: list[str]) -> list[str]:
    if not blocking_checks:
        return [
            "Use the insight only in local/private review lanes.",
            "Keep network absorption blocked until the full promotion bundle passes.",
        ]
    return [
        "Keep this insight out of shared doctrine until blockers are repaired.",
        "Re-link it to a canonical status packet and strip private/raw payload exports.",
    ]


def _base_blockers(packet: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if packet.get("schema_version") != SCHEMA_VERSION:
        blockers.append("schema_version")
    if packet.get("decision") not in DECISIONS:
        blockers.append("decision")

    domain_chip = packet.get("domain_chip")
    if not isinstance(domain_chip, dict):
        blockers.append("domain_chip")
    else:
        if domain_chip.get("owner_repo") != DOMAIN_CHIP_OWNER_REPO:
            blockers.append("domain_chip_owner_repo")
        if domain_chip.get("ownership_scope") != OWNERSHIP_SCOPE:
            blockers.append("domain_chip_ownership_scope")

    if not str(packet.get("loop_id") or "").strip():
        blockers.append("loop_id")
    return blockers


def _proof_has_allowed_status(
    proof: Any,
    allowed_statuses: set[str],
    *,
    require_artifact_ref: bool,
) -> bool:
    if not isinstance(proof, dict):
        return False
    status = _proof_status(proof)
    if status not in allowed_statuses:
        return False
    if require_artifact_ref and not str(proof.get("artifact_ref") or "").strip():
        return False
    return True


def _proof_status(proof: Any) -> str:
    if not isinstance(proof, dict):
        return "missing"
    return str(proof.get("status") or "missing")


def _looks_like_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and re.fullmatch(r"[a-f0-9]{64}", value) is not None
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))
