"""Stakeholder persona generator.

Creates differentiated agent archetypes that simulate domain adoption dynamics.
11 customer persona types matching real Spark users: investors, entrepreneurs,
content creators, solopreneurs, AI newcomers, developers, marketers, creatives,
traders, tool makers, and opportunity hunters.
"""

from __future__ import annotations

import hashlib
from typing import Any

from .graph import DomainGraph


# 11 real customer persona types
CUSTOMER_PERSONAS: dict[str, dict[str, Any]] = {
    "investor": {
        "label": "Investor",
        "influence_score": 0.9,
        "adoption_threshold": 0.45,
        "risk_tolerance": 0.6,
        "network_reach": 0.85,
        "description": "Wants deal flow, alpha, portfolio intelligence. High influence, cautious adoption.",
        "values": ["deal_flow", "alpha", "portfolio_intelligence", "roi"],
        "pain_points": ["information_overload", "slow_due_diligence", "missed_deals"],
    },
    "entrepreneur": {
        "label": "Entrepreneur",
        "influence_score": 0.75,
        "adoption_threshold": 0.3,
        "risk_tolerance": 0.85,
        "network_reach": 0.7,
        "description": "Wants to ship products fast, validate ideas. Action-oriented.",
        "values": ["speed_to_ship", "idea_validation", "mvp_quality", "market_fit"],
        "pain_points": ["too_slow", "feature_bloat", "analysis_paralysis"],
    },
    "content_creator": {
        "label": "Content Creator",
        "influence_score": 0.8,
        "adoption_threshold": 0.25,
        "risk_tolerance": 0.7,
        "network_reach": 0.9,
        "description": "Wants audience growth, content quality, distribution. Very high reach.",
        "values": ["audience_growth", "content_quality", "distribution", "engagement"],
        "pain_points": ["writer_block", "inconsistency", "platform_algorithms"],
    },
    "solopreneur": {
        "label": "Solopreneur",
        "influence_score": 0.5,
        "adoption_threshold": 0.35,
        "risk_tolerance": 0.75,
        "network_reach": 0.4,
        "description": "Builds with limited time/capital. Values simplicity and leverage.",
        "values": ["time_leverage", "low_cost", "simplicity", "all_in_one"],
        "pain_points": ["no_team", "limited_budget", "too_complex"],
    },
    "ai_newcomer": {
        "label": "AI Newcomer",
        "influence_score": 0.3,
        "adoption_threshold": 0.2,
        "risk_tolerance": 0.5,
        "network_reach": 0.3,
        "description": "Wants to start using AI, low learning curve. Eager but inexperienced.",
        "values": ["easy_start", "low_learning_curve", "quick_wins", "outcompete"],
        "pain_points": ["overwhelmed", "dont_know_where_to_start", "fear_of_ai"],
    },
    "developer": {
        "label": "Developer",
        "influence_score": 0.7,
        "adoption_threshold": 0.4,
        "risk_tolerance": 0.65,
        "network_reach": 0.65,
        "description": "Wants better tools, code quality, productivity. Technical evaluation.",
        "values": ["code_quality", "productivity", "dx", "extensibility"],
        "pain_points": ["bad_docs", "vendor_lock_in", "over_engineering"],
    },
    "marketer": {
        "label": "Marketer",
        "influence_score": 0.65,
        "adoption_threshold": 0.3,
        "risk_tolerance": 0.6,
        "network_reach": 0.75,
        "description": "Wants campaigns, attribution, conversion. ROI-focused.",
        "values": ["campaign_roi", "attribution", "conversion", "audience_targeting"],
        "pain_points": ["cant_prove_roi", "ad_fatigue", "fragmented_data"],
    },
    "creative": {
        "label": "Creative",
        "influence_score": 0.6,
        "adoption_threshold": 0.25,
        "risk_tolerance": 0.8,
        "network_reach": 0.55,
        "description": "Wants aesthetic quality, creative control. Low threshold, high risk tolerance.",
        "values": ["aesthetic_quality", "creative_control", "uniqueness", "visual_impact"],
        "pain_points": ["ai_looks_generic", "loss_of_style", "uncanny_valley"],
    },
    "trader": {
        "label": "Trader",
        "influence_score": 0.65,
        "adoption_threshold": 0.35,
        "risk_tolerance": 0.9,
        "network_reach": 0.5,
        "description": "Wants alpha, speed, risk management. Highest risk tolerance, speed-obsessed.",
        "values": ["alpha", "speed", "risk_management", "edge"],
        "pain_points": ["slow_execution", "information_lag", "blown_stops"],
    },
    "tool_maker": {
        "label": "Tool Maker",
        "influence_score": 0.75,
        "adoption_threshold": 0.5,
        "risk_tolerance": 0.7,
        "network_reach": 0.7,
        "description": "Builds infrastructure for other builders. Evaluates carefully.",
        "values": ["infrastructure", "api_quality", "developer_adoption", "composability"],
        "pain_points": ["poor_docs", "breaking_changes", "low_adoption"],
    },
    "opportunity_hunter": {
        "label": "Opportunity Hunter",
        "influence_score": 0.55,
        "adoption_threshold": 0.15,
        "risk_tolerance": 0.95,
        "network_reach": 0.6,
        "description": "Spots trends early, acts fast. Lowest threshold, highest risk tolerance.",
        "values": ["early_access", "trend_spotting", "speed", "first_mover"],
        "pain_points": ["fomo", "too_late", "noise_vs_signal"],
    },
    # v4 personas -- 2026 macro-driven archetypes
    "displaced_worker": {
        "label": "Displaced Worker",
        "influence_score": 0.35,
        "adoption_threshold": 0.15,
        "risk_tolerance": 0.4,
        "network_reach": 0.3,
        "description": "Lost job or fears losing it to AI. Desperate to reskill. Very low threshold, low influence.",
        "values": ["reskill", "career", "easy_start", "low_learning_curve", "quick_wins", "ai_survival"],
        "pain_points": ["job_loss", "overwhelmed", "cant_afford_courses", "time_pressure"],
    },
    "corporate_innovator": {
        "label": "Corporate Innovator",
        "influence_score": 0.7,
        "adoption_threshold": 0.4,
        "risk_tolerance": 0.5,
        "network_reach": 0.75,
        "description": "Enterprise mandate to adopt AI. Needs compliance, security, ROI proof.",
        "values": ["compliance", "roi", "infrastructure", "audit", "productivity"],
        "pain_points": ["red_tape", "vendor_lock_in", "security_concerns", "budget_approval"],
    },
    "student_builder": {
        "label": "Student Builder",
        "influence_score": 0.4,
        "adoption_threshold": 0.1,
        "risk_tolerance": 0.9,
        "network_reach": 0.5,
        "description": "Gen Z, nothing to lose. Tries everything, builds fast, low commitment.",
        "values": ["easy_start", "speed_to_ship", "low_cost", "trend_spotting", "outcompete"],
        "pain_points": ["no_budget", "no_experience", "too_many_options"],
    },
    "skeptic": {
        "label": "Skeptic",
        "influence_score": 0.8,
        "adoption_threshold": 0.6,
        "risk_tolerance": 0.2,
        "network_reach": 0.7,
        "description": "Hard to convert but extremely influential when converted. Demands proof.",
        "values": ["code_quality", "infrastructure", "extensibility", "audit"],
        "pain_points": ["hype_fatigue", "broken_promises", "vendor_lock_in", "ai_looks_generic"],
    },
}

