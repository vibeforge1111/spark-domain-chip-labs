"""Meta-evaluator -- scores chip quality and lab research progress."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .quality_rubric import score_chip, score_portfolio
from .registry import discover_chips


def evaluate(mutations: dict[str, str], chip_search_dir: str | Path | None = None) -> dict[str, Any]:
    """Run the lab's evaluate hook.

    Depending on research_focus mutation:
    - quality_audit: Score chip(s) against the quality rubric
    - portfolio_health: Score entire portfolio
    - methodology / domain_discovery / transfer_patterns / agi_theory:
      Return methodology coverage and research progress metrics

    Returns metrics dict with lab_research_quality_score as primary.
    """
    research_focus = mutations.get("research_focus", "quality_audit")
    portfolio_target = mutations.get("portfolio_target")

    if research_focus == "quality_audit" and portfolio_target:
        # Score a specific chip
        chips = discover_chips(chip_search_dir)
        target_chip = None
        for chip in chips:
            if portfolio_target in chip["name"]:
                target_chip = chip
                break

        if target_chip:
            result = score_chip(target_chip["path"])
            return {
                "lab_research_quality_score": round(result["total_score"] / 100.0, 4),
                "portfolio_health": round(result["total_score"] / 100.0, 4),
                "methodology_coverage": 0.0,
                "chips_evaluated": 1,
                "graduation_pipeline_count": 0,
                "chip_result": result,
                "comparison_class": "benchmark_grounded",
            }
        else:
            return {
                "lab_research_quality_score": 0.0,
                "portfolio_health": 0.0,
                "methodology_coverage": 0.0,
                "chips_evaluated": 0,
                "graduation_pipeline_count": 0,
                "error": f"Chip not found: {portfolio_target}",
                "comparison_class": "benchmark_grounded",
            }

    elif research_focus in ("quality_audit", "portfolio_health"):
        # Score entire portfolio
        chips = discover_chips(chip_search_dir)
        chip_paths = [Path(c["path"]) for c in chips if c["has_manifest"]]
        portfolio_result = score_portfolio(chip_paths)

        return {
            "lab_research_quality_score": round(portfolio_result["average_score"] / 100.0, 4),
            "portfolio_health": round(portfolio_result["average_score"] / 100.0, 4),
            "methodology_coverage": 0.0,
            "chips_evaluated": portfolio_result["portfolio_size"],
            "graduation_pipeline_count": 0,
            "portfolio_result": portfolio_result,
            "comparison_class": "benchmark_grounded",
        }

    elif research_focus == "methodology":
        methodology_area = mutations.get("methodology_area", "evaluation_frameworks")
        # Methodology research -- deterministic scoring based on area coverage
        area_scores = {
            "evaluation_frameworks": 0.55,
            "evidence_lanes": 0.50,
            "scoring_systems": 0.60,
            "graduation_criteria": 0.45,
            "frontier_design": 0.40,
            "source_registry": 0.35,
            "packet_quality": 0.42,
        }
        coverage = area_scores.get(methodology_area, 0.30)
        return {
            "lab_research_quality_score": round(coverage, 4),
            "portfolio_health": 0.0,
            "methodology_coverage": round(coverage, 4),
            "chips_evaluated": 0,
            "graduation_pipeline_count": 0,
            "methodology_area": methodology_area,
            "comparison_class": "exploratory_frontier",
        }

    elif research_focus == "domain_discovery":
        trend_source = mutations.get("trend_source", "github")
        # Domain discovery -- heuristic scoring based on source coverage
        source_coverage = {
            "github": 0.52,
            "producthunt": 0.48,
            "x_twitter": 0.45,
            "arxiv": 0.40,
            "community": 0.43,
            "spark_ecosystem": 0.55,
            "vc_landscape": 0.47,
        }
        coverage = source_coverage.get(trend_source, 0.30)
        return {
            "lab_research_quality_score": round(coverage, 4),
            "portfolio_health": 0.0,
            "methodology_coverage": 0.0,
            "chips_evaluated": 0,
            "graduation_pipeline_count": 0,
            "trend_source": trend_source,
            "comparison_class": "exploratory_frontier",
        }

    elif research_focus == "transfer_patterns":
        return {
            "lab_research_quality_score": 0.38,
            "portfolio_health": 0.0,
            "methodology_coverage": 0.0,
            "chips_evaluated": 0,
            "graduation_pipeline_count": 0,
            "comparison_class": "exploratory_frontier",
            "note": "Transfer pattern research is early-stage. Study startup-yc and trading-crypto evidence first.",
        }

    elif research_focus == "trend_simulation":
        # Run MiroFish trend simulation and return prediction quality metrics
        from .trend_scanner import simulate_opportunities, SEED_OPPORTUNITIES
        sim = simulate_opportunities(SEED_OPPORTUNITIES, seed=42)
        report = sim.get("simulation_report", {})
        cal = sim.get("calibration", {})
        hist = cal.get("historical_calibration", {})
        agg_brier = hist.get("aggregate_brier", 1.0)
        # Prediction quality = inverse of Brier score (lower Brier = better)
        prediction_score = round(1.0 - agg_brier, 4)
        return {
            "lab_research_quality_score": prediction_score,
            "portfolio_health": 0.0,
            "methodology_coverage": 0.0,
            "chips_evaluated": 0,
            "graduation_pipeline_count": 0,
            "trend_prediction_score": prediction_score,
            "simulation_calibration": agg_brier,
            "domain_predictions_count": len(report.get("domain_predictions", [])),
            "comparison_class": "exploratory_frontier",
            "note": "Simulation predictions are exploratory_frontier. Calibration via Brier scoring.",
        }

    elif research_focus == "agi_theory":
        return {
            "lab_research_quality_score": 0.25,
            "portfolio_health": 0.0,
            "methodology_coverage": 0.0,
            "chips_evaluated": 0,
            "graduation_pipeline_count": 0,
            "comparison_class": "exploratory_frontier",
            "note": "AGI theory research requires more chip maturity data before meaningful scoring.",
        }

    else:
        return {
            "lab_research_quality_score": 0.0,
            "portfolio_health": 0.0,
            "methodology_coverage": 0.0,
            "chips_evaluated": 0,
            "graduation_pipeline_count": 0,
            "comparison_class": "exploratory_frontier",
            "error": f"Unknown research_focus: {research_focus}",
        }
