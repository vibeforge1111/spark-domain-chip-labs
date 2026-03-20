"""System-level prediction within domain chips.

Each domain chip is composed of systems (sub-features/capabilities).
This module predicts which systems to build first by cross-referencing
persona adoption data with system value alignment.

Output example:
    System Build Priority for trading-crypto:
      1. Signal Scanner     priority=0.82  demand=[trader(0.35), opportunity_hunter(0.28)]
      2. Portfolio Tracker   priority=0.61  demand=[investor(0.22), trader(0.18)]

Zero external dependencies. Uses only stdlib.
"""

from __future__ import annotations

from typing import Any

from .personas import CUSTOMER_PERSONAS


# ---------------------------------------------------------------------------
# System definitions per domain
# ---------------------------------------------------------------------------

DOMAIN_SYSTEMS: dict[str, list[dict[str, Any]]] = {
    "trading-crypto": [
        {
            "system_id": "signal-scanner",
            "label": "Signal Scanner",
            "description": "Real-time market signal detection, whale tracking, momentum alerts.",
            "value_tags": ["speed", "alpha", "edge", "trend_spotting"],
            "complexity": 0.6,
            "depends_on": [],
        },
        {
            "system_id": "backtester",
            "label": "Strategy Backtester",
            "description": "Historical strategy validation, risk metrics, drawdown analysis.",
            "value_tags": ["risk_management", "code_quality", "roi"],
            "complexity": 0.7,
            "depends_on": ["signal-scanner"],
        },
        {
            "system_id": "portfolio-tracker",
            "label": "Portfolio Tracker",
            "description": "Multi-wallet tracking, PnL attribution, portfolio rebalancing.",
            "value_tags": ["portfolio_intelligence", "deal_flow", "roi"],
            "complexity": 0.5,
            "depends_on": [],
        },
        {
            "system_id": "execution-engine",
            "label": "Trade Execution",
            "description": "Order routing, slippage minimization, multi-venue execution.",
            "value_tags": ["speed", "alpha", "risk_management"],
            "complexity": 0.8,
            "depends_on": ["signal-scanner", "backtester"],
        },
    ],
    "meme-coin-launcher": [
        {
            "system_id": "token-deployer",
            "label": "Token Deployer",
            "description": "One-click token creation on pump.fun/moonshot with safety checks.",
            "value_tags": ["speed_to_ship", "easy_start", "speed"],
            "complexity": 0.5,
            "depends_on": [],
        },
        {
            "system_id": "community-builder",
            "label": "Community Builder",
            "description": "Telegram/Discord community setup, engagement automation, holder tracking.",
            "value_tags": ["audience_growth", "engagement", "distribution"],
            "complexity": 0.6,
            "depends_on": [],
        },
        {
            "system_id": "launch-analyzer",
            "label": "Launch Analyzer",
            "description": "Bonding curve analysis, timing optimization, competitor monitoring.",
            "value_tags": ["alpha", "trend_spotting", "edge"],
            "complexity": 0.7,
            "depends_on": ["token-deployer"],
        },
        {
            "system_id": "anti-rug-checker",
            "label": "Anti-Rug Checker",
            "description": "Contract audit, liquidity lock verification, red flag detection.",
            "value_tags": ["risk_management", "roi", "deal_flow"],
            "complexity": 0.6,
            "depends_on": [],
        },
    ],
    "mcp-server-builder": [
        {
            "system_id": "scaffold-generator",
            "label": "Scaffold Generator",
            "description": "Project template generation, boilerplate reduction, standard patterns.",
            "value_tags": ["speed_to_ship", "productivity", "dx", "easy_start"],
            "complexity": 0.4,
            "depends_on": [],
        },
        {
            "system_id": "tool-registry",
            "label": "Tool Registry",
            "description": "Tool definition management, validation, documentation generation.",
            "value_tags": ["api_quality", "infrastructure", "composability"],
            "complexity": 0.6,
            "depends_on": ["scaffold-generator"],
        },
        {
            "system_id": "test-harness",
            "label": "Test Harness",
            "description": "Automated MCP tool testing, mock clients, integration verification.",
            "value_tags": ["code_quality", "productivity", "extensibility"],
            "complexity": 0.7,
            "depends_on": ["tool-registry"],
        },
        {
            "system_id": "publish-pipeline",
            "label": "Publish Pipeline",
            "description": "NPM/PyPI packaging, version management, marketplace listing.",
            "value_tags": ["developer_adoption", "distribution", "infrastructure"],
            "complexity": 0.5,
            "depends_on": ["tool-registry"],
        },
    ],
    "tiktok-creator": [
        {
            "system_id": "hook-generator",
            "label": "Hook Generator",
            "description": "Attention-grabbing opening lines, trend-aware hook patterns.",
            "value_tags": ["content_quality", "engagement", "audience_growth"],
            "complexity": 0.4,
            "depends_on": [],
        },
        {
            "system_id": "trend-surfer",
            "label": "Trend Surfer",
            "description": "Real-time trend detection, sound selection, hashtag optimization.",
            "value_tags": ["trend_spotting", "speed", "first_mover"],
            "complexity": 0.6,
            "depends_on": [],
        },
        {
            "system_id": "content-calendar",
            "label": "Content Calendar",
            "description": "Posting schedule optimization, content batching, consistency tracker.",
            "value_tags": ["time_leverage", "simplicity", "all_in_one"],
            "complexity": 0.5,
            "depends_on": ["hook-generator"],
        },
        {
            "system_id": "analytics-dashboard",
            "label": "Analytics Dashboard",
            "description": "View tracking, engagement analysis, audience demographics.",
            "value_tags": ["campaign_roi", "attribution", "conversion"],
            "complexity": 0.6,
            "depends_on": [],
        },
    ],
    "cursor-copilot": [
        {
            "system_id": "prompt-library",
            "label": "Prompt Library",
            "description": "Curated coding prompts, context templates, workflow presets.",
            "value_tags": ["productivity", "easy_start", "quick_wins", "dx"],
            "complexity": 0.3,
            "depends_on": [],
        },
        {
            "system_id": "context-optimizer",
            "label": "Context Optimizer",
            "description": "Intelligent file selection, context window management, codebase indexing.",
            "value_tags": ["code_quality", "productivity", "extensibility"],
            "complexity": 0.7,
            "depends_on": ["prompt-library"],
        },
        {
            "system_id": "workflow-automator",
            "label": "Workflow Automator",
            "description": "Multi-step task automation, review chains, deployment pipelines.",
            "value_tags": ["speed_to_ship", "time_leverage", "speed"],
            "complexity": 0.8,
            "depends_on": ["context-optimizer"],
        },
    ],
    "linkedin-ghostwriter": [
        {
            "system_id": "post-crafter",
            "label": "Post Crafter",
            "description": "Hook-body-CTA structure, engagement patterns, formatting rules.",
            "value_tags": ["content_quality", "engagement", "audience_growth"],
            "complexity": 0.4,
            "depends_on": [],
        },
        {
            "system_id": "voice-cloner",
            "label": "Voice Cloner",
            "description": "Learn writing style from past posts, maintain consistent voice.",
            "value_tags": ["creative_control", "uniqueness", "aesthetic_quality"],
            "complexity": 0.7,
            "depends_on": ["post-crafter"],
        },
        {
            "system_id": "engagement-engine",
            "label": "Engagement Engine",
            "description": "Comment strategy, connection requests, DM sequences.",
            "value_tags": ["distribution", "audience_targeting", "conversion"],
            "complexity": 0.6,
            "depends_on": [],
        },
    ],
}


