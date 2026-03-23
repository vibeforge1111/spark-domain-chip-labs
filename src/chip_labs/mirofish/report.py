"""Trend prediction report generator.

Synthesizes simulation results into structured prediction reports.
All output is exploratory_frontier -- never auto-promote to doctrine.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def generate_prediction_report(
    simulation_results: dict[str, Any],
    static_rankings: list[dict[str, Any]] | None = None,
    calibration_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate a comprehensive trend prediction report.

    Args:
        simulation_results: Output from run_simulation() or run_dual_context().
        static_rankings: Rankings from trend_scanner.rank_opportunities() for comparison.
        calibration_data: Output from calibration_report() for trust metrics.

    Returns:
        Structured prediction report with per-domain and cross-domain analysis.
    """
    now = datetime.now(timezone.utc).isoformat()

    # Detect if this is a dual-context result
    is_dual = "comparison" in simulation_results
    if is_dual:
        builder_domains = simulation_results.get("builder_community", {}).get("domains", {})
        enterprise_domains = simulation_results.get("enterprise_market", {}).get("domains", {})
        comparison = simulation_results.get("comparison", {})
        primary_domains = builder_domains
    else:
        primary_domains = simulation_results.get("domains", {})
        comparison = {}

    # Per-domain predictions
    domain_predictions: list[dict[str, Any]] = []
    for domain_id, data in primary_domains.items():
        adoption_prob = data.get("final_adoption_rate", 0.0)
        final_active = data.get("final_active_rate", adoption_prob)
        peak_adoption = data.get("peak_adoption_rate", adoption_prob)
        peak_active = data.get("peak_active_rate", final_active)
        peak_interest = data.get("peak_interest_rate", 0.0)
        tipping_round = data.get("tipping_point_round")

        # Timeline estimate based on tipping point
        if tipping_round is not None:
            if tipping_round <= 5:
                timeline = "near-term (0-3 months)"
            elif tipping_round <= 12:
                timeline = "medium-term (3-6 months)"
            else:
                timeline = "long-term (6-12 months)"
        else:
            timeline = "uncertain (no tipping point detected)"

        # Confidence from consensus
        consensus = data.get("final_consensus", 0.0)
        if consensus > 0.7:
            confidence = "high"
        elif consensus > 0.4:
            confidence = "medium"
        else:
            confidence = "low"

        # Key drivers and risks from adoption curve shape
        drivers = _identify_drivers(data)
        risks = _identify_risks(data)

        prediction = {
            "domain_id": domain_id,
            "adoption_probability": round(adoption_prob, 4),
            "final_active_probability": round(final_active, 4),
            "peak_adoption_probability": round(peak_adoption, 4),
            "peak_active_probability": round(peak_active, 4),
            "peak_interest_probability": round(peak_interest, 4),
            "agent_choice_signal": round(peak_active, 4),
            "peak_active_round": data.get("peak_active_round"),
            "peak_interest_round": data.get("peak_interest_round"),
            "timeline_estimate": timeline,
            "confidence": confidence,
            "consensus_score": consensus,
            "disagreement_score": data.get("disagreement_score", 0.0),
            "tipping_point_round": tipping_round,
            "key_drivers": drivers,
            "key_risks": risks,
        }

        # Add dual-context comparison if available
        if domain_id in comparison:
            prediction["dual_context"] = comparison[domain_id]

        domain_predictions.append(prediction)

    # Sort by adoption probability
    domain_predictions.sort(
        key=lambda x: (
            x.get("agent_choice_signal", 0.0),
            x.get("adoption_probability", 0.0),
        ),
        reverse=True,
    )

    # Cross-domain analysis
    cross_domain = _cross_domain_analysis(domain_predictions, static_rankings)

    report = {
        "report_type": "trend_prediction",
        "generated_at": now,
        "evidence_lane": "exploratory_frontier",
        "is_dual_context": is_dual,
        "simulation_context": simulation_results.get("context", "dual" if is_dual else "single"),
        "rounds_simulated": simulation_results.get("rounds_run",
            simulation_results.get("builder_community", {}).get("rounds_run", 0)),
        "persona_count": simulation_results.get("persona_count",
            simulation_results.get("builder_community", {}).get("persona_count", 0)),
        "domain_predictions": domain_predictions,
        "cross_domain": cross_domain,
        "calibration": calibration_data,
        "governance_note": "All predictions are exploratory_frontier. "
                          "Do not auto-promote to doctrine without replay-benchmarking.",
    }

    return report


