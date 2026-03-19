"""Signal ingestion and shock grammar.

Defines signal types, shock templates, and scenario branching
for injecting market/regulatory/viral events into simulations.
"""

from __future__ import annotations

from typing import Any


# Signal types with default strength ranges
SIGNAL_TYPES: dict[str, dict[str, Any]] = {
    "github_trending": {
        "label": "GitHub Trending",
        "default_strength": 0.6,
        "decay_per_round": 0.08,
        "description": "Repository trending on GitHub, indicates developer interest.",
    },
    "producthunt_launch": {
        "label": "Product Hunt Launch",
        "default_strength": 0.7,
        "decay_per_round": 0.10,
        "description": "Product launched on Product Hunt, indicates market interest.",
    },
    "viral_tweet": {
        "label": "Viral Tweet / Thread",
        "default_strength": 0.5,
        "decay_per_round": 0.15,
        "description": "Viral social media content, high initial impact but fast decay.",
    },
    "vc_funding": {
        "label": "VC Funding Round",
        "default_strength": 0.8,
        "decay_per_round": 0.03,
        "description": "Venture capital investment, strong signal with slow decay.",
    },
    "regulation": {
        "label": "Regulatory Action",
        "default_strength": 0.9,
        "decay_per_round": 0.02,
        "description": "Government regulation or policy change, persistent impact.",
    },
    "competitor_chip": {
        "label": "Competitor Chip Launch",
        "default_strength": 0.65,
        "decay_per_round": 0.05,
        "description": "Similar domain chip launched by competitor, competitive pressure.",
    },
    "community_request": {
        "label": "Community Feature Request",
        "default_strength": 0.4,
        "decay_per_round": 0.06,
        "description": "Community requests for a domain chip, grassroots demand signal.",
    },
}


# Shock templates for scenario injection
SHOCK_TEMPLATES: dict[str, dict[str, Any]] = {
    "market_crash": {
        "label": "Market Crash",
        "signal_type": "regulation",
        "strength_override": 0.95,
        "affected_persona_types": ["investor", "enterprise_buyer"],
        "effect": "negative",
        "description": "Broad market downturn reduces investment appetite.",
    },
    "breakout_tool": {
        "label": "Breakout Tool Launch",
        "signal_type": "producthunt_launch",
        "strength_override": 0.90,
        "affected_persona_types": ["early_adopter", "builder", "content_creator"],
        "effect": "positive",
        "description": "A tool goes viral and creates massive awareness for the domain.",
    },
    "regulatory_ban": {
        "label": "Regulatory Ban / Restriction",
        "signal_type": "regulation",
        "strength_override": 0.95,
        "affected_persona_types": ["regulator", "enterprise_buyer", "investor"],
        "effect": "negative",
        "description": "Government restricts or bans activity in the domain.",
    },
    "viral_adoption": {
        "label": "Viral Adoption Wave",
        "signal_type": "viral_tweet",
        "strength_override": 0.85,
        "affected_persona_types": ["content_creator", "early_adopter", "builder"],
        "effect": "positive",
        "description": "Social media drives mass awareness and adoption.",
    },
    "ecosystem_integration": {
        "label": "Major Ecosystem Integration",
        "signal_type": "github_trending",
        "strength_override": 0.80,
        "affected_persona_types": ["builder", "enterprise_buyer"],
        "effect": "positive",
        "description": "A major platform integrates with the domain, reducing friction.",
    },
}


