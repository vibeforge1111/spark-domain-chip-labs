"""Domain category templates for accelerated chip creation.

Each category provides pre-configured mutation axes, evidence lanes,
scoring approaches, research source types, and watchtower pages that
are common across domains within that category.

These templates are used by scaffold.py to generate domain-specific
chips faster than generic scaffolding alone.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Category template definitions
# ---------------------------------------------------------------------------

CATEGORY_TEMPLATES: dict[str, dict[str, Any]] = {
    "finance": {
        "label": "Finance & Trading",
        "description": "Financial markets, trading strategies, risk management, DeFi",
        "default_mutation_axes": [
            {"name": "risk_model", "values": ["var_95", "var_99", "cvar", "stress_test"]},
            {"name": "time_horizon", "values": ["intraday", "daily", "weekly", "monthly"]},
            {"name": "data_regime", "values": ["bull", "bear", "sideways", "volatile", "crisis"]},
            {"name": "strategy_class", "values": ["momentum", "mean_reversion", "statistical_arb", "fundamental"]},
        ],
        "default_evidence_lanes": [
            "research_grounded",
            "benchmark_grounded",
            "realworld_validated",
            "backtest_benchmark",
        ],
        "scoring_template": "additive_with_regime_gates",
        "research_source_types": [
            "academic_papers",
            "market_data",
            "regulatory_filings",
            "industry_reports",
        ],
        "promotion_gates": [
            {"type": "backtest", "threshold": 0.6, "description": "Walk-forward backtest passing"},
            {"type": "paper_trade", "threshold": 0.7, "description": "Paper trade validation"},
            {"type": "live_validation", "threshold": 0.8, "description": "Live market validation"},
        ],
        "watchtower_pages": [
            "Leaderboard",
            "Regime Analysis",
            "Risk Dashboard",
            "Promotion Pipeline",
        ],
        "default_primary_metric": "risk_adjusted_return",
        "example_domains": ["trading-crypto", "portfolio-optimization", "defi-strategies", "risk-modeling"],
    },

    "creative": {
        "label": "Creative & Design",
        "description": "Web design, graphic design, UX, content creation, branding",
        "default_mutation_axes": [
            {"name": "style_direction", "values": ["minimal", "expressive", "brutalist", "organic", "systematic"]},
            {"name": "medium", "values": ["web", "print", "motion", "interactive"]},
            {"name": "audience", "values": ["consumer", "enterprise", "developer", "luxury"]},
            {"name": "complexity", "values": ["simple", "moderate", "complex", "experimental"]},
        ],
        "default_evidence_lanes": [
            "research_grounded",
            "exploratory_frontier",
            "heuristic_frontier",
            "realworld_validated",
        ],
        "scoring_template": "multi_axis_with_pair_bonuses",
        "research_source_types": [
            "award_sites",
            "case_studies",
            "design_systems",
            "user_research",
        ],
        "promotion_gates": [
            {"type": "heuristic_review", "threshold": 0.6, "description": "Expert heuristic evaluation"},
            {"type": "user_testing", "threshold": 0.7, "description": "User testing validation"},
            {"type": "production_deployment", "threshold": 0.8, "description": "Live deployment metrics"},
        ],
        "watchtower_pages": [
            "Reference Library",
            "Critique Queue",
            "Style Doctrine",
            "Benchmark Gallery",
        ],
        "default_primary_metric": "design_quality_score",
        "example_domains": ["web-designer", "brand-identity", "ux-research", "content-strategy"],
    },

    "technology": {
        "label": "Technology & Engineering",
        "description": "Software architecture, DevOps, AI/ML, infrastructure, security",
        "default_mutation_axes": [
            {"name": "architecture_pattern", "values": ["monolith", "microservices", "serverless", "event_driven"]},
            {"name": "scale_tier", "values": ["prototype", "startup", "growth", "enterprise"]},
            {"name": "reliability_target", "values": ["best_effort", "three_nines", "four_nines", "five_nines"]},
            {"name": "optimization_axis", "values": ["latency", "throughput", "cost", "developer_experience"]},
        ],
        "default_evidence_lanes": [
            "research_grounded",
            "benchmark_grounded",
            "exploratory_frontier",
            "realworld_validated",
        ],
        "scoring_template": "additive_with_constraint_gates",
        "research_source_types": [
            "technical_papers",
            "documentation",
            "benchmark_suites",
            "production_case_studies",
        ],
        "promotion_gates": [
            {"type": "benchmark", "threshold": 0.6, "description": "Benchmark suite passing"},
            {"type": "integration_test", "threshold": 0.7, "description": "Integration test validation"},
            {"type": "production_metric", "threshold": 0.8, "description": "Production metric thresholds"},
        ],
        "watchtower_pages": [
            "Architecture Overview",
            "Benchmark Results",
            "Decision Log",
            "Tech Radar",
        ],
        "default_primary_metric": "engineering_quality_score",
        "example_domains": ["cloud-architecture", "ml-pipeline", "security-posture", "devops-maturity"],
    },

    "gaming": {
        "label": "Game Development",
        "description": "Game design, balance, mechanics, player psychology, monetization",
        "default_mutation_axes": [
            {"name": "game_genre", "values": ["action", "rpg", "strategy", "simulation", "puzzle"]},
            {"name": "balance_focus", "values": ["pvp_fairness", "pve_progression", "economy", "difficulty_curve"]},
            {"name": "engagement_model", "values": ["session_based", "persistent", "competitive", "cooperative"]},
            {"name": "monetization", "values": ["premium", "free_to_play", "cosmetic_only", "battle_pass"]},
        ],
        "default_evidence_lanes": [
            "research_grounded",
            "benchmark_grounded",
            "exploratory_frontier",
            "realworld_validated",
        ],
        "scoring_template": "multi_axis_with_balance_checks",
        "research_source_types": [
            "game_design_documents",
            "player_data",
            "balance_simulations",
            "postmortem_analyses",
        ],
        "promotion_gates": [
            {"type": "simulation", "threshold": 0.6, "description": "Balance simulation passing"},
            {"type": "playtest", "threshold": 0.7, "description": "Playtest feedback threshold"},
            {"type": "live_metrics", "threshold": 0.8, "description": "Live game metrics validation"},
        ],
        "watchtower_pages": [
            "Balance Dashboard",
            "Player Metrics",
            "Design Doctrine",
            "Playtest Results",
        ],
        "default_primary_metric": "game_feel_score",
        "example_domains": ["pokemon-red", "roblox-development", "game-balance", "level-design"],
    },

    "science": {
        "label": "Science & Research",
        "description": "Scientific research, hypothesis testing, data analysis, modeling",
        "default_mutation_axes": [
            {"name": "methodology", "values": ["experimental", "observational", "computational", "theoretical"]},
            {"name": "evidence_strength", "values": ["preliminary", "replicated", "meta_analyzed", "consensus"]},
            {"name": "scale", "values": ["bench", "pilot", "clinical", "population"]},
            {"name": "domain_specificity", "values": ["general", "domain_adapted", "highly_specialized"]},
        ],
        "default_evidence_lanes": [
            "research_grounded",
            "benchmark_grounded",
            "exploratory_frontier",
            "realworld_validated",
        ],
        "scoring_template": "additive_with_reproducibility_gate",
        "research_source_types": [
            "peer_reviewed_papers",
            "preprints",
            "datasets",
            "replication_studies",
        ],
        "promotion_gates": [
            {"type": "statistical_significance", "threshold": 0.6, "description": "Statistical tests passing"},
            {"type": "replication", "threshold": 0.7, "description": "Independent replication"},
            {"type": "meta_analysis", "threshold": 0.8, "description": "Meta-analysis inclusion"},
        ],
        "watchtower_pages": [
            "Literature Review",
            "Experiment Log",
            "Results Dashboard",
            "Hypothesis Tracker",
        ],
        "default_primary_metric": "research_quality_score",
        "example_domains": ["predictive-worlds-lab", "drug-discovery", "climate-modeling", "materials-science"],
    },

    "business": {
        "label": "Business & Strategy",
        "description": "Startup strategy, marketing, growth, operations, product management",
        "default_mutation_axes": [
            {"name": "business_model", "values": ["saas", "marketplace", "e_commerce", "enterprise", "consumer"]},
            {"name": "growth_stage", "values": ["pre_seed", "seed", "series_a", "growth", "mature"]},
            {"name": "market_type", "values": ["blue_ocean", "red_ocean", "emerging", "disrupting"]},
            {"name": "strategy_focus", "values": ["product_led", "sales_led", "marketing_led", "community_led"]},
        ],
        "default_evidence_lanes": [
            "research_grounded",
            "benchmark_grounded",
            "exploratory_frontier",
            "realworld_validated",
        ],
        "scoring_template": "additive_with_pmf_gates",
        "research_source_types": [
            "founder_interviews",
            "market_reports",
            "case_studies",
            "financial_data",
        ],
        "promotion_gates": [
            {"type": "market_research", "threshold": 0.6, "description": "Market research validation"},
            {"type": "customer_validation", "threshold": 0.7, "description": "Customer interview validation"},
            {"type": "revenue_metric", "threshold": 0.8, "description": "Revenue/growth metric threshold"},
        ],
        "watchtower_pages": [
            "Strategy Map",
            "Market Analysis",
            "Competitor Radar",
            "Growth Dashboard",
        ],
        "default_primary_metric": "strategy_score",
        "example_domains": ["startup-yc", "agentic-marketing", "product-strategy", "growth-hacking"],
    },
}


# ---------------------------------------------------------------------------
# Template access functions
# ---------------------------------------------------------------------------

def get_template(category: str) -> dict[str, Any] | None:
    """Get a category template by name."""
    return CATEGORY_TEMPLATES.get(category)


def list_categories() -> list[dict[str, str]]:
    """List all available category templates."""
    return [
        {
            "id": cat_id,
            "label": cat["label"],
            "description": cat["description"],
            "example_domains": cat["example_domains"],
        }
        for cat_id, cat in CATEGORY_TEMPLATES.items()
    ]


def apply_template(brief: dict[str, Any]) -> dict[str, Any]:
    """Apply a category template to a brief, filling in defaults.

    The brief's explicit values always override template defaults.
    Template values are only used when the brief doesn't specify them.
    """
    category = brief.get("category", "technology")
    template = CATEGORY_TEMPLATES.get(category)

    if not template:
        return brief

    enhanced = dict(brief)

    # Apply mutation axes if not specified
    if not enhanced.get("mutation_axes"):
        enhanced["mutation_axes"] = template["default_mutation_axes"]

    # Apply primary metric if not specified
    if not enhanced.get("primary_metric"):
        enhanced["primary_metric"] = template["default_primary_metric"]

    # Apply evidence lanes if not specified
    if not enhanced.get("evidence_lanes"):
        enhanced["evidence_lanes"] = template["default_evidence_lanes"]

    # Store template metadata for reference
    enhanced["_template_applied"] = category
    enhanced["_scoring_template"] = template.get("scoring_template")
    enhanced["_research_source_types"] = template.get("research_source_types", [])
    enhanced["_promotion_gates"] = template.get("promotion_gates", [])
    enhanced["_watchtower_pages"] = template.get("watchtower_pages", [])

    return enhanced


def detect_category(brief: dict[str, Any]) -> str:
    """Attempt to detect the best category for a brief based on keywords.

    Returns the category ID or 'technology' as default.
    """
    domain_id = brief.get("domain_id", "").lower()
    domain_name = brief.get("domain_name", "").lower()
    description = brief.get("description", "").lower()
    text = f"{domain_id} {domain_name} {description}"

    category_keywords = {
        "finance": ["trading", "finance", "portfolio", "risk", "defi", "crypto", "market",
                     "stock", "option", "hedge", "quant", "backtest"],
        "creative": ["design", "creative", "ux", "ui", "brand", "content", "visual",
                      "typography", "layout", "aesthetic", "art"],
        "technology": ["software", "engineering", "devops", "cloud", "api", "security",
                       "infrastructure", "ml", "ai", "data", "architecture"],
        "gaming": ["game", "gaming", "player", "balance", "level", "rpg", "pvp",
                    "roblox", "pokemon", "unity", "godot"],
        "science": ["research", "science", "hypothesis", "experiment", "model",
                     "prediction", "lab", "clinical", "study"],
        "business": ["startup", "business", "strategy", "growth", "marketing",
                      "product", "saas", "revenue", "customer"],
    }

    scores = {}
    for cat, keywords in category_keywords.items():
        scores[cat] = sum(1 for kw in keywords if kw in text)

    if max(scores.values()) == 0:
        return "technology"

    return max(scores, key=scores.get)
