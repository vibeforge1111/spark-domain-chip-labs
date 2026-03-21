"""Chip creation methodology knowledge base.

Extracted from studying mature chips (startup-yc as reference implementation).
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Core methodology patterns (proven across 2+ chips)
# ---------------------------------------------------------------------------

PROVEN_PATTERNS: list[dict[str, Any]] = [
    {
        "id": "fixed_evaluator",
        "label": "Fixed Evaluator, Changing Strategy",
        "description": "Use one deterministic scoring function. Vary the inputs (mutations), not the scorer.",
        "evidence_chips": ["startup-yc", "trading-crypto", "agentic-marketing"],
        "evidence_lane": "benchmark_grounded",
        "transferable": True,
    },
    {
        "id": "four_hook_contract",
        "label": "Four Hook Contract",
        "description": "Every chip implements exactly four hooks: evaluate, suggest, packets, watchtower.",
        "evidence_chips": ["startup-yc", "trading-crypto", "agentic-marketing", "web-designer"],
        "evidence_lane": "benchmark_grounded",
        "transferable": True,
    },
    {
        "id": "bounded_mutation_space",
        "label": "Bounded Mutation Space",
        "description": "Define allowed_mutations explicitly. Use field_patterns for validation. Open mutation fields get regex gates.",
        "evidence_chips": ["startup-yc", "trading-crypto", "vibe-incubator"],
        "evidence_lane": "benchmark_grounded",
        "transferable": True,
    },
    {
        "id": "baseline_plus_variants",
        "label": "Baseline + Variants",
        "description": "Always include a global-baseline trial with empty mutations to establish the floor.",
        "evidence_chips": ["startup-yc", "trading-crypto"],
        "evidence_lane": "benchmark_grounded",
        "transferable": True,
    },
    {
        "id": "evidence_lane_separation",
        "label": "Evidence Lane Separation",
        "description": "Keep research_grounded, benchmark_grounded, realworld_validated, and exploratory_frontier structurally distinct.",
        "evidence_chips": ["startup-yc", "trading-crypto", "agentic-marketing"],
        "evidence_lane": "research_grounded",
        "transferable": True,
    },
    {
        "id": "family_priors",
        "label": "Family Priors for Missing Data",
        "description": "When specific data is missing, fall back to family-level priors rather than zero.",
        "evidence_chips": ["startup-yc"],
        "evidence_lane": "benchmark_grounded",
        "transferable": True,
    },
    {
        "id": "doctrine_strategy_separation",
        "label": "Doctrine + Strategy Separation",
        "description": "Separate 'what to believe' (doctrine) from 'how to act' (strategy).",
        "evidence_chips": ["trading-crypto"],
        "evidence_lane": "benchmark_grounded",
        "transferable": True,
    },
    {
        "id": "obsidian_vault_integration",
        "label": "Obsidian Vault Integration",
        "description": "Generate human-readable Obsidian pages for domain knowledge navigation.",
        "evidence_chips": ["startup-yc", "trading-crypto", "agentic-marketing", "roblox-development"],
        "evidence_lane": "benchmark_grounded",
        "transferable": True,
    },
    {
        "id": "zero_external_deps",
        "label": "Zero External Dependencies",
        "description": "Chip base packages have zero dependencies. Domain logic is self-contained.",
        "evidence_chips": ["startup-yc", "trading-crypto", "content", "roblox-development"],
        "evidence_lane": "benchmark_grounded",
        "transferable": True,
    },
    {
        "id": "promotion_discipline",
        "label": "Promotion Discipline",
        "description": "Evidence must flow: exploration -> benchmark -> real-world. No shortcuts to production.",
        "evidence_chips": ["startup-yc", "trading-crypto"],
        "evidence_lane": "research_grounded",
        "transferable": True,
    },
]


# ---------------------------------------------------------------------------
# Chip creation checklist
# ---------------------------------------------------------------------------

CREATION_CHECKLIST: list[dict[str, Any]] = [
    {"step": 1, "label": "Domain Brief", "description": "Document the domain, market, data availability, and benchmark feasibility."},
    {"step": 2, "label": "Source Registry", "description": "Identify the best people, materials, datasets, and feedback loops."},
    {"step": 3, "label": "Manifest Design", "description": "Design spark-chip.json with frontier mutation space."},
    {"step": 4, "label": "Scoring Logic", "description": "Implement deterministic evaluate hook with fixed evaluator."},
    {"step": 5, "label": "Candidate Trials", "description": "Define baseline + at least 2 variant trials."},
    {"step": 6, "label": "Suggest Hook", "description": "Implement suggestion engine for next candidates."},
    {"step": 7, "label": "Packets Hook", "description": "Implement packet emitter with evidence lane separation."},
    {"step": 8, "label": "Watchtower Hook", "description": "Implement Obsidian page generator."},
    {"step": 9, "label": "Project Config", "description": "Create spark-researcher.project.json with guardrails."},
    {"step": 10, "label": "Quality Gate", "description": "Run quality rubric. Score >= 60 for beta."},
    {"step": 11, "label": "Benchmark Pack", "description": "Create at least one benchmark evaluation pack."},
    {"step": 12, "label": "Graduation Review", "description": "Human review of the complete chip."},
]


def get_proven_patterns() -> list[dict[str, Any]]:
    """Return all proven methodology patterns."""
    return PROVEN_PATTERNS


def get_creation_checklist() -> list[dict[str, Any]]:
    """Return the chip creation checklist."""
    return CREATION_CHECKLIST


def get_patterns_for_area(area: str) -> list[dict[str, Any]]:
    """Get methodology patterns relevant to a specific area."""
    area_keywords = {
        "evaluation_frameworks": ["evaluator", "scoring", "metric", "baseline"],
        "evidence_lanes": ["evidence", "lane", "separation", "promotion"],
        "scoring_systems": ["score", "scoring", "rubric", "deterministic"],
        "graduation_criteria": ["graduation", "checklist", "quality", "gate"],
        "frontier_design": ["frontier", "mutation", "bounded", "pattern"],
        "source_registry": ["source", "registry", "data", "material"],
        "packet_quality": ["packet", "document", "promotion", "evidence"],
    }
    keywords = area_keywords.get(area, [])
    if not keywords:
        return PROVEN_PATTERNS

    return [p for p in PROVEN_PATTERNS if any(k in p["description"].lower() for k in keywords)]
