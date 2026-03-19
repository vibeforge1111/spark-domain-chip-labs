"""Trend adoption simulation engine.

Runs bounded multi-round simulation where personas evaluate domains,
share signals, and influence neighbors. Produces adoption curves,
consensus scores, and tipping point detection.
"""

from __future__ import annotations

from typing import Any

from .graph import DomainGraph
from .personas import (
    generate_personas, update_persona_activity,
    persona_evaluates_domain, persona_influence_score,
)
from .signals import decay_signal


# Adoption stages in order
ADOPTION_STAGES = ["unaware", "aware", "interested", "evaluating", "adopted", "advocating"]

# Maximum simulation rounds
MAX_ROUNDS = 20


def run_simulation(
    graph: DomainGraph,
    domain_ids: list[str] | None = None,
    personas: list[dict[str, Any]] | None = None,
    signals: list[dict[str, Any]] | None = None,
    shocks: list[dict[str, Any]] | None = None,
    max_rounds: int = MAX_ROUNDS,
    seed: int = 42,
    context: str = "builder_community",
) -> dict[str, Any]:
    """Run a bounded multi-round adoption simulation.

    Args:
        graph: Domain knowledge graph.
        domain_ids: Domains to simulate (all graph domains if None).
        personas: Pre-generated personas (auto-generated if None).
        signals: Initial signals to inject.
        shocks: Shock events with inject_at_round.
        max_rounds: Maximum simulation rounds (capped at 20).
        seed: Random seed for deterministic simulation.
        context: Simulation context ("builder_community" or "enterprise_market").

    Returns:
        Simulation results with adoption curves, consensus, and tipping points.
    """
    max_rounds = min(max_rounds, MAX_ROUNDS)
    domains = domain_ids or [
        n["id"] for n in graph.nodes.values() if n["type"] == "domain"
    ]

    if personas is None:
        personas = generate_personas(graph, domains, seed=seed)

    # Apply context-specific trait adjustments
    _apply_context(personas, context)

    # Initialize tracking
    adoption_curves: dict[str, list[dict[str, Any]]] = {d: [] for d in domains}
    consensus_history: dict[str, list[float]] = {d: [] for d in domains}
    tipping_points: dict[str, int | None] = {d: None for d in domains}
    active_signals: list[dict[str, Any]] = list(signals or [])
    shock_list = list(shocks or [])

    # Run simulation rounds
    for round_num in range(max_rounds):
        # Inject shocks scheduled for this round
        for shock in shock_list:
            if shock.get("inject_at_round", 0) == round_num:
                active_signals.append(shock)

        # Phase 1: Signal propagation -- each persona receives domain awareness
        # Attention budget: personas compute awareness for all domains but only
        # deeply evaluate their top-N (sorted by signal strength). This models
        # finite attention -- you can't seriously adopt 32 things at once.
        attention_budget = min(10, max(4, len(domains) // 3))

        for persona in personas:
            update_persona_activity(persona, round_num)

            # Compute raw awareness for every domain
            domain_awareness: list[tuple[str, float]] = []
            for domain_id in domains:
                awareness = _compute_awareness(
                    persona, domain_id, active_signals, round_num,
                )
                domain_awareness.append((domain_id, awareness))

            # Always evaluate domains persona already has traction with
            active_domains = {
                d_id for d_id, stage in persona["adoption_state"].items()
                if stage not in ("unaware",)
            }

            # Sort remaining by awareness strength, pick top-N
            domain_awareness.sort(key=lambda x: x[1], reverse=True)

            evaluated = 0
            for domain_id, awareness in domain_awareness:
                in_budget = domain_id in active_domains or evaluated < attention_budget
                if in_budget:
                    persona_evaluates_domain(persona, domain_id, awareness)
                    if domain_id not in active_domains:
                        evaluated += 1
                else:
                    # Below attention budget -- only allow unaware->aware (discovery)
                    # with heavily dampened signal
                    current = persona["adoption_state"].get(domain_id, "unaware")
                    if current == "unaware" and awareness > 0.5:
                        persona_evaluates_domain(persona, domain_id, awareness * 0.3)

        # Phase 2: Influence propagation -- personas influence each other
        _propagate_influence(personas, domains, graph)

        # Phase 3: Record adoption state
        for domain_id in domains:
            snapshot = _adoption_snapshot(personas, domain_id, round_num)
            adoption_curves[domain_id].append(snapshot)

            consensus = _compute_consensus(personas, domain_id)
            consensus_history[domain_id].append(consensus)

            # Detect tipping point (first round where adoption > 50%)
            adoption_rate = snapshot["adoption_rate"]
            if adoption_rate > 0.5 and tipping_points[domain_id] is None:
                tipping_points[domain_id] = round_num

        # Decay signals
        active_signals = [
            s for s in active_signals
            if decay_signal(s, round_num - s.get("inject_at_round", 0)) > 0.01
        ]

    # Compile results
    results: dict[str, Any] = {
        "context": context,
        "rounds_run": max_rounds,
        "persona_count": len(personas),
        "domain_count": len(domains),
        "domains": {},
    }

    for domain_id in domains:
        final_snapshot = adoption_curves[domain_id][-1] if adoption_curves[domain_id] else {}
        results["domains"][domain_id] = {
            "adoption_curve": adoption_curves[domain_id],
            "final_adoption_rate": final_snapshot.get("adoption_rate", 0.0),
            "final_advocacy_rate": final_snapshot.get("advocacy_rate", 0.0),
            "consensus_history": consensus_history[domain_id],
            "final_consensus": consensus_history[domain_id][-1] if consensus_history[domain_id] else 0.0,
            "tipping_point_round": tipping_points[domain_id],
            "disagreement_score": _compute_disagreement(personas, domain_id),
        }

    return results


def run_dual_context(
    graph: DomainGraph,
    domain_ids: list[str] | None = None,
    signals: list[dict[str, Any]] | None = None,
    shocks: list[dict[str, Any]] | None = None,
    max_rounds: int = MAX_ROUNDS,
    seed: int = 42,
) -> dict[str, Any]:
    """Run simulation in both builder and enterprise contexts for comparison."""
    builder_result = run_simulation(
        graph, domain_ids, signals=signals, shocks=shocks,
        max_rounds=max_rounds, seed=seed, context="builder_community",
    )
    enterprise_result = run_simulation(
        graph, domain_ids, signals=signals, shocks=shocks,
        max_rounds=max_rounds, seed=seed, context="enterprise_market",
    )

    domains = list(builder_result["domains"].keys())
    comparison: dict[str, dict[str, Any]] = {}
    for domain_id in domains:
        b = builder_result["domains"].get(domain_id, {})
        e = enterprise_result["domains"].get(domain_id, {})
        comparison[domain_id] = {
            "builder_adoption": b.get("final_adoption_rate", 0.0),
            "enterprise_adoption": e.get("final_adoption_rate", 0.0),
            "builder_tipping_point": b.get("tipping_point_round"),
            "enterprise_tipping_point": e.get("tipping_point_round"),
            "adoption_gap": round(
                b.get("final_adoption_rate", 0.0) - e.get("final_adoption_rate", 0.0), 4
            ),
        }

    return {
        "builder_community": builder_result,
        "enterprise_market": enterprise_result,
        "comparison": comparison,
    }


def _apply_context(personas: list[dict[str, Any]], context: str) -> None:
    """Adjust persona traits based on simulation context."""
    if context == "enterprise_market":
        for p in personas:
            # Enterprise context: higher thresholds, lower risk
            p["adoption_threshold"] = min(1.0, p["adoption_threshold"] * 1.2)
            p["risk_tolerance"] = max(0.0, p["risk_tolerance"] * 0.8)
    # builder_community uses default traits


def _compute_awareness(
    persona: dict[str, Any],
    domain_id: str,
    signals: list[dict[str, Any]],
    current_round: int,
) -> float:
    """Compute awareness score for a persona-domain pair from active signals.

    Uses probability union (diminishing returns) instead of additive sum:
      P(aware) = 1 - product(1 - signal_i)
    This means 10 signals at 0.5 = 0.999, but 2 signals at 0.5 = 0.75.
    Prevents saturation when many signals target the same domain.
    """
    miss_probability = 1.0  # probability of NOT being reached by any signal

    for signal in signals:
        if domain_id not in signal.get("affects_domains", []):
            continue

        elapsed = current_round - signal.get("inject_at_round", 0)
        decayed = decay_signal(signal, max(0, elapsed))
        if decayed <= 0.0:
            continue

        # Shock effect modifier
        effect = signal.get("effect", "neutral")
        if effect == "negative":
            if persona["persona_type"] in signal.get("affected_persona_types", []):
                decayed *= 0.5
            else:
                decayed *= 0.3
        elif effect == "positive":
            if persona["persona_type"] in signal.get("affected_persona_types", []):
                decayed *= 1.3

        # Persona-signal affinity: expertise match boosts signal reception
        expertise = persona.get("expertise_domains", [])
        if domain_id in expertise:
            decayed = min(1.0, decayed * 1.15)

        decayed = min(1.0, decayed)
        miss_probability *= (1.0 - decayed)

    awareness = 1.0 - miss_probability
    return round(awareness, 4)


def _propagate_influence(
    personas: list[dict[str, Any]],
    domains: list[str],
    graph: DomainGraph,
) -> None:
    """Simulate influence propagation between personas.

    Uses geometric mean of influence scores to prevent large agent counts
    from overwhelming individual adoption thresholds. The influence
    represents "quality of adoption signal" not "quantity of adopters".
    """
    influence_map: dict[str, float] = {}
    for domain_id in domains:
        # Count how many personas are in each meaningful stage
        advocates = 0
        adopters = 0
        evaluators = 0
        total = len(personas)
        influence_sum = 0.0

        for persona in personas:
            stage = persona["adoption_state"].get(domain_id, "unaware")
            inf = persona_influence_score(persona, domain_id)
            if stage == "advocating":
                advocates += 1
                influence_sum += inf
            elif stage == "adopted":
                adopters += 1
                influence_sum += inf * 0.6
            elif stage == "evaluating":
                evaluators += 1
                influence_sum += inf * 0.2

        # Influence is the fraction of weighted adopters, not absolute count
        # This makes it independent of total persona count
        adoption_fraction = (advocates + adopters * 0.6 + evaluators * 0.2) / max(total, 1)
        avg_influence = influence_sum / max(advocates + adopters + evaluators, 1)
        # Combined: adoption breadth * influence quality
        influence_map[domain_id] = round(adoption_fraction * avg_influence, 4)

    # Apply aggregate influence as additional awareness
    for persona in personas:
        for domain_id in domains:
            current_stage = persona["adoption_state"].get(domain_id, "unaware")
            if current_stage in ("unaware", "aware", "interested"):
                aggregate = influence_map.get(domain_id, 0.0)
                if aggregate > persona["adoption_threshold"] * 0.8:
                    persona_evaluates_domain(persona, domain_id, aggregate)


def _adoption_snapshot(
    personas: list[dict[str, Any]], domain_id: str, round_num: int,
) -> dict[str, Any]:
    """Take a snapshot of adoption state for a domain at a given round."""
    stage_counts: dict[str, int] = {s: 0 for s in ADOPTION_STAGES}
    total = len(personas)

    for persona in personas:
        stage = persona["adoption_state"].get(domain_id, "unaware")
        if stage in stage_counts:
            stage_counts[stage] += 1

    adopted_plus = stage_counts.get("adopted", 0) + stage_counts.get("advocating", 0)
    interested_plus = adopted_plus + stage_counts.get("interested", 0) + stage_counts.get("evaluating", 0)

    return {
        "round": round_num,
        "stage_distribution": stage_counts,
        "adoption_rate": round(adopted_plus / max(total, 1), 4),
        "advocacy_rate": round(stage_counts.get("advocating", 0) / max(total, 1), 4),
        "interest_rate": round(interested_plus / max(total, 1), 4),
    }


def _compute_consensus(personas: list[dict[str, Any]], domain_id: str) -> float:
    """Compute consensus score (0-1) for a domain.

    High consensus = most personas agree on adoption stage.
    Low consensus = personas are spread across stages (disagreement).
    """
    if not personas:
        return 0.0

    stages = [p["adoption_state"].get(domain_id, "unaware") for p in personas]
    total = len(stages)
    stage_counts = {}
    for s in stages:
        stage_counts[s] = stage_counts.get(s, 0) + 1

    max_count = max(stage_counts.values())
    return round(max_count / total, 4)


def _compute_disagreement(personas: list[dict[str, Any]], domain_id: str) -> float:
    """Compute disagreement score (inverse of consensus)."""
    return round(1.0 - _compute_consensus(personas, domain_id), 4)
