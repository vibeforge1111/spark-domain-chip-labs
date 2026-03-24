"""Discovery-first candidate intake for hybrid MiroFish runs.

This module keeps open-ended domain discovery separate from simulation scoring.
It turns raw observations about demand, specialization, and mastery into a
canonical candidate packet that can later feed MiroFish evaluation.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any


DISCOVERY_OUTPUT_CLASSES = {
    "clear_domain_chip",
    "proto_domain_chip",
    "workflow_not_domain",
    "persona_only_not_domain",
    "duplicate_of_existing",
    "too_vague_to_keep",
}

DEFAULT_DISCOVERY_PILOT_CLUSTERS = [
    {
        "cluster_id": "security-compliance-response",
        "label": "Security / Compliance Response",
        "agent_count": 16,
        "focus": "Recurring vendor reviews, questionnaires, control mapping, and compliance-response loops.",
        "seed_domains": [
            "vendor-security-review-copilot",
            "ai-security-questionnaire-copilot",
            "data-loss-prevention",
        ],
    },
    {
        "cluster_id": "healthcare-revenue-cycle",
        "label": "Healthcare Revenue Cycle",
        "agent_count": 14,
        "focus": "Appeals, denial management, reimbursement ops, and recurring healthcare admin loops.",
        "seed_domains": [
            "dental-insurance-appeals-ai",
            "chronic-disease-mgr",
            "continuing-ed-ai",
        ],
    },
    {
        "cluster_id": "hvac-field-maintenance",
        "label": "HVAC / Field Maintenance",
        "agent_count": 10,
        "focus": "Maintenance scheduling, dispatch, inspection, and recurring field-service optimization loops.",
        "seed_domains": [
            "hvac-maintenance-planner-ai",
            "hvac-optimizer-ai",
            "quality-inspection-ai",
        ],
    },
    {
        "cluster_id": "insurance-claims-appeals",
        "label": "Insurance / Claims / Appeals",
        "agent_count": 10,
        "focus": "Claim follow-up, dispute resolution, evidence packaging, and payout recovery loops.",
        "seed_domains": [
            "dental-insurance-appeals-ai",
            "appraisal-ai",
            "legal-ops",
        ],
    },
    {
        "cluster_id": "vendor-procurement-ops",
        "label": "Vendor / Procurement Ops",
        "agent_count": 10,
        "focus": "Recurring vendor onboarding, procurement evidence, and buyer-side workflow loops.",
        "seed_domains": [
            "vendor-security-review-copilot",
            "ai-rfp-response-copilot",
            "ai-compliance-evidence-copilot",
        ],
    },
    {
        "cluster_id": "legal-audit-evidence",
        "label": "Legal / Audit / Evidence",
        "agent_count": 10,
        "focus": "Document-heavy compliance, evidence compilation, audit readiness, and legal-ops loops.",
        "seed_domains": [
            "legal-ops",
            "ai-compliance-evidence-copilot",
            "patent-writer",
        ],
    },
    {
        "cluster_id": "workplace-training-compliance",
        "label": "Workplace Training / Compliance",
        "agent_count": 8,
        "focus": "Recurring workplace AI onboarding, reskilling, training compliance, and policy rollout loops.",
        "seed_domains": [
            "workplace-ai-trainer",
            "continuing-ed-ai",
            "safety-compliance-ai",
        ],
    },
    {
        "cluster_id": "industrial-quality-inspection",
        "label": "Industrial Quality / Inspection",
        "agent_count": 8,
        "focus": "Recurring inspections, defect logging, quality evidence, and plant-floor operations loops.",
        "seed_domains": [
            "quality-inspection-ai",
            "manufacturing-ai",
            "safety-compliance-ai",
        ],
    },
    {
        "cluster_id": "finance-reconciliation-backoffice",
        "label": "Finance / Reconciliation / Backoffice",
        "agent_count": 8,
        "focus": "Recurring reconciliation, exception review, renewal risk, and backoffice finance loops.",
        "seed_domains": [
            "ai-renewal-risk-briefing-copilot",
            "legal-ops",
            "carbon-credit-ai",
        ],
    },
    {
        "cluster_id": "logistics-last-mile-ops",
        "label": "Logistics / Last Mile Ops",
        "agent_count": 6,
        "focus": "Recurring route planning, delivery exception handling, and logistics coordination loops.",
        "seed_domains": [
            "last-mile-delivery-ai",
            "warehouse-optimizer",
            "inventory-tracker-ai",
        ],
    },
]


@dataclass
class DiscoveryDecision:
    """Canonical classification outcome for a raw discovery candidate."""

    candidate: dict[str, Any]
    classification: str
    reasons: list[str]
    duplicate_of: str | None = None


@dataclass
class CanonicalizationResult:
    """Shared accepted / merged / rejected outputs from discovery canonicalization."""

    accepted: list[dict[str, Any]]
    merged: list[dict[str, Any]]
    rejected: list[dict[str, Any]]


def slugify_domain_label(label: str) -> str:
    """Turn a free-form label into a stable domain ID."""
    text = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    text = re.sub(r"-{2,}", "-", text)
    return text or "unnamed-domain"


def canonicalize_raw_candidate(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize a raw discovery observation into the candidate contract."""
    candidate = deepcopy(raw)

    label = str(candidate.get("label", "")).strip()
    candidate["label"] = label
    candidate["domain_id"] = str(candidate.get("domain_id") or slugify_domain_label(label)).strip()
    candidate["description"] = str(candidate.get("description", "")).strip()
    candidate["specialization_surface"] = str(candidate.get("specialization_surface", "")).strip()
    candidate["mastery_surface"] = str(candidate.get("mastery_surface", "")).strip()
    candidate["user_value_loop"] = str(candidate.get("user_value_loop", "")).strip()
    candidate["evidence_summary"] = str(candidate.get("evidence_summary", "")).strip()
    candidate["confidence_read"] = str(candidate.get("confidence_read", "low")).strip() or "low"
    candidate["promotion_status"] = str(candidate.get("promotion_status", "candidate")).strip() or "candidate"

    for key in ("domain_tags", "evidence_sources", "adjacent_domains", "duplicate_aliases"):
        values = candidate.get(key, [])
        if not isinstance(values, list):
            values = [values]
        cleaned = []
        seen: set[str] = set()
        for value in values:
            text = str(value).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            cleaned.append(text)
        candidate[key] = cleaned

    candidate["raw_observation"] = str(candidate.get("raw_observation", "")).strip()
    return candidate


