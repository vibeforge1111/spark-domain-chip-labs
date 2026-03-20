"""Research direction suggestion engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .quality_rubric import score_chip
from .registry import discover_chips
from .trend_scanner import SEED_OPPORTUNITIES, rank_opportunities


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

    # 2c. Simulation-backed domain suggestions (if enough opportunities exist)
    sim_suggestions = _simulation_backed_suggestions(chips, recent_set)
    suggestions.extend(sim_suggestions)

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


def _simulation_backed_suggestions(
    chips: list[dict[str, Any]],
    recent_set: set[frozenset],
) -> list[dict[str, Any]]:
    """Generate suggestions backed by Monte Carlo ensemble simulation.

    Runs a lightweight ensemble (3 runs, 2 personas/type) to identify
    high-adoption domains that don't have chips yet. Uses confidence
    intervals to separate high-confidence picks from uncertain bets.
    """
    from .mirofish.graph import build_graph_from_opportunities
    from .mirofish.simulation import run_ensemble
    from .mirofish.signals import signals_from_opportunities, signals_from_graph

    suggestions: list[dict[str, Any]] = []

    ranked = rank_opportunities()
    if len(ranked) < 2:
        return suggestions

    graph = build_graph_from_opportunities(ranked)
    domain_ids = [opp["domain_id"] for opp in ranked]

    opp_signals = signals_from_opportunities(ranked)
    graph_signals = signals_from_graph(graph)
    all_signals = opp_signals + graph_signals

    # Lightweight ensemble: 3 runs, 2 per type = fast
    ensemble = run_ensemble(
        graph, domain_ids, signals=all_signals,
        max_rounds=10, n_runs=3, base_seed=42,
        count_per_type=2,
    )

    chip_names = {c["name"] for c in chips}
    # Also match by domain_id pattern (domain-chip-X -> X)
    chip_domains = set()
    for c in chips:
        name = c["name"]
        if name.startswith("domain-chip-"):
            chip_domains.add(name[len("domain-chip-"):])
        chip_domains.add(name)

    for domain_id in domain_ids:
        stats = ensemble["domains"].get(domain_id, {})
        mean_adoption = stats.get("mean_adoption", 0)
        p10 = stats.get("p10_adoption", 0)
        p90 = stats.get("p90_adoption", 0)
        width = p90 - p10

        # Skip domains that already have chips
        if domain_id in chip_domains:
            continue

        if mean_adoption < 0.15:
            continue

        if mean_adoption > 0.4 and width < 0.15:
            priority = "high"
            confidence = "high"
        elif mean_adoption > 0.25:
            priority = "medium"
            confidence = "medium" if width < 0.2 else "low"
        else:
            priority = "low"
            confidence = "low"

        mutation = {
            "research_focus": "domain_discovery",
            "simulation_domain": domain_id,
        }
        if frozenset(mutation.items()) not in recent_set:
            suggestions.append({
                "candidate_id": f"sim-backed-{domain_id}",
                "candidate_summary": (
                    f"Build {domain_id} chip (ensemble adoption: "
                    f"{mean_adoption:.0%}, CI: {p10:.0%}-{p90:.0%})."
                ),
                "hypothesis": (
                    f"Monte Carlo ensemble predicts {mean_adoption:.0%} adoption "
                    f"with {confidence} confidence. "
                    f"{'Strong signal across runs.' if width < 0.1 else 'Variable across runs -- needs more data.'}"
                ),
                "mutations": mutation,
                "priority": priority,
                "simulation_data": {
                    "mean_adoption": mean_adoption,
                    "p10": p10,
                    "p90": p90,
                    "confidence": confidence,
                },
            })

    # Sort by mean adoption descending
    suggestions.sort(key=lambda x: x.get("simulation_data", {}).get("mean_adoption", 0), reverse=True)
    return suggestions