# Backwards compatibility alias
PERSONA_TYPES = CUSTOMER_PERSONAS


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
    count_per_type = max(1, count_per_type)
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
                "values": list(traits.get("values", [])),
                "pain_points": list(traits.get("pain_points", [])),
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


def _adoption_roll(
    signal: float, threshold: float,
    persona: dict[str, Any], domain_id: str, stage_idx: int,
) -> bool:
    """Probabilistic adoption decision using sigmoid curve.

    When signal == threshold: 50% chance of advancing.
    When signal >> threshold: ~100% chance.
    When signal << threshold: ~0% chance.

    Deterministic given the persona+domain+stage combination (uses hash PRNG).
    """
    steepness = 8.0
    x = (signal - threshold) * steepness
    x = max(-20.0, min(20.0, x))
    probability = 1.0 / (1.0 + 2.718281828 ** (-x))

    # Deterministic "random" roll from persona identity + domain + stage
    seed_str = f"{persona['persona_id']}:{domain_id}:{stage_idx}"
    h = hashlib.md5(seed_str.encode()).hexdigest()
    roll = (int(h[:8], 16) % 10000) / 10000.0

    return roll < probability


def persona_evaluates_domain(
    persona: dict[str, Any],
    domain_id: str,
    awareness_score: float,
    domain_tags: list[str] | None = None,
) -> str:
    """Determine a persona's adoption stage for a domain.

    Adoption funnel: unaware -> aware -> interested -> evaluating -> adopted -> advocating

    Each stage has a progressively higher threshold multiplier, so advancing
    from "evaluating" to "adopted" is much harder than "unaware" to "aware".

    The persona's values are compared against domain_tags to compute a fit
    multiplier -- domains that match what the persona cares about get a boost.

    Returns new adoption stage.
    """
    current = persona["adoption_state"].get(domain_id, "unaware")
    threshold = persona["adoption_threshold"]
    risk = persona["risk_tolerance"]
    activity = persona["activity_score"]

    # Value-based fit: how well does this domain match what this persona wants?
    fit = persona_domain_fit(persona, domain_id, domain_tags)

    effective_signal = awareness_score * activity * fit

    stages = [
        "unaware", "aware", "interested", "evaluating",
        "trial", "adopted", "committed", "advocating", "churned",
    ]
    current_idx = stages.index(current) if current in stages else 0

    # Churned is terminal -- cannot advance from it
    if current == "churned":
        return current

    # Stage difficulty -- recalibrated for 9-stage funnel
    # Trial is easy to enter (low commitment) but adopted requires proof of value
    stage_difficulty = {
        0: 0.2,    # unaware -> aware: easy, just some signal
        1: 0.45,   # aware -> interested: moderate
        2: 0.8,    # interested -> evaluating: needs real signal
        3: 1.0,    # evaluating -> trial: easier gate (low commitment tryout)
        4: 1.4,    # trial -> adopted: must prove value, harder than old gate
        5: 1.2,    # adopted -> committed: regular use becoming daily habit
        6: 1.7,    # committed -> advocating: strong conviction required
    }

    difficulty = stage_difficulty.get(current_idx, 2.5)
    # Risk discount capped at 20% to prevent easy late-stage advancement
    advance_threshold = threshold * difficulty * (1.0 - risk * 0.2)

    # Attention fatigue: once a persona has several retained domains,
    # it becomes harder to push more domains into deeper commitment.
    # Trial should not count the same as real adoption here or the
    # funnel self-chokes on exploratory behavior.
    adopted_count = sum(
        1 for s in persona["adoption_state"].values()
        if s in ("adopted", "committed", "advocating")
    )
    if adopted_count > 5 and current_idx >= 3:
        # Penalty grows with each additional adopted domain beyond 5
        advance_threshold *= 1.0 + (adopted_count - 5) * 0.15

    if current_idx < len(stages) - 1:
        if _adoption_roll(effective_signal, advance_threshold, persona, domain_id, current_idx):
            new_stage = stages[current_idx + 1]
            advanced = True
        else:
            new_stage = current
            advanced = False
    else:
        new_stage = current
        advanced = False

    # Decision driver tracking
    if "decision_log" not in persona:
        persona["decision_log"] = []
    matched_values = list(set(persona.get("values", [])) & set(domain_tags or []))
    persona["decision_log"].append({
        "domain_id": domain_id,
        "from_stage": current,
        "to_stage": new_stage,
        "advanced": advanced,
        "effective_signal": round(effective_signal, 4),
        "threshold": round(advance_threshold, 4),
        "fit_score": round(fit, 4),
        "matched_values": matched_values,
    })
    # Cap log to prevent unbounded growth
    if len(persona["decision_log"]) > 100:
        persona["decision_log"] = persona["decision_log"][-100:]

    persona["adoption_state"][domain_id] = new_stage
    return new_stage


