"""Lab packet emitter -- generates methodology and quality documents."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..quality_rubric import score_portfolio
from ..registry import discover_chips


PACKET_KINDS = [
    "methodology_doctrine",
    "domain_opportunity",
    "quality_assessment",
    "transfer_pattern",
    "graduation_candidate",
    "trend_prediction",
]


def generate_packets(mutations: dict[str, str],
                     chip_search_dir: str | Path | None = None) -> list[dict[str, Any]]:
    """Generate lab research packets based on current mutations and portfolio state.

    Returns a list of packet dicts ready for memory promotion.
    """
    research_focus = mutations.get("research_focus", "quality_audit")
    packets: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc).isoformat()

    if research_focus in ("quality_audit", "portfolio_health"):
        chips = discover_chips(chip_search_dir)
        chip_paths = [Path(c["path"]) for c in chips if c["has_manifest"]]
        portfolio = score_portfolio(chip_paths)

        packets.append({
            "packet_kind": "quality_assessment",
            "evidence_lane": "benchmark_grounded",
            "created_at": now,
            "content": {
                "title": "Portfolio Quality Assessment",
                "portfolio_size": portfolio["portfolio_size"],
                "average_score": portfolio["average_score"],
                "verdict_distribution": portfolio["verdict_distribution"],
                "weakest_chips": [
                    {"name": c["chip_name"], "score": c["total_score"], "verdict": c["verdict"]}
                    for c in sorted(portfolio["chips"], key=lambda x: x["total_score"])[:3]
                ],
                "strongest_chips": [
                    {"name": c["chip_name"], "score": c["total_score"], "verdict": c["verdict"]}
                    for c in sorted(portfolio["chips"], key=lambda x: x["total_score"], reverse=True)[:3]
                ],
            },
            "promotion_status": "benchmark_grounded",
        })

    elif research_focus == "methodology":
        methodology_area = mutations.get("methodology_area", "evaluation_frameworks")
        packets.append({
            "packet_kind": "methodology_doctrine",
            "evidence_lane": "exploratory_frontier",
            "created_at": now,
            "content": {
                "title": f"Methodology Research: {methodology_area}",
                "area": methodology_area,
                "findings": _get_methodology_findings(methodology_area),
                "next_probes": _get_methodology_probes(methodology_area),
            },
            "promotion_status": "exploratory_frontier",
        })

    elif research_focus == "domain_discovery":
        trend_source = mutations.get("trend_source", "github")
        packets.append({
            "packet_kind": "domain_opportunity",
            "evidence_lane": "exploratory_frontier",
            "created_at": now,
            "content": {
                "title": f"Domain Discovery: {trend_source}",
                "source": trend_source,
                "opportunities": _get_domain_opportunities(trend_source),
            },
            "promotion_status": "exploratory_frontier",
        })

    elif research_focus == "trend_simulation":
        from ..trend_scanner import simulate_opportunities, SEED_OPPORTUNITIES
        sim = simulate_opportunities(SEED_OPPORTUNITIES, seed=42)
        report = sim.get("simulation_report", {})
        cal = sim.get("calibration", {})

        packets.append({
            "packet_kind": "trend_prediction",
            "evidence_lane": "exploratory_frontier",
            "created_at": now,
            "content": {
                "title": "MiroFish Trend Prediction Report",
                "domain_predictions": report.get("domain_predictions", []),
                "cross_domain": report.get("cross_domain", {}),
                "calibration_summary": {
                    "aggregate_brier": cal.get("historical_calibration", {}).get("aggregate_brier"),
                    "better_than_constant": cal.get("historical_calibration", {}).get("better_than_constant"),
                    "contract_count": cal.get("contract_count", 0),
                },
                "governance": report.get("governance_note", ""),
            },
            "promotion_status": "exploratory_frontier",
            "comparison_class": "exploratory_frontier",
        })

    elif research_focus == "transfer_patterns":
        packets.append({
            "packet_kind": "transfer_pattern",
            "evidence_lane": "research_grounded",
            "created_at": now,
            "content": {
                "title": "Cross-Chip Transfer Patterns",
                "patterns": [
                    {
                        "pattern": "fixed_evaluator_with_mutation_space",
                        "source_chips": ["startup-yc", "trading-crypto"],
                        "description": "All mature chips use a deterministic scoring function with bounded mutation parameters.",
                        "transferable": True,
                    },
                    {
                        "pattern": "doctrine_plus_strategy_separation",
                        "source_chips": ["trading-crypto"],
                        "description": "Separating 'what to believe' (doctrine) from 'how to act' (strategy) produces cleaner evaluation.",
                        "transferable": True,
                    },
                    {
                        "pattern": "factor_catalog_with_family_priors",
                        "source_chips": ["startup-yc"],
                        "description": "When specific data is missing, fall back to family-level priors rather than zero.",
                        "transferable": True,
                    },
                ],
            },
            "promotion_status": "research_grounded",
        })

    return packets


def _get_methodology_findings(area: str) -> list[str]:
    """Return known findings for a methodology area."""
    findings = {
        "evaluation_frameworks": [
            "Fixed evaluator + changing strategy is the core Spark pattern.",
            "Multiple subsidiary metrics prevent gaming a single score.",
            "Baseline trial with empty mutations establishes the floor.",
        ],
        "evidence_lanes": [
            "Four lanes (research, benchmark, real-world, exploratory) must stay structurally distinct.",
            "Mixing evidence lanes causes false promotion.",
            "Exploratory frontier should never auto-promote to doctrine.",
        ],
        "scoring_systems": [
            "Deterministic scoring (no LLM in the evaluator) ensures reproducibility.",
            "Uplifts and penalties should be small (0.01-0.05 range).",
            "Readiness scores should weight multiple factors, not rely on one metric.",
        ],
        "graduation_criteria": [
            "Working CLI with all 4 hooks is minimum viable chip.",
            "Quality rubric score >= 60/100 for beta graduation.",
            "At least one successful benchmark pack before claiming beta.",
        ],
        "frontier_design": [
            "Bounded mutation spaces prevent infinite drift.",
            "Open mutation fields need regex pattern validation.",
            "Prompt hints guide LLM suggestions within domain constraints.",
        ],
        "source_registry": [
            "Document the best people, materials, and datasets for each domain.",
            "Source quality matters more than source quantity.",
            "Real-world feedback loops are the strongest evidence.",
        ],
        "packet_quality": [
            "Packets should include claim, mechanism, boundary, and contradiction fields.",
            "Confidence scores reflect evidence strength, not belief strength.",
            "Promotion status tracks the packet's position in the evidence pipeline.",
        ],
    }
    return findings.get(area, ["No findings yet for this methodology area."])


def _get_methodology_probes(area: str) -> list[str]:
    """Return next probes for a methodology area."""
    probes = {
        "evaluation_frameworks": ["Study how trading-crypto combines doctrine and strategy scores."],
        "evidence_lanes": ["Compare evidence lane separation across all beta+ chips."],
        "scoring_systems": ["Test whether startup-yc's token bonus pattern transfers to other domains."],
        "graduation_criteria": ["Track which graduation criteria predict real-world chip success."],
        "frontier_design": ["Compare frontier mutation complexity across all chips."],
        "source_registry": ["Map which source types produce the highest-signal evidence."],
        "packet_quality": ["Define minimum viable packet schema for new chips."],
    }
    return probes.get(area, ["Explore this area further."])


def _get_domain_opportunities(source: str) -> list[dict[str, Any]]:
    """Return domain opportunities for a trend source."""
    # Deterministic seed opportunities based on market research
    opportunities = {
        "github": [
            {"domain": "defi-architect", "signal_strength": 0.85, "rationale": "DeFi + AI agents is the hottest intersection in 2026. $7.7B AI agent token market."},
            {"domain": "ai-agent-builder", "signal_strength": 0.82, "rationale": "AI agents are #1 category on Product Hunt. MCP has 10,000+ servers."},
            {"domain": "compliance-shield", "signal_strength": 0.70, "rationale": "Domain-specific AI in enterprise is 'Year of 2026'. SOX/GDPR automation demand."},
        ],
        "producthunt": [
            {"domain": "ai-agent-builder", "signal_strength": 0.88, "rationale": "AI Agents and AI Coding Agents are top Product Hunt categories in 2026."},
            {"domain": "ai-sales-ops", "signal_strength": 0.72, "rationale": "AI Sales Tools are a top-5 Product Hunt category."},
        ],
        "x_twitter": [
            {"domain": "indie-hacker", "signal_strength": 0.80, "rationale": "Micro SaaS market growing 30% annually. Solo founders are most active sharers."},
            {"domain": "x-growth", "signal_strength": 0.75, "rationale": "Content creators with AI tools are the viral loop."},
        ],
        "spark_ecosystem": [
            {"domain": "defi-architect", "signal_strength": 0.82, "rationale": "Natural extension of trading-crypto chip into smart contract patterns."},
            {"domain": "indie-hacker", "signal_strength": 0.78, "rationale": "Natural extension of startup-yc into micro-SaaS validation."},
        ],
        "community": [
            {"domain": "game-balance", "signal_strength": 0.68, "rationale": "Game dev studios actively adopting AI tools. 97% use AI-assisted asset creation."},
        ],
        "arxiv": [
            {"domain": "rl-agent-training", "signal_strength": 0.65, "rationale": "Reinforcement learning for agent optimization is an active research area."},
        ],
        "vc_landscape": [
            {"domain": "legal-ops", "signal_strength": 0.72, "rationale": "Harvey (legal AI) is a vertical AI poster child. Strong VC interest."},
            {"domain": "healthcare-admin", "signal_strength": 0.68, "rationale": "Healthcare admin AI has strong VC backing but high regulatory bar."},
        ],
    }
    return opportunities.get(source, [])
