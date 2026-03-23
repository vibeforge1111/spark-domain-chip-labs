"""Hybrid discovery-to-evaluation bridge for MiroFish.

Turns canonicalized discovery packets into conservative opportunity specs
that can feed the existing MiroFish graph, signal, and simulation layers.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from ..trend_scanner import SEED_OPPORTUNITIES, rank_opportunities, score_opportunity
from .graph import build_graph_from_opportunities
from .report import generate_prediction_report
from .signals import build_scenario, create_shock, signals_from_graph, signals_from_opportunities
from .simulation import run_dual_context, run_ensemble


DEFAULT_BENCHMARK_IDS = [
    "trading-crypto",
    "startup-yc",
    "cursor-copilot",
    "mcp-server-builder",
    "ai-agent-builder",
]

_FIT_KEYWORDS = {
    "ai", "agent", "agents", "developer", "developers", "mcp",
    "creator", "content", "startup", "founder", "trading", "crypto",
    "ops", "workflow", "copilot", "automation",
}
_DATA_RICH_SOURCES = {"github", "arxiv", "producthunt", "vc_landscape"}
_DEMAND_HEAVY_SOURCES = {"community", "x_twitter", "live_twitter", "producthunt", "spark_ecosystem"}
_MONETIZATION_KEYWORDS = {
    "revenue", "operator", "sales", "trading", "compliance", "legal",
    "workflow", "automation", "founder", "startup", "copilot",
}

_EXTRA_BENCHMARK_PRIORS: list[dict[str, Any]] = [
    {
        "domain_id": "trading-crypto",
        "label": "Crypto Trading Intelligence",
        "description": "Crypto strategy evaluation, execution discipline, and market-adaptive trading workflows.",
        "scores": {
            "market_size": 0.92,
            "data_availability": 0.94,
            "benchmark_feasibility": 0.90,
            "community_demand": 0.88,
            "spark_ecosystem_fit": 0.78,
            "monetization_potential": 0.91,
        },
        "rationale": "Existing mature benchmark chip with clear strategy loops and durable market signal.",
        "related_chips": ["defi-architect"],
        "evidence_sources": ["github", "community", "x_twitter"],
        "benchmark_tier": "leadership",
    },
    {
        "domain_id": "startup-yc",
        "label": "Startup YC Intelligence",
        "description": "Founder decision support around startup formation, validation, growth, and fundraising.",
        "scores": {
            "market_size": 0.86,
            "data_availability": 0.78,
            "benchmark_feasibility": 0.74,
            "community_demand": 0.87,
            "spark_ecosystem_fit": 0.84,
            "monetization_potential": 0.89,
        },
        "rationale": "Existing benchmark chip for startup specialization and repeated founder workflow mastery.",
        "related_chips": ["indie-hacker", "agentic-marketing"],
        "evidence_sources": ["community", "producthunt", "x_twitter"],
        "benchmark_tier": "leadership",
    },
    {
        "domain_id": "cursor-copilot",
        "label": "AI Coding Workflow",
        "description": "Prompt-to-code workflow acceleration, codebase navigation, and developer throughput improvement.",
        "scores": {
            "market_size": 0.87,
            "data_availability": 0.90,
            "benchmark_feasibility": 0.84,
            "community_demand": 0.85,
            "spark_ecosystem_fit": 0.93,
            "monetization_potential": 0.80,
        },
        "rationale": "Strong developer workflow benchmark with clear tooling demand and visible ecosystem pull.",
        "related_chips": ["mcp-server-builder", "ai-agent-builder"],
        "evidence_sources": ["github", "producthunt", "community"],
        "benchmark_tier": "midfield",
    },
    {
        "domain_id": "mcp-server-builder",
        "label": "MCP Server Development",
        "description": "MCP server scaffolding, packaging, testing, and integration workflows for developers.",
        "scores": {
            "market_size": 0.83,
            "data_availability": 0.89,
            "benchmark_feasibility": 0.85,
            "community_demand": 0.82,
            "spark_ecosystem_fit": 0.95,
            "monetization_potential": 0.76,
        },
        "rationale": "High-fit benchmark for protocol-native developer tooling in the current ecosystem.",
        "related_chips": ["cursor-copilot", "ai-agent-builder"],
        "evidence_sources": ["github", "community"],
        "benchmark_tier": "midfield",
    },
]


def benchmark_library() -> dict[str, dict[str, Any]]:
    """Return the benchmark opportunity library keyed by domain_id."""
    library: dict[str, dict[str, Any]] = {}
    for opportunity in rank_opportunities(SEED_OPPORTUNITIES):
        enriched = deepcopy(opportunity)
        enriched["benchmark_tier"] = "seed_panel"
        enriched["origin"] = "benchmark_panel"
        library[enriched["domain_id"]] = enriched
    for opportunity in _EXTRA_BENCHMARK_PRIORS:
        enriched = deepcopy(opportunity)
        enriched["composite_score"] = score_opportunity(enriched)
        enriched["origin"] = "benchmark_panel"
        library[enriched["domain_id"]] = enriched
    return library


def build_hybrid_evaluation_spec(
    packet: dict[str, Any],
    benchmark_ids: list[str] | None = None,
    promoted_domain_ids: list[str] | None = None,
    proposed_benchmark_domain_ids: list[str] | None = None,
    max_rounds: int = 20,
    flagship_count_per_type: int = 30,
    ensemble_runs: int = 15,
    ensemble_count_per_type: int = 15,
    scenario_label: str = "mirofish-hybrid-discovery",
) -> dict[str, Any]:
    """Build a simulation-ready hybrid evaluation spec from a discovery packet."""
    accepted_candidates = list(packet.get("accepted_candidates", []))
    if not accepted_candidates:
        return {
            "packet_kind": "mirofish_hybrid_evaluation_spec",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source_batch_id": packet.get("batch_id"),
            "error": "No accepted discovery candidates were available to build a hybrid evaluation spec.",
        }

    proposed_ids = {domain_id for domain_id in (proposed_benchmark_domain_ids or []) if domain_id}
    promoted_ids = {
        domain_id
        for domain_id in (promoted_domain_ids or [])
        if domain_id and domain_id not in proposed_ids
    }
    discovered: list[dict[str, Any]] = []
    promoted: list[dict[str, Any]] = []
    proposed: list[dict[str, Any]] = []
    for candidate in accepted_candidates:
        opportunity = discovery_candidate_to_opportunity(candidate)
        if opportunity["domain_id"] in proposed_ids:
            proposed.append(_as_proposed_benchmark(opportunity))
        elif opportunity["domain_id"] in promoted_ids:
            promoted.append(_as_review_benchmark(opportunity))
        else:
            discovered.append(opportunity)

    benchmarks = select_benchmark_panel(benchmark_ids) + proposed + promoted

    combined_map: dict[str, dict[str, Any]] = {}
    for opportunity in benchmarks + discovered:
        combined_map[opportunity["domain_id"]] = deepcopy(opportunity)
    combined = list(combined_map.values())
    ranked = rank_opportunities(combined)

    graph = build_graph_from_opportunities(ranked)
    signals = signals_from_opportunities(ranked) + signals_from_graph(graph)
    scenario = recommended_hybrid_scenario(discovered, ranked, label=scenario_label)

    persona_types = 15
    return {
        "packet_kind": "mirofish_hybrid_evaluation_spec",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_batch_id": packet.get("batch_id"),
        "source_packet_kind": packet.get("packet_kind"),
        "evidence_lane": "exploratory_frontier",
        "discovered_domain_ids": [item["domain_id"] for item in discovered],
        "proposed_benchmark_domain_ids": [item["domain_id"] for item in proposed],
        "promotion_review_domain_ids": [item["domain_id"] for item in promoted],
        "benchmark_domain_ids": [item["domain_id"] for item in benchmarks],
        "harness": {
            "max_rounds": max_rounds,
            "flagship_count_per_type": flagship_count_per_type,
            "flagship_agent_count": flagship_count_per_type * persona_types,
            "ensemble_runs": ensemble_runs,
            "ensemble_count_per_type": ensemble_count_per_type,
            "ensemble_agent_count": ensemble_count_per_type * persona_types,
            "persona_types": persona_types,
            "read_order": [
                "agent_choice_signal",
                "peak_interest_probability",
                "final_adoption_rate",
            ],
        },
        "benchmark_panel": benchmarks,
        "discovered_opportunities": discovered,
        "proposed_benchmark_opportunities": proposed,
        "promotion_review_opportunities": promoted,
        "static_rankings": ranked,
        "simulation_inputs": {
            "domain_ids": [item["domain_id"] for item in ranked],
            "opportunities": ranked,
            "signals": signals,
            "scenario": scenario,
            "graph": graph.to_dict(),
        },
        "summary": {
            "discovered_count": len(discovered),
            "benchmark_count": len(benchmarks),
            "proposed_benchmark_count": len(proposed),
            "promotion_review_count": len(promoted),
            "combined_domain_count": len(ranked),
            "signal_count": len(signals),
            "shock_count": len(scenario.get("shocks", [])),
            "top_ranked_domain": ranked[0]["domain_id"] if ranked else None,
        },
        "governance_note": (
            "Discovered candidates use conservative inferred priors. "
            "Hybrid specs are exploratory_frontier and must not auto-promote benchmark membership, "
            "including proposed benchmark members and promotion-review candidates."
        ),
    }


def run_hybrid_evaluation(spec: dict[str, Any], seed: int = 42) -> dict[str, Any]:
    """Run the hybrid evaluation spec through MiroFish and return a compact artifact."""
    simulation_inputs = spec.get("simulation_inputs", {})
    opportunities = list(simulation_inputs.get("opportunities", []))
    domain_ids = list(simulation_inputs.get("domain_ids", []))
    signals = list(simulation_inputs.get("signals", []))
    scenario = simulation_inputs.get("scenario", {})
    shocks = list(scenario.get("shocks", []))
    harness = spec.get("harness", {})

    graph = build_graph_from_opportunities(opportunities)

    dual = run_dual_context(
        graph,
        domain_ids=domain_ids,
        signals=signals,
        shocks=shocks,
        max_rounds=int(harness.get("max_rounds", 20)),
        seed=seed,
    )
    report = generate_prediction_report(dual, static_rankings=spec.get("static_rankings"))

    ensemble = run_ensemble(
        graph,
        domain_ids=domain_ids,
        signals=signals,
        shocks=shocks,
        max_rounds=int(harness.get("max_rounds", 20)),
        n_runs=int(harness.get("ensemble_runs", 15)),
        base_seed=seed,
        context="builder_community",
        count_per_type=int(harness.get("ensemble_count_per_type", 15)),
    )

    return {
        "packet_kind": "mirofish_hybrid_evaluation_run",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_batch_id": spec.get("source_batch_id"),
        "source_spec_created_at": spec.get("created_at"),
        "evidence_lane": "exploratory_frontier",
        "seed": seed,
        "harness": harness,
        "scenario": scenario,
        "discovered_domain_ids": spec.get("discovered_domain_ids", []),
        "proposed_benchmark_domain_ids": spec.get("proposed_benchmark_domain_ids", []),
        "promotion_review_domain_ids": spec.get("promotion_review_domain_ids", []),
        "benchmark_domain_ids": spec.get("benchmark_domain_ids", []),
        "top_line": _top_line_summary(report, ensemble),
        "domain_predictions": report.get("domain_predictions", []),
        "cross_domain": report.get("cross_domain", {}),
        "builder_ensemble_summary": _compact_ensemble_summary(ensemble),
        "governance_note": (
            "Hybrid evaluation output remains exploratory_frontier. "
            "Use it to compare discovered candidates against the benchmark panel, not to auto-promote them."
        ),
    }


def build_promotion_brief(
    run_packet: dict[str, Any],
    candidate_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Build a promotion-review brief from a saved hybrid run packet."""
    discovered_ids = list(run_packet.get("discovered_domain_ids", []))
    benchmark_ids = list(run_packet.get("benchmark_domain_ids", []))
    selected_ids = candidate_ids or discovered_ids

    prediction_map = {
        item.get("domain_id"): item
        for item in run_packet.get("domain_predictions", [])
        if item.get("domain_id")
    }
    ensemble_map = {
        item.get("domain_id"): item
        for item in run_packet.get("builder_ensemble_summary", [])
        if item.get("domain_id")
    }

    benchmark_rows = [
        _merged_domain_metrics(domain_id, prediction_map, ensemble_map)
        for domain_id in benchmark_ids
        if domain_id in prediction_map or domain_id in ensemble_map
    ]
    benchmark_mean_values = [row.get("mean_adoption", 0.0) for row in benchmark_rows]
    benchmark_floor = _median(benchmark_mean_values)

    candidate_rows: list[dict[str, Any]] = []
    for domain_id in selected_ids:
        merged = _merged_domain_metrics(domain_id, prediction_map, ensemble_map)
        if not merged:
            continue
        mean_adoption = merged.get("mean_adoption", 0.0)
        benchmark_wins = [
            row["domain_id"]
            for row in benchmark_rows
            if mean_adoption > row.get("mean_adoption", 0.0)
        ]
        readiness_score = round(
            mean_adoption * 0.4
            + merged.get("agent_choice_signal", 0.0) * 0.25
            + merged.get("peak_interest_probability", 0.0) * 0.1
            + merged.get("adoption_probability", 0.0) * 0.1
            + merged.get("consensus_score", 0.0) * 0.1
            + (len(benchmark_wins) / max(1, len(benchmark_rows))) * 0.05,
            4,
        )
        candidate_rows.append({
            **merged,
            "benchmark_wins": benchmark_wins,
            "benchmark_win_count": len(benchmark_wins),
            "benchmark_loss_count": max(0, len(benchmark_rows) - len(benchmark_wins)),
            "benchmark_floor_gap": round(mean_adoption - benchmark_floor, 4),
            "promotion_readiness_score": readiness_score,
        })

    candidate_rows.sort(
        key=lambda item: (
            item.get("promotion_readiness_score", 0.0),
            item.get("mean_adoption", 0.0),
            item.get("agent_choice_signal", 0.0),
        ),
        reverse=True,
    )

    for index, row in enumerate(candidate_rows, start=1):
        row["rank"] = index
        row["promotion_recommendation"] = _promotion_recommendation(row, benchmark_floor)
        row["promotion_rationale"] = _promotion_rationale(row, benchmark_floor)

    top_candidate = candidate_rows[0] if candidate_rows else {}
    return {
        "packet_kind": "mirofish_promotion_brief",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_batch_id": run_packet.get("source_batch_id"),
        "source_run_created_at": run_packet.get("created_at"),
        "evidence_lane": "exploratory_frontier",
        "candidate_domain_ids": [row["domain_id"] for row in candidate_rows],
        "benchmark_domain_ids": benchmark_ids,
        "benchmark_summary": {
            "benchmark_count": len(benchmark_rows),
            "mean_benchmark_ensemble_adoption": round(_mean(benchmark_mean_values), 4),
            "median_benchmark_ensemble_adoption": round(benchmark_floor, 4),
            "max_benchmark_ensemble_adoption": round(max(benchmark_mean_values or [0.0]), 4),
        },
        "promotion_table": candidate_rows,
        "recommendation": {
            "domain_id": top_candidate.get("domain_id"),
            "action": (
                "promote_for_human_review"
                if top_candidate and top_candidate.get("promotion_recommendation") == "review_now"
                else "hold_in_frontier"
            ),
            "reason": _promotion_decision_reason(top_candidate, benchmark_floor),
        },
        "governance_note": (
            "Promotion briefs recommend candidates for human review only. "
            "They do not modify benchmark membership or auto-promote any domain."
        ),
    }