def persona_churn_check(
    persona: dict[str, Any],
    domain_id: str,
    awareness_score: float,
    rounds_since_advance: int,
) -> str:
    """Check if a persona should regress (churn) from their current stage.

    Churn happens when:
    1. Signal has decayed significantly below what got them to this stage
    2. They've been stalled at the same stage for too long without reinforcement

    v4 design: committed/advocating are sticky (don't churn in 20 rounds).
    Trial and adopted CAN churn -- trial is low commitment, and adopted
    users who lose signal can regress to trial. Pre-commitment stages
    (aware, interested, evaluating) regress as before.

    Returns the (possibly regressed) adoption stage.
    """
    current = persona["adoption_state"].get(domain_id, "unaware")
    stages = [
        "unaware", "aware", "interested", "evaluating",
        "trial", "adopted", "committed", "advocating", "churned",
    ]
    current_idx = stages.index(current) if current in stages else 0

    # Can't regress below "unaware" or from churned/terminal
    if current_idx <= 0 or current == "churned":
        return current

    # Committed/advocating = deeply invested. Don't churn in 20-round window.
    if current in ("committed", "advocating"):
        return current

    threshold = persona["adoption_threshold"]
    risk = persona["risk_tolerance"]
    activity = persona["activity_score"]

    effective_signal = awareness_score * activity

    # Regression thresholds -- how low must signal drop to trigger regression?
    # Higher stages have more sunk cost, so regression requires more signal loss
    regression_threshold = {
        1: 0.05,   # aware -> unaware: very easy to forget
        2: 0.12,   # interested -> aware: moderate inertia
        3: 0.25,   # evaluating -> interested: invested real time, harder
        4: 0.15,   # trial -> evaluating: low commitment, easy to drop
        5: 0.35,   # adopted -> trial: significant sunk cost, hard to regress
    }

    # The signal level below which regression triggers
    regress_below = threshold * regression_threshold.get(current_idx, 0.3)

    # Sunk cost effect: risk-tolerant personas are stickier (invested emotionally)
    regress_below *= (1.0 - risk * 0.25)

    # Time decay: if stalled for many rounds, resistance to regression weakens
    if rounds_since_advance > 7:
        stall_factor = 1.0 + (rounds_since_advance - 7) * 0.06
        regress_below *= stall_factor

    if effective_signal < regress_below and current_idx > 0:
        new_stage = stages[current_idx - 1]
        persona["adoption_state"][domain_id] = new_stage
        return new_stage

    return current


