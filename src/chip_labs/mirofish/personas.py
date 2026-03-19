"""Stakeholder persona generator.

Creates differentiated agent archetypes that simulate domain adoption dynamics.
Bounded at 12-30 personas per domain (not thousands).
"""

from __future__ import annotations

import hashlib
from typing import Any

from .graph import DomainGraph


# 8 persona types with default trait ranges
PERSONA_TYPES: dict[str, dict[str, Any]] = {
    "early_adopter": {
        "label": "Early Adopter",
        "influence_score": 0.7,
        "adoption_threshold": 0.2,
        "risk_tolerance": 0.9,
        "network_reach": 0.6,
        "description": "Jumps on new tech fast, high risk tolerance, moderate influence.",
    },
    "builder": {
        "label": "Builder / Developer",
        "influence_score": 0.8,
        "adoption_threshold": 0.35,
        "risk_tolerance": 0.7,
        "network_reach": 0.7,
        "description": "Builds with the tech, high influence through shipping code.",
    },
    "investor": {
        "label": "Investor / VC",
        "influence_score": 0.9,
        "adoption_threshold": 0.4,
        "risk_tolerance": 0.6,
        "network_reach": 0.9,
        "description": "Funds the ecosystem, high network reach, moderate risk tolerance.",
    },
    "skeptic": {
        "label": "Skeptic / Critic",
        "influence_score": 0.5,
        "adoption_threshold": 0.8,
        "risk_tolerance": 0.2,
        "network_reach": 0.4,
        "description": "Slow to adopt, provides critical feedback, raises valid concerns.",
    },
    "enterprise_buyer": {
        "label": "Enterprise Buyer",
        "influence_score": 0.6,
        "adoption_threshold": 0.7,
        "risk_tolerance": 0.3,
        "network_reach": 0.5,
        "description": "Large budgets but high adoption barrier, needs proven ROI.",
    },
    "content_creator": {
        "label": "Content Creator",
        "influence_score": 0.75,
        "adoption_threshold": 0.3,
        "risk_tolerance": 0.65,
        "network_reach": 0.85,
        "description": "Amplifies signal, creates tutorials and content, high reach.",
    },
    "researcher": {
        "label": "Researcher / Academic",
        "influence_score": 0.55,
        "adoption_threshold": 0.5,
        "risk_tolerance": 0.5,
        "network_reach": 0.4,
        "description": "Provides rigor and validation, moderate influence, domain expert.",
    },
    "regulator": {
        "label": "Regulator / Policy Maker",
        "influence_score": 0.85,
        "adoption_threshold": 0.9,
        "risk_tolerance": 0.1,
        "network_reach": 0.3,
        "description": "Can block or enable adoption, extremely high threshold, low risk.",
    },
}