def discovery_candidate_to_opportunity(candidate: dict[str, Any]) -> dict[str, Any]:
    """Convert a canonical discovery candidate into a conservative MiroFish opportunity."""
    scores = infer_discovery_scores(candidate)
    return {
        "domain_id": candidate["domain_id"],
        "label": candidate["label"],
        "description": candidate.get("description", ""),
        "scores": scores,
        "composite_score": score_opportunity({"scores": scores}),
        "rationale": candidate.get("evidence_summary") or candidate.get("raw_observation", ""),
        "related_chips": list(candidate.get("adjacent_domains", [])),
        "evidence_sources": list(candidate.get("evidence_sources", [])),
        "origin": "discovered_candidate",
        "classification": candidate.get("classification"),
        "confidence_read": candidate.get("confidence_read", "low"),
        "benchmark_tier": "new_candidate",
        "candidate_context": {
            "specialization_surface": candidate.get("specialization_surface", ""),
            "mastery_surface": candidate.get("mastery_surface", ""),
            "user_value_loop": candidate.get("user_value_loop", ""),
            "domain_tags": list(candidate.get("domain_tags", [])),
            "promotion_status": candidate.get("promotion_status", "candidate"),
        },
    }


def _as_review_benchmark(opportunity: dict[str, Any]) -> dict[str, Any]:
    review_candidate = deepcopy(opportunity)
    review_candidate["origin"] = "promotion_review_candidate"
    review_candidate["benchmark_tier"] = "review_candidate"
    candidate_context = deepcopy(review_candidate.get("candidate_context", {}))
    candidate_context["promotion_status"] = "benchmark_review"
    review_candidate["candidate_context"] = candidate_context
    return review_candidate


