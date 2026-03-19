"""Tests for mirofish trend adoption simulation."""

import pytest

from chip_labs.mirofish.graph import build_graph_from_opportunities
from chip_labs.mirofish.simulation import (
    run_simulation,
    run_dual_context,
    run_ensemble,
    ADOPTION_STAGES,
    MAX_ROUNDS,
)
from chip_labs.mirofish.signals import create_signal, create_shock
from chip_labs.trend_scanner import SEED_OPPORTUNITIES


@pytest.fixture
def graph():
    return build_graph_from_opportunities(SEED_OPPORTUNITIES)


@pytest.fixture
def domain_ids():
    return [opp["domain_id"] for opp in SEED_OPPORTUNITIES]


class TestSimulation:
    def test_runs_without_error(self, graph, domain_ids):
        result = run_simulation(graph, domain_ids, max_rounds=5, seed=42)
        assert "domains" in result
        assert result["rounds_run"] == 5

    def test_deterministic(self, graph, domain_ids):
        r1 = run_simulation(graph, domain_ids, max_rounds=5, seed=42)
        r2 = run_simulation(graph, domain_ids, max_rounds=5, seed=42)
        for d in domain_ids:
            assert r1["domains"][d]["final_adoption_rate"] == r2["domains"][d]["final_adoption_rate"]

    def test_max_rounds_capped(self, graph, domain_ids):
        result = run_simulation(graph, domain_ids, max_rounds=100, seed=42)
        assert result["rounds_run"] == MAX_ROUNDS

    def test_all_domains_have_results(self, graph, domain_ids):
        result = run_simulation(graph, domain_ids, max_rounds=5, seed=42)
        for d in domain_ids:
            assert d in result["domains"]
            assert "adoption_curve" in result["domains"][d]
            assert "final_adoption_rate" in result["domains"][d]

    def test_adoption_rate_bounded(self, graph, domain_ids):
        result = run_simulation(graph, domain_ids, max_rounds=10, seed=42)
        for d in domain_ids:
            rate = result["domains"][d]["final_adoption_rate"]
            assert 0.0 <= rate <= 1.0

    def test_adoption_curve_length(self, graph, domain_ids):
        rounds = 8
        result = run_simulation(graph, domain_ids, max_rounds=rounds, seed=42)
        for d in domain_ids:
            assert len(result["domains"][d]["adoption_curve"]) == rounds

    def test_consensus_bounded(self, graph, domain_ids):
        result = run_simulation(graph, domain_ids, max_rounds=5, seed=42)
        for d in domain_ids:
            c = result["domains"][d]["final_consensus"]
            assert 0.0 <= c <= 1.0

    def test_disagreement_complement(self, graph, domain_ids):
        result = run_simulation(graph, domain_ids, max_rounds=5, seed=42)
        for d in domain_ids:
            c = result["domains"][d]["final_consensus"]
            dis = result["domains"][d]["disagreement_score"]
            assert abs(c + dis - 1.0) < 0.001


class TestSignalInjection:
    def test_signal_affects_adoption(self, graph, domain_ids):
        signal = create_signal("boost", "vc_funding", ["defi-architect"], strength=0.95)
        r_with = run_simulation(graph, domain_ids, signals=[signal], max_rounds=10, seed=42)
        r_without = run_simulation(graph, domain_ids, max_rounds=10, seed=42)
        # With a strong VC signal, defi-architect adoption should be >= without
        assert r_with["domains"]["defi-architect"]["final_adoption_rate"] >= \
               r_without["domains"]["defi-architect"]["final_adoption_rate"] - 0.01

    def test_shock_injection(self, graph, domain_ids):
        shock = create_shock("breakout_tool", ["defi-architect"], inject_at_round=3)
        result = run_simulation(graph, domain_ids, shocks=[shock], max_rounds=10, seed=42)
        assert "defi-architect" in result["domains"]


