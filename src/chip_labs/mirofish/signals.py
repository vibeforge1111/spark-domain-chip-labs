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