# ---------------------------------------------------------------------------
# Priority scoring
# ---------------------------------------------------------------------------

def compute_system_priority(
    domain_id: str,
    persona_breakdown: dict[str, dict[str, Any]],
    custom_systems: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Rank systems within a domain by persona demand.

    Cross-references persona adoption data with system value tags:
    1. For each system, check which persona types' values it serves
    2. Weight by each persona type's adoption rate (high adopters matter more)
    3. Discount by complexity (simpler = build first when demand is equal)
    4. Sort respecting dependency order

    Args:
        domain_id: The domain to analyze.
        persona_breakdown: Per-type adoption data from simulation results
            (the "adoption_by_persona_type" dict).
        custom_systems: Override default system definitions for this domain.

    Returns:
        Sorted list of systems with priority scores and demand attribution.
    """
    systems = custom_systems or DOMAIN_SYSTEMS.get(domain_id, [])
    if not systems:
        return []

    scored: list[dict[str, Any]] = []
    for system in systems:
        demand = 0.0
        demand_sources: list[tuple[str, float]] = []
        sys_values = set(system.get("value_tags", []))

        for ptype, pdata in persona_breakdown.items():
            adoption = pdata.get("adoption_rate", 0.0)
            persona_values = set(CUSTOMER_PERSONAS.get(ptype, {}).get("values", []))
            overlap = len(sys_values & persona_values)
            if overlap > 0:
                contribution = adoption * overlap * 0.25
                demand += contribution
                demand_sources.append((ptype, round(contribution, 4)))

        # Complexity discount: simpler systems are easier wins
        complexity_factor = 1.0 - system.get("complexity", 0.5) * 0.3
        priority = round(demand * complexity_factor, 4)

        scored.append({
            "system_id": system["system_id"],
            "label": system["label"],
            "description": system.get("description", ""),
            "priority_score": priority,
            "demand_score": round(demand, 4),
            "complexity": system.get("complexity", 0.5),
            "depends_on": list(system.get("depends_on", [])),
            "demand_sources": sorted(demand_sources, key=lambda x: x[1], reverse=True),
            "value_tags": list(system.get("value_tags", [])),
        })

    return _topo_sort_by_priority(scored)


def _topo_sort_by_priority(systems: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort systems respecting dependency order, breaking ties by priority."""
    # Build adjacency
    by_id = {s["system_id"]: s for s in systems}
    in_degree: dict[str, int] = {s["system_id"]: 0 for s in systems}
    dependents: dict[str, list[str]] = {s["system_id"]: [] for s in systems}

    for s in systems:
        for dep in s.get("depends_on", []):
            if dep in in_degree:
                in_degree[s["system_id"]] += 1
                dependents[dep].append(s["system_id"])

    # Kahn's algorithm with priority ordering
    result: list[dict[str, Any]] = []
    available = [sid for sid, deg in in_degree.items() if deg == 0]

    while available:
        # Pick highest priority among available
        available.sort(key=lambda sid: by_id[sid]["priority_score"], reverse=True)
        chosen = available.pop(0)
        result.append(by_id[chosen])

        for dep in dependents[chosen]:
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                available.append(dep)

    # Any remaining (cyclic deps) get appended by priority
    remaining = [s for s in systems if s["system_id"] not in {r["system_id"] for r in result}]
    remaining.sort(key=lambda s: s["priority_score"], reverse=True)
    result.extend(remaining)

    return result


def format_system_priority(
    domain_id: str,
    ranked_systems: list[dict[str, Any]],
) -> str:
    """Format system priority as a readable string."""
    lines = [f"System Build Priority for {domain_id}:"]
    for i, sys in enumerate(ranked_systems, 1):
        sources = ", ".join(f"{s[0]}({s[1]:.2f})" for s in sys["demand_sources"][:3])
        deps = f"  depends on: {', '.join(sys['depends_on'])}" if sys["depends_on"] else ""
        lines.append(
            f"  {i}. {sys['label']:<22} priority={sys['priority_score']:.2f}  "
            f"demand=[{sources}]{deps}"
        )
    return "\n".join(lines)