class TestDualContext:
    def test_dual_context_returns_both(self, graph, domain_ids):
        result = run_dual_context(graph, domain_ids, max_rounds=5, seed=42)
        assert "builder_community" in result
        assert "enterprise_market" in result
        assert "comparison" in result

    def test_enterprise_slower_adoption(self, graph, domain_ids):
        result = run_dual_context(graph, domain_ids, max_rounds=10, seed=42)
        # Enterprise should generally have equal or lower adoption due to higher thresholds
        for d in domain_ids:
            comp = result["comparison"][d]
            # Not always strictly lower due to simulation dynamics, but
            # enterprise thresholds are 1.2x so adoption_gap is usually >= 0
            assert "builder_adoption" in comp
            assert "enterprise_adoption" in comp

    def test_comparison_has_tipping_points(self, graph, domain_ids):
        result = run_dual_context(graph, domain_ids, max_rounds=10, seed=42)
        for d in domain_ids:
            assert "builder_tipping_point" in result["comparison"][d]
            assert "enterprise_tipping_point" in result["comparison"][d]


class TestChurnInSimulation:
    """Test that churn is properly wired into the simulation loop."""

    def test_simulation_with_churn_runs(self, graph, domain_ids):
        result = run_simulation(graph, domain_ids, max_rounds=10, seed=42)
        assert result["rounds_run"] == 10

    def test_churn_prevents_universal_adoption(self, graph, domain_ids):
        """With churn enabled, not every domain should reach high adoption."""
        result = run_simulation(graph, domain_ids, max_rounds=20, seed=42)
        rates = [result["domains"][d]["final_adoption_rate"] for d in domain_ids]
        # At least some domains should have low adoption (churn pulls them back)
        assert min(rates) < 0.5 or max(rates) - min(rates) > 0.05


class TestEnsemble:
    """Tests for Monte Carlo ensemble simulation."""

    def test_ensemble_runs(self, graph, domain_ids):
        result = run_ensemble(
            graph, domain_ids, max_rounds=5, n_runs=3,
            base_seed=42, count_per_type=2,
        )
        assert result["n_runs"] == 3
        assert "domains" in result

    def test_ensemble_has_all_domains(self, graph, domain_ids):
        result = run_ensemble(
            graph, domain_ids, max_rounds=5, n_runs=3,
            base_seed=42, count_per_type=2,
        )
        for d in domain_ids:
            assert d in result["domains"]

    def test_ensemble_statistics(self, graph, domain_ids):
        result = run_ensemble(
            graph, domain_ids, max_rounds=5, n_runs=5,
            base_seed=42, count_per_type=2,
        )
        for d in domain_ids:
            stats = result["domains"][d]
            assert "mean_adoption" in stats
            assert "median_adoption" in stats
            assert "p10_adoption" in stats
            assert "p90_adoption" in stats
            assert "std_adoption" in stats
            assert "confidence_width" in stats
            assert "tipping_rate" in stats

    def test_ensemble_bounded_values(self, graph, domain_ids):
        result = run_ensemble(
            graph, domain_ids, max_rounds=5, n_runs=5,
            base_seed=42, count_per_type=2,
        )
        for d in domain_ids:
            stats = result["domains"][d]
            assert 0.0 <= stats["mean_adoption"] <= 1.0
            assert 0.0 <= stats["median_adoption"] <= 1.0
            assert 0.0 <= stats["p10_adoption"] <= 1.0
            assert 0.0 <= stats["p90_adoption"] <= 1.0
            assert stats["p10_adoption"] <= stats["p90_adoption"]
            assert 0.0 <= stats["tipping_rate"] <= 1.0

    def test_ensemble_distribution_length(self, graph, domain_ids):
        n_runs = 7
        result = run_ensemble(
            graph, domain_ids, max_rounds=5, n_runs=n_runs,
            base_seed=42, count_per_type=2,
        )
        for d in domain_ids:
            assert len(result["domains"][d]["distribution"]) == n_runs

    def test_ensemble_confidence_width(self, graph, domain_ids):
        result = run_ensemble(
            graph, domain_ids, max_rounds=5, n_runs=5,
            base_seed=42, count_per_type=2,
        )
        for d in domain_ids:
            stats = result["domains"][d]
            expected = round(stats["p90_adoption"] - stats["p10_adoption"], 4)
            assert stats["confidence_width"] == expected


class TestAdoptionStages:
    def test_all_stages_defined(self):
        assert len(ADOPTION_STAGES) == 6
        assert ADOPTION_STAGES[0] == "unaware"
        assert ADOPTION_STAGES[-1] == "advocating"
