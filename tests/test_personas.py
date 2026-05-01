"""Tests for mirofish persona generation."""

import pytest

from chip_labs.mirofish.graph import build_graph_from_opportunities
from chip_labs.mirofish.personas import (
    generate_personas,
    update_persona_activity,
    persona_evaluates_domain,
    persona_churn_check,
    persona_influence_score,
    persona_learn_from_round,
    persona_domain_fit,
    PERSONA_TYPES,
    CUSTOMER_PERSONAS,
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
        assert len(PERSONA_TYPES) >= 11
        for persona_type in (
            "investor",
            "entrepreneur",
            "content_creator",
            "solopreneur",
            "ai_newcomer",
            "developer",
            "marketer",
            "creative",
            "trader",
            "tool_maker",
            "opportunity_hunter",
        ):
            assert persona_type in PERSONA_TYPES

    def test_each_type_has_required_fields(self):
        for ptype, traits in PERSONA_TYPES.items():
            assert "label" in traits
            assert "influence_score" in traits
            assert "adoption_threshold" in traits
            assert "risk_tolerance" in traits
            assert "network_reach" in traits

    def test_each_type_has_values_and_pain_points(self):
        for ptype, traits in PERSONA_TYPES.items():
            assert "values" in traits, f"{ptype} missing values"
            assert "pain_points" in traits, f"{ptype} missing pain_points"
            assert len(traits["values"]) >= 2, f"{ptype} needs at least 2 values"
            assert len(traits["pain_points"]) >= 2, f"{ptype} needs at least 2 pain_points"

    def test_trait_values_in_range(self):
        for ptype, traits in PERSONA_TYPES.items():
            for key in ["influence_score", "adoption_threshold", "risk_tolerance", "network_reach"]:
                assert 0.0 <= traits[key] <= 1.0, f"{ptype}.{key} out of range"


class TestPersonaGeneration:
    def test_generates_personas(self, personas):
        assert len(personas) >= 11  # 11 types * at least 1 each

    def test_persona_bounded(self, graph):
        count_per_type = 4
        personas = generate_personas(graph, count_per_type=4)
        assert len(personas) <= len(PERSONA_TYPES) * count_per_type

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

    def test_persona_has_values(self, personas):
        for p in personas:
            assert "values" in p
            assert isinstance(p["values"], list)
            assert len(p["values"]) >= 2

    def test_persona_has_pain_points(self, personas):
        for p in personas:
            assert "pain_points" in p
            assert isinstance(p["pain_points"], list)


class TestPersonaDomainFit:
    def test_perfect_match(self):
        persona = {"values": ["speed", "alpha", "edge"]}
        fit = persona_domain_fit(persona, "test", ["speed", "alpha", "edge", "risk_management"])
        assert fit == 0.9  # 0.3 + 3 * 0.2

    def test_no_match(self):
        persona = {"values": ["speed", "alpha"]}
        fit = persona_domain_fit(persona, "test", ["aesthetics", "creativity"])
        assert fit == 0.3  # base, no overlap

    def test_partial_match(self):
        persona = {"values": ["speed", "alpha", "edge"]}
        fit = persona_domain_fit(persona, "test", ["speed", "creativity"])
        assert fit == 0.5  # 0.3 + 1 * 0.2

    def test_no_tags_returns_neutral(self):
        persona = {"values": ["speed"]}
        fit = persona_domain_fit(persona, "test", [])
        assert fit == 0.5

    def test_no_values_returns_neutral(self):
        persona = {}
        fit = persona_domain_fit(persona, "test", ["speed"])
        assert fit == 0.5

    def test_capped_at_1(self):
        persona = {"values": ["a", "b", "c", "d", "e"]}
        fit = persona_domain_fit(persona, "test", ["a", "b", "c", "d", "e"])
        assert fit == 1.0


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
            "persona_type": "developer",
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
        """Deeper adoption stages are stickier than early awareness."""
        # Aware persona regresses easily
        p_aware = self._make_persona(stage="aware", threshold=0.3, risk=0.0)
        r_aware = persona_churn_check(p_aware, "test-domain", 0.0, 3)
        assert r_aware == "unaware"

        # Adopted persona has sunk cost, so it regresses at most one stage.
        p_adopted = self._make_persona(stage="adopted", threshold=0.3, risk=0.0)
        r_adopted = persona_churn_check(p_adopted, "test-domain", 0.0, 3)
        assert r_adopted == "trial"

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


class TestPersonaLearning:
    """Tests for persona learning/adaptation mechanics."""

    def _make_adopted_persona(self, threshold=0.5):
        return {
            "persona_id": "learn-0",
            "persona_type": "developer",
            "adoption_state": {"domain-a": "adopted"},
            "adoption_threshold": threshold,
            "risk_tolerance": 0.5,
            "activity_score": 1.0,
            "influence_score": 0.7,
            "network_reach": 0.5,
            "expertise_domains": [],
            "signal_memory": [],
        }

    def test_no_learning_when_not_adopted(self):
        p = self._make_adopted_persona()
        p["adoption_state"] = {"domain-a": "interested"}
        original_threshold = p["adoption_threshold"]
        persona_learn_from_round(p, "domain-a", 0.8)
        assert p["adoption_threshold"] == original_threshold

    def test_confidence_boost_on_success(self):
        p = self._make_adopted_persona(threshold=0.5)
        persona_learn_from_round(p, "domain-a", 0.6)
        assert p["adoption_threshold"] < 0.5

    def test_caution_on_failure(self):
        p = self._make_adopted_persona(threshold=0.5)
        persona_learn_from_round(p, "domain-a", 0.01)
        assert p["adoption_threshold"] > 0.5

    def test_learning_history_tracked(self):
        p = self._make_adopted_persona()
        persona_learn_from_round(p, "domain-a", 0.6)
        assert "learning_history" in p
        assert len(p["learning_history"]) == 1
        assert p["learning_history"][0]["outcome"] == "validated"

    def test_learning_history_capped(self):
        p = self._make_adopted_persona()
        for i in range(30):
            persona_learn_from_round(p, "domain-a", 0.6)
        assert len(p["learning_history"]) <= 20

    def test_threshold_floor(self):
        p = self._make_adopted_persona(threshold=0.1)
        for _ in range(100):
            persona_learn_from_round(p, "domain-a", 0.9)
        assert p["adoption_threshold"] >= 0.1

    def test_threshold_ceiling(self):
        p = self._make_adopted_persona(threshold=0.95)
        for _ in range(100):
            persona_learn_from_round(p, "domain-a", 0.01)
        assert p["adoption_threshold"] <= 0.95


class TestDecisionLog:
    """Tests for decision driver tracking in persona_evaluates_domain."""

    def _make_persona(self, ptype="developer"):
        traits = CUSTOMER_PERSONAS[ptype]
        return {
            "persona_id": f"{ptype}-test",
            "persona_type": ptype,
            "influence_score": traits["influence_score"],
            "adoption_threshold": traits["adoption_threshold"],
            "risk_tolerance": traits["risk_tolerance"],
            "network_reach": traits["network_reach"],
            "values": list(traits["values"]),
            "pain_points": list(traits["pain_points"]),
            "expertise_domains": [],
            "adoption_state": {},
            "signal_memory": [],
            "activity_score": 1.0,
        }

    def test_decision_log_created(self):
        p = self._make_persona()
        persona_evaluates_domain(p, "test-domain", 0.5, ["code_quality"])
        assert "decision_log" in p
        assert len(p["decision_log"]) == 1

    def test_decision_log_records_domain(self):
        p = self._make_persona()
        persona_evaluates_domain(p, "test-domain", 0.5, ["code_quality"])
        entry = p["decision_log"][0]
        assert entry["domain_id"] == "test-domain"

    def test_decision_log_records_stages(self):
        p = self._make_persona()
        persona_evaluates_domain(p, "test-domain", 0.5)
        entry = p["decision_log"][0]
        assert entry["from_stage"] == "unaware"
        assert entry["to_stage"] in ["unaware", "aware", "interested"]

    def test_decision_log_records_fit_score(self):
        p = self._make_persona()
        persona_evaluates_domain(p, "test-domain", 0.5, ["code_quality", "productivity"])
        entry = p["decision_log"][0]
        assert "fit_score" in entry
        assert entry["fit_score"] > 0.3  # has value matches

    def test_decision_log_records_matched_values(self):
        p = self._make_persona("developer")  # values: code_quality, productivity, dx, extensibility
        persona_evaluates_domain(p, "test-domain", 0.5, ["code_quality", "productivity", "speed"])
        entry = p["decision_log"][0]
        assert "matched_values" in entry
        assert "code_quality" in entry["matched_values"]
        assert "productivity" in entry["matched_values"]
        assert "speed" not in entry["matched_values"]  # not in developer values

    def test_decision_log_accumulates(self):
        p = self._make_persona()
        for i in range(5):
            persona_evaluates_domain(p, f"domain-{i}", 0.5)
        assert len(p["decision_log"]) == 5

    def test_decision_log_capped(self):
        p = self._make_persona()
        for i in range(150):
            persona_evaluates_domain(p, f"domain-{i}", 0.5)
        assert len(p["decision_log"]) <= 100

    def test_advanced_flag_set(self):
        p = self._make_persona("opportunity_hunter")  # low threshold 0.15
        persona_evaluates_domain(p, "test-domain", 0.9)
        entry = p["decision_log"][0]
        assert "advanced" in entry
        # With very high signal and low threshold, likely advanced
        assert isinstance(entry["advanced"], bool)
