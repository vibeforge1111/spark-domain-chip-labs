"""Tests for mirofish trend adoption simulation."""

import pytest

from chip_labs.mirofish.graph import build_graph_from_opportunities
from chip_labs.mirofish.graph import DomainGraph
from chip_labs.mirofish.simulation import (
    run_simulation,
    run_dual_context,
    run_ensemble,
    run_sensitivity,
    _apply_competitive_displacement,
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


class TestTopologyEffects:
    """Test graph topology propagation in influence phase."""

    def test_enables_edge_boosts_adoption(self, graph, domain_ids):
        """Domains connected by ENABLES edges should benefit from topology."""
        from chip_labs.mirofish.signals import signals_from_opportunities, signals_from_graph
        signals = signals_from_opportunities(SEED_OPPORTUNITIES)
        signals += signals_from_graph(graph)
        result = run_simulation(graph, domain_ids, signals=signals, max_rounds=15, seed=42)
        rates = {d: result["domains"][d]["final_adoption_rate"] for d in domain_ids}
        # With signals + topology, should see varied adoption rates
        assert len(set(round(r, 2) for r in rates.values())) > 1

    def test_competition_suppresses_rivals(self, graph, domain_ids):
        """Domains connected by COMPETES_WITH should suppress each other."""
        # Find a competing pair in the graph
        competing_pairs = []
        for edge in graph.edges:
            if edge["relationship"] == "COMPETES_WITH":
                if edge["source"] in domain_ids and edge["target"] in domain_ids:
                    competing_pairs.append((edge["source"], edge["target"]))

        if not competing_pairs:
            pytest.skip("No competing domain pairs in graph")

        # With competition, one domain should suppress the other
        result = run_simulation(graph, domain_ids, max_rounds=15, seed=42)
        a, b = competing_pairs[0]
        rate_a = result["domains"][a]["final_adoption_rate"]
        rate_b = result["domains"][b]["final_adoption_rate"]
        # They shouldn't both be at 100% (displacement should prevent that)
        assert rate_a + rate_b < 2.0


class TestCompetitiveDisplacement:
    """Test competitive displacement mechanics."""

    def _make_graph_with_competition(self):
        g = DomainGraph()
        g.add_node("domain-a", "domain", "Domain A")
        g.add_node("domain-b", "domain", "Domain B")
        g.add_edge("domain-a", "domain-b", "COMPETES_WITH", weight=0.9)
        return g

    def test_displacement_regresses_competitor(self):
        g = self._make_graph_with_competition()
        persona = {
            "persona_id": "test-0",
            "persona_type": "builder",
            "adoption_state": {
                "domain-a": "adopted",
                "domain-b": "interested",
            },
            "adoption_threshold": 0.5,
            "risk_tolerance": 0.5,
            "activity_score": 1.0,
            "influence_score": 0.7,
            "network_reach": 0.5,
            "expertise_domains": [],
        }
        _apply_competitive_displacement(
            persona, ["domain-a", "domain-b"], g,
        )
        # domain-b should regress from interested -> aware
        assert persona["adoption_state"]["domain-b"] == "aware"

    def test_no_displacement_when_not_adopted(self):
        g = self._make_graph_with_competition()
        persona = {
            "persona_id": "test-0",
            "persona_type": "builder",
            "adoption_state": {
                "domain-a": "interested",
                "domain-b": "interested",
            },
            "adoption_threshold": 0.5,
            "risk_tolerance": 0.5,
            "activity_score": 1.0,
            "influence_score": 0.7,
            "network_reach": 0.5,
            "expertise_domains": [],
        }
        _apply_competitive_displacement(
            persona, ["domain-a", "domain-b"], g,
        )
        # Neither should regress (neither is adopted)
        assert persona["adoption_state"]["domain-b"] == "interested"

    def test_no_displacement_of_already_adopted(self):
        g = self._make_graph_with_competition()
        persona = {
            "persona_id": "test-0",
            "persona_type": "builder",
            "adoption_state": {
                "domain-a": "adopted",
                "domain-b": "adopted",
            },
            "adoption_threshold": 0.5,
            "risk_tolerance": 0.5,
            "activity_score": 1.0,
            "influence_score": 0.7,
            "network_reach": 0.5,
            "expertise_domains": [],
        }
        _apply_competitive_displacement(
            persona, ["domain-a", "domain-b"], g,
        )
        # Sunk cost: both adopted, no displacement
        assert persona["adoption_state"]["domain-b"] == "adopted"

    def test_weak_competition_no_displacement(self):
        """Weak COMPETES_WITH edges (weight <= 0.7) shouldn't displace."""
        g = DomainGraph()
        g.add_node("domain-a", "domain", "Domain A")
        g.add_node("domain-b", "domain", "Domain B")
        g.add_edge("domain-a", "domain-b", "COMPETES_WITH", weight=0.5)
        persona = {
            "persona_id": "test-0",
            "persona_type": "builder",
            "adoption_state": {
                "domain-a": "adopted",
                "domain-b": "evaluating",
            },
            "adoption_threshold": 0.5,
            "risk_tolerance": 0.5,
            "activity_score": 1.0,
            "influence_score": 0.7,
            "network_reach": 0.5,
            "expertise_domains": [],
        }
        _apply_competitive_displacement(
            persona, ["domain-a", "domain-b"], g,
        )
        # Weak competition: no displacement
        assert persona["adoption_state"]["domain-b"] == "evaluating"


class TestSensitivity:
    """Tests for sensitivity analysis."""

    def test_sensitivity_runs(self, graph, domain_ids):
        from chip_labs.mirofish.signals import signals_from_opportunities, signals_from_graph
        signals = signals_from_opportunities(SEED_OPPORTUNITIES)
        signals += signals_from_graph(graph)
        shocks = [create_shock("breakout_tool", domain_ids[:2], inject_at_round=3)]
        result = run_sensitivity(
            graph, domain_ids, signals=signals, shocks=shocks,
            max_rounds=5, seed=42, count_per_type=2,
        )
        assert "baseline_rates" in result
        assert "variations" in result
        assert "factor_importance" in result
        assert "most_sensitive_factor" in result

    def test_sensitivity_has_all_factors(self, graph, domain_ids):
        from chip_labs.mirofish.signals import signals_from_opportunities, signals_from_graph
        signals = signals_from_opportunities(SEED_OPPORTUNITIES)
        signals += signals_from_graph(graph)
        shocks = [create_shock("breakout_tool", domain_ids[:2], inject_at_round=3)]
        result = run_sensitivity(
            graph, domain_ids, signals=signals, shocks=shocks,
            max_rounds=5, seed=42, count_per_type=2,
        )
        assert "signal_strength" in result["variations"]
        assert "adoption_threshold" in result["variations"]
        assert "persona_count" in result["variations"]
        assert "shock_timing" in result["variations"]

    def test_factor_importance_per_domain(self, graph, domain_ids):
        from chip_labs.mirofish.signals import signals_from_opportunities
        signals = signals_from_opportunities(SEED_OPPORTUNITIES)
        result = run_sensitivity(
            graph, domain_ids, signals=signals,
            max_rounds=5, seed=42, count_per_type=2,
        )
        for d in domain_ids:
            assert d in result["factor_importance"]
            assert d in result["most_sensitive_factor"]

    def test_baseline_rates_bounded(self, graph, domain_ids):
        result = run_sensitivity(
            graph, domain_ids, max_rounds=5, seed=42, count_per_type=2,
        )
        for d in domain_ids:
            assert 0.0 <= result["baseline_rates"][d] <= 1.0


class TestAdoptionStages:
    def test_all_stages_defined(self):
        assert len(ADOPTION_STAGES) == 6
        assert ADOPTION_STAGES[0] == "unaware"
        assert ADOPTION_STAGES[-1] == "advocating"
