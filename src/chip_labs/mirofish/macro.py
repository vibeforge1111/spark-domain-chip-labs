"""Macro context system for MiroFish v4.

Global conditions that modify ALL agent behavior across the simulation.
Models real-world forces like economic sentiment, AI displacement pressure,
speculative appetite, geopolitical stability, and regulatory pressure.

Each macro dimension modifies persona adoption thresholds via domain tag
matching -- domains tagged with relevant keywords become easier or harder
to adopt depending on the macro state.
"""

from __future__ import annotations

from typing import Any


class MacroContext:
    """Global macro conditions that affect all persona behavior.

    Each dimension is a float from -1.0 to 1.0:
    - Negative = suppresses related domains
    - Positive = amplifies related domains
    - Zero = neutral (no effect)
    """

    __slots__ = (
        "economic_sentiment",
        "ai_displacement_pressure",
        "speculative_appetite",
        "geopolitical_stability",
        "regulatory_pressure",
    )

    def __init__(
        self,
        economic_sentiment: float = 0.0,
        ai_displacement_pressure: float = 0.0,
        speculative_appetite: float = 0.0,
        geopolitical_stability: float = 0.0,
        regulatory_pressure: float = 0.0,
    ) -> None:
        self.economic_sentiment = max(-1.0, min(1.0, economic_sentiment))
        self.ai_displacement_pressure = max(-1.0, min(1.0, ai_displacement_pressure))
        self.speculative_appetite = max(-1.0, min(1.0, speculative_appetite))
        self.geopolitical_stability = max(-1.0, min(1.0, geopolitical_stability))
        self.regulatory_pressure = max(-1.0, min(1.0, regulatory_pressure))

    def copy(self) -> "MacroContext":
        return MacroContext(
            economic_sentiment=self.economic_sentiment,
            ai_displacement_pressure=self.ai_displacement_pressure,
            speculative_appetite=self.speculative_appetite,
            geopolitical_stability=self.geopolitical_stability,
            regulatory_pressure=self.regulatory_pressure,
        )

    def to_dict(self) -> dict[str, float]:
        return {
            "economic_sentiment": round(self.economic_sentiment, 3),
            "ai_displacement_pressure": round(self.ai_displacement_pressure, 3),
            "speculative_appetite": round(self.speculative_appetite, 3),
            "geopolitical_stability": round(self.geopolitical_stability, 3),
            "regulatory_pressure": round(self.regulatory_pressure, 3),
        }


# ---------------------------------------------------------------------------
# Tag -> macro dimension mapping
# ---------------------------------------------------------------------------

# Which domain tags are affected by each macro dimension, and in which direction.
# positive_modifier = macro_value * weight is SUBTRACTED from threshold (easier to adopt)
# negative_modifier = macro_value * weight is ADDED to threshold (harder to adopt)

TAG_MACRO_EFFECTS: dict[str, list[tuple[str, float]]] = {
    # AI displacement pressure HIGH -> lowers threshold for career/learning domains
    "ai_displacement_pressure": [
        ("productivity", 0.15),
        ("career", 0.2),
        ("easy_start", 0.15),
        ("low_learning_curve", 0.15),
        ("outcompete", 0.12),
        ("reskill", 0.25),
        ("ai_survival", 0.25),
        ("quick_wins", 0.1),
    ],
    # Speculative appetite HIGH -> lowers threshold for speculative domains
    # LOW -> raises threshold (people avoid risk)
    "speculative_appetite": [
        ("alpha", 0.15),
        ("edge", 0.12),
        ("first_mover", 0.15),
        ("trend_spotting", 0.1),
        ("speed", 0.08),
        ("defi", 0.2),
        ("trading", 0.18),
        ("meme", 0.2),
        ("airdrop", 0.15),
    ],
    # Economic sentiment HIGH -> general adoption boost for business tools
    "economic_sentiment": [
        ("roi", 0.1),
        ("campaign_roi", 0.1),
        ("speed_to_ship", 0.08),
        ("market_fit", 0.08),
        ("time_leverage", 0.1),
        ("low_cost", 0.12),
    ],
    # Geopolitical stability LOW -> raises threshold for luxury/optional domains,
    # but lowers threshold for security/survival domains
    "geopolitical_stability": [
        ("security", -0.15),
        ("compliance", -0.1),
        ("infrastructure", -0.08),
    ],
    # Regulatory pressure HIGH -> makes compliance easier to adopt,
    # makes unregulated domains (defi, meme) harder to adopt
    "regulatory_pressure": [
        ("compliance", 0.15),
        ("audit", 0.12),
        ("defi", -0.15),
        ("meme", -0.12),
        ("airdrop", -0.1),
    ],
}