def format_report_markdown(report: dict[str, Any]) -> str:
    """Format a prediction report as Markdown for Obsidian."""
    lines = [
        "# Trend Prediction Report",
        "",
        f"> Generated: {report['generated_at']}",
        f"> Evidence lane: {report['evidence_lane']}",
        f"> Rounds simulated: {report['rounds_simulated']}",
        f"> Personas: {report['persona_count']}",
        "",
        "## Domain Predictions",
        "",
        "| Domain | Choice Signal | Final Adoption | Peak Interest | Timeline |",
        "|--------|---------------|----------------|---------------|----------|",
    ]

    for pred in report.get("domain_predictions", []):
        lines.append(
            f"| {pred['domain_id']} | {pred.get('agent_choice_signal', 0.0):.2%} "
            f"| {pred['adoption_probability']:.2%} | {pred.get('peak_interest_probability', 0.0):.2%} "
            f"| {pred['timeline_estimate']} |"
        )

    lines.extend(["", "## Cross-Domain Analysis", ""])

    cross = report.get("cross_domain", {})
    if cross.get("portfolio_gaps"):
        lines.append("### Portfolio Gaps")
        for gap in cross["portfolio_gaps"]:
            lines.append(f"- {gap}")

    if cross.get("synergy_opportunities"):
        lines.append("")
        lines.append("### Synergy Opportunities")
        for syn in cross["synergy_opportunities"]:
            lines.append(f"- {syn}")

    if cross.get("simulation_vs_static"):
        lines.extend(["", "### Simulation vs Static Scoring", ""])
        lines.append("| Domain | Simulation | Static | Delta |")
        lines.append("|--------|-----------|--------|-------|")
        for item in cross["simulation_vs_static"]:
            lines.append(
                f"| {item['domain_id']} | {item['simulation']:.2%} "
                f"| {item['static']:.4f} | {item['delta']:+.4f} |"
            )

    calibration = report.get("calibration")
    if calibration:
        hist = calibration.get("historical_calibration", {})
        lines.extend([
            "", "## Calibration",
            f"- Aggregate Brier score: {hist.get('aggregate_brier', 'N/A')}",
            f"- Better than constant (0.5): {hist.get('better_than_constant', 'N/A')}",
            f"- Better than frequency: {hist.get('better_than_frequency', 'N/A')}",
            f"- Open prediction contracts: {calibration.get('contract_count', 0)}",
        ])

    lines.extend([
        "",
        "---",
        "",
        f"*{report.get('governance_note', '')}*",
    ])

    return "\n".join(lines)


def _identify_drivers(domain_data: dict[str, Any]) -> list[str]:
    """Identify key adoption drivers from simulation data."""
    drivers: list[str] = []
    adoption = domain_data.get("final_adoption_rate", 0.0)
    advocacy = domain_data.get("final_advocacy_rate", 0.0)
    consensus = domain_data.get("final_consensus", 0.0)
    tipping = domain_data.get("tipping_point_round")
    peak_active = domain_data.get("peak_active_rate", adoption)
    peak_interest = domain_data.get("peak_interest_rate", 0.0)

    if adoption > 0.6:
        drivers.append("Strong adoption signal across persona types")
    if advocacy > 0.2:
        drivers.append("Active advocacy from adopters driving viral growth")
    if consensus > 0.7:
        drivers.append("High consensus indicates clear market demand")
    if tipping is not None and tipping <= 8:
        drivers.append("Early tipping point suggests rapid adoption potential")

    # v4 metrics
    retention = domain_data.get("final_retention_rate", 0.0)
    committed = domain_data.get("final_committed_rate", 0.0)
    trial = domain_data.get("final_trial_rate", 0.0)
    if retention > 0.7:
        drivers.append("High retention rate indicates sticky usage pattern")
    if committed > 0.1:
        drivers.append("Committed users show deep workflow integration")
    if trial > 0.3:
        drivers.append("High trial rate shows low barrier to experimentation")
    if peak_active > adoption + 0.1:
        drivers.append("Agents showed real try-out behavior before retention normalized")
    if peak_interest > 0.35:
        drivers.append("The domain captured broad attention during the run")

    if not drivers:
        drivers.append("No strong adoption drivers detected yet")
    return drivers