def classify_candidate(
    candidate: dict[str, Any],
    existing_domain_ids: set[str] | None = None,
    alias_map: dict[str, str] | None = None,
) -> DiscoveryDecision:
    """Classify a canonical candidate into one discovery output class."""
    existing = existing_domain_ids or set()
    alias_map = alias_map or {}
    reasons: list[str] = []

    domain_id = candidate["domain_id"]
    label = candidate["label"]
    description = candidate["description"]
    specialization = candidate["specialization_surface"]
    mastery = candidate["mastery_surface"]
    value_loop = candidate["user_value_loop"]
    evidence = candidate["evidence_summary"]
    raw_observation = candidate["raw_observation"]
    persona_text = " ".join([label, description, raw_observation]).lower()

    duplicate_of = alias_map.get(domain_id)
    if duplicate_of:
        reasons.append("Duplicate of another candidate in the same batch.")
        return DiscoveryDecision(candidate, "duplicate_of_existing", reasons, duplicate_of=duplicate_of)

    if domain_id in existing:
        reasons.append("Already exists in the current benchmark or known universe.")
        return DiscoveryDecision(candidate, "duplicate_of_existing", reasons, duplicate_of=domain_id)

    if len(label) < 4 or not description:
        reasons.append("Missing enough naming or description detail to define a domain.")
        return DiscoveryDecision(candidate, "too_vague_to_keep", reasons)

    if (
        ("persona" in persona_text or "audience" in persona_text or "people" in persona_text)
        and not specialization
        and not mastery
        and not value_loop
    ):
        reasons.append("Describes a persona or audience but not a repeated operating domain.")
        return DiscoveryDecision(candidate, "persona_only_not_domain", reasons)

    if not specialization and not mastery:
        reasons.append("Does not specify a specialization or mastery surface.")
        return DiscoveryDecision(candidate, "workflow_not_domain", reasons)

    if specialization and not mastery:
        reasons.append("Has specialization intent but not enough mastery definition yet.")
        return DiscoveryDecision(candidate, "proto_domain_chip", reasons)

    if mastery and not specialization:
        reasons.append("Has mastery intent but lacks a clear repeated specialization loop.")
        return DiscoveryDecision(candidate, "proto_domain_chip", reasons)

    if not value_loop:
        reasons.append("Missing the repeated user-value loop that would justify a chip.")
        return DiscoveryDecision(candidate, "workflow_not_domain", reasons)

    if not evidence:
        reasons.append("Clear chip shape, but evidence is still too thin.")
        return DiscoveryDecision(candidate, "proto_domain_chip", reasons)

    reasons.append("Has domain shape, specialization surface, mastery surface, and evidence summary.")
    return DiscoveryDecision(candidate, "clear_domain_chip", reasons)