def create_signal(
    signal_id: str,
    signal_type: str,
    affects_domains: list[str],
    strength: float | None = None,
    label: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a signal instance for injection into simulation."""
    type_info = SIGNAL_TYPES.get(signal_type, {})
    return {
        "signal_id": signal_id,
        "signal_type": signal_type,
        "label": label or type_info.get("label", signal_id),
        "strength": strength or type_info.get("default_strength", 0.5),
        "decay_per_round": type_info.get("decay_per_round", 0.05),
        "affects_domains": affects_domains,
        "metadata": metadata or {},
    }


def create_shock(
    shock_template: str,
    affects_domains: list[str],
    inject_at_round: int = 0,
    strength_override: float | None = None,
) -> dict[str, Any]:
    """Create a shock event from a template for scenario injection."""
    template = SHOCK_TEMPLATES.get(shock_template, {})
    return {
        "shock_id": f"shock-{shock_template}-r{inject_at_round}",
        "template": shock_template,
        "signal_type": template.get("signal_type", "community_request"),
        "label": template.get("label", shock_template),
        "strength": strength_override or template.get("strength_override", 0.8),
        "effect": template.get("effect", "neutral"),
        "affected_persona_types": template.get("affected_persona_types", []),
        "affects_domains": affects_domains,
        "inject_at_round": inject_at_round,
        "description": template.get("description", ""),
    }


def decay_signal(signal: dict[str, Any], rounds_elapsed: int) -> float:
    """Calculate decayed signal strength after N rounds."""
    base = signal.get("strength", 0.5)
    decay = signal.get("decay_per_round", 0.05)
    return max(0.0, round(base - (decay * rounds_elapsed), 4))


def build_scenario(
    shocks: list[dict[str, Any]],
    label: str = "default",
) -> dict[str, Any]:
    """Build a named scenario from a sequence of shocks."""
    return {
        "scenario_id": f"scenario-{label}",
        "label": label,
        "shocks": sorted(shocks, key=lambda s: s.get("inject_at_round", 0)),
        "shock_count": len(shocks),
    }


# ---------------------------------------------------------------------------
# Static score -> signal bridge
# ---------------------------------------------------------------------------

# Maps evidence_source names to signal types
_SOURCE_TO_SIGNAL: dict[str, str] = {
    "github": "github_trending",
    "producthunt": "producthunt_launch",
    "x_twitter": "viral_tweet",
    "community": "community_request",
    "arxiv": "github_trending",       # academic signal ~ developer signal
    "vc_landscape": "vc_funding",
    "spark_ecosystem": "community_request",
}


def signals_from_opportunities(
    opportunities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Convert scored domain opportunities into initial simulation signals.

    Each opportunity generates signals proportional to its dimension scores,
    routed through the evidence sources it declared. This bridges the gap
    between static scoring and the simulation engine.
    """
    signals: list[dict[str, Any]] = []

    for opp in opportunities:
        domain_id = opp.get("domain_id", "")
        scores = opp.get("scores", {})
        sources = opp.get("evidence_sources", [])
        composite = opp.get("composite_score", 0.0)

        # 1. Community demand signal -- strongest organic driver
        community = scores.get("community_demand", 0.0)
        if community > 0.5:
            signals.append(create_signal(
                f"{domain_id}-community-demand",
                "community_request",
                [domain_id],
                strength=community,
                label=f"{opp.get('label', domain_id)} community demand",
            ))

        # 2. Market signal from each evidence source
        for source in sources:
            signal_type = _SOURCE_TO_SIGNAL.get(source, "community_request")
            # Strength = composite score * source-specific boost
            source_boost = {
                "github": scores.get("data_availability", 0.5),
                "producthunt": scores.get("market_size", 0.5),
                "x_twitter": scores.get("community_demand", 0.5),
                "community": scores.get("community_demand", 0.5),
                "arxiv": scores.get("benchmark_feasibility", 0.5),
                "vc_landscape": scores.get("monetization_potential", 0.5),
                "spark_ecosystem": scores.get("spark_ecosystem_fit", 0.5),
            }
            strength = round(composite * source_boost.get(source, 0.5), 4)
            if strength > 0.3:  # only meaningful signals
                signals.append(create_signal(
                    f"{domain_id}-{source}",
                    signal_type,
                    [domain_id],
                    strength=strength,
                    label=f"{opp.get('label', domain_id)} via {source}",
                ))

        # 3. Ecosystem fit signal -- related chips create cross-domain pull
        related = opp.get("related_chips", [])
        eco_fit = scores.get("spark_ecosystem_fit", 0.0)
        if related and eco_fit > 0.6:
            signals.append(create_signal(
                f"{domain_id}-ecosystem-pull",
                "competitor_chip",  # reuse as "existing chip validates domain"
                [domain_id],
                strength=round(eco_fit * 0.9, 4),
                label=f"{opp.get('label', domain_id)} ecosystem pull from {', '.join(related)}",
                metadata={"related_chips": related},
            ))

    return signals


def signals_from_graph(graph: "Any") -> list[dict[str, Any]]:
    """Generate cross-domain influence signals from graph relationships.

    Domains connected by ENABLES or EXTENDS relationships propagate
    awareness to each other. Domains connected by COMPETES_WITH
    create competitive pressure signals.
    """
    signals: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for edge in graph.edges:
        src, tgt = edge["source"], edge["target"]
        rel = edge["relationship"]
        weight = edge.get("weight", 0.5)

        # Only domain-to-domain or chip-to-domain edges matter
        src_node = graph.nodes.get(src, {})
        tgt_node = graph.nodes.get(tgt, {})

        if rel == "EXTENDS" and tgt_node.get("type") == "technology":
            # Existing chip validates the domain
            pair = (src, tgt)
            if pair not in seen:
                seen.add(pair)
                signals.append(create_signal(
                    f"graph-extends-{src}-{tgt}",
                    "competitor_chip",
                    [src],
                    strength=round(weight * 0.85, 4),
                    label=f"{src} extends {tgt_node.get('label', tgt)}",
                ))

        elif rel == "ENABLES" and src_node.get("type") == "technology":
            # Technology enables domain
            pair = (src, tgt)
            if pair not in seen and tgt_node.get("type") == "domain":
                seen.add(pair)
                signals.append(create_signal(
                    f"graph-enables-{src}-{tgt}",
                    "github_trending",
                    [tgt],
                    strength=round(weight * 0.6, 4),
                    label=f"{src_node.get('label', src)} enables {tgt}",
                ))

        elif rel == "COMPETES_WITH":
            # Competition creates pressure on both domains
            for a, b in [(src, tgt), (tgt, src)]:
                pair = (a, b, "compete")
                if pair not in seen and graph.nodes.get(a, {}).get("type") == "domain":
                    seen.add(pair)
                    signals.append(create_signal(
                        f"graph-competes-{a}-{b}",
                        "competitor_chip",
                        [a],
                        strength=round(weight * 0.4, 4),
                        label=f"Competitive pressure from {b}",
                    ))

    return signals
