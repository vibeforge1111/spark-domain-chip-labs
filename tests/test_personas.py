"""Tests for mirofish persona generation."""

import pytest

from chip_labs.mirofish.graph import build_graph_from_opportunities
from chip_labs.mirofish.personas import (
    generate_personas,
    update_persona_activity,
    persona_evaluates_domain,
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
