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
    domain_predictions.sort(key=lambda x: x["adoption_probability"], reverse=True)

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
        "| Domain | Adoption Prob | Timeline | Confidence | Tipping Point |",
        "|--------|--------------|----------|------------|---------------|",
    ]

    for pred in report.get("domain_predictions", []):
        tp = pred.get("tipping_point_round")
        tp_str = f"Round {tp}" if tp is not None else "None"
        lines.append(
            f"| {pred['domain_id']} | {pred['adoption_probability']:.2%} "
            f"| {pred['timeline_estimate']} | {pred['confidence']} | {tp_str} |"
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

    if adoption > 0.6:
        drivers.append("Strong adoption signal across persona types")
    if advocacy > 0.2:
        drivers.append("Active advocacy from adopters driving viral growth")
    if consensus > 0.7:
        drivers.append("High consensus indicates clear market demand")
    if tipping is not None and tipping <= 8:
        drivers.append("Early tipping point suggests rapid adoption potential")

    if not drivers:
        drivers.append("No strong adoption drivers detected yet")
    return drivers


def _identify_risks(domain_data: dict[str, Any]) -> list[str]:
    """Identify key adoption risks from simulation data."""
    risks: list[str] = []
    disagreement = domain_data.get("disagreement_score", 0.0)
    adoption = domain_data.get("final_adoption_rate", 0.0)
    tipping = domain_data.get("tipping_point_round")

    if disagreement > 0.6:
        risks.append("High disagreement across persona types signals uncertainty")
    if adoption < 0.3:
        risks.append("Low adoption rate indicates weak demand signal")
    if tipping is None:
        risks.append("No tipping point reached -- adoption may stall")

    if not risks:
        risks.append("No major risks identified")
    return risks


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