def canonicalize_discovery_batch(batch: dict[str, Any]) -> dict[str, Any]:
    """Turn raw discovery observations into a canonical packet."""
    now = datetime.now(timezone.utc).isoformat()
    batch_id = str(batch.get("batch_id", "mirofish-discovery-batch")).strip() or "mirofish-discovery-batch"
    existing_domain_ids = {
        str(item).strip()
        for item in batch.get("existing_domain_ids", [])
        if str(item).strip()
    }
    raw_candidates = batch.get("raw_candidates", [])
    canonical_candidates = [canonicalize_raw_candidate(item) for item in raw_candidates]
    outputs = _canonicalize_candidates(canonical_candidates, existing_domain_ids=existing_domain_ids)
    summary = _build_summary(
        raw_count=len(raw_candidates),
        accepted=outputs.accepted,
        merged=outputs.merged,
        rejected=outputs.rejected,
    )

    return {
        "packet_kind": "mirofish_discovery_batch",
        "evidence_lane": "exploratory_frontier",
        "created_at": now,
        "batch_id": batch_id,
        "summary": summary,
        "accepted_candidates": outputs.accepted,
        "merged_candidates": outputs.merged,
        "rejected_candidates": outputs.rejected,
        "next_actions": _next_actions(outputs.accepted, outputs.rejected),
    }


def canonicalize_discovery_program(program: dict[str, Any]) -> dict[str, Any]:
    """Canonicalize a staged multi-agent discovery program into one packet."""
    now = datetime.now(timezone.utc).isoformat()
    program_id = str(program.get("program_id", "mirofish-discovery-program")).strip() or "mirofish-discovery-program"
    target_agent_count = int(program.get("target_agent_count", 0) or 0)
    stage_label = str(program.get("stage_label", "pilot")).strip() or "pilot"
    existing_domain_ids = {
        str(item).strip()
        for item in program.get("existing_domain_ids", [])
        if str(item).strip()
    }

    agent_submissions = list(program.get("agent_submissions", []))
    flattened_candidates: list[dict[str, Any]] = []
    agent_rollup: dict[str, dict[str, Any]] = {}
    for idx, submission in enumerate(agent_submissions, start=1):
        agent_id = str(submission.get("agent_id") or f"agent-{idx:04d}").strip() or f"agent-{idx:04d}"
        raw_candidates = list(submission.get("raw_candidates", []))
        agent_rollup[agent_id] = {
            "agent_id": agent_id,
            "candidate_count": len(raw_candidates),
            "notes": str(submission.get("notes", "")).strip(),
        }
        for candidate_index, raw_candidate in enumerate(raw_candidates, start=1):
            enriched = deepcopy(raw_candidate)
            enriched["submitted_by_agent"] = agent_id
            enriched["submission_index"] = candidate_index
            flattened_candidates.append(enriched)

    canonical_candidates = [canonicalize_raw_candidate(item) for item in flattened_candidates]
    outputs = _canonicalize_candidates(canonical_candidates, existing_domain_ids=existing_domain_ids)
    _attach_supporting_agents(outputs.accepted, canonical_candidates)
    _attach_agent_rollup(agent_rollup, outputs.accepted, outputs.merged, outputs.rejected)
    summary = _build_summary(
        raw_count=len(flattened_candidates),
        accepted=outputs.accepted,
        merged=outputs.merged,
        rejected=outputs.rejected,
    )
    participating_agent_count = len(agent_submissions)
    scale_readiness = _scale_readiness(
        summary=summary,
        participating_agent_count=participating_agent_count,
        target_agent_count=target_agent_count,
    )

    return {
        "packet_kind": "mirofish_discovery_program",
        "evidence_lane": "exploratory_frontier",
        "created_at": now,
        "program_id": program_id,
        "stage_label": stage_label,
        "target_agent_count": target_agent_count,
        "participating_agent_count": participating_agent_count,
        "summary": summary,
        "scale_readiness": scale_readiness,
        "agent_rollup": list(agent_rollup.values()),
        "accepted_candidates": outputs.accepted,
        "merged_candidates": outputs.merged,
        "rejected_candidates": outputs.rejected,
        "next_actions": _program_next_actions(
            accepted_candidates=outputs.accepted,
            rejected_candidates=outputs.rejected,
            scale_readiness=scale_readiness,
        ),
    }


