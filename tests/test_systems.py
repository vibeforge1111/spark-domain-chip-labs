"""Tests for system-level prediction within domain chips."""

import pytest

from chip_labs.mirofish.systems import (
    compute_system_priority,
    format_system_priority,
    DOMAIN_SYSTEMS,
    _topo_sort_by_priority,
)


class TestDomainSystems:
    def test_domain_systems_defined(self):
        assert len(DOMAIN_SYSTEMS) >= 4
        assert "trading-crypto" in DOMAIN_SYSTEMS
        assert "mcp-server-builder" in DOMAIN_SYSTEMS

    def test_each_system_has_required_fields(self):
        for domain_id, systems in DOMAIN_SYSTEMS.items():
            for sys in systems:
                assert "system_id" in sys, f"{domain_id} system missing system_id"
                assert "label" in sys, f"{domain_id} system missing label"
                assert "value_tags" in sys, f"{domain_id} system missing value_tags"
                assert "complexity" in sys, f"{domain_id} system missing complexity"
                assert "depends_on" in sys, f"{domain_id} system missing depends_on"

    def test_complexity_in_range(self):
        for domain_id, systems in DOMAIN_SYSTEMS.items():
            for sys in systems:
                assert 0.0 <= sys["complexity"] <= 1.0, \
                    f"{domain_id}/{sys['system_id']} complexity out of range"

    def test_dependencies_reference_valid_systems(self):
        for domain_id, systems in DOMAIN_SYSTEMS.items():
            sys_ids = {s["system_id"] for s in systems}
            for sys in systems:
                for dep in sys["depends_on"]:
                    assert dep in sys_ids, \
                        f"{domain_id}/{sys['system_id']} depends on unknown '{dep}'"


class TestComputeSystemPriority:
    @pytest.fixture
    def persona_breakdown(self):
        return {
            "trader": {"adoption_rate": 0.9, "advocacy_rate": 0.6, "count": 100},
            "investor": {"adoption_rate": 0.4, "advocacy_rate": 0.1, "count": 100},
            "developer": {"adoption_rate": 0.7, "advocacy_rate": 0.3, "count": 100},
            "content_creator": {"adoption_rate": 0.5, "advocacy_rate": 0.2, "count": 100},
            "ai_newcomer": {"adoption_rate": 0.2, "advocacy_rate": 0.0, "count": 100},
        }

    def test_returns_ranked_list(self, persona_breakdown):
        result = compute_system_priority("trading-crypto", persona_breakdown)
        assert len(result) == 4
        assert all("priority_score" in s for s in result)

    def test_respects_dependencies(self, persona_breakdown):
        result = compute_system_priority("trading-crypto", persona_breakdown)
        ids = [s["system_id"] for s in result]
        # execution-engine depends on signal-scanner and backtester
        exec_idx = ids.index("execution-engine")
        scanner_idx = ids.index("signal-scanner")
        assert scanner_idx < exec_idx

    def test_demand_sources_attributed(self, persona_breakdown):
        result = compute_system_priority("trading-crypto", persona_breakdown)
        scanner = next(s for s in result if s["system_id"] == "signal-scanner")
        assert len(scanner["demand_sources"]) > 0
        # Traders should be top demand source for signal scanner
        top_source = scanner["demand_sources"][0]
        assert top_source[0] == "trader"

    def test_empty_domain_returns_empty(self, persona_breakdown):
        result = compute_system_priority("nonexistent", persona_breakdown)
        assert result == []

    def test_custom_systems(self, persona_breakdown):
        custom = [
            {"system_id": "custom-a", "label": "A", "value_tags": ["speed"],
             "complexity": 0.3, "depends_on": []},
        ]
        result = compute_system_priority("any", persona_breakdown, custom_systems=custom)
        assert len(result) == 1
        assert result[0]["system_id"] == "custom-a"

    def test_priority_scores_positive(self, persona_breakdown):
        result = compute_system_priority("trading-crypto", persona_breakdown)
        for sys in result:
            assert sys["priority_score"] >= 0.0


class TestTopoSort:
    def test_simple_ordering(self):
        systems = [
            {"system_id": "b", "priority_score": 0.5, "depends_on": ["a"]},
            {"system_id": "a", "priority_score": 0.8, "depends_on": []},
        ]
        result = _topo_sort_by_priority(systems)
        ids = [s["system_id"] for s in result]
        assert ids == ["a", "b"]

    def test_priority_breaks_ties(self):
        systems = [
            {"system_id": "low", "priority_score": 0.3, "depends_on": []},
            {"system_id": "high", "priority_score": 0.9, "depends_on": []},
        ]
        result = _topo_sort_by_priority(systems)
        assert result[0]["system_id"] == "high"

    def test_no_systems(self):
        assert _topo_sort_by_priority([]) == []


class TestFormatOutput:
    def test_format_produces_string(self):
        ranked = [
            {"system_id": "a", "label": "Alpha", "priority_score": 0.8,
             "demand_sources": [("trader", 0.35)], "depends_on": []},
        ]
        output = format_system_priority("test", ranked)
        assert "Alpha" in output
        assert "priority=0.80" in output
        assert "trader" in output
