"""Tests for mirofish domain knowledge graph."""


from chip_labs.mirofish.graph import (
    DomainGraph,
    build_graph_from_opportunities,
    ENTITY_TYPES,
    RELATIONSHIP_TYPES,
)
from chip_labs.trend_scanner import SEED_OPPORTUNITIES


class TestDomainGraph:
    def test_add_node(self):
        g = DomainGraph()
        g.add_node("test-1", "technology", "Test Tech")
        assert g.node_count == 1
        assert g.nodes["test-1"]["label"] == "Test Tech"

    def test_add_edge(self):
        g = DomainGraph()
        g.add_node("a", "technology", "A")
        g.add_node("b", "platform", "B")
        g.add_edge("a", "b", "ENABLES", weight=0.9)
        assert g.edge_count == 1
        assert g.edges[0]["relationship"] == "ENABLES"

    def test_get_neighbors(self):
        g = DomainGraph()
        g.add_node("a", "technology", "A")
        g.add_node("b", "platform", "B")
        g.add_node("c", "community", "C")
        g.add_edge("a", "b", "ENABLES")
        g.add_edge("a", "c", "SERVES")
        neighbors = g.get_neighbors("a")
        assert len(neighbors) == 2

    def test_get_edges_for(self):
        g = DomainGraph()
        g.add_node("a", "technology", "A")
        g.add_node("b", "platform", "B")
        g.add_edge("a", "b", "ENABLES")
        edges = g.get_edges_for("a")
        assert len(edges) == 1

    def test_track_variable(self):
        g = DomainGraph()
        g.track_variable("adoption_rate", 0.75)
        assert g.tracked_variables["adoption_rate"] == 0.75

    def test_to_dict(self):
        g = DomainGraph()
        g.add_node("x", "trend", "X")
        d = g.to_dict()
        assert d["node_count"] == 1
        assert d["edge_count"] == 0
        assert len(d["nodes"]) == 1


class TestBuildGraph:
    def test_build_from_seed_opportunities(self):
        graph = build_graph_from_opportunities(SEED_OPPORTUNITIES)
        # Should have domain nodes for each opportunity
        domain_nodes = [n for n in graph.nodes.values() if n["type"] == "domain"]
        assert len(domain_nodes) == len(SEED_OPPORTUNITIES)

    def test_graph_has_ecosystem_nodes(self):
        graph = build_graph_from_opportunities(SEED_OPPORTUNITIES)
        # Should have platform and technology nodes from ecosystem
        platform_nodes = [n for n in graph.nodes.values() if n["type"] == "platform"]
        assert len(platform_nodes) >= 4  # github, producthunt, x_twitter, arxiv

    def test_graph_has_edges(self):
        graph = build_graph_from_opportunities(SEED_OPPORTUNITIES)
        assert graph.edge_count > 0

    def test_related_chips_create_edges(self):
        graph = build_graph_from_opportunities(SEED_OPPORTUNITIES)
        # defi-architect relates to trading-crypto
        defi_edges = graph.get_edges_for("defi-architect")
        extends_edges = [e for e in defi_edges if e["relationship"] == "EXTENDS"]
        assert len(extends_edges) >= 1

    def test_extra_signals_inject(self):
        signals = [{
            "signal_id": "test-signal",
            "label": "Test Signal",
            "strength": 0.8,
            "affects_domains": ["defi-architect"],
        }]
        graph = build_graph_from_opportunities(SEED_OPPORTUNITIES, extra_signals=signals)
        assert "signal-test-signal" in graph.nodes

    def test_entity_types_defined(self):
        assert len(ENTITY_TYPES) >= 6

    def test_relationship_types_defined(self):
        assert len(RELATIONSHIP_TYPES) >= 5