def build_discovery_program_scaffold(
    program_id: str = "mirofish-discovery-program-pilot-100",
    target_agent_count: int = 100,
    stage_label: str = "pilot_100",
) -> dict[str, Any]:
    """Build a structured multi-agent discovery pilot scaffold."""
    now = datetime.now(timezone.utc).isoformat()
    cluster_plan = deepcopy(DEFAULT_DISCOVERY_PILOT_CLUSTERS)
    assigned_total = sum(int(cluster.get("agent_count", 0)) for cluster in cluster_plan)
    if target_agent_count != assigned_total:
        raise ValueError(
            f"Pilot scaffold target_agent_count={target_agent_count} does not match cluster plan total={assigned_total}."
        )

    agent_submissions: list[dict[str, Any]] = []
    next_agent_number = 1
    for cluster in cluster_plan:
        cluster_id = cluster["cluster_id"]
        cluster_label = cluster["label"]
        focus = cluster["focus"]
        seed_domains = list(cluster.get("seed_domains", []))
        for within_cluster_index in range(1, int(cluster["agent_count"]) + 1):
            agent_submissions.append({
                "agent_id": f"agent-{next_agent_number:03d}",
                "cluster_id": cluster_id,
                "notes": (
                    f"Pilot agent {within_cluster_index} for {cluster_label}. "
                    f"Focus on repeated domain loops, not generic tooling."
                ),
                "agent_brief": {
                    "cluster_label": cluster_label,
                    "focus": focus,
                    "seed_domains": seed_domains,
                    "candidate_requirements": [
                        "Return 1-3 candidate domain chips only",
                        "Every candidate must describe a repeated specialization loop",
                        "Every candidate must describe a repeated mastery loop",
                        "Reject personas, generic features, and vague workflow ideas",
                    ],
                },
                "raw_candidates": [],
            })
            next_agent_number += 1

    return {
        "packet_kind": "mirofish_discovery_program_scaffold",
        "created_at": now,
        "program_id": program_id,
        "stage_label": stage_label,
        "target_agent_count": target_agent_count,
        "cluster_plan": cluster_plan,
        "collection_rules": {
            "max_candidates_per_agent": 3,
            "min_candidates_per_agent": 1,
            "required_candidate_fields": [
                "label",
                "description",
                "specialization_surface",
                "mastery_surface",
                "user_value_loop",
                "evidence_summary",
                "adjacent_domains",
                "raw_observation",
            ],
            "scale_gate_for_250": {
                "min_acceptance_rate": 0.3,
                "max_merge_rate": 0.4,
                "max_too_vague_rate": 0.3,
                "min_clear_count": 5,
                "needs_hybrid_ready_cluster": True,
            },
        },
        "agent_submissions": agent_submissions,
        "next_actions": [
            "Fill each agent submission with 1-3 concrete candidates from the assigned cluster.",
            "Run the filled packet through `mirofish-discovery-program`.",
            "Promote only the accepted candidate set into focused hybrid evaluation.",
        ],
    }


def split_discovery_program_scaffold(scaffold: dict[str, Any]) -> dict[str, Any]:
    """Split a scaffold into operator-facing per-cluster collection packets."""
    if scaffold.get("packet_kind") != "mirofish_discovery_program_scaffold":
        raise ValueError("Expected a `mirofish_discovery_program_scaffold` packet.")

    now = datetime.now(timezone.utc).isoformat()
    cluster_plan = list(scaffold.get("cluster_plan", []))
    collection_rules = deepcopy(scaffold.get("collection_rules", {}))
    agent_submissions = list(scaffold.get("agent_submissions", []))
    agents_by_cluster: dict[str, list[dict[str, Any]]] = {}
    for submission in agent_submissions:
        agents_by_cluster.setdefault(str(submission.get("cluster_id", "unassigned")), []).append(deepcopy(submission))

    cluster_packets: list[dict[str, Any]] = []
    for cluster in cluster_plan:
        cluster_id = cluster["cluster_id"]
        cluster_agents = agents_by_cluster.get(cluster_id, [])
        cluster_packets.append({
            "packet_kind": "mirofish_discovery_cluster_packet",
            "created_at": now,
            "program_id": scaffold.get("program_id", "mirofish-discovery-program"),
            "stage_label": scaffold.get("stage_label", "pilot"),
            "cluster_id": cluster_id,
            "cluster_label": cluster["label"],
            "focus": cluster["focus"],
            "seed_domains": list(cluster.get("seed_domains", [])),
            "target_agent_count": int(cluster.get("agent_count", 0)),
            "collection_rules": deepcopy(collection_rules),
            "agent_submissions": cluster_agents,
            "next_actions": [
                "Collect 1-3 concrete candidates from each assigned agent.",
                "Reject vague workflows, personas, and generic tooling before canonicalization.",
                "Merge the completed cluster packets back into one filled discovery-program packet.",
            ],
        })

    return {
        "packet_kind": "mirofish_discovery_program_cluster_packets",
        "created_at": now,
        "program_id": scaffold.get("program_id", "mirofish-discovery-program"),
        "stage_label": scaffold.get("stage_label", "pilot"),
        "target_agent_count": int(scaffold.get("target_agent_count", 0)),
        "cluster_plan": deepcopy(cluster_plan),
        "collection_rules": collection_rules,
        "cluster_packet_count": len(cluster_packets),
        "summary": {
            "cluster_count": len(cluster_packets),
            "agent_count": len(agent_submissions),
        },
        "cluster_packets": cluster_packets,
        "next_actions": [
            "Assign each cluster packet to a collection owner or agent swarm tranche.",
            "Fill the per-cluster packets with real discoveries.",
            "Recombine the filled packets into one discovery-program packet before canonicalization.",
        ],
    }


