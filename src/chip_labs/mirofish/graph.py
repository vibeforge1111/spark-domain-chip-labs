"""Domain knowledge graph builder.

Builds entity-relationship graphs from domain opportunity data.
Zero deps -- uses dicts, not Neo4j/Zep (matching chip pattern).
"""

from __future__ import annotations

from typing import Any


# Entity types
ENTITY_TYPES = [
    "technology", "community", "company", "trend",
    "platform", "regulation", "domain",
]

# Relationship types
RELATIONSHIP_TYPES = [
    "ENABLES", "COMPETES_WITH", "DEPENDS_ON",
    "SERVES", "DISRUPTS", "EXTENDS",
]


class DomainGraph:
    """In-memory domain knowledge graph using plain dicts."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []
        self.tracked_variables: dict[str, float] = {}

    def add_node(self, node_id: str, entity_type: str,
                 label: str, properties: dict[str, Any] | None = None) -> None:
        """Add a node to the graph."""
        self.nodes[node_id] = {
            "id": node_id,
            "type": entity_type,
            "label": label,
            "properties": properties or {},
        }

    def add_edge(self, source: str, target: str,
                 relationship: str, weight: float = 1.0) -> None:
        """Add a directed edge between two nodes."""
        self.edges.append({
            "source": source,
            "target": target,
            "relationship": relationship,
            "weight": weight,
        })

    def get_neighbors(self, node_id: str) -> list[dict[str, Any]]:
        """Get all nodes connected to a given node."""
        neighbor_ids: set[str] = set()
        for edge in self.edges:
            if edge["source"] == node_id:
                neighbor_ids.add(edge["target"])
            elif edge["target"] == node_id:
                neighbor_ids.add(edge["source"])
        return [self.nodes[nid] for nid in neighbor_ids if nid in self.nodes]

    def get_edges_for(self, node_id: str) -> list[dict[str, Any]]:
        """Get all edges involving a node."""
        return [e for e in self.edges
                if e["source"] == node_id or e["target"] == node_id]

    def track_variable(self, name: str, value: float) -> None:
        """Track a simulation variable on the graph."""
        self.tracked_variables[name] = value

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    def to_dict(self) -> dict[str, Any]:
        """Serialize graph to dict."""
        return {
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
            "tracked_variables": self.tracked_variables,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
        }


def build_graph_from_opportunities(
    opportunities: list[dict[str, Any]],
    extra_signals: list[dict[str, Any]] | None = None,
) -> DomainGraph:
    """Build a domain graph from seed opportunities and optional signals.

    Each opportunity becomes a domain node. Related technologies, communities,
    and platforms become connected nodes.
    """
    graph = DomainGraph()

    # Seed technology/platform nodes
    _seed_ecosystem_nodes(graph)

    # Add domain nodes from opportunities
    for opp in opportunities:
        domain_id = opp["domain_id"]
        graph.add_node(
            domain_id, "domain", opp["label"],
            properties={
                "description": opp.get("description", ""),
                "composite_score": opp.get("composite_score", 0.0),
                "scores": opp.get("scores", {}),
                "rationale": opp.get("rationale", ""),
            },
        )

        # Connect to related chips
        for related in opp.get("related_chips", []):
            chip_id = f"chip-{related}"
            if chip_id not in graph.nodes:
                graph.add_node(chip_id, "technology", related)
            graph.add_edge(domain_id, chip_id, "EXTENDS", weight=0.8)

        # Connect to evidence sources as platforms
        for source in opp.get("evidence_sources", []):
            platform_id = f"platform-{source}"
            if platform_id not in graph.nodes:
                graph.add_node(platform_id, "platform", source)
            graph.add_edge(domain_id, platform_id, "SERVES", weight=0.5)

    # Cross-domain relationships based on score similarity
    domain_nodes = [n for n in graph.nodes.values() if n["type"] == "domain"]
    for i, d1 in enumerate(domain_nodes):
        for d2 in domain_nodes[i + 1:]:
            s1 = d1["properties"].get("scores", {})
            s2 = d2["properties"].get("scores", {})
            overlap = _score_similarity(s1, s2)
            if overlap > 0.85:
                graph.add_edge(d1["id"], d2["id"], "COMPETES_WITH", weight=overlap)
            elif overlap > 0.70:
                graph.add_edge(d1["id"], d2["id"], "ENABLES", weight=overlap * 0.5)

    # Inject extra signals as nodes/edges
    for signal in (extra_signals or []):
        sig_id = f"signal-{signal.get('signal_id', 'unknown')}"
        graph.add_node(sig_id, "trend", signal.get("label", sig_id),
                       properties=signal)
        for target in signal.get("affects_domains", []):
            if target in graph.nodes:
                graph.add_edge(sig_id, target, "DISRUPTS",
                               weight=signal.get("strength", 0.5))

    return graph


def _seed_ecosystem_nodes(graph: DomainGraph) -> None:
    """Add core ecosystem entities to the graph."""
    ecosystem = [
        ("platform-github", "platform", "GitHub"),
        ("platform-producthunt", "platform", "Product Hunt"),
        ("platform-x_twitter", "platform", "X/Twitter"),
        ("platform-arxiv", "platform", "arXiv"),
        ("community-spark", "community", "Spark Ecosystem"),
        ("community-indie", "community", "Indie Hackers"),
        ("community-defi", "community", "DeFi Builders"),
        ("tech-mcp", "technology", "Model Context Protocol"),
        ("tech-llm", "technology", "Large Language Models"),
        ("tech-agents", "technology", "AI Agents"),
        ("regulation-gdpr", "regulation", "GDPR"),
        ("regulation-sox", "regulation", "SOX"),
    ]
    for node_id, etype, label in ecosystem:
        graph.add_node(node_id, etype, label)

    # Core ecosystem edges
    graph.add_edge("tech-mcp", "tech-agents", "ENABLES", weight=0.9)
    graph.add_edge("tech-llm", "tech-agents", "ENABLES", weight=0.95)
    graph.add_edge("tech-agents", "community-spark", "SERVES", weight=0.8)
    graph.add_edge("regulation-gdpr", "community-defi", "DISRUPTS", weight=0.3)


def _score_similarity(s1: dict[str, float], s2: dict[str, float]) -> float:
    """Compute similarity between two score dicts (0-1)."""
    if not s1 or not s2:
        return 0.0
    keys = set(s1.keys()) & set(s2.keys())
    if not keys:
        return 0.0
    diffs = [abs(s1[k] - s2[k]) for k in keys]
    return round(1.0 - (sum(diffs) / len(diffs)), 4)
