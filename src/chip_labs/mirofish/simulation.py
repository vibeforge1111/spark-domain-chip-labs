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
    persona_churn_check, persona_learn_from_round,
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

    # Track when each persona last advanced in each domain (for churn)
    last_advance: dict[str, dict[str, int]] = {
        p["persona_id"]: {} for p in personas
    }

    # Extract domain_tags from graph node properties and signal metadata
    domain_tags: dict[str, list[str]] = {}
    for d_id in domains:
        node = graph.nodes.get(d_id, {})
        tags = list(node.get("properties", {}).get("domain_tags", []))
        domain_tags[d_id] = tags
    # Also extract tags from signal metadata
    for sig in active_signals:
        sig_tags = sig.get("metadata", {}).get("domain_tags", [])
        if sig_tags:
            for d_id in sig.get("affects_domains", []):
                existing = set(domain_tags.get(d_id, []))
                existing.update(sig_tags)
                domain_tags[d_id] = list(existing)

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
                prev_stage = persona["adoption_state"].get(domain_id, "unaware")
                d_tags = domain_tags.get(domain_id, [])
                if in_budget:
                    new_stage = persona_evaluates_domain(persona, domain_id, awareness, d_tags)
                    if domain_id not in active_domains:
                        evaluated += 1
                else:
                    # Below attention budget -- only allow unaware->aware (discovery)
                    # with heavily dampened signal
                    if prev_stage == "unaware" and awareness > 0.5:
                        new_stage = persona_evaluates_domain(persona, domain_id, awareness * 0.3, d_tags)
                    else:
                        new_stage = prev_stage

                # Track when persona last advanced
                pid = persona["persona_id"]
                if new_stage != prev_stage:
                    last_advance[pid][domain_id] = round_num

        # Phase 1b: Churn check -- personas can regress if signal fades
        # Recompute awareness per persona (domain_awareness above was scoped
        # to the last persona in the Phase 1 loop).
        for persona in personas:
            pid = persona["persona_id"]
            for domain_id in domains:
                current_stage = persona["adoption_state"].get(domain_id, "unaware")
                if current_stage == "unaware":
                    continue
                awareness = _compute_awareness(
                    persona, domain_id, active_signals, round_num,
                )
                last_adv_round = last_advance[pid].get(domain_id, 0)
                rounds_since = round_num - last_adv_round
                persona_churn_check(persona, domain_id, awareness, rounds_since)

        # Phase 2: Influence propagation -- personas influence each other
        _propagate_influence(personas, domains, graph, domain_tags)

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

        # Phase 4: Persona learning -- personas adapt based on outcomes
        for persona in personas:
            for domain_id in domains:
                snapshot = adoption_curves[domain_id][-1]
                persona_learn_from_round(
                    persona, domain_id, snapshot["adoption_rate"],
                )

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
            "adoption_by_persona_type": _adoption_snapshot_by_type(personas, domain_id),
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
    domain_tags: dict[str, list[str]] | None = None,
) -> None:
    """Simulate influence propagation between personas.

    Uses geometric mean of influence scores to prevent large agent counts
    from overwhelming individual adoption thresholds. The influence
    represents "quality of adoption signal" not "quantity of adopters".

    Graph topology effects:
    - ENABLES edges propagate positive influence (domain A adoption boosts B)
    - EXTENDS edges propagate stronger positive influence (proven ecosystem)
    - COMPETES_WITH edges propagate negative influence (competitive displacement)
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

    # Phase 2b: Graph topology propagation
    # Influence flows along graph edges between domains
    topology_bonus: dict[str, float] = {d: 0.0 for d in domains}
    topology_penalty: dict[str, float] = {d: 0.0 for d in domains}

    for domain_id in domains:
        if domain_id not in graph.nodes:
            continue
        edges = graph.get_edges_for(domain_id)
        for edge in edges:
            other = edge["target"] if edge["source"] == domain_id else edge["source"]
            if other not in influence_map:
                continue

            rel = edge.get("relationship", "")
            weight = edge.get("weight", 0.5)
            neighbor_influence = influence_map.get(other, 0.0)

            if rel == "ENABLES":
                # Synergistic: adoption of enabler boosts this domain
                topology_bonus[domain_id] += neighbor_influence * weight * 0.3
            elif rel == "EXTENDS":
                # Proven ecosystem: stronger boost
                topology_bonus[domain_id] += neighbor_influence * weight * 0.4
            elif rel == "COMPETES_WITH":
                # Competitive displacement: competitor adoption hurts this domain
                topology_penalty[domain_id] += neighbor_influence * weight * 0.5

    # Apply aggregate influence + topology as additional awareness
    for persona in personas:
        for domain_id in domains:
            current_stage = persona["adoption_state"].get(domain_id, "unaware")
            if current_stage in ("unaware", "aware", "interested"):
                base = influence_map.get(domain_id, 0.0)
                bonus = topology_bonus.get(domain_id, 0.0)
                penalty = topology_penalty.get(domain_id, 0.0)
                aggregate = max(0.0, base + bonus - penalty)
                if aggregate > persona["adoption_threshold"] * 0.8:
                    d_tags = (domain_tags or {}).get(domain_id, [])
                    persona_evaluates_domain(persona, domain_id, aggregate, d_tags)

        # Competitive displacement: if persona adopted domain A and A
        # COMPETES_WITH domain B, raise B's effective threshold for this
        # persona (they already picked a winner in that space).
        _apply_competitive_displacement(persona, domains, graph)


def _apply_competitive_displacement(
    persona: dict[str, Any],
    domains: list[str],
    graph: DomainGraph,
) -> None:
    """If persona adopted domain A and A COMPETES_WITH B, regress B.

    Models the "I already picked a winner" effect. Once you've committed
    to one competing domain, the rival loses mindshare. Only triggers
    from adopted/advocating stages (real commitment, not just interest).

    Displacement is gentle — drops one stage at most — because personas
    can rationally use competing products (just less likely to champion both).
    """
    stages = ["unaware", "aware", "interested", "evaluating", "adopted", "advocating"]

    # Collect domains this persona has strongly committed to
    committed = {
        d_id for d_id, stage in persona["adoption_state"].items()
        if stage in ("adopted", "advocating")
    }
    if not committed:
        return

    for adopted_domain in committed:
        if adopted_domain not in graph.nodes:
            continue
        edges = graph.get_edges_for(adopted_domain)
        for edge in edges:
            if edge.get("relationship") != "COMPETES_WITH":
                continue
            competitor = edge["target"] if edge["source"] == adopted_domain else edge["source"]
            if competitor not in persona["adoption_state"]:
                continue

            comp_stage = persona["adoption_state"][competitor]
            comp_idx = stages.index(comp_stage) if comp_stage in stages else 0

            # Only displace if competitor is in early-mid funnel
            # Don't displace already-adopted (sunk cost too high)
            if comp_idx in (1, 2, 3):  # aware, interested, evaluating
                weight = edge.get("weight", 0.5)
                # Stronger competition = more displacement
                if weight > 0.7:
                    persona["adoption_state"][competitor] = stages[comp_idx - 1]


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


def _adoption_snapshot_by_type(
    personas: list[dict[str, Any]], domain_id: str,
) -> dict[str, dict[str, Any]]:
    """Per-persona-type adoption breakdown for a domain.

    Returns a dict keyed by persona type, each containing:
    - adoption_rate: fraction of this type that adopted/advocating
    - advocacy_rate: fraction that reached advocating
    - count: number of personas of this type
    - stage_distribution: count per stage for this type
    """
    by_type: dict[str, list[str]] = {}
    for p in personas:
        ptype = p["persona_type"]
        stage = p["adoption_state"].get(domain_id, "unaware")
        by_type.setdefault(ptype, []).append(stage)

    result: dict[str, dict[str, Any]] = {}
    for ptype, stages in by_type.items():
        total = len(stages)
        adopted = sum(1 for s in stages if s in ("adopted", "advocating"))
        advocates = sum(1 for s in stages if s == "advocating")
        result[ptype] = {
            "adoption_rate": round(adopted / max(total, 1), 4),
            "advocacy_rate": round(advocates / max(total, 1), 4),
            "count": total,
            "stage_distribution": {s: stages.count(s) for s in set(stages)},
        }
    return result


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


# ---------------------------------------------------------------------------
# Monte Carlo Ensemble
# ---------------------------------------------------------------------------

def run_ensemble(
    graph: DomainGraph,
    domain_ids: list[str] | None = None,
    signals: list[dict[str, Any]] | None = None,
    shocks: list[dict[str, Any]] | None = None,
    max_rounds: int = MAX_ROUNDS,
    n_runs: int = 50,
    base_seed: int = 42,
    context: str = "builder_community",
    count_per_type: int = 125,
) -> dict[str, Any]:
    """Run Monte Carlo ensemble of N simulations with different seeds.

    Each run uses a different seed for persona generation, producing
    different trait variations and expertise assignments. The signals
    and shocks remain the same across runs (they're the scenario).

    Returns per-domain statistics: median, mean, p10, p90, std, plus
    the full distribution of adoption rates across runs.

    Args:
        graph: Domain knowledge graph.
        domain_ids: Domains to simulate.
        signals: Signals to inject (same across all runs).
        shocks: Shocks to inject (same across all runs).
        max_rounds: Rounds per simulation.
        n_runs: Number of Monte Carlo runs (default 50).
        base_seed: Starting seed (incremented per run).
        context: Simulation context.
        count_per_type: Personas per type per run.
    """
    domains = domain_ids or [
        n["id"] for n in graph.nodes.values() if n["type"] == "domain"
    ]

    # Collect adoption rates across runs
    adoption_runs: dict[str, list[float]] = {d: [] for d in domains}
    advocacy_runs: dict[str, list[float]] = {d: [] for d in domains}
    tipping_runs: dict[str, list[int | None]] = {d: [] for d in domains}

    for run_idx in range(n_runs):
        seed = base_seed + run_idx
        personas = generate_personas(graph, domains, count_per_type=count_per_type, seed=seed)

        result = run_simulation(
            graph, domains, personas=personas,
            signals=signals, shocks=shocks,
            max_rounds=max_rounds, seed=seed, context=context,
        )

        for d_id in domains:
            d_result = result["domains"].get(d_id, {})
            adoption_runs[d_id].append(d_result.get("final_adoption_rate", 0.0))
            advocacy_runs[d_id].append(d_result.get("final_advocacy_rate", 0.0))
            tipping_runs[d_id].append(d_result.get("tipping_point_round"))

    # Compute statistics
    ensemble_results: dict[str, Any] = {
        "context": context,
        "n_runs": n_runs,
        "max_rounds": max_rounds,
        "base_seed": base_seed,
        "domains": {},
    }

    for d_id in domains:
        rates = sorted(adoption_runs[d_id])
        adv_rates = sorted(advocacy_runs[d_id])
        tips = [t for t in tipping_runs[d_id] if t is not None]

        n = len(rates)
        p10_idx = max(0, int(n * 0.1))
        p90_idx = min(n - 1, int(n * 0.9))
        median_idx = n // 2

        mean_rate = sum(rates) / n if n > 0 else 0.0
        mean_adv = sum(adv_rates) / n if n > 0 else 0.0
        variance = sum((r - mean_rate) ** 2 for r in rates) / n if n > 0 else 0.0
        std = variance ** 0.5

        ensemble_results["domains"][d_id] = {
            "mean_adoption": round(mean_rate, 4),
            "median_adoption": round(rates[median_idx], 4) if n > 0 else 0.0,
            "p10_adoption": round(rates[p10_idx], 4) if n > 0 else 0.0,
            "p90_adoption": round(rates[p90_idx], 4) if n > 0 else 0.0,
            "std_adoption": round(std, 4),
            "mean_advocacy": round(mean_adv, 4),
            "tipping_rate": round(len(tips) / n, 4) if n > 0 else 0.0,
            "mean_tipping_round": round(sum(tips) / len(tips), 1) if tips else None,
            "distribution": rates,
            "confidence_width": round(rates[p90_idx] - rates[p10_idx], 4) if n > 0 else 0.0,
        }

    return ensemble_results


# ---------------------------------------------------------------------------
# Sensitivity Analysis
# ---------------------------------------------------------------------------

def run_sensitivity(
    graph: DomainGraph,
    domain_ids: list[str] | None = None,
    signals: list[dict[str, Any]] | None = None,
    shocks: list[dict[str, Any]] | None = None,
    max_rounds: int = MAX_ROUNDS,
    seed: int = 42,
    context: str = "builder_community",
    count_per_type: int = 2,
) -> dict[str, Any]:
    """Run sensitivity analysis by varying key parameters one at a time.

    Tests how sensitive adoption outcomes are to changes in:
    - Signal strength (0.5x, 1.0x, 1.5x, 2.0x)
    - Adoption thresholds (0.5x, 1.0x, 1.5x)
    - Number of personas per type (1, 2, 4)
    - Shock timing (early, baseline, late)

    For each parameter variation, runs the simulation and records
    the resulting adoption rates. The delta from baseline shows
    which factors have the most influence on predictions.

    Returns per-domain sensitivity data with factor importance ranking.
    """
    domains = domain_ids or [
        n["id"] for n in graph.nodes.values() if n["type"] == "domain"
    ]

    # Baseline run
    baseline = run_simulation(
        graph, domains, signals=signals, shocks=shocks,
        max_rounds=max_rounds, seed=seed, context=context,
    )
    baseline_rates = {
        d: baseline["domains"][d]["final_adoption_rate"] for d in domains
    }

    variations: dict[str, list[dict[str, Any]]] = {}

    # 1. Signal strength sensitivity
    strength_multipliers = [0.5, 1.0, 1.5, 2.0]
    strength_results = []
    for mult in strength_multipliers:
        varied_signals = None
        if signals:
            varied_signals = []
            for s in signals:
                vs = dict(s)
                vs["strength"] = min(1.0, s.get("strength", 0.5) * mult)
                varied_signals.append(vs)
        result = run_simulation(
            graph, domains, signals=varied_signals, shocks=shocks,
            max_rounds=max_rounds, seed=seed, context=context,
        )
        rates = {d: result["domains"][d]["final_adoption_rate"] for d in domains}
        strength_results.append({"multiplier": mult, "rates": rates})
    variations["signal_strength"] = strength_results

    # 2. Adoption threshold sensitivity
    threshold_multipliers = [0.5, 1.0, 1.5]
    threshold_results = []
    for mult in threshold_multipliers:
        personas = generate_personas(graph, domains, count_per_type=count_per_type, seed=seed)
        for p in personas:
            p["adoption_threshold"] = min(1.0, p["adoption_threshold"] * mult)
        result = run_simulation(
            graph, domains, personas=personas, signals=signals, shocks=shocks,
            max_rounds=max_rounds, seed=seed, context=context,
        )
        rates = {d: result["domains"][d]["final_adoption_rate"] for d in domains}
        threshold_results.append({"multiplier": mult, "rates": rates})
    variations["adoption_threshold"] = threshold_results

    # 3. Persona count sensitivity
    count_variations = [1, 2, 4]
    count_results = []
    for cnt in count_variations:
        personas = generate_personas(graph, domains, count_per_type=cnt, seed=seed)
        result = run_simulation(
            graph, domains, personas=personas, signals=signals, shocks=shocks,
            max_rounds=max_rounds, seed=seed, context=context,
        )
        rates = {d: result["domains"][d]["final_adoption_rate"] for d in domains}
        count_results.append({"count_per_type": cnt, "rates": rates})
    variations["persona_count"] = count_results

    # 4. Shock timing sensitivity
    if shocks:
        timing_offsets = {"early": -3, "baseline": 0, "late": 3}
        timing_results = []
        for label, offset in timing_offsets.items():
            shifted = []
            for s in shocks:
                ss = dict(s)
                ss["inject_at_round"] = max(0, s.get("inject_at_round", 0) + offset)
                shifted.append(ss)
            result = run_simulation(
                graph, domains, signals=signals, shocks=shifted,
                max_rounds=max_rounds, seed=seed, context=context,
            )
            rates = {d: result["domains"][d]["final_adoption_rate"] for d in domains}
            timing_results.append({"timing": label, "offset": offset, "rates": rates})
        variations["shock_timing"] = timing_results

    # Compute factor importance per domain
    factor_importance: dict[str, dict[str, float]] = {}
    for domain_id in domains:
        base = baseline_rates[domain_id]
        importance: dict[str, float] = {}

        for factor_name, results in variations.items():
            max_delta = 0.0
            for entry in results:
                rate = entry["rates"].get(domain_id, 0.0)
                delta = abs(rate - base)
                max_delta = max(max_delta, delta)
            importance[factor_name] = round(max_delta, 4)

        factor_importance[domain_id] = importance

    return {
        "baseline_rates": baseline_rates,
        "variations": variations,
        "factor_importance": factor_importance,
        "most_sensitive_factor": _most_sensitive_factor(factor_importance, domains),
    }


def _most_sensitive_factor(
    factor_importance: dict[str, dict[str, float]],
    domains: list[str],
) -> dict[str, str]:
    """Find the most sensitive factor per domain."""
    result: dict[str, str] = {}
    for domain_id in domains:
        importance = factor_importance.get(domain_id, {})
        if importance:
            result[domain_id] = max(importance, key=importance.get)
        else:
            result[domain_id] = "none"
    return result