def merge_discovery_cluster_packets(cluster_bundle: dict[str, Any]) -> dict[str, Any]:
    """Recombine filled cluster packets into one discovery-program input packet."""
    if cluster_bundle.get("packet_kind") != "mirofish_discovery_program_cluster_packets":
        raise ValueError("Expected a `mirofish_discovery_program_cluster_packets` packet.")

    now = datetime.now(timezone.utc).isoformat()
    cluster_packets = list(cluster_bundle.get("cluster_packets", []))
    agent_submissions: list[dict[str, Any]] = []
    for cluster_packet in cluster_packets:
        for submission in cluster_packet.get("agent_submissions", []):
            agent_submissions.append(deepcopy(submission))
    agent_submissions.sort(key=lambda item: str(item.get("agent_id", "")))

    return {
        "packet_kind": "mirofish_discovery_program_input",
        "created_at": now,
        "program_id": cluster_bundle.get("program_id", "mirofish-discovery-program"),
        "stage_label": cluster_bundle.get("stage_label", "pilot"),
        "target_agent_count": int(cluster_bundle.get("target_agent_count", len(agent_submissions))),
        "cluster_plan": deepcopy(cluster_bundle.get("cluster_plan", [])),
        "collection_rules": deepcopy(cluster_bundle.get("collection_rules", {})),
        "agent_submissions": agent_submissions,
        "next_actions": [
            "Run this merged packet through `mirofish-discovery-program` for canonicalization.",
            "Inspect acceptance, merge, and vague-reject rates before scaling.",
            "Promote only the accepted subset into focused hybrid evaluation.",
        ],
    }


def format_discovery_program_markdown(
    packet: dict[str, Any],
    title: str | None = None,
) -> str:
    """Render a scaffold, cluster split, or canonicalized program as operator-facing markdown."""
    packet_kind = packet.get("packet_kind", "")
    heading = title or "MiroFish Discovery Program"
    lines = [f"# {heading}", ""]

    if packet_kind == "mirofish_discovery_program_scaffold":
        lines.extend(_format_discovery_scaffold_markdown(packet))
    elif packet_kind == "mirofish_discovery_program_input":
        lines.extend(_format_discovery_program_input_markdown(packet))
    elif packet_kind == "mirofish_discovery_program_cluster_packets":
        lines.extend(_format_discovery_cluster_packets_markdown(packet))
    elif packet_kind == "mirofish_discovery_program":
        lines.extend(_format_discovery_result_markdown(packet))
    else:
        raise ValueError(f"Unsupported discovery packet_kind for markdown export: {packet_kind}")

    return "\n".join(lines).rstrip() + "\n"


def _format_discovery_scaffold_markdown(scaffold: dict[str, Any]) -> list[str]:
    cluster_plan = list(scaffold.get("cluster_plan", []))
    lines = [
        f"- Program ID: `{scaffold.get('program_id', 'unknown')}`",
        f"- Stage: `{scaffold.get('stage_label', 'unknown')}`",
        f"- Target Agents: `{scaffold.get('target_agent_count', 0)}`",
        f"- Clusters: `{len(cluster_plan)}`",
        "",
        "## Cluster Allocation",
        "",
    ]
    for cluster in cluster_plan:
        lines.append(
            f"- `{cluster['cluster_id']}`: {cluster['label']} "
            f"({int(cluster.get('agent_count', 0))} agents)"
        )
        lines.append(f"  Focus: {cluster['focus']}")
        seed_domains = ", ".join(f"`{domain_id}`" for domain_id in cluster.get("seed_domains", []))
        if seed_domains:
            lines.append(f"  Seed domains: {seed_domains}")
    collection_rules = scaffold.get("collection_rules", {})
    lines.extend([
        "",
        "## Collection Rules",
        "",
        f"- Candidates per agent: `{collection_rules.get('min_candidates_per_agent', 1)}-{collection_rules.get('max_candidates_per_agent', 3)}`",
        f"- Required fields: {', '.join(f'`{field}`' for field in collection_rules.get('required_candidate_fields', []))}",
        "",
        "## Next Actions",
        "",
    ])
    for action in scaffold.get("next_actions", []):
        lines.append(f"- {action}")
    return lines