def persona_retention_check(
    persona: dict[str, Any],
    domain_id: str,
    awareness_score: float,
    rounds_in_stage: int,
    domain_retention_score: float = 0.5,
) -> str:
    """Check if a trial/adopted persona should churn or regress.

    This models the "tried it, didn't stick" dynamic that churn_check
    doesn't cover. Specifically:

    - Trial users churn to "churned" (terminal) after 3+ rounds without
      reinforcement signal, scaled by domain retention_score.
    - Adopted users regress to "trial" under sustained signal loss,
      but only if domain_retention_score is low (not habitual).

    Args:
        domain_retention_score: 0-1, how habitual/sticky this domain is.
            High (>0.7) = daily habit, low (<0.3) = curiosity-driven.

    Returns the (possibly changed) adoption stage.
    """
    current = persona["adoption_state"].get(domain_id, "unaware")

    if current == "trial":
        # Trial users should churn, but not before the simulation has a fair
        # chance to observe whether curiosity turns into retained use.
        churn_window = max(4, int(5 + domain_retention_score * 5))
        if rounds_in_stage >= churn_window and awareness_score < persona["adoption_threshold"] * 0.35:
            persona["adoption_state"][domain_id] = "churned"
            return "churned"

    elif current == "adopted":
        # Adopted users can regress to trial if signal drops AND domain
        # has low retention (not a daily-use habit)
        if domain_retention_score < 0.3 and rounds_in_stage >= 7:
            if awareness_score < persona["adoption_threshold"] * 0.2:
                persona["adoption_state"][domain_id] = "trial"
                return "trial"

    return current


