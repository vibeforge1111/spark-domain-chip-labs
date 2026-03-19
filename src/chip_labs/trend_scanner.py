"""Domain opportunity detection and scoring."""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Domain opportunity scoring framework
# ---------------------------------------------------------------------------

SCORING_WEIGHTS = {
    "market_size": 0.20,
    "data_availability": 0.15,
    "benchmark_feasibility": 0.20,
    "community_demand": 0.20,
    "spark_ecosystem_fit": 0.15,
    "monetization_potential": 0.10,
}


# Seed domain opportunities based on market research (March 2026)
SEED_OPPORTUNITIES: list[dict[str, Any]] = [
    {
        "domain_id": "defi-architect",
        "label": "DeFi Architecture",
        "description": "Smart contract patterns, MEV protection, liquidity strategies, gas optimization.",
        "scores": {
            "market_size": 0.90,
            "data_availability": 0.85,
            "benchmark_feasibility": 0.80,
            "community_demand": 0.92,
            "spark_ecosystem_fit": 0.85,
            "monetization_potential": 0.95,
        },
        "rationale": "AI agent token market cap at $7.7B. Natural extension of trading-crypto chip.",
        "related_chips": ["trading-crypto"],
        "evidence_sources": ["github", "x_twitter", "community"],
    },
    {
        "domain_id": "ai-agent-builder",
        "label": "AI Agent Architecture",
        "description": "Agent patterns, tool selection, prompt engineering, evaluation frameworks.",
        "scores": {
            "market_size": 0.88,
            "data_availability": 0.82,
            "benchmark_feasibility": 0.75,
            "community_demand": 0.90,
            "spark_ecosystem_fit": 0.80,
            "monetization_potential": 0.78,
        },
        "rationale": "AI agents are #1 category on Product Hunt 2026. MCP has 10,000+ servers.",
        "related_chips": [],
        "evidence_sources": ["producthunt", "github", "arxiv"],
    },
    {
        "domain_id": "indie-hacker",
        "label": "Indie Hacker / Micro SaaS",
        "description": "Micro SaaS validation, pricing strategy, launch playbook, distribution channels.",
        "scores": {
            "market_size": 0.82,
            "data_availability": 0.78,
            "benchmark_feasibility": 0.72,
            "community_demand": 0.85,
            "spark_ecosystem_fit": 0.82,
            "monetization_potential": 0.80,
        },
        "rationale": "Micro SaaS market growing 30% annually. Solo founders are most active sharers.",
        "related_chips": ["startup-yc", "agentic-marketing"],
        "evidence_sources": ["community", "x_twitter", "producthunt"],
    },
    {
        "domain_id": "compliance-shield",
        "label": "Compliance Automation",
        "description": "SOX, GDPR, SOC2, HIPAA automated checks and evidence collection.",
        "scores": {
            "market_size": 0.75,
            "data_availability": 0.60,
            "benchmark_feasibility": 0.65,
            "community_demand": 0.68,
            "spark_ecosystem_fit": 0.55,
            "monetization_potential": 0.88,
        },
        "rationale": "Domain-specific AI in enterprise is 'Year of 2026'. High willingness to pay.",
        "related_chips": [],
        "evidence_sources": ["vc_landscape", "community"],
    },
    {
        "domain_id": "legal-ops",
        "label": "Legal Operations",
        "description": "Contract analysis, clause identification, risk scoring, due diligence.",
        "scores": {
            "market_size": 0.78,
            "data_availability": 0.55,
            "benchmark_feasibility": 0.58,
            "community_demand": 0.65,
            "spark_ecosystem_fit": 0.50,
            "monetization_potential": 0.85,
        },
        "rationale": "Harvey (legal AI) is a vertical AI poster child. Strong VC interest.",
        "related_chips": [],
        "evidence_sources": ["vc_landscape"],
    },
    {
        "domain_id": "game-balance",
        "label": "Game Balance & Systems",
        "description": "Game economy design, difficulty curves, player progression, monetization balance.",
        "scores": {
            "market_size": 0.72,
            "data_availability": 0.70,
            "benchmark_feasibility": 0.78,
            "community_demand": 0.74,
            "spark_ecosystem_fit": 0.75,
            "monetization_potential": 0.65,
        },
        "rationale": "97% of game studios use AI-assisted tools. Natural extension of pokemon-red and roblox chips.",
        "related_chips": ["pokemon-red", "roblox-development"],
        "evidence_sources": ["github", "community"],
    },
]


def score_opportunity(opportunity: dict[str, Any]) -> float:
    """Score a domain opportunity using weighted dimensions."""
    scores = opportunity.get("scores", {})
    total = 0.0
    for dim, weight in SCORING_WEIGHTS.items():
        total += scores.get(dim, 0.0) * weight
    return round(total, 4)


def rank_opportunities(opportunities: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Rank domain opportunities by composite score."""
    opps = opportunities or SEED_OPPORTUNITIES
    ranked = []
    for opp in opps:
        composite = score_opportunity(opp)
        ranked.append({**opp, "composite_score": composite})
    ranked.sort(key=lambda x: x["composite_score"], reverse=True)
    return ranked


def get_top_opportunities(n: int = 5) -> list[dict[str, Any]]:
    """Get the top N domain opportunities."""
    return rank_opportunities()[:n]