def _format_discovery_cluster_packets_markdown(cluster_bundle: dict[str, Any]) -> list[str]:
    cluster_packets = list(cluster_bundle.get("cluster_packets", []))
    lines = [
        f"- Program ID: `{cluster_bundle.get('program_id', 'unknown')}`",
        f"- Stage: `{cluster_bundle.get('stage_label', 'unknown')}`",
        f"- Cluster packets: `{len(cluster_packets)}`",
        f"- Total agents: `{cluster_bundle.get('summary', {}).get('agent_count', 0)}`",
        "",
        "## Cluster Packets",
        "",
    ]
    for packet in cluster_packets:
        lines.append(
            f"- `{packet['cluster_id']}`: {packet['cluster_label']} "
            f"({int(packet.get('target_agent_count', 0))} agents)"
        )
        lines.append(f"  Focus: {packet['focus']}")
        seed_domains = ", ".join(f"`{domain_id}`" for domain_id in packet.get("seed_domains", []))
        if seed_domains:
            lines.append(f"  Seed domains: {seed_domains}")
    lines.extend([
        "",
        "## Next Actions",
        "",
    ])
    for action in cluster_bundle.get("next_actions", []):
        lines.append(f"- {action}")
    return lines


def _format_discovery_result_markdown(result: dict[str, Any]) -> list[str]:
    summary = result.get("summary", {})
    scale_readiness = result.get("scale_readiness", {})
    accepted_candidates = list(result.get("accepted_candidates", []))
    lines = [
        f"- Program ID: `{result.get('program_id', 'unknown')}`",
        f"- Stage: `{result.get('stage_label', 'unknown')}`",
        f"- Participating Agents: `{result.get('participating_agent_count', 0)}` / `{result.get('target_agent_count', 0)}`",
        f"- Accepted: `{summary.get('accepted_count', 0)}`",
        f"- Merged: `{summary.get('merged_count', 0)}`",
        f"- Rejected: `{summary.get('rejected_count', 0)}`",
        f"- Recommended next stage: `{scale_readiness.get('next_stage', 'unknown')}`",
        "",
        "## Accepted Candidates",
        "",
    ]
    if not accepted_candidates:
        lines.append("- No accepted candidates yet.")
    else:
        for candidate in accepted_candidates[:15]:
            lines.append(
                f"- `{candidate['domain_id']}`: {candidate.get('label', candidate['domain_id'])} "
                f"({candidate.get('classification', 'accepted')})"
            )
    lines.extend([
        "",
        "## Next Actions",
        "",
    ])
    for action in result.get("next_actions", []):
        lines.append(f"- {action}")
    return lines


def _format_discovery_program_input_markdown(program_input: dict[str, Any]) -> list[str]:
    agent_submissions = list(program_input.get("agent_submissions", []))
    filled_agent_count = sum(1 for submission in agent_submissions if submission.get("raw_candidates"))
    raw_candidate_count = sum(len(submission.get("raw_candidates", [])) for submission in agent_submissions)
    lines = [
        f"- Program ID: `{program_input.get('program_id', 'unknown')}`",
        f"- Stage: `{program_input.get('stage_label', 'unknown')}`",
        f"- Agent submissions: `{len(agent_submissions)}` / `{program_input.get('target_agent_count', 0)}`",
        f"- Filled agents: `{filled_agent_count}`",
        f"- Raw candidates: `{raw_candidate_count}`",
        "",
        "## Next Actions",
        "",
    ]
    for action in program_input.get("next_actions", []):
        lines.append(f"- {action}")
    return lines


def _build_alias_map(canonical_candidates: list[dict[str, Any]]) -> dict[str, str]:
    """Build an alias map for duplicates inside one intake set."""
    alias_map: dict[str, str] = {}
    seen_domain_ids: set[str] = set()
    label_map: dict[str, str] = {}
    for candidate in canonical_candidates:
        domain_id = candidate["domain_id"]
        label_slug = slugify_domain_label(candidate.get("label", ""))
        if domain_id in seen_domain_ids and domain_id not in alias_map:
            alias_map[domain_id] = domain_id
        for alias in candidate.get("duplicate_aliases", []):
            alias_slug = slugify_domain_label(alias)
            if alias_slug in label_map:
                alias_map[domain_id] = label_map[alias_slug]
                break
        seen_domain_ids.add(domain_id)
        if label_slug not in label_map:
            label_map[label_slug] = domain_id
    return alias_map