def generate_personas(
    graph: DomainGraph,
    domain_ids: list[str] | None = None,
    count_per_type: int = 2,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """Generate differentiated stakeholder personas from graph entities.

    Args:
        graph: Domain knowledge graph.
        domain_ids: Which domains to create personas for (all if None).
        count_per_type: How many personas per type (1-4, default 2).
        seed: Random seed for deterministic persona variation.

    Returns:
        List of persona dicts (12-30 depending on parameters).
    """
    count_per_type = max(1, min(4, count_per_type))
    domains = domain_ids or [
        n["id"] for n in graph.nodes.values() if n["type"] == "domain"
    ]

    personas: list[dict[str, Any]] = []
    persona_idx = 0

    for ptype, traits in PERSONA_TYPES.items():
        for variant in range(count_per_type):
            persona_idx += 1
            # Deterministic variation using seed
            variation = _deterministic_variation(seed, persona_idx)

            # Assign expertise domains based on graph neighbors
            expertise = _assign_expertise(graph, domains, ptype, variant)

            persona = {
                "persona_id": f"{ptype}-{variant}",
                "persona_type": ptype,
                "label": f"{traits['label']} #{variant + 1}",
                "influence_score": _vary(traits["influence_score"], variation, 0.15),
                "adoption_threshold": _vary(traits["adoption_threshold"], variation, 0.1),
                "risk_tolerance": _vary(traits["risk_tolerance"], variation, 0.15),
                "network_reach": _vary(traits["network_reach"], variation, 0.1),
                "expertise_domains": expertise,
                "adoption_state": {},  # domain_id -> adoption stage
                "signal_memory": [],   # recent signals this persona has seen
                "activity_score": 1.0, # decays over simulation rounds
            }
            personas.append(persona)

    return personas


def update_persona_activity(persona: dict[str, Any], round_num: int,
                            decay_rate: float = 0.05) -> None:
    """Apply time-decay to persona activity."""
    persona["activity_score"] = max(0.1, 1.0 - (round_num * decay_rate))


def persona_evaluates_domain(
    persona: dict[str, Any],
    domain_id: str,
    awareness_score: float,
) -> str:
    """Determine a persona's adoption stage for a domain.

    Adoption funnel: unaware -> aware -> interested -> evaluating -> adopted -> advocating

    Each stage has a progressively higher threshold multiplier, so advancing
    from "evaluating" to "adopted" is much harder than "unaware" to "aware".
    This prevents all personas from rocketing to max adoption in a few rounds.

    Returns new adoption stage.
    """
    current = persona["adoption_state"].get(domain_id, "unaware")
    threshold = persona["adoption_threshold"]
    risk = persona["risk_tolerance"]
    activity = persona["activity_score"]

    effective_signal = awareness_score * activity

    stages = ["unaware", "aware", "interested", "evaluating", "adopted", "advocating"]
    current_idx = stages.index(current) if current in stages else 0

    # Each stage demands progressively more signal to advance
    # unaware->aware is easy (0.3x), adopted->advocating is very hard (2.0x)
    stage_difficulty = {
        0: 0.3,   # unaware -> aware: just needs some signal
        1: 0.6,   # aware -> interested: needs moderate signal
        2: 0.9,   # interested -> evaluating: needs strong signal
        3: 1.3,   # evaluating -> adopted: needs very strong, sustained signal
        4: 1.8,   # adopted -> advocating: needs exceptional conviction
    }

    difficulty = stage_difficulty.get(current_idx, 2.0)
    advance_threshold = threshold * difficulty * (1.0 - risk * 0.3)

    if effective_signal > advance_threshold and current_idx < len(stages) - 1:
        new_stage = stages[current_idx + 1]
    else:
        new_stage = current

    persona["adoption_state"][domain_id] = new_stage
    return new_stage


def persona_influence_score(persona: dict[str, Any], domain_id: str) -> float:
    """Calculate influence a persona exerts on a domain.

    Higher if: persona is adopted/advocating, has high influence, and domain is in expertise.
    """
    stage = persona["adoption_state"].get(domain_id, "unaware")
    stage_multiplier = {
        "unaware": 0.0, "aware": 0.1, "interested": 0.3,
        "evaluating": 0.5, "adopted": 0.8, "advocating": 1.0,
    }
    mult = stage_multiplier.get(stage, 0.0)

    expertise_bonus = 1.2 if domain_id in persona.get("expertise_domains", []) else 1.0
    return round(
        persona["influence_score"] * persona["network_reach"] * mult * expertise_bonus * persona["activity_score"],
        4,
    )


def _deterministic_variation(seed: int, idx: int) -> float:
    """Generate a deterministic pseudo-random variation from seed and index."""
    h = hashlib.md5(f"{seed}-{idx}".encode()).hexdigest()
    return (int(h[:8], 16) % 1000) / 1000.0


def _vary(base: float, variation: float, amplitude: float) -> float:
    """Apply bounded variation to a base value."""
    offset = (variation - 0.5) * 2.0 * amplitude
    return round(max(0.0, min(1.0, base + offset)), 4)


def _assign_expertise(graph: DomainGraph, domains: list[str],
                      ptype: str, variant: int) -> list[str]:
    """Assign expertise domains based on persona type and graph structure."""
    # Each persona type has affinity for certain graph entity types
    type_affinity = {
        "early_adopter": ["technology", "trend"],
        "builder": ["technology", "platform"],
        "investor": ["company", "trend"],
        "skeptic": ["regulation", "community"],
        "enterprise_buyer": ["company", "regulation"],
        "content_creator": ["platform", "community"],
        "researcher": ["technology", "trend"],
        "regulator": ["regulation"],
    }
    affinities = type_affinity.get(ptype, [])

    # Pick domains that connect to entities matching this persona's affinity
    scored: list[tuple[str, int]] = []
    for domain_id in domains:
        if domain_id not in graph.nodes:
            continue
        edges = graph.get_edges_for(domain_id)
        affinity_count = 0
        for edge in edges:
            other = edge["target"] if edge["source"] == domain_id else edge["source"]
            if other in graph.nodes and graph.nodes[other]["type"] in affinities:
                affinity_count += 1
        scored.append((domain_id, affinity_count))

    scored.sort(key=lambda x: x[1], reverse=True)
    # Pick top domains, offset by variant for diversity
    start = variant % max(len(scored), 1)
    selected = [s[0] for s in scored[start:start + 3]]
    return selected or domains[:2]
