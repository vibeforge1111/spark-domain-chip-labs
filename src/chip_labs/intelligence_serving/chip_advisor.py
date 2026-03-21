"""Pre-action / post-action advisory middleware for domain chip intelligence.

Evaluates agent plans against chip doctrines, surfaces contradictions, and
writes feedback from real-world outcomes back into chip evidence lanes.

Zero external dependencies (stdlib + chip_labs siblings only).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..chip_runtime import ChipHandle

from .intelligence_server import (
    ChipIntelligence,
    _score_relevance,
    extract_intelligence,
)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

_CONFIDENCE_PRIORITY = {"very high": 0, "high": 1, "medium": 2, "low": 3}

# Evidence lane weights for computing effective confidence
_LANE_WEIGHTS = {
    "realworld_validated": 1.0,
    "benchmark_grounded": 0.8,
    "research_grounded": 0.6,
    "exploratory_frontier": 0.3,
}


@dataclass
class AdvisoryRequest:
    """Input for advisory operations."""

    action_description: str
    domain_hint: str | None = None
    action_type: str = "general"  # tool_call, code_generation, decision, general


@dataclass
class DoctrineGuidance:
    """A single piece of doctrine-based guidance for an action."""

    claim: str
    confidence: str
    evidence_lane: str = ""
    relevance: float = 0.0
    guidance_type: str = "informs"  # supports, warns, contradicts, uncertain, informs
    source_chip: str = ""


@dataclass
class AdvisoryResponse:
    """Full advisory output for a requested action."""

    verdict: str = "proceed"  # proceed, caution, reconsider
    guidance: list[DoctrineGuidance] = field(default_factory=list)
    contradictions: list[dict[str, Any]] = field(default_factory=list)
    uncertainty_areas: list[str] = field(default_factory=list)
    trajectory_context: str = ""
    chips_consulted: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core advisory logic
# ---------------------------------------------------------------------------


def _select_chips(
    query: str,
    portfolio: list["ChipHandle"],
    max_chips: int = 3,
) -> list["ChipHandle"]:
    """Select chips most relevant to *query* using Jaccard similarity."""
    if not portfolio:
        return []
    if not query.strip():
        return portfolio[:max_chips]

    scored: list[tuple[float, "ChipHandle"]] = []
    for chip in portfolio:
        intel = _get_intel(chip)
        if not intel:
            continue
        chip_text = f"{chip.domain} {chip.chip_name} {intel.mission}"
        for doc in intel.doctrines[:5]:
            chip_text += " " + doc.get("claim", "")
        relevance = _score_relevance(query, chip_text)
        scored.append((relevance, chip))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chip for _, chip in scored[:max_chips]]


def _get_intel(chip: "ChipHandle") -> ChipIntelligence | None:
    """Get intelligence from a chip, using the property or extracting."""
    try:
        intel = chip.intelligence
        if intel is not None:
            return intel
    except Exception:
        pass
    try:
        return extract_intelligence(chip.chip_path)
    except Exception:
        return None


def _compute_effective_confidence(doc: dict[str, Any]) -> float:
    """Weight doctrine confidence by its evidence lane."""
    conf = str(doc.get("confidence", "low")).lower()
    base = 1.0 - _CONFIDENCE_PRIORITY.get(conf, 3) * 0.25  # 1.0, 0.75, 0.5, 0.25
    lane = str(doc.get("evidence_lane", "")).lower()
    lane_w = _LANE_WEIGHTS.get(lane, 0.5)
    return base * lane_w


def _classify_guidance(action: str, claim: str) -> str:
    """Classify how a doctrine relates to an action."""
    action_lower = action.lower()
    claim_lower = claim.lower()

    # Simple heuristic: keyword overlap hints at relevance
    action_words = set(action_lower.split())
    claim_words = set(claim_lower.split())
    overlap = len(action_words & claim_words)

    # Look for warning-ish keywords in the claim
    warn_words = {"avoid", "never", "don't", "risk", "danger", "critical", "careful", "warning"}
    if warn_words & claim_words:
        return "warns"

    if overlap >= 2:
        return "supports"
    return "informs"


def _build_trajectory_context(chips: list["ChipHandle"]) -> str:
    """Summarize score trajectories for consulted chips."""
    parts: list[str] = []
    for chip in chips:
        intel = _get_intel(chip)
        if not intel or not intel.score_trajectory:
            continue
        traj = intel.score_trajectory
        if len(traj) >= 2:
            delta = traj[-1] - traj[0]
            direction = "improving" if delta > 0 else ("stagnant" if delta == 0 else "declining")
            parts.append(f"{chip.chip_name}: {direction} ({traj[0]}→{traj[-1]})")
    return "; ".join(parts) if parts else "No trajectory data available"


def _identify_uncertainty(chips: list["ChipHandle"]) -> list[str]:
    """Find areas where chips lack evidence."""
    areas: list[str] = []
    for chip in chips:
        intel = _get_intel(chip)
        if not intel:
            continue
        evidence = intel.evidence_summary
        empty_lanes = [
            lane for lane in ("realworld_validated", "benchmark_grounded")
            if evidence.get(lane, 0) == 0
        ]
        if empty_lanes:
            areas.append(f"{chip.chip_name}: no evidence in {', '.join(empty_lanes)}")
    return areas


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def advise_pre_action(
    request: AdvisoryRequest,
    portfolio: list["ChipHandle"] | None = None,
) -> AdvisoryResponse:
    """Get pre-action advisory from domain chips.

    Selects relevant chips, evaluates doctrines against the planned action,
    and returns guidance with confidence and contradiction awareness.
    """
    if portfolio is None:
        try:
            from ..chip_runtime import load_portfolio
            portfolio = load_portfolio(min_score=35)
        except (ImportError, Exception):
            return AdvisoryResponse(verdict="proceed")

    if not portfolio:
        return AdvisoryResponse(verdict="proceed")

    # Select relevant chips
    query = request.action_description
    if request.domain_hint:
        query = f"{request.domain_hint} {query}"

    selected = _select_chips(query, portfolio, max_chips=3)
    if not selected:
        return AdvisoryResponse(verdict="proceed")

    guidance: list[DoctrineGuidance] = []
    all_contradictions: list[dict[str, Any]] = []

    for chip in selected:
        intel = _get_intel(chip)
        if not intel:
            continue

        for doc in intel.doctrines:
            claim = doc.get("claim", "")
            if not claim:
                continue

            relevance = _score_relevance(request.action_description, claim)
            gtype = _classify_guidance(request.action_description, claim)

            guidance.append(DoctrineGuidance(
                claim=claim,
                confidence=doc.get("confidence", "low"),
                evidence_lane=doc.get("evidence_lane", ""),
                relevance=relevance,
                guidance_type=gtype,
                source_chip=chip.chip_name,
            ))

        for c in intel.contradictions:
            tagged = dict(c)
            tagged["source_chip"] = chip.chip_name
            all_contradictions.append(tagged)

    # Sort by relevance then confidence
    guidance.sort(key=lambda g: (
        g.relevance,
        1.0 - _CONFIDENCE_PRIORITY.get(g.confidence, 3) * 0.25,
    ), reverse=True)

    # Determine verdict
    has_warnings = any(g.guidance_type == "warns" for g in guidance[:5])
    has_contradictions = len(all_contradictions) > 0
    if has_warnings and has_contradictions:
        verdict = "reconsider"
    elif has_warnings or has_contradictions:
        verdict = "caution"
    else:
        verdict = "proceed"

    return AdvisoryResponse(
        verdict=verdict,
        guidance=guidance[:10],
        contradictions=all_contradictions[:5],
        uncertainty_areas=_identify_uncertainty(selected),
        trajectory_context=_build_trajectory_context(selected),
        chips_consulted=[c.chip_name for c in selected],
    )


def advise_post_action(
    request: AdvisoryRequest,
    outcome: dict[str, Any],
    portfolio: list["ChipHandle"] | None = None,
) -> dict[str, Any]:
    """Record action outcome as feedback for chip learning.

    Writes a feedback packet to the most relevant chip's
    research/realworld_validated/ directory.
    """
    if portfolio is None:
        try:
            from ..chip_runtime import load_portfolio
            portfolio = load_portfolio(min_score=35)
        except (ImportError, Exception):
            return {"feedback_written": False, "reason": "no portfolio"}

    if not portfolio:
        return {"feedback_written": False, "reason": "empty portfolio"}

    selected = _select_chips(request.action_description, portfolio, max_chips=1)
    if not selected:
        return {"feedback_written": False, "reason": "no relevant chips"}

    chip = selected[0]
    rw_dir = chip.chip_path / "research" / "realworld_validated"
    try:
        rw_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return {"feedback_written": False, "reason": "cannot create directory"}

    timestamp = datetime.now(timezone.utc)
    packet = {
        "packet_kind": "realworld_feedback",
        "evidence_lane": "realworld_validated",
        "action": request.action_description,
        "action_type": request.action_type,
        "outcome": outcome,
        "timestamp": timestamp.isoformat(),
        "source": "chip_advisor_post_action",
    }

    filename = f"feedback_{timestamp.strftime('%Y%m%dT%H%M%SZ')}.json"
    filepath = rw_dir / filename
    try:
        filepath.write_text(json.dumps(packet, indent=2, default=str), encoding="utf-8")
    except OSError:
        return {"feedback_written": False, "reason": "write failed"}

    return {
        "feedback_written": True,
        "chip_name": chip.chip_name,
        "feedback_path": str(filepath),
    }


def doctrine_check(
    claim: str,
    portfolio: list["ChipHandle"] | None = None,
    domain: str | None = None,
) -> list[DoctrineGuidance]:
    """Check a claim against all chip doctrines.

    Returns matching doctrines sorted by relevance.
    """
    if portfolio is None:
        try:
            from ..chip_runtime import load_portfolio
            portfolio = load_portfolio(min_score=35)
        except (ImportError, Exception):
            return []

    if not portfolio:
        return []

    if domain:
        portfolio = [c for c in portfolio if domain.lower() in c.domain.lower()]

    results: list[DoctrineGuidance] = []
    for chip in portfolio:
        intel = _get_intel(chip)
        if not intel:
            continue

        for doc in intel.doctrines:
            doc_claim = doc.get("claim", "")
            if not doc_claim:
                continue

            relevance = _score_relevance(claim, doc_claim)
            if relevance > 0.05:  # minimum relevance threshold
                results.append(DoctrineGuidance(
                    claim=doc_claim,
                    confidence=doc.get("confidence", "low"),
                    evidence_lane=doc.get("evidence_lane", ""),
                    relevance=relevance,
                    guidance_type="informs",
                    source_chip=chip.chip_name,
                ))

    results.sort(key=lambda g: g.relevance, reverse=True)
    return results