def _identify_risks(domain_data: dict[str, Any]) -> list[str]:
    """Identify key adoption risks from simulation data."""
    risks: list[str] = []
    disagreement = domain_data.get("disagreement_score", 0.0)
    adoption = domain_data.get("final_adoption_rate", 0.0)
    tipping = domain_data.get("tipping_point_round")
    peak_active = domain_data.get("peak_active_rate", adoption)
    peak_interest = domain_data.get("peak_interest_rate", 0.0)

    if disagreement > 0.6:
        risks.append("High disagreement across persona types signals uncertainty")
    if adoption < 0.3:
        risks.append("Low adoption rate indicates weak demand signal")
    if tipping is None:
        risks.append("No tipping point reached -- adoption may stall")

    # v4 metrics
    churn = domain_data.get("final_churn_rate", 0.0)
    retention = domain_data.get("final_retention_rate", 0.0)
    if churn > 0.1:
        risks.append(f"High churn rate ({churn:.0%}) indicates retention problem")
    if retention < 0.3 and adoption > 0.1:
        risks.append("Low retention despite adoption -- users trying but not sticking")
    if peak_interest > 0.3 and adoption < 0.05:
        risks.append("Attention converted poorly into durable adoption")
    if peak_active > 0.08 and adoption < peak_active * 0.4:
        risks.append("Many agents tried it, but the funnel lost them before retention")

    if not risks:
        risks.append("No major risks identified")
    return risks


def generate_driver_summary(
    personas: list[dict[str, Any]],
    domain_id: str,
) -> dict[str, Any]:
    """Summarize WHY each persona type adopted or stalled for a domain.

    Aggregates decision_log entries across all personas of each type
    to produce per-type driver summaries showing matched values,
    average fit scores, and signal-vs-threshold ratios.
    """
    by_type: dict[str, dict[str, Any]] = {}

    for persona in personas:
        ptype = persona.get("persona_type", "unknown")
        stage = persona.get("adoption_state", {}).get(domain_id, "unaware")
        logs = [
            entry for entry in persona.get("decision_log", [])
            if entry.get("domain_id") == domain_id
        ]

        if ptype not in by_type:
            by_type[ptype] = {
                "count": 0,
                "adopted": 0,
                "advocating": 0,
                "committed": 0,
                "trialing": 0,
                "churned": 0,
                "stalled_at": {},
                "total_fit": 0.0,
                "value_matches": {},
                "signal_sum": 0.0,
                "threshold_sum": 0.0,
                "log_count": 0,
            }

        entry = by_type[ptype]
        entry["count"] += 1
        if stage in ("adopted", "committed", "advocating"):
            entry["adopted"] += 1
        if stage == "advocating":
            entry["advocating"] += 1
        if stage == "committed":
            entry["committed"] += 1
        if stage == "trial":
            entry["trialing"] += 1
        if stage == "churned":
            entry["churned"] += 1
        if stage not in ("adopted", "committed", "advocating"):
            entry["stalled_at"][stage] = entry["stalled_at"].get(stage, 0) + 1

        for log in logs:
            entry["total_fit"] += log.get("fit_score", 0.5)
            entry["signal_sum"] += log.get("effective_signal", 0.0)
            entry["threshold_sum"] += log.get("threshold", 0.0)
            entry["log_count"] += 1
            for val in log.get("matched_values", []):
                entry["value_matches"][val] = entry["value_matches"].get(val, 0) + 1

    # Build summary
    summaries: list[dict[str, Any]] = []
    for ptype, data in sorted(by_type.items(), key=lambda x: x[1]["adopted"], reverse=True):
        count = data["count"]
        adoption_rate = data["adopted"] / max(count, 1)
        avg_fit = data["total_fit"] / max(data["log_count"], 1)
        avg_signal = data["signal_sum"] / max(data["log_count"], 1)
        avg_threshold = data["threshold_sum"] / max(data["log_count"], 1)
        top_values = sorted(data["value_matches"].items(), key=lambda x: x[1], reverse=True)[:3]

        reason = _explain_outcome(adoption_rate, avg_fit, avg_signal, avg_threshold, top_values, data["stalled_at"])

        summaries.append({
            "persona_type": ptype,
            "adoption_rate": round(adoption_rate, 4),
            "advocacy_rate": round(data["advocating"] / max(count, 1), 4),
            "committed_rate": round(data["committed"] / max(count, 1), 4),
            "trial_rate": round(data["trialing"] / max(count, 1), 4),
            "churn_rate": round(data["churned"] / max(count, 1), 4),
            "count": count,
            "avg_fit_score": round(avg_fit, 4),
            "top_matched_values": [v[0] for v in top_values],
            "signal_to_threshold": round(avg_signal / max(avg_threshold, 0.01), 4),
            "stalled_at": data["stalled_at"],
            "reason": reason,
        })

    return {
        "domain_id": domain_id,
        "type_summaries": summaries,
    }


