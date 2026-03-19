"""Research direction suggestion engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .quality_rubric import score_chip
from .registry import discover_chips


def suggest(recent_mutations: list[dict[str, str]] | None = None,
            chip_search_dir: str | Path | None = None) -> list[dict[str, Any]]:
    """Suggest next research directions based on portfolio gaps and methodology needs.

    Returns a list of candidate suggestions for the frontier queue.
    """
    suggestions: list[dict[str, Any]] = []

    # Discover current portfolio
    chips = discover_chips(chip_search_dir)
    recent_set = {frozenset(m.items()) for m in (recent_mutations or [])}

    # 1. Find weakest chips for quality audit
    chip_scores: list[tuple[str, int]] = []
    for chip in chips:
        if chip["has_manifest"]:
            result = score_chip(chip["path"])
            chip_scores.append((chip["name"], result["total_score"]))

    chip_scores.sort(key=lambda x: x[1])

    for name, total_score in chip_scores[:3]:
        mutation = {"research_focus": "quality_audit", "portfolio_target": name}
        if frozenset(mutation.items()) not in recent_set:
            suggestions.append({
                "candidate_id": f"quality-audit-{name}",
                "candidate_summary": f"Quality audit for {name} (current score: {total_score}/100).",
                "hypothesis": f"Auditing {name} will reveal specific improvement paths.",
                "mutations": mutation,
                "priority": "high" if total_score < 50 else "medium",
            })

    # 2. Suggest methodology research for weakest areas
    methodology_areas = [
        ("graduation_criteria", 0.45, "Graduation criteria are undertested."),
        ("frontier_design", 0.40, "Frontier mutation design needs more study."),
        ("source_registry", 0.35, "Source registry patterns are underdocumented."),
        ("packet_quality", 0.42, "Packet quality standards need refinement."),
    ]

    for area, score, rationale in methodology_areas:
        mutation = {"research_focus": "methodology", "methodology_area": area}
        if frozenset(mutation.items()) not in recent_set:
            suggestions.append({
                "candidate_id": f"methodology-{area}",
                "candidate_summary": f"Research methodology improvement: {area}.",
                "hypothesis": rationale,
                "mutations": mutation,
                "priority": "high" if score < 0.40 else "medium",
            })

    # 2b. Suggest trend simulation for data-driven domain discovery
    mutation = {"research_focus": "trend_simulation"}
    if frozenset(mutation.items()) not in recent_set:
        suggestions.append({
            "candidate_id": "trend-simulation-mirofish",
            "candidate_summary": "Run MiroFish trend simulation for data-driven domain predictions.",
            "hypothesis": "Multi-agent simulation reveals adoption dynamics invisible to static scoring.",
            "mutations": mutation,
            "priority": "high",
        })

    # 3. Suggest domain discovery if portfolio has gaps
    if len(chips) < 15:
        for source in ["github", "producthunt", "spark_ecosystem"]:
            mutation = {"research_focus": "domain_discovery", "trend_source": source}
            if frozenset(mutation.items()) not in recent_set:
                suggestions.append({
                    "candidate_id": f"domain-discovery-{source}",
                    "candidate_summary": f"Scan {source} for new domain chip opportunities.",
                    "hypothesis": f"{source} may reveal high-demand domains without existing chips.",
                    "mutations": mutation,
                    "priority": "medium",
                })

    # 4. Suggest transfer pattern research if mature chips exist
    mature_chips = [c for c in chips if (c.get("version") or "").startswith("0.3")]
    if len(mature_chips) >= 1:
        mutation = {"research_focus": "transfer_patterns"}
        if frozenset(mutation.items()) not in recent_set:
            suggestions.append({
                "candidate_id": "transfer-patterns-cross-chip",
                "candidate_summary": "Study cross-chip transfer patterns from mature chips.",
                "hypothesis": "Mature chips contain portable methodology that can be extracted.",
                "mutations": mutation,
                "priority": "medium",
            })

    return suggestions
