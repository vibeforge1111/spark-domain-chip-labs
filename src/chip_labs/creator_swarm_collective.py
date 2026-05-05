"""Dry-run Spark Swarm Collective payload projection for creator runs.

This module builds a SparkResearcherCollectiveSyncPayload-shaped object from a
local creator run. It does not sync, publish, mutate product surfaces, or grant
network absorption.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .creator_run import load_json, validate_creator_run


NETWORK_BOUNDARY = (
    "dry-run private workspace projection only; does not publish, sync, or "
    "approve network_absorbable"
)
ARTIFACT_REF_PATHS = (
    ("creator_intent", "source_note", "Creator intent", "creator-intent.json"),
    (
        "artifact_manifest",
        "source_note",
        "Created artifact manifest",
        "created-artifact-manifest.json",
    ),
    (
        "swarm_packet",
        "chip_packet",
        "Swarm contribution packet",
        "swarm/contribution_packet.json",
    ),
    (
        "absorption_summary",
        "benchmark_bridge",
        "Absorption summary",
        "reports/absorption_summary.json",
    ),
    (
        "transfer_summary",
        "benchmark_bridge",
        "Transfer summary",
        "reports/transfer_summary.json",
    ),
    (
        "evidence_ladder",
        "source_note",
        "Evidence ladder",
        "reports/evidence_ladder.md",
    ),
)


def build_creator_swarm_collective_payload(
    run_dir: str | Path,
    *,
    workspace_id: str,
    agent_id: str,
    emitted_at: str | None = None,
    repo_id: str | None = None,
    repo_label: str | None = None,
) -> dict[str, Any]:
    """Build a local Spark Swarm Collective dry-run payload from a creator run."""

    run_path = Path(run_dir)
    emitted = emitted_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    smoke = validate_creator_run(run_path).to_dict()
    intent = load_json(run_path / "creator-intent.json")
    swarm_packet = load_json(run_path / "swarm" / "contribution_packet.json")
    artifact_refs = _artifact_refs(run_path)

    contribution = swarm_packet.get("contribution") or {}
    evidence = swarm_packet.get("evidence") or {}
    domain_name = str(_nested(intent, "domain", "name") or contribution.get("domain") or "creator-system")
    domain_slug = str(_nested(intent, "domain", "short_slug") or _slug(domain_name))
    title = str(contribution.get("title") or f"{domain_name} creator run")
    summary = str(contribution.get("summary") or _nested(intent, "goal", "plain_language_goal") or title)
    evidence_tier = str(evidence.get("tier") or smoke.get("evidence_tier") or "candidate_review")
    insight_id = f"creator-insight-{domain_slug}"
    mastery_id = f"creator-mastery-{domain_slug}"
    outcome_id = f"creator-outcome-{domain_slug}"
    insight = _insight_record(
        insight_id=insight_id,
        specialization_id=domain_slug,
        summary=summary,
        evidence_tier=evidence_tier,
        artifact_refs=artifact_refs,
        emitted_at=emitted,
        confidence=_score_or_none(evidence.get("candidate_score")),
    )
    mastery = _mastery_record(
        mastery_id=mastery_id,
        insight_id=insight_id,
        specialization_scope=domain_slug,
        summary=title,
        evidence=evidence,
        evidence_tier=evidence_tier,
        emitted_at=emitted,
    )
    outcome = _outcome_record(
        outcome_id=outcome_id,
        target_id=mastery_id,
        summary=summary,
        evidence=evidence,
        emitted_at=emitted,
    )
    intelligence_pulse = _intelligence_pulse(
        specialization_id=domain_slug,
        specialization_label=domain_name,
        insight=insight,
        mastery=mastery,
        artifact_refs=artifact_refs,
        evidence=evidence,
    )
    return {
        "workspaceId": workspace_id,
        "agentId": agent_id,
        "runtimeSource": {
            "kind": "specialization_path",
            "version": "creator-system-dry-run.v1",
            "loopKind": "benchmark",
            "sourceInstanceId": str(swarm_packet.get("packet_id") or intent.get("run_id")),
            "sourceRunId": str(swarm_packet.get("creator_run_id") or intent.get("run_id")),
            "chipKey": domain_slug,
            "chipLabel": domain_name,
        },
        "specialization": {
            "id": domain_slug,
            "key": domain_slug,
            "label": domain_name,
            "memoryPolicy": "isolated",
        },
        "runtimePulse": {
            "agentId": agent_id,
            "repoId": repo_id,
            "repoLabel": repo_label,
            "runtimeState": _runtime_state(smoke),
            "passNumber": None,
            "stageKey": str(smoke.get("verdict") or "unknown"),
            "stageLabel": f"Creator run {smoke.get('verdict') or 'unknown'}",
            "blocker": _first_blocker(smoke),
            "recommendation": _nested(smoke, "automation", "recommended_next_command"),
            "lastUpdatedAt": emitted,
            "intelligencePulse": intelligence_pulse,
        },
        "intelligencePulse": intelligence_pulse,
        "evolutionPaths": [],
        "insights": [insight],
        "masteries": [mastery],
        "patterns": [],
        "masteryReviews": [
            {
                "id": f"creator-review-{domain_slug}",
                "targetId": mastery_id,
                "reviewType": "mastery",
                "decision": "defer",
                "reason": NETWORK_BOUNDARY,
                "recommendedNextStep": (
                    "Use the network proposal bundle and verified PR proof before "
                    "requesting public Spark Swarm absorption."
                ),
                "rollbackCondition": _nested(
                    swarm_packet, "governance", "rollback_or_deprecation_rule"
                ),
                "createdAt": emitted,
            }
        ],
        "contradictions": [],
        "upgrades": [],
        "upgradeDeliveries": [],
        "outcomes": [outcome],
        "artifactRefs": artifact_refs,
        "emittedAt": emitted,
    }


def _artifact_refs(run_path: Path) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for ref_id, kind, label, relative_path in ARTIFACT_REF_PATHS:
        path = run_path / relative_path
        if not path.is_file():
            continue
        refs.append({
            "id": ref_id,
            "kind": kind,
            "label": label,
            "path": relative_path,
            "url": None,
            "hash": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    return refs


def _insight_record(
    *,
    insight_id: str,
    specialization_id: str,
    summary: str,
    evidence_tier: str,
    artifact_refs: list[dict[str, Any]],
    emitted_at: str,
    confidence: float | None,
) -> dict[str, Any]:
    return {
        "id": insight_id,
        "specializationId": specialization_id,
        "summary": summary,
        "mechanism": "Creator run with benchmark, absorption, and Swarm packet evidence.",
        "boundary": NETWORK_BOUNDARY,
        "contradiction": None,
        "confidence": confidence,
        "evidenceLane": "benchmark_evidence",
        "sourceRefs": [ref["id"] for ref in artifact_refs],
        "status": _insight_status(evidence_tier),
        "createdAt": emitted_at,
        "updatedAt": emitted_at,
    }


def _mastery_record(
    *,
    mastery_id: str,
    insight_id: str,
    specialization_scope: str,
    summary: str,
    evidence: dict[str, Any],
    evidence_tier: str,
    emitted_at: str,
) -> dict[str, Any]:
    return {
        "id": mastery_id,
        "derivedFromInsightId": insight_id,
        "specializationScope": specialization_scope,
        "shareScope": "private",
        "status": _mastery_status(evidence_tier),
        "supportCount": len(evidence.get("report_paths") or []),
        "contradictionCount": 0,
        "benchmarkStrength": _score_or_none(evidence.get("candidate_score")),
        "liveStrength": None,
        "summary": summary,
        "createdAt": emitted_at,
        "updatedAt": emitted_at,
    }


def _outcome_record(
    *,
    outcome_id: str,
    target_id: str,
    summary: str,
    evidence: dict[str, Any],
    emitted_at: str,
) -> dict[str, Any]:
    delta = _score_or_none(evidence.get("mean_delta"))
    return {
        "id": outcome_id,
        "targetType": "mastery",
        "targetId": target_id,
        "evidenceLane": "benchmark_evidence",
        "verdict": _outcome_verdict(delta),
        "summary": summary,
        "metricName": "mean_delta",
        "metricValue": delta,
        "context": {
            "scorecard": {
                "headlineLabel": "Candidate score",
                "headlineValue": _score_or_none(evidence.get("candidate_score")),
                "headlineGoal": "higher",
                "modelLabel": "creator-system dry-run",
                "components": [
                    {
                        "key": "baseline_score",
                        "label": "Baseline score",
                        "value": _score_or_zero(evidence.get("baseline_score")),
                        "goal": "higher",
                    },
                    {
                        "key": "candidate_score",
                        "label": "Candidate score",
                        "value": _score_or_zero(evidence.get("candidate_score")),
                        "goal": "higher",
                    },
                ],
                "details": [
                    {
                        "key": "network_boundary",
                        "label": "Network boundary",
                        "value": NETWORK_BOUNDARY,
                    }
                ],
            }
        },
        "createdAt": emitted_at,
    }


def _intelligence_pulse(
    *,
    specialization_id: str,
    specialization_label: str,
    insight: dict[str, Any],
    mastery: dict[str, Any],
    artifact_refs: list[dict[str, Any]],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "specializationId": specialization_id,
        "specializationLabel": specialization_label,
        "activeEvolutionPathId": None,
        "activeEvolutionPathSummary": None,
        "benchmarkFocus": None,
        "newestInsightId": insight["id"],
        "newestInsightSummary": insight["summary"],
        "strongestMasteryId": mastery["id"],
        "strongestMasterySummary": mastery["summary"],
        "pendingContradictionCount": 0,
        "pendingUpgradeCount": 0,
        "recommendedAbsorbTargetId": None,
        "recommendedUpgradeId": None,
        "evidence": [
            {
                "lane": "benchmark_evidence",
                "support": _support_label(evidence),
                "summary": NETWORK_BOUNDARY,
                "artifactRefs": artifact_refs,
            }
        ],
    }


def _runtime_state(smoke: dict[str, Any]) -> str:
    if smoke.get("verdict") == "blocked" or _nested(smoke, "automation", "blocked"):
        return "blocked"
    return "idle"


def _first_blocker(smoke: dict[str, Any]) -> str | None:
    blockers = smoke.get("blocking_checks")
    if isinstance(blockers, list) and blockers:
        return str(blockers[0])
    return None


def _nested(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _score_or_none(value: Any) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    return None


def _score_or_zero(value: Any) -> float:
    return _score_or_none(value) or 0.0


def _slug(value: str) -> str:
    slug = value.strip().lower().replace("_", "-").replace(" ", "-")
    return "-".join(part for part in slug.split("-") if part) or "creator-system"


def _insight_status(evidence_tier: str) -> str:
    if evidence_tier == "transfer_supported":
        return "validation_supported"
    return "benchmark_supported"


def _mastery_status(evidence_tier: str) -> str:
    if evidence_tier == "transfer_supported":
        return "transfer_supported"
    return "validation_supported"


def _outcome_verdict(delta: float | None) -> str:
    if delta is None or delta == 0:
        return "flat"
    if delta > 0:
        return "improved"
    return "regressed"


def _support_label(evidence: dict[str, Any]) -> str:
    delta = _score_or_none(evidence.get("mean_delta"))
    if delta is not None and delta > 0:
        return "moderate"
    return "weak"