def format_driver_summary(summary: dict[str, Any]) -> str:
    """Format driver summary as human-readable text."""
    lines = [f"Decision Drivers for {summary['domain_id']}:", ""]
    for s in summary["type_summaries"]:
        pct = f"{s['adoption_rate']:.0%}"
        values_str = ", ".join(s["top_matched_values"]) if s["top_matched_values"] else "none"
        lines.append(f"  {s['persona_type']:20s} {pct:>5s} adopted  fit={s['avg_fit_score']:.2f}  values=[{values_str}]")
        lines.append(f"    {s['reason']}")
    return "\n".join(lines)


def _explain_outcome(
    adoption_rate: float,
    avg_fit: float,
    avg_signal: float,
    avg_threshold: float,
    top_values: list[tuple[str, int]],
    stalled_at: dict[str, int],
) -> str:
    """Generate a human-readable explanation for why a persona type adopted or stalled."""
    if adoption_rate >= 0.7:
        values_str = ", ".join(v[0] for v in top_values[:2]) if top_values else "general interest"
        ratio = avg_signal / max(avg_threshold, 0.01)
        return f"Strong adoption: values [{values_str}] matched, signal {ratio:.1f}x threshold"
    elif adoption_rate >= 0.3:
        values_str = ", ".join(v[0] for v in top_values[:2]) if top_values else "partial match"
        return f"Moderate adoption: [{values_str}] resonated but threshold filtered some"
    else:
        stall_stage = max(stalled_at, key=stalled_at.get) if stalled_at else "unaware"
        if avg_fit < 0.4:
            return f"Low adoption: poor value fit ({avg_fit:.2f}), most stalled at {stall_stage}"
        else:
            return f"Low adoption: signal too weak ({avg_signal:.2f} vs {avg_threshold:.2f} threshold), stalled at {stall_stage}"


def _cross_domain_analysis(
    predictions: list[dict[str, Any]],
    static_rankings: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """Generate cross-domain analysis."""
    # Portfolio gaps
    gaps: list[str] = []
    high_adoption = [p for p in predictions if p["adoption_probability"] > 0.5]
    low_adoption = [p for p in predictions if p["adoption_probability"] < 0.2]
    if len(high_adoption) < 2:
        gaps.append("Fewer than 2 domains show strong adoption -- portfolio concentration risk.")
    if low_adoption:
        gap_names = ", ".join(p["domain_id"] for p in low_adoption)
        gaps.append(f"Weak adoption signals for: {gap_names}")

    # Synergy opportunities
    synergies: list[str] = []
    for i, p1 in enumerate(predictions):
        for p2 in predictions[i + 1:]:
            if (p1["adoption_probability"] > 0.4 and p2["adoption_probability"] > 0.4):
                synergies.append(
                    f"{p1['domain_id']} + {p2['domain_id']} -- "
                    f"both show adoption potential, consider cross-chip patterns."
                )

    # Simulation vs static scoring delta
    sim_vs_static: list[dict[str, Any]] = []
    if static_rankings:
        static_map = {r["domain_id"]: r.get("composite_score", 0.0) for r in static_rankings}
        for pred in predictions:
            static_score = static_map.get(pred["domain_id"], 0.0)
            sim_vs_static.append({
                "domain_id": pred["domain_id"],
                "simulation": pred["adoption_probability"],
                "static": static_score,
                "delta": round(pred["adoption_probability"] - static_score, 4),
            })

    return {
        "portfolio_gaps": gaps,
        "synergy_opportunities": synergies[:5],  # cap at 5
        "simulation_vs_static": sim_vs_static,
        "top_recommendation": predictions[0]["domain_id"] if predictions else None,
    }
