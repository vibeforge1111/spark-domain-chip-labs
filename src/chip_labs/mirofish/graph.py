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
        self._edges_by_node: dict[str, list[dict[str, Any]]] = {}
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
        edge = {
            "source": source,
            "target": target,
            "relationship": relationship,
            "weight": weight,
        }
        self.edges.append(edge)
        self._edges_by_node.setdefault(source, []).append(edge)
        self._edges_by_node.setdefault(target, []).append(edge)

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
        return list(self._edges_by_node.get(node_id, []))

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
                "domain_tags": _behavioral_domain_tags(opp),
                "retention_score": _inferred_retention_score(opp),
                "choice_score": _inferred_choice_score(opp),
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


def _behavioral_domain_tags(opportunity: dict[str, Any]) -> list[str]:
    """Infer persona-relevant tags used by fit and macro logic."""
    candidate_context = opportunity.get("candidate_context", {})
    source_tags = [str(tag).strip().lower() for tag in candidate_context.get("domain_tags", []) if str(tag).strip()]
    text = " ".join([
        opportunity.get("domain_id", ""),
        opportunity.get("label", ""),
        opportunity.get("description", ""),
        opportunity.get("rationale", ""),
        candidate_context.get("specialization_surface", ""),
        candidate_context.get("mastery_surface", ""),
        candidate_context.get("user_value_loop", ""),
        " ".join(opportunity.get("related_chips", [])),
    ]).lower()

    inferred = set(source_tags)

    keyword_map = {
        "security": {"audit", "compliance", "infrastructure", "productivity", "roi"},
        "questionnaire": {"audit", "compliance", "productivity", "roi"},
        "rfp": {"roi", "productivity", "campaign_roi"},
        "procurement": {"audit", "roi", "productivity"},
        "compliance": {"audit", "compliance", "infrastructure", "roi"},
        "audit": {"audit", "compliance", "infrastructure"},
        "evidence": {"audit", "compliance", "productivity"},
        "renewal": {"roi", "productivity", "portfolio_intelligence"},
        "customer": {"roi", "productivity", "portfolio_intelligence"},
        "support": {"productivity", "portfolio_intelligence"},
        "startup": {"speed_to_ship", "idea_validation", "market_fit", "roi"},
        "founder": {"speed_to_ship", "idea_validation", "market_fit", "roi"},
        "investor": {"portfolio_intelligence", "roi", "deal_flow"},
        "board": {"portfolio_intelligence", "roi"},
        "sales": {"roi", "campaign_roi", "audience_targeting"},
        "partner": {"roi", "audience_targeting"},
        "developer": {"productivity", "dx", "extensibility", "infrastructure"},
        "coding": {"productivity", "dx", "extensibility"},
        "workflow": {"productivity"},
        "copilot": {"productivity", "quick_wins"},
        "automation": {"productivity", "time_leverage"},
        "risk": {"portfolio_intelligence", "roi"},
    }

    for keyword, tags in keyword_map.items():
        if keyword in text:
            inferred.update(tags)

    # Always keep a small neutral base so fit is not empty for semantically rich domains.
    if inferred:
        inferred.add("productivity")

    return sorted(inferred)


def _inferred_retention_score(opportunity: dict[str, Any]) -> float:
    """Infer how sticky a domain is likely to be once tried."""
    candidate_context = opportunity.get("candidate_context", {})
    text = " ".join([
        opportunity.get("domain_id", ""),
        opportunity.get("label", ""),
        opportunity.get("description", ""),
        opportunity.get("rationale", ""),
        candidate_context.get("specialization_surface", ""),
        candidate_context.get("mastery_surface", ""),
        candidate_context.get("user_value_loop", ""),
    ]).lower()

    score = 0.42

    sticky_keywords = {
        "recurring": 0.08,
        "repeated": 0.08,
        "workflow": 0.05,
        "renewal": 0.12,
        "questionnaire": 0.10,
        "security": 0.07,
        "audit": 0.08,
        "compliance": 0.08,
        "evidence": 0.06,
        "review": 0.05,
        "account": 0.05,
        "board": 0.04,
        "weekly": 0.05,
        "daily": 0.08,
    }
    weak_keywords = {
        "prospecting": -0.04,
        "launch": -0.03,
        "viral": -0.04,
        "idea": -0.03,
    }

    for keyword, delta in sticky_keywords.items():
        if keyword in text:
            score += delta
    for keyword, delta in weak_keywords.items():
        if keyword in text:
            score += delta

    return round(max(0.2, min(0.85, score)), 4)


def _inferred_choice_score(opportunity: dict[str, Any]) -> float:
    """Infer how easy it is to justify an actual try once interest exists."""
    candidate_context = opportunity.get("candidate_context", {})
    source_tags = {
        str(tag).strip().lower()
        for tag in candidate_context.get("domain_tags", [])
        if str(tag).strip()
    }
    text = " ".join([
        opportunity.get("domain_id", ""),
        opportunity.get("label", ""),
        opportunity.get("description", ""),
        opportunity.get("rationale", ""),
        candidate_context.get("specialization_surface", ""),
        candidate_context.get("mastery_surface", ""),
        candidate_context.get("user_value_loop", ""),
    ]).lower()

    score = 0.34

    if {"compliance", "enterprise-sales", "enterprise-ops"} & source_tags:
        score += 0.05

    proof_keywords = {
        "rfp": 0.12,
        "response": 0.08,
        "questionnaire": 0.10,
        "evidence": 0.11,
        "artifact": 0.08,
        "audit": 0.09,
        "compliance": 0.08,
        "control": 0.08,
        "controls": 0.08,
        "mapping": 0.06,
        "map": 0.04,
        "package": 0.08,
        "packaging": 0.07,
        "submit": 0.07,
        "procurement": 0.09,
        "retrieve": 0.05,
        "reusable": 0.05,
        "reuse": 0.05,
        "proof": 0.08,
        "approval": 0.06,
    }
    softer_keywords = {
        "brief": -0.06,
        "briefing": -0.06,
        "dashboard": -0.05,
        "synthes": -0.04,
        "research": -0.03,
        "idea": -0.04,
    }

    for keyword, delta in proof_keywords.items():
        if keyword in text:
            score += delta
    for keyword, delta in softer_keywords.items():
        if keyword in text:
            score += delta

    return round(max(0.2, min(0.9, score)), 4)
