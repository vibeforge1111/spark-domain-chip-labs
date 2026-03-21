"""Context injection for LLM prompts from domain chip intelligence.

Builds formatted context blocks that inject chip doctrines, contradictions,
and guardrails into LLM system prompts or conversation context.  Three
styles: concise, detailed, guardrails_only.

Zero external dependencies (stdlib + chip_labs siblings only).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
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
# Token estimation
# ---------------------------------------------------------------------------

def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for English text."""
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Chip selection
# ---------------------------------------------------------------------------

def _get_chip_text(chip: "ChipHandle") -> str:
    """Build searchable text from chip domain + mission for relevance scoring."""
    parts = [chip.domain, chip.chip_name]
    intel = _ensure_intel(chip)
    if intel:
        parts.append(intel.mission)
        for doc in intel.doctrines[:5]:
            parts.append(doc.get("claim", ""))
    return " ".join(parts)


def _ensure_intel(chip: "ChipHandle") -> ChipIntelligence | None:
    """Lazy-load intelligence for a chip handle."""
    if chip.intelligence is not None:
        return chip.intelligence
    try:
        chip.intelligence = extract_intelligence(chip.chip_path)
        return chip.intelligence
    except Exception:
        return None


# Minimum Jaccard relevance score for a chip to be considered.
# Chip text includes domain, name, mission, and top 5 doctrines (many words),
# so even a clear domain query like "crypto trading" scores ~0.03 due to the
# large union denominator.  0.03 filters pure noise (git/npm/ls → score 0.0)
# while allowing any query with at least one domain-relevant word through.
MIN_RELEVANCE_THRESHOLD = 0.03


def select_chips_for_task(
    task_description: str,
    portfolio: list["ChipHandle"],
    max_chips: int = 2,
    min_relevance: float = MIN_RELEVANCE_THRESHOLD,
) -> list["ChipHandle"]:
    """Select the most relevant chips for a task description.

    Uses Jaccard similarity between task description and chip domain/mission/doctrines.
    Chips scoring below *min_relevance* are excluded entirely -- this prevents
    injecting irrelevant domain intelligence for unrelated actions.
    """
    if not portfolio or not task_description.strip():
        return portfolio[:max_chips] if portfolio else []

    scored: list[tuple[float, "ChipHandle"]] = []
    for chip in portfolio:
        chip_text = _get_chip_text(chip)
        relevance = _score_relevance(task_description, chip_text)
        scored.append((relevance, chip))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Apply minimum relevance threshold
    filtered = [(score, chip) for score, chip in scored if score >= min_relevance]
    return [chip for _, chip in filtered[:max_chips]]


# ---------------------------------------------------------------------------
# Format helpers
# ---------------------------------------------------------------------------

_CONFIDENCE_PRIORITY = {"very high": 0, "high": 1, "medium": 2, "low": 3}