def _as_proposed_benchmark(opportunity: dict[str, Any]) -> dict[str, Any]:
    proposed_candidate = deepcopy(opportunity)
    proposed_candidate["origin"] = "proposed_benchmark_candidate"
    proposed_candidate["benchmark_tier"] = "proposed_benchmark"
    candidate_context = deepcopy(proposed_candidate.get("candidate_context", {}))
    candidate_context["promotion_status"] = "maintained_benchmark_proposal"
    proposed_candidate["candidate_context"] = candidate_context
    return proposed_candidate


def infer_discovery_scores(candidate: dict[str, Any]) -> dict[str, float]:
    """Infer conservative static scores from discovery-only evidence."""
    text = " ".join([
        candidate.get("label", ""),
        candidate.get("description", ""),
        candidate.get("specialization_surface", ""),
        candidate.get("mastery_surface", ""),
        candidate.get("user_value_loop", ""),
        candidate.get("evidence_summary", ""),
    ]).lower()
    tags = [str(tag).lower() for tag in candidate.get("domain_tags", [])]
    sources = [str(source).lower() for source in candidate.get("evidence_sources", [])]
    adjacent_domains = [str(item).strip() for item in candidate.get("adjacent_domains", []) if str(item).strip()]
    confidence = str(candidate.get("confidence_read", "low")).lower()
    confidence_bonus = {"low": 0.0, "medium": 0.08, "high": 0.16}.get(confidence, 0.0)

    data_rich = sum(1 for source in sources if source in _DATA_RICH_SOURCES)
    demand_heavy = sum(1 for source in sources if source in _DEMAND_HEAVY_SOURCES)
    fit_keywords = sum(1 for token in _FIT_KEYWORDS if token in text or token in tags)
    monetization_keywords = sum(1 for token in _MONETIZATION_KEYWORDS if token in text or token in tags)

    has_specialization = bool(candidate.get("specialization_surface"))
    has_mastery = bool(candidate.get("mastery_surface"))
    has_value_loop = bool(candidate.get("user_value_loop"))
    has_evidence = bool(candidate.get("evidence_summary"))

    market_size = _clamp(0.42 + len(tags) * 0.05 + len(sources) * 0.04 + confidence_bonus * 0.6)
    data_availability = _clamp(0.34 + data_rich * 0.16 + len(sources) * 0.04 + len(adjacent_domains) * 0.02)
    benchmark_feasibility = _clamp(
        0.32 + (0.12 if has_value_loop else 0.0) + (0.10 if has_mastery else 0.0)
        + data_rich * 0.08 + len(adjacent_domains) * 0.03
    )
    community_demand = _clamp(
        0.34 + demand_heavy * 0.12 + (0.08 if has_evidence else 0.0)
        + len(tags) * 0.03 + confidence_bonus
    )
    spark_ecosystem_fit = _clamp(
        0.28 + min(fit_keywords, 4) * 0.08 + len(adjacent_domains) * 0.05
        + (0.08 if has_specialization else 0.0)
    )
    monetization_potential = _clamp(
        0.36 + (0.10 if has_value_loop else 0.0) + (0.08 if has_mastery else 0.0)
        + min(monetization_keywords, 3) * 0.07 + confidence_bonus * 0.5
    )

    return {
        "market_size": market_size,
        "data_availability": data_availability,
        "benchmark_feasibility": benchmark_feasibility,
        "community_demand": community_demand,
        "spark_ecosystem_fit": spark_ecosystem_fit,
        "monetization_potential": monetization_potential,
    }