def compute_macro_modifier(
    macro: MacroContext,
    domain_tags: list[str],
) -> float:
    """Compute the threshold modifier for a domain given current macro context.

    Returns a float that is SUBTRACTED from the persona's adoption threshold.
    Positive = easier to adopt (threshold goes down).
    Negative = harder to adopt (threshold goes up).

    The modifier is bounded to [-0.15, 0.15] to prevent macro from
    overwhelming individual persona traits.
    """
    modifier = 0.0

    macro_values = {
        "ai_displacement_pressure": macro.ai_displacement_pressure,
        "speculative_appetite": macro.speculative_appetite,
        "economic_sentiment": macro.economic_sentiment,
        "geopolitical_stability": macro.geopolitical_stability,
        "regulatory_pressure": macro.regulatory_pressure,
    }

    tag_set = set(domain_tags)

    for dimension, tag_effects in TAG_MACRO_EFFECTS.items():
        macro_val = macro_values.get(dimension, 0.0)
        if macro_val == 0.0:
            continue

        for tag, weight in tag_effects:
            if tag not in tag_set:
                continue
            # Positive weight: macro amplifies this tag (e.g., high displacement
            # makes career domains easier to adopt)
            # Negative weight: macro suppresses this tag (e.g., low stability
            # makes security domains easier -- note the double negative)
            if weight > 0:
                modifier += macro_val * weight
            else:
                # Negative weight means the effect is inverted relative to macro
                modifier -= macro_val * abs(weight)

    # Clamp to prevent macro from dominating
    return max(-0.15, min(0.15, modifier))


# ---------------------------------------------------------------------------
# Macro event timeline
# ---------------------------------------------------------------------------

MacroEvent = dict[str, Any]


def create_macro_event(
    round_num: int,
    label: str,
    changes: dict[str, float],
) -> MacroEvent:
    """Create a macro event that modifies context at a specific round.

    Args:
        round_num: When this event fires.
        label: Human-readable description.
        changes: Dict of dimension_name -> delta (added to current value).
    """
    return {
        "inject_at_round": round_num,
        "label": label,
        "changes": changes,
    }


def apply_macro_event(macro: MacroContext, event: MacroEvent) -> None:
    """Apply a macro event's changes to the context (mutates in place)."""
    for dim, delta in event.get("changes", {}).items():
        current = getattr(macro, dim, None)
        if current is not None:
            setattr(macro, dim, max(-1.0, min(1.0, current + delta)))


# ---------------------------------------------------------------------------
# Presets for 2026 scenarios
# ---------------------------------------------------------------------------

MARCH_2026 = MacroContext(
    economic_sentiment=-0.3,
    ai_displacement_pressure=0.8,
    speculative_appetite=0.3,
    geopolitical_stability=0.4,
    regulatory_pressure=0.6,
)

MARCH_2026_EVENTS: list[MacroEvent] = [
    create_macro_event(3, "Mass AI layoffs in tech",
                       {"ai_displacement_pressure": 0.15, "economic_sentiment": -0.1}),
    create_macro_event(5, "Crypto mini-rally",
                       {"speculative_appetite": 0.15}),
    create_macro_event(8, "Major AI regulation bill passes",
                       {"regulatory_pressure": 0.15, "ai_displacement_pressure": 0.05}),
    create_macro_event(10, "Middle East escalation",
                       {"geopolitical_stability": -0.15, "economic_sentiment": -0.1}),
    create_macro_event(13, "Open source AI model released free",
                       {"ai_displacement_pressure": 0.1, "speculative_appetite": 0.1}),
    create_macro_event(16, "Government AI retraining subsidy announced",
                       {"ai_displacement_pressure": -0.1, "economic_sentiment": 0.1}),
]


def generate_macro_signals(
    macro: MacroContext,
    domain_tags: dict[str, list[str]],
    round_num: int,
) -> list[dict[str, Any]]:
    """Generate ambient signals based on current macro state.

    High macro pressure in a dimension injects weak signals into
    domains tagged with that dimension's keywords. This creates
    a "rising tide" or "headwind" effect on adoption.
    """
    signals: list[dict[str, Any]] = []

    macro_values = {
        "ai_displacement_pressure": macro.ai_displacement_pressure,
        "speculative_appetite": macro.speculative_appetite,
        "economic_sentiment": macro.economic_sentiment,
    }

    for dimension, macro_val in macro_values.items():
        if abs(macro_val) < 0.2:
            continue

        tag_effects = TAG_MACRO_EFFECTS.get(dimension, [])
        affected_tags = {tag for tag, w in tag_effects if w > 0}

        # Find domains with matching tags
        affected_domains = []
        for d_id, tags in domain_tags.items():
            if affected_tags & set(tags):
                affected_domains.append(d_id)

        if not affected_domains:
            continue

        # Ambient signal strength proportional to macro pressure
        strength = min(0.4, abs(macro_val) * 0.35)
        effect = "positive" if macro_val > 0 else "negative"

        signals.append({
            "signal_type": f"macro_{dimension}",
            "affects_domains": affected_domains,
            "strength": strength,
            "inject_at_round": round_num,
            "effect": effect,
            "affected_persona_types": [],
            "metadata": {"source": "macro_context", "dimension": dimension},
        })

    return signals