def _canonicalize_candidates(
    canonical_candidates: list[dict[str, Any]],
    existing_domain_ids: set[str],
) -> CanonicalizationResult:
    """Canonicalize already-normalized candidates into accepted / merged / rejected outputs."""
    alias_map = _build_alias_map(canonical_candidates)
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    merged: list[dict[str, Any]] = []

    accepted_by_id: dict[str, dict[str, Any]] = {}
    for candidate in canonical_candidates:
        decision = classify_candidate(candidate, existing_domain_ids=existing_domain_ids, alias_map=alias_map)
        output = {
            **candidate,
            "classification": decision.classification,
            "classification_reasons": decision.reasons,
        }

        if decision.classification == "duplicate_of_existing":
            output["duplicate_of"] = decision.duplicate_of
            merged.append(output)
            continue

        if decision.classification in {"clear_domain_chip", "proto_domain_chip"}:
            if candidate["domain_id"] in accepted_by_id:
                output["duplicate_of"] = candidate["domain_id"]
                output["classification"] = "duplicate_of_existing"
                output["classification_reasons"] = ["Merged into the first accepted canonical candidate."]
                merged.append(output)
                continue
            accepted_by_id[candidate["domain_id"]] = output
            accepted.append(output)
            continue

        rejected.append(output)

    return CanonicalizationResult(
        accepted=accepted,
        merged=merged,
        rejected=rejected,
    )