def select_benchmark_panel(benchmark_ids: list[str] | None = None) -> list[dict[str, Any]]:
    """Select benchmark opportunities by id from the library."""
    library = benchmark_library()
    ids = benchmark_ids or DEFAULT_BENCHMARK_IDS
    panel: list[dict[str, Any]] = []
    for domain_id in ids:
        if domain_id in library:
            panel.append(deepcopy(library[domain_id]))
    return panel


def recommended_hybrid_scenario(
    discovered: list[dict[str, Any]],
    combined: list[dict[str, Any]],
    label: str = "mirofish-hybrid-discovery",
) -> dict[str, Any]:
    """Create a simple shock scenario for hybrid runs."""
    shocks: list[dict[str, Any]] = []

    breakout_targets = [
        item["domain_id"]
        for item in sorted(
            discovered,
            key=lambda opportunity: opportunity.get("composite_score", 0.0),
            reverse=True,
        )[:3]
    ]
    if breakout_targets:
        shocks.append(create_shock("breakout_tool", breakout_targets, inject_at_round=4))

    infra_ids = [
        item["domain_id"]
        for item in combined
        if _contains_any(item, {"developer", "mcp", "agent", "coding", "server", "protocol"})
    ]
    if infra_ids:
        shocks.append(create_shock("open_source_release", infra_ids, inject_at_round=7))

    risk_ids = [
        item["domain_id"]
        for item in combined
        if _contains_any(item, {"crypto", "trading", "defi"})
    ]
    if risk_ids:
        shocks.append(create_shock("market_crash", risk_ids, inject_at_round=11))

    reskill_ids = [
        item["domain_id"]
        for item in combined
        if _contains_any(item, {"career", "reskill", "training", "worker"})
    ]
    if reskill_ids:
        shocks.append(create_shock("government_subsidy", reskill_ids, inject_at_round=9))

    return build_scenario(shocks, label=label)