def _sort_doctrines_by_confidence(
    doctrines: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Sort doctrines highest confidence first."""
    return sorted(
        doctrines,
        key=lambda d: _CONFIDENCE_PRIORITY.get(
            str(d.get("confidence", "low")).lower(), 3
        ),
    )


def _format_doctrine_concise(doc: dict[str, Any]) -> str:
    """Format a single doctrine in concise mode (1-2 lines)."""
    claim = doc.get("claim", "")
    confidence = doc.get("confidence", "medium")
    lane = doc.get("evidence_lane", "")
    return f"- [{confidence}] {claim}" + (f" (evidence: {lane})" if lane else "")


def _format_doctrine_detailed(doc: dict[str, Any]) -> str:
    """Format a single doctrine in detailed mode (full info)."""
    lines = []
    claim = doc.get("claim", "")
    confidence = doc.get("confidence", "medium")
    lines.append(f"- **{claim}** (confidence: {confidence})")
    if doc.get("mechanism"):
        lines.append(f"  - Mechanism: {doc['mechanism']}")
    if doc.get("boundary"):
        lines.append(f"  - Boundary: {doc['boundary']}")
    if doc.get("evidence_lane"):
        lines.append(f"  - Evidence: {doc['evidence_lane']}")
    if doc.get("source"):
        lines.append(f"  - Source: {doc['source']}")
    return "\n".join(lines)


def _format_contradiction(contradiction: dict[str, Any]) -> str:
    """Format a contradiction entry."""
    a = contradiction.get("belief_a", "")
    b = contradiction.get("belief_b", "")
    status = contradiction.get("status", "open")
    if a and b:
        return f"- {a} vs {b} (status: {status})"
    elif a:
        return f"- {a} (status: {status})"
    return ""


# ---------------------------------------------------------------------------
# Main injection functions
# ---------------------------------------------------------------------------

def build_system_prompt_section(
    chips: list["ChipHandle"],
    style: str = "concise",
    max_tokens: int = 2000,
) -> str:
    """Build a system prompt section from chip intelligence.

    Args:
        chips: List of ChipHandle objects to include.
        style: "concise" (top 5 per chip), "detailed" (full), "guardrails_only" (constraints).
        max_tokens: Maximum estimated token budget.

    Returns:
        Formatted markdown string for system prompt injection.
    """
    if style == "guardrails_only":
        return build_guardrails_block(chips)

    sections: list[str] = []
    sections.append("## Domain Intelligence (from chip portfolio)\n")

    for chip in chips:
        intel = _ensure_intel(chip)
        if not intel:
            continue

        quality_tag = f"{chip.quality_score:.0f}/100 ({chip.quality_verdict})"
        if chip.quality_score < 35:
            quality_tag += " [scaffold - low reliability]"
        elif chip.quality_score < 60:
            quality_tag += " [alpha - moderate reliability]"

        sections.append(f"### {intel.chip_name} ({intel.domain}) -- Quality: {quality_tag}\n")

        # Doctrines
        sorted_docs = _sort_doctrines_by_confidence(intel.doctrines)

        if style == "concise":
            top_docs = sorted_docs[:5]
            if top_docs:
                sections.append("**Key doctrines:**")
                for doc in top_docs:
                    sections.append(_format_doctrine_concise(doc))
        elif style == "detailed":
            if sorted_docs:
                sections.append("**Doctrines:**")
                for doc in sorted_docs:
                    sections.append(_format_doctrine_detailed(doc))

        # Contradictions (always include top ones)
        if intel.contradictions:
            sections.append("\n**Active contradictions:**")
            for c in intel.contradictions[:3]:
                line = _format_contradiction(c)
                if line:
                    sections.append(line)

        sections.append("")  # blank line between chips

    result = "\n".join(sections)

    # Trim to token budget
    while _estimate_tokens(result) > max_tokens and "\n" in result:
        # Remove last non-empty line
        lines = result.rstrip().rsplit("\n", 1)
        if len(lines) > 1:
            result = lines[0]
        else:
            break

    return result


def build_guardrails_block(
    chips: list["ChipHandle"],
    min_confidence: str = "high",
) -> str:
    """Build a constraints block from high-confidence doctrines.

    Only includes doctrines at or above min_confidence from chips scoring >= 35.

    Returns:
        Formatted markdown with MUST/SHOULD/WATCH/UNCERTAIN sections.
    """
    min_level = _CONFIDENCE_PRIORITY.get(min_confidence.lower(), 1)

    must_items: list[str] = []
    should_items: list[str] = []
    watch_items: list[str] = []
    uncertain_items: list[str] = []

    for chip in chips:
        if chip.quality_score < 35:
            continue

        intel = _ensure_intel(chip)
        if not intel:
            continue

        chip_label = f"[{intel.chip_name}]"

        # High/very-high confidence doctrines -> MUST/SHOULD
        for doc in intel.doctrines:
            conf = str(doc.get("confidence", "low")).lower()
            conf_level = _CONFIDENCE_PRIORITY.get(conf, 3)

            if conf_level > min_level:
                continue

            claim = doc.get("claim", "")
            if not claim:
                continue

            if conf == "very high":
                must_items.append(f"- {chip_label} {claim}")
            elif conf == "high":
                should_items.append(f"- {chip_label} {claim}")

        # Contradictions -> WATCH
        for c in intel.contradictions:
            text = _format_contradiction(c)
            if text:
                watch_items.append(f"  {chip_label} {text.lstrip('- ')}")

        # Empty evidence lanes -> UNCERTAIN
        evidence = intel.evidence_summary
        empty_lanes = [
            lane for lane in ["realworld_validated", "benchmark_grounded"]
            if evidence.get(lane, 0) == 0
        ]
        if empty_lanes:
            uncertain_items.append(
                f"- {chip_label} No evidence in: {', '.join(empty_lanes)}"
            )

    sections = ["## Domain Guardrails (from chip intelligence)\n"]

    if must_items:
        sections.append("**MUST** (very high confidence):")
        sections.extend(must_items)
        sections.append("")

    if should_items:
        sections.append("**SHOULD** (high confidence):")
        sections.extend(should_items)
        sections.append("")

    if watch_items:
        sections.append("**WATCH** (active contradictions):")
        sections.extend(watch_items)
        sections.append("")

    if uncertain_items:
        sections.append("**UNCERTAIN** (evidence gaps):")
        sections.extend(uncertain_items)
        sections.append("")

    if not (must_items or should_items or watch_items or uncertain_items):
        sections.append("No high-confidence guardrails available from current chip portfolio.")

    return "\n".join(sections)


def inject_context_for_task(
    task_description: str,
    portfolio: list["ChipHandle"] | None = None,
    max_chips: int = 2,
    max_tokens: int = 1500,
    style: str = "concise",
) -> str:
    """Auto-select relevant chips and build injection context for a task.

    This is the primary entry point. It:
    1. Loads portfolio if not provided
    2. Selects most relevant chips for the task
    3. Builds formatted context within token budget

    Args:
        task_description: Description of what the agent is working on.
        portfolio: Optional pre-loaded portfolio. Loaded via load_portfolio if None.
        max_chips: Maximum number of chips to include.
        max_tokens: Token budget for the context block.
        style: "concise", "detailed", or "guardrails_only".

    Returns:
        Formatted context string ready for LLM injection.
    """
    if portfolio is None:
        try:
            from .chip_runtime import load_portfolio
            portfolio = load_portfolio(min_score=35)
        except (ImportError, Exception):
            return "<!-- No chip intelligence available -->"

    if not portfolio:
        return "<!-- No chips meet quality threshold -->"

    selected = select_chips_for_task(task_description, portfolio, max_chips)
    if not selected:
        return "<!-- No relevant chips found for this task -->"

    return build_system_prompt_section(selected, style=style, max_tokens=max_tokens)
