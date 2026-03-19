"""End-to-end tests for the MiroFish trend prediction pipeline."""

import pytest

from chip_labs.trend_scanner import (
    simulate_opportunities,
    rank_opportunities,
    SEED_OPPORTUNITIES,
)
from chip_labs.mirofish.report import generate_prediction_report, format_report_markdown


class TestEndToEnd:
    def test_simulate_opportunities(self):
        result = simulate_opportunities(SEED_OPPORTUNITIES, seed=42, max_rounds=5)
        assert "static_rankings" in result
        assert "simulation_report" in result
        assert "calibration" in result

    def test_report_has_predictions(self):
        result = simulate_opportunities(SEED_OPPORTUNITIES, seed=42, max_rounds=5)
        report = result["simulation_report"]
        assert "domain_predictions" in report
        assert len(report["domain_predictions"]) == len(SEED_OPPORTUNITIES)

    def test_predictions_sorted_by_adoption(self):
        result = simulate_opportunities(SEED_OPPORTUNITIES, seed=42, max_rounds=5)
        predictions = result["simulation_report"]["domain_predictions"]
        for i in range(len(predictions) - 1):
            assert predictions[i]["adoption_probability"] >= predictions[i + 1]["adoption_probability"]

    def test_report_has_cross_domain(self):
        result = simulate_opportunities(SEED_OPPORTUNITIES, seed=42, max_rounds=5)
        report = result["simulation_report"]
        assert "cross_domain" in report
        assert "portfolio_gaps" in report["cross_domain"]

    def test_report_evidence_lane(self):
        result = simulate_opportunities(SEED_OPPORTUNITIES, seed=42, max_rounds=5)
        report = result["simulation_report"]
        assert report["evidence_lane"] == "exploratory_frontier"

    def test_governance_note(self):
        result = simulate_opportunities(SEED_OPPORTUNITIES, seed=42, max_rounds=5)
        report = result["simulation_report"]
        assert "exploratory_frontier" in report["governance_note"]

    def test_calibration_present(self):
        result = simulate_opportunities(SEED_OPPORTUNITIES, seed=42, max_rounds=5)
        cal = result["calibration"]
        assert "historical_calibration" in cal
        assert cal["historical_calibration"]["aggregate_brier"] < 0.5

    def test_format_markdown(self):
        result = simulate_opportunities(SEED_OPPORTUNITIES, seed=42, max_rounds=5)
        md = format_report_markdown(result["simulation_report"])
        assert "# Trend Prediction Report" in md
        assert "Domain Predictions" in md
        assert "exploratory_frontier" in md

    def test_deterministic(self):
        r1 = simulate_opportunities(SEED_OPPORTUNITIES, seed=42, max_rounds=5)
        r2 = simulate_opportunities(SEED_OPPORTUNITIES, seed=42, max_rounds=5)
        p1 = r1["simulation_report"]["domain_predictions"]
        p2 = r2["simulation_report"]["domain_predictions"]
        for a, b in zip(p1, p2):
            assert a["domain_id"] == b["domain_id"]
            assert a["adoption_probability"] == b["adoption_probability"]

    def test_different_seeds_produce_different_personas(self):
        """Different seeds produce different persona traits even if simulation converges."""
        from chip_labs.mirofish.graph import build_graph_from_opportunities
        from chip_labs.mirofish.personas import generate_personas
        graph = build_graph_from_opportunities(SEED_OPPORTUNITIES)
        p1 = generate_personas(graph, seed=42)
        p2 = generate_personas(graph, seed=99)
        diffs = sum(1 for a, b in zip(p1, p2) if a["influence_score"] != b["influence_score"])
        assert diffs > 0