def _build_summary(
    raw_count: int,
    accepted: list[dict[str, Any]],
    merged: list[dict[str, Any]],
    rejected: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build discovery summary metrics used by both batch and program packets."""
    too_vague_count = sum(1 for item in rejected if item["classification"] == "too_vague_to_keep")
    persona_only_count = sum(1 for item in rejected if item["classification"] == "persona_only_not_domain")
    workflow_only_count = sum(1 for item in rejected if item["classification"] == "workflow_not_domain")
    duplicate_existing_count = sum(
        1 for item in merged
        if item.get("duplicate_of") == item.get("domain_id") or item.get("duplicate_of") in item.get("domain_tags", [])
    )
    accepted_count = len(accepted)
    merged_count = len(merged)
    rejected_count = len(rejected)
    denominator = raw_count or 1
    return {
        "raw_count": raw_count,
        "accepted_count": accepted_count,
        "merged_count": merged_count,
        "rejected_count": rejected_count,
        "clear_count": sum(1 for item in accepted if item["classification"] == "clear_domain_chip"),
        "proto_count": sum(1 for item in accepted if item["classification"] == "proto_domain_chip"),
        "acceptance_rate": round(accepted_count / denominator, 4),
        "merge_rate": round(merged_count / denominator, 4),
        "too_vague_rate": round(too_vague_count / denominator, 4),
        "persona_only_rate": round(persona_only_count / denominator, 4),
        "workflow_only_rate": round(workflow_only_count / denominator, 4),
        "duplicate_existing_count": duplicate_existing_count,
    }


def _attach_supporting_agents(
    accepted_candidates: list[dict[str, Any]],
    canonical_candidates: list[dict[str, Any]],
) -> None:
    """Attach supporting-agent provenance to accepted candidates."""
    support_map: dict[str, set[str]] = {}
    for candidate in canonical_candidates:
        agent_id = str(candidate.get("submitted_by_agent", "")).strip()
        if not agent_id:
            continue
        support_map.setdefault(candidate["domain_id"], set()).add(agent_id)

    for candidate in accepted_candidates:
        supporting_agents = sorted(support_map.get(candidate["domain_id"], set()))
        candidate["supporting_agent_ids"] = supporting_agents
        candidate["supporting_agent_count"] = len(supporting_agents)


def _attach_agent_rollup(
    agent_rollup: dict[str, dict[str, Any]],
    accepted_candidates: list[dict[str, Any]],
    merged_candidates: list[dict[str, Any]],
    rejected_candidates: list[dict[str, Any]],
) -> None:
    """Attach accepted / merged / rejected counts back to each agent rollup row."""
    for row in accepted_candidates:
        agent_id = str(row.get("submitted_by_agent", "")).strip()
        if agent_id in agent_rollup:
            agent_rollup[agent_id]["accepted_count"] = agent_rollup[agent_id].get("accepted_count", 0) + 1
    for row in merged_candidates:
        agent_id = str(row.get("submitted_by_agent", "")).strip()
        if agent_id in agent_rollup:
            agent_rollup[agent_id]["merged_count"] = agent_rollup[agent_id].get("merged_count", 0) + 1
    for row in rejected_candidates:
        agent_id = str(row.get("submitted_by_agent", "")).strip()
        if agent_id in agent_rollup:
            agent_rollup[agent_id]["rejected_count"] = agent_rollup[agent_id].get("rejected_count", 0) + 1

    for row in agent_rollup.values():
        row.setdefault("accepted_count", 0)
        row.setdefault("merged_count", 0)
        row.setdefault("rejected_count", 0)


def _scale_readiness(
    summary: dict[str, Any],
    participating_agent_count: int,
    target_agent_count: int,
) -> dict[str, Any]:
    """Recommend whether the discovery program is ready to scale."""
    acceptance_rate = float(summary.get("acceptance_rate", 0.0))
    merge_rate = float(summary.get("merge_rate", 0.0))
    too_vague_rate = float(summary.get("too_vague_rate", 0.0))
    clear_count = int(summary.get("clear_count", 0))

    reasons: list[str] = []
    if clear_count >= 3:
        reasons.append("The program already produces multiple clear_domain_chip candidates.")
    else:
        reasons.append("The program still produces too few clear_domain_chip candidates.")

    if acceptance_rate >= 0.3:
        reasons.append("Acceptance rate is high enough to justify a larger intake pass.")
    else:
        reasons.append("Acceptance rate is still too weak for immediate scale-up.")

    if merge_rate <= 0.35:
        reasons.append("Duplicate pressure is still manageable.")
    else:
        reasons.append("Duplicate pressure is already high and should be reduced before scaling.")

    if too_vague_rate <= 0.25:
        reasons.append("Vague-candidate rejection is under control.")
    else:
        reasons.append("Too much of the intake is still vague.")

    next_stage = "refine_contract_before_scaling"
    if (
        participating_agent_count < 20
        and clear_count >= 2
        and acceptance_rate >= 0.25
        and merge_rate <= 0.5
        and too_vague_rate <= 0.35
    ):
        next_stage = "run_100_agent_pilot"
    elif (
        participating_agent_count < 500
        and clear_count >= 5
        and acceptance_rate >= 0.3
        and merge_rate <= 0.4
        and too_vague_rate <= 0.3
    ):
        next_stage = "run_250_agent_pilot"
    elif (
        participating_agent_count >= 250
        and clear_count >= 12
        and acceptance_rate >= 0.28
        and merge_rate <= 0.45
        and too_vague_rate <= 0.3
    ):
        next_stage = "run_1000_agent_program"

    return {
        "participating_agent_count": participating_agent_count,
        "target_agent_count": target_agent_count,
        "next_stage": next_stage,
        "reasons": reasons,
    }


def _program_next_actions(
    accepted_candidates: list[dict[str, Any]],
    rejected_candidates: list[dict[str, Any]],
    scale_readiness: dict[str, Any],
) -> list[str]:
    """Suggest immediate next steps for a multi-agent discovery program."""
    actions = _next_actions(accepted_candidates, rejected_candidates)
    next_stage = scale_readiness.get("next_stage", "refine_contract_before_scaling")
    if next_stage == "run_100_agent_pilot":
        actions.append("Promote this smoke pass into a 100-agent pilot using the same candidate contract and review metrics.")
    elif next_stage == "run_250_agent_pilot":
        actions.append("The current pilot is strong enough to justify a 250-agent scale pass.")
    elif next_stage == "run_1000_agent_program":
        actions.append("The discovery program is ready for the full 1,000-agent intake if the operator still wants the larger sweep.")
    else:
        actions.append("Refine the intake contract and rejection reasons before scaling to a larger agent count.")
    return actions


def _next_actions(
    accepted_candidates: list[dict[str, Any]],
    rejected_candidates: list[dict[str, Any]],
) -> list[str]:
    """Suggest immediate next steps for the packet operator."""
    actions: list[str] = []
    clear_count = sum(1 for item in accepted_candidates if item["classification"] == "clear_domain_chip")
    proto_count = sum(1 for item in accepted_candidates if item["classification"] == "proto_domain_chip")

    if clear_count:
        actions.append("Feed the clear_domain_chip set into a smaller MiroFish evaluation run.")
    if proto_count:
        actions.append("Strengthen evidence summaries for proto_domain_chip candidates before evaluation.")
    if rejected_candidates:
        actions.append("Review rejected candidates to ensure duplicates and vague ideas were not misclassified.")
    if not actions:
        actions.append("Gather another discovery batch with more concrete specialization and mastery observations.")
    return actions