def _contains_any(opportunity: dict[str, Any], terms: set[str]) -> bool:
    text = " ".join([
        opportunity.get("domain_id", ""),
        opportunity.get("label", ""),
        opportunity.get("description", ""),
        opportunity.get("rationale", ""),
    ]).lower()
    return any(term in text for term in terms)


def _clamp(value: float) -> float:
    return round(min(0.95, max(0.05, value)), 4)


def _compact_ensemble_summary(ensemble: dict[str, Any]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for domain_id, data in ensemble.get("domains", {}).items():
        summary.append({
            "domain_id": domain_id,
            "mean_adoption": data.get("mean_adoption", 0.0),
            "median_adoption": data.get("median_adoption", 0.0),
            "mean_trial": data.get("mean_trial", 0.0),
            "mean_churn": data.get("mean_churn", 0.0),
            "confidence_width": data.get("confidence_width", 0.0),
            "tipping_rate": data.get("tipping_rate", 0.0),
        })
    summary.sort(key=lambda item: (item["mean_adoption"], item["mean_trial"]), reverse=True)
    return summary


def _top_line_summary(report: dict[str, Any], ensemble: dict[str, Any]) -> dict[str, Any]:
    predictions = report.get("domain_predictions", [])
    ensemble_summary = _compact_ensemble_summary(ensemble)
    top_prediction = predictions[0] if predictions else {}
    top_ensemble = ensemble_summary[0] if ensemble_summary else {}
    return {
        "top_choice_signal_domain": top_prediction.get("domain_id"),
        "top_choice_signal": top_prediction.get("agent_choice_signal", 0.0),
        "top_final_adoption_domain": top_prediction.get("domain_id"),
        "top_final_adoption": top_prediction.get("adoption_probability", 0.0),
        "top_ensemble_domain": top_ensemble.get("domain_id"),
        "top_ensemble_mean_adoption": top_ensemble.get("mean_adoption", 0.0),
    }


def _merged_domain_metrics(
    domain_id: str,
    prediction_map: dict[str, dict[str, Any]],
    ensemble_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    prediction = deepcopy(prediction_map.get(domain_id, {}))
    ensemble = deepcopy(ensemble_map.get(domain_id, {}))
    if not prediction and not ensemble:
        return {}
    return {
        "domain_id": domain_id,
        "adoption_probability": prediction.get("adoption_probability", 0.0),
        "peak_interest_probability": prediction.get("peak_interest_probability", 0.0),
        "agent_choice_signal": prediction.get("agent_choice_signal", 0.0),
        "consensus_score": prediction.get("consensus_score", 0.0),
        "mean_adoption": ensemble.get("mean_adoption", 0.0),
        "mean_trial": ensemble.get("mean_trial", 0.0),
        "mean_churn": ensemble.get("mean_churn", 0.0),
        "confidence_width": ensemble.get("confidence_width", 0.0),
    }


def _promotion_recommendation(row: dict[str, Any], benchmark_floor: float) -> str:
    if (
        row.get("mean_adoption", 0.0) >= benchmark_floor
        and row.get("agent_choice_signal", 0.0) >= 0.15
        and row.get("benchmark_win_count", 0) >= 2
    ):
        return "review_now"
    if row.get("mean_adoption", 0.0) >= 0.015 or row.get("agent_choice_signal", 0.0) >= 0.15:
        return "watchlist"
    return "hold"


def _promotion_rationale(row: dict[str, Any], benchmark_floor: float) -> list[str]:
    reasons: list[str] = []
    if row.get("mean_adoption", 0.0) >= benchmark_floor:
        reasons.append("Builder ensemble adoption clears the current benchmark median.")
    if row.get("benchmark_win_count", 0) >= 2:
        reasons.append("Outruns at least two benchmark domains on builder ensemble adoption.")
    if row.get("agent_choice_signal", 0.0) >= 0.2:
        reasons.append("Flagship choice signal shows strong in-run agent selection.")
    elif row.get("agent_choice_signal", 0.0) >= 0.15:
        reasons.append("Flagship choice signal is high enough to justify closer review.")
    if row.get("mean_churn", 0.0) > 0.08:
        reasons.append("Churn remains elevated, so benchmark promotion should stay provisional.")
    if not reasons:
        reasons.append("Signal is still exploratory and does not yet clear the promotion floor.")
    return reasons


def _promotion_decision_reason(top_candidate: dict[str, Any], benchmark_floor: float) -> str:
    if not top_candidate:
        return "No candidate metrics were available."
    if top_candidate.get("promotion_recommendation") == "review_now":
        return (
            f"{top_candidate.get('domain_id')} leads the promotion table, clears the benchmark median "
            f"({benchmark_floor:.4f}), and shows enough agent-choice signal to justify benchmark review."
        )
    return (
        f"{top_candidate.get('domain_id')} leads the current frontier set, but its metrics do not yet justify "
        "promotion review against the benchmark floor."
    )


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2
