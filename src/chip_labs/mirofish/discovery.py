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


@dataclass
class DiscoveryDecision:
    """Canonical classification outcome for a raw discovery candidate."""

    candidate: dict[str, Any]
    classification: str
    reasons: list[str]
    duplicate_of: str | None = None


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

    summary = {
        "raw_count": len(raw_candidates),
        "accepted_count": len(accepted),
        "merged_count": len(merged),
        "rejected_count": len(rejected),
        "clear_count": sum(1 for item in accepted if item["classification"] == "clear_domain_chip"),
        "proto_count": sum(1 for item in accepted if item["classification"] == "proto_domain_chip"),
    }

    return {
        "packet_kind": "mirofish_discovery_batch",
        "evidence_lane": "exploratory_frontier",
        "created_at": now,
        "batch_id": batch_id,
        "summary": summary,
        "accepted_candidates": accepted,
        "merged_candidates": merged,
        "rejected_candidates": rejected,
        "next_actions": _next_actions(accepted, rejected),
    }


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