def persona_influence_score(persona: dict[str, Any], domain_id: str) -> float:
    """Calculate influence a persona exerts on a domain.

    Higher if: persona is adopted/advocating, has high influence, and domain is in expertise.
    """
    stage = persona["adoption_state"].get(domain_id, "unaware")
    stage_multiplier = {
        "unaware": 0.0, "aware": 0.1, "interested": 0.3,
        "evaluating": 0.5, "trial": 0.6, "adopted": 0.8,
        "committed": 0.95, "advocating": 1.0, "churned": 0.0,
    }
    mult = stage_multiplier.get(stage, 0.0)

    expertise_bonus = 1.2 if domain_id in persona.get("expertise_domains", []) else 1.0
    return round(
        persona["influence_score"] * persona["network_reach"] * mult * expertise_bonus * persona["activity_score"],
        4,
    )


def persona_learn_from_round(
    persona: dict[str, Any],
    domain_id: str,
    round_adoption_rate: float,
) -> None:
    """Persona adapts based on observed adoption outcomes.

    If a domain the persona adopted is gaining traction (high adoption rate),
    the persona becomes more confident and receptive to adjacent domains.
    If their adopted domain is stalling, they become more cautious.

    This creates a feedback loop: successful adoption breeds confidence,
    failed bets breed skepticism. Models real-world learning behavior.
    """
    stage = persona["adoption_state"].get(domain_id, "unaware")
    if stage not in ("adopted", "committed", "advocating"):
        return

    # Track learning history
    if "learning_history" not in persona:
        persona["learning_history"] = []

    # Successful adoption: domain is gaining traction
    if round_adoption_rate > 0.4:
        # Confidence boost: slightly lower adoption threshold for future domains
        persona["adoption_threshold"] = max(
            0.1, persona["adoption_threshold"] * 0.985
        )
        persona["learning_history"].append({
            "domain": domain_id, "outcome": "validated",
            "adjustment": -0.015,
        })
    elif round_adoption_rate < 0.03:
        # Cautionary: weak end-state outcomes should make personas a little
        # more selective, but not so much that exploratory trials freeze the
        # rest of the simulation.
        persona["adoption_threshold"] = min(
            0.95, persona["adoption_threshold"] * 1.005
        )
        persona["learning_history"].append({
            "domain": domain_id, "outcome": "disappointing",
            "adjustment": 0.005,
        })

    # Cap learning history to prevent unbounded growth
    if len(persona["learning_history"]) > 20:
        persona["learning_history"] = persona["learning_history"][-20:]


def _deterministic_variation(seed: int, idx: int) -> float:
    """Generate a deterministic pseudo-random variation from seed and index."""
    h = hashlib.md5(f"{seed}-{idx}".encode()).hexdigest()
    return (int(h[:8], 16) % 1000) / 1000.0


def _vary(base: float, variation: float, amplitude: float) -> float:
    """Apply bounded variation to a base value."""
    offset = (variation - 0.5) * 2.0 * amplitude
    return round(max(0.0, min(1.0, base + offset)), 4)


def persona_domain_fit(
    persona: dict[str, Any],
    domain_id: str,
    domain_tags: list[str] | None = None,
) -> float:
    """How well does this domain match this persona's values?

    Returns 0.0-1.0 fit score used as a multiplier on awareness.
    Higher fit means the persona is naturally drawn to this domain.
    """
    values = persona.get("values", [])
    tags = domain_tags or []
    if not values or not tags:
        return 0.5  # neutral if no data
    overlap = len(set(values) & set(tags))
    return min(1.0, round(0.3 + overlap * 0.2, 4))  # base 0.3, +0.2 per match, cap 1.0


def _assign_expertise(graph: DomainGraph, domains: list[str],
                      ptype: str, variant: int) -> list[str]:
    """Assign expertise domains based on persona type and graph structure."""
    # Each persona type has affinity for certain graph entity types
    type_affinity = {
        "investor": ["company", "trend"],
        "entrepreneur": ["technology", "platform", "trend"],
        "content_creator": ["platform", "community"],
        "solopreneur": ["technology", "platform"],
        "ai_newcomer": ["technology", "platform"],
        "developer": ["technology", "platform"],
        "marketer": ["platform", "community"],
        "creative": ["platform", "community"],
        "trader": ["technology", "trend"],
        "tool_maker": ["technology", "platform"],
        "opportunity_hunter": ["trend", "community"],
        "displaced_worker": ["technology", "platform"],
        "corporate_innovator": ["technology", "company"],
        "student_builder": ["technology", "platform", "trend"],
        "skeptic": ["technology", "platform"],
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
