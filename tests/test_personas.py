"""Tests for mirofish persona generation."""

import pytest

from chip_labs.mirofish.graph import build_graph_from_opportunities
from chip_labs.mirofish.personas import (
    generate_personas,
    update_persona_activity,
    persona_evaluates_domain,
    persona_churn_check,
    persona_influence_score,
    PERSONA_TYPES,
)
from chip_labs.trend_scanner import SEED_OPPORTUNITIES


@pytest.fixture
def graph():
    return build_graph_from_opportunities(SEED_OPPORTUNITIES)


@pytest.fixture
def personas(graph):
    return generate_personas(graph, seed=42)


class TestPersonaTypes:
    def test_all_types_defined(self):
        assert len(PERSONA_TYPES) == 8

    def test_each_type_has_required_fields(self):
        for ptype, traits in PERSONA_TYPES.items():
            assert "label" in traits
            assert "influence_score" in traits
            assert "adoption_threshold" in traits
            assert "risk_tolerance" in traits
            assert "network_reach" in traits

    def test_trait_values_in_range(self):
        for ptype, traits in PERSONA_TYPES.items():
            for key in ["influence_score", "adoption_threshold", "risk_tolerance", "network_reach"]:
                assert 0.0 <= traits[key] <= 1.0, f"{ptype}.{key} out of range"


class TestPersonaGeneration:
    def test_generates_personas(self, personas):
        assert len(personas) >= 12  # 8 types * at least 1 each

    def test_persona_bounded(self, graph):
        personas = generate_personas(graph, count_per_type=4)
        assert len(personas) <= 32  # 8 types * 4 max

    def test_deterministic_with_seed(self, graph):
        p1 = generate_personas(graph, seed=42)
        p2 = generate_personas(graph, seed=42)
        assert len(p1) == len(p2)
        for a, b in zip(p1, p2):
            assert a["persona_id"] == b["persona_id"]
            assert a["influence_score"] == b["influence_score"]

    def test_different_seeds_differ(self, graph):
        p1 = generate_personas(graph, seed=42)
        p2 = generate_personas(graph, seed=99)
        # At least some traits should differ
        diffs = sum(1 for a, b in zip(p1, p2) if a["influence_score"] != b["influence_score"])
        assert diffs > 0

    def test_persona_has_expertise(self, personas):
        for p in personas:
            assert "expertise_domains" in p
            assert isinstance(p["expertise_domains"], list)

    def test_persona_has_adoption_state(self, personas):
        for p in personas:
            assert "adoption_state" in p
            assert isinstance(p["adoption_state"], dict)


class TestPersonaDynamics:
    def test_activity_decay(self, personas):
        p = personas[0].copy()
        p["activity_score"] = 1.0
        update_persona_activity(p, 10)
        assert p["activity_score"] < 1.0
        assert p["activity_score"] >= 0.1

    def test_adoption_funnel(self, personas):
        p = personas[0]
        p["adoption_state"] = {}
        # With high awareness, persona should advance
        stage = persona_evaluates_domain(p, "defi-architect", 0.9)
        assert stage in ["aware", "interested", "evaluating", "adopted", "advocating"]

    def test_influence_zero_when_unaware(self, personas):
        p = personas[0]
        p["adoption_state"] = {}
        score = persona_influence_score(p, "defi-architect")
        assert score == 0.0

    def test_influence_positive_when_adopted(self, personas):
        p = personas[0]
        p["adoption_state"] = {"defi-architect": "adopted"}
        score = persona_influence_score(p, "defi-architect")
        assert score > 0.0


class TestChurn:
    """Tests for persona regression (churn) mechanics."""

    def _make_persona(self, stage="adopted", threshold=0.5, risk=0.5, activity=1.0):
        return {
            "persona_id": "test-0",
            "persona_type": "builder",
            "adoption_state": {"test-domain": stage},
            "adoption_threshold": threshold,
            "risk_tolerance": risk,
            "activity_score": activity,
            "influence_score": 0.7,
            "network_reach": 0.5,
            "expertise_domains": [],
            "signal_memory": [],
        }

    def test_no_regression_when_unaware(self):
        p = self._make_persona(stage="unaware")
        result = persona_churn_check(p, "test-domain", 0.0, 10)
        assert result == "unaware"

    def test_no_regression_with_strong_signal(self):
        p = self._make_persona(stage="adopted")
        result = persona_churn_check(p, "test-domain", 0.9, 0)
        assert result == "adopted"

    def test_regression_with_zero_signal(self):
        p = self._make_persona(stage="aware", threshold=0.5, risk=0.0)
        result = persona_churn_check(p, "test-domain", 0.0, 10)
        assert result == "unaware"

    def test_sunk_cost_effect(self):
        """Adopted/advocating personas never churn (committed)."""
        # Aware persona regresses easily
        p_aware = self._make_persona(stage="aware", threshold=0.3, risk=0.0)
        r_aware = persona_churn_check(p_aware, "test-domain", 0.0, 3)
        assert r_aware == "unaware"

        # Adopted persona does NOT regress (committed, sunk cost)
        p_adopted = self._make_persona(stage="adopted", threshold=0.3, risk=0.0)
        r_adopted = persona_churn_check(p_adopted, "test-domain", 0.0, 3)
        assert r_adopted == "adopted"

    def test_adopted_immune_to_churn(self):
        """Adopted/advocating are immune to churn within simulation window."""
        p = self._make_persona(stage="advocating", threshold=0.3, risk=0.0)
        result = persona_churn_check(p, "test-domain", 0.0, 10)
        assert result == "advocating"

    def test_evaluating_can_regress(self):
        """Pre-commitment stages (evaluating) can still churn."""
        p = self._make_persona(stage="evaluating", threshold=0.3, risk=0.0)
        result = persona_churn_check(p, "test-domain", 0.0, 10)
        assert result == "interested"

    def test_risk_tolerant_stickier(self):
        """High-risk personas should resist regression more (emotional investment)."""
        # Low-risk persona
        p_low = self._make_persona(stage="interested", threshold=0.4, risk=0.1)
        r_low = persona_churn_check(p_low, "test-domain", 0.0, 3)

        # High-risk persona with same signal
        p_high = self._make_persona(stage="interested", threshold=0.4, risk=0.9)
        r_high = persona_churn_check(p_high, "test-domain", 0.0, 3)

        # High-risk should be stickier (regression threshold lower due to risk discount)
        # At minimum, the high-risk persona shouldn't regress more than the low-risk one
        stages = ["unaware", "aware", "interested", "evaluating", "adopted", "advocating"]
        assert stages.index(r_high) >= stages.index(r_low)

    def test_stall_increases_regression_risk(self):
        """Long stalls should make regression more likely."""
        # Short stall
        p_short = self._make_persona(stage="evaluating", threshold=0.4, risk=0.3)
        r_short = persona_churn_check(p_short, "test-domain", 0.06, 2)

        # Long stall with same signal
        p_long = self._make_persona(stage="evaluating", threshold=0.4, risk=0.3)
        r_long = persona_churn_check(p_long, "test-domain", 0.06, 15)

        stages = ["unaware", "aware", "interested", "evaluating", "adopted", "advocating"]
        # Long stall should regress more (or at least equally)
        assert stages.index(r_long) <= stages.index(r_short)
