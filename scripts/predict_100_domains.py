"""MiroFish v2: 100-Domain Prediction Run.

Combines all existing domains (10 chips + 22 candidates + 20 viral)
with 48 new domain ideas across AI, creator economy, crypto, dev tools,
business, marketing, finance, lifestyle, and professional services.

Runs the full MiroFish v2 pipeline:
- 1375 agents (11 customer persona types x 125 each)
- 20-round simulation with probabilistic adoption
- Monte Carlo ensemble (10 runs) for confidence intervals
- Per-persona-type breakdown for each domain
- System-level build priority for top domains
- Decision driver analysis
"""

import os
import time
import json
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, "..", "src"))

from chip_labs.mirofish.graph import DomainGraph, build_graph_from_opportunities
from chip_labs.mirofish.personas import generate_personas, CUSTOMER_PERSONAS
from chip_labs.mirofish.simulation import run_simulation, run_ensemble
from chip_labs.mirofish.signals import (
    create_signal, create_shock, signals_from_opportunities, signals_from_graph,
)
from chip_labs.mirofish.systems import compute_system_priority, format_system_priority
from chip_labs.mirofish.report import generate_driver_summary, format_driver_summary


# =============================================================================
# EXISTING CHIPS (10 production/alpha/beta chips)
# =============================================================================
EXISTING_CHIPS = [
    {"domain_id": "startup-yc", "label": "Y Combinator Startup Strategy", "composite_score": 0.88,
     "scores": {"market_size": 0.8, "community_demand": 0.85, "data_availability": 0.9, "benchmark_feasibility": 0.8,
                "monetization_potential": 0.9, "spark_ecosystem_fit": 0.95}, "evidence_sources": ["community", "x_twitter"],
     "related_chips": ["agentic-marketing", "content"], "status": "production",
     "domain_tags": ["speed_to_ship", "idea_validation", "mvp_quality", "market_fit", "roi"]},

    {"domain_id": "trading-crypto", "label": "Crypto Trading Intelligence", "composite_score": 0.86,
     "scores": {"market_size": 0.9, "community_demand": 0.9, "data_availability": 0.85, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.95, "spark_ecosystem_fit": 0.8}, "evidence_sources": ["github", "x_twitter", "community"],
     "related_chips": ["defi-architect"], "status": "production",
     "domain_tags": ["speed", "alpha", "edge", "risk_management", "deal_flow", "portfolio_intelligence"]},

    {"domain_id": "agentic-marketing", "label": "Agentic Marketing Campaigns", "composite_score": 0.84,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.85, "benchmark_feasibility": 0.85,
                "monetization_potential": 0.9, "spark_ecosystem_fit": 0.9}, "evidence_sources": ["community", "producthunt"],
     "related_chips": ["xcontent", "content"], "status": "beta",
     "domain_tags": ["campaign_roi", "attribution", "conversion", "audience_targeting", "content_quality"]},

    {"domain_id": "web-designer", "label": "AI Web Design", "composite_score": 0.78,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.85}, "evidence_sources": ["github", "producthunt"],
     "related_chips": ["content"], "status": "alpha",
     "domain_tags": ["aesthetic_quality", "creative_control", "visual_impact", "speed_to_ship", "productivity"]},

    {"domain_id": "xcontent", "label": "X/Twitter Content Strategy", "composite_score": 0.82,
     "scores": {"market_size": 0.85, "community_demand": 0.85, "data_availability": 0.9, "benchmark_feasibility": 0.8,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.85}, "evidence_sources": ["x_twitter", "community"],
     "related_chips": ["agentic-marketing", "content"], "status": "alpha",
     "domain_tags": ["audience_growth", "content_quality", "distribution", "engagement", "trend_spotting"]},

    {"domain_id": "pokemon-red", "label": "Pokemon Red AI Companion", "composite_score": 0.65,
     "scores": {"market_size": 0.5, "community_demand": 0.6, "data_availability": 0.7, "benchmark_feasibility": 0.8,
                "monetization_potential": 0.4, "spark_ecosystem_fit": 0.6}, "evidence_sources": ["github", "community"],
     "related_chips": ["roblox-development", "game-balance"], "status": "alpha",
     "domain_tags": ["easy_start", "quick_wins"]},

    {"domain_id": "roblox-development", "label": "Roblox Game Development", "composite_score": 0.76,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.7, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.75}, "evidence_sources": ["github", "community"],
     "related_chips": ["game-balance", "pokemon-red"], "status": "alpha",
     "domain_tags": ["creative_control", "code_quality", "easy_start", "quick_wins"]},

    {"domain_id": "vibe-incubator", "label": "Vibe Coding Incubator", "composite_score": 0.72,
     "scores": {"market_size": 0.7, "community_demand": 0.75, "data_availability": 0.65, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.9}, "evidence_sources": ["community", "spark_ecosystem"],
     "related_chips": ["indie-hacker", "startup-yc"], "status": "alpha",
     "domain_tags": ["speed_to_ship", "mvp_quality", "low_learning_curve", "productivity"]},

    {"domain_id": "content", "label": "AI Content Creation", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.75}, "evidence_sources": ["community", "producthunt"],
     "related_chips": ["xcontent", "agentic-marketing"], "status": "alpha",
     "domain_tags": ["content_quality", "audience_growth", "distribution", "time_leverage"]},

    {"domain_id": "predictive-worlds-lab", "label": "Predictive Worlds Research Lab", "composite_score": 0.45,
     "scores": {"market_size": 0.3, "community_demand": 0.3, "data_availability": 0.5, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.3, "spark_ecosystem_fit": 0.7}, "evidence_sources": ["arxiv"],
     "related_chips": [], "status": "alpha",
     "domain_tags": ["infrastructure"]},
]


# =============================================================================
# NEW CANDIDATES (22 from original run)
# =============================================================================
NEW_CANDIDATES = [
    {"domain_id": "defi-architect", "label": "DeFi Protocol Architecture", "composite_score": 0.874,
     "scores": {"market_size": 0.9, "community_demand": 0.85, "data_availability": 0.85, "benchmark_feasibility": 0.8,
                "monetization_potential": 0.95, "spark_ecosystem_fit": 0.85},
     "evidence_sources": ["github", "x_twitter", "vc_landscape"], "related_chips": ["trading-crypto", "solana-dev"],
     "domain_tags": ["alpha", "edge", "infrastructure", "code_quality", "composability"]},

    {"domain_id": "ai-agent-builder", "label": "AI Agent Development Kit", "composite_score": 0.827,
     "scores": {"market_size": 0.9, "community_demand": 0.9, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.9},
     "evidence_sources": ["github", "producthunt", "x_twitter"], "related_chips": ["mcp-server-builder", "prompt-engineer"],
     "domain_tags": ["code_quality", "productivity", "dx", "extensibility", "infrastructure", "composability"]},

    {"domain_id": "indie-hacker", "label": "Indie Hacker Toolkit", "composite_score": 0.798,
     "scores": {"market_size": 0.85, "community_demand": 0.85, "data_availability": 0.8, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.85},
     "evidence_sources": ["x_twitter", "community", "producthunt"], "related_chips": ["startup-yc", "no-code-saas"],
     "domain_tags": ["speed_to_ship", "mvp_quality", "low_cost", "time_leverage", "market_fit"]},

    {"domain_id": "game-balance", "label": "Game Balance & Economy Design", "composite_score": 0.7305,
     "scores": {"market_size": 0.75, "community_demand": 0.7, "data_availability": 0.75, "benchmark_feasibility": 0.8,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "community"], "related_chips": ["roblox-development", "pokemon-red"],
     "domain_tags": ["code_quality", "creative_control", "uniqueness"]},

    {"domain_id": "solana-dev", "label": "Solana Development", "composite_score": 0.8015,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.8},
     "evidence_sources": ["github", "x_twitter", "community"], "related_chips": ["defi-architect", "trading-crypto"],
     "domain_tags": ["code_quality", "speed", "infrastructure", "developer_adoption", "composability"]},

    {"domain_id": "prompt-engineer", "label": "Prompt Engineering Mastery", "composite_score": 0.8235,
     "scores": {"market_size": 0.9, "community_demand": 0.85, "data_availability": 0.85, "benchmark_feasibility": 0.8,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.85},
     "evidence_sources": ["github", "x_twitter", "community"], "related_chips": ["ai-agent-builder"],
     "domain_tags": ["productivity", "dx", "quick_wins", "low_learning_curve", "extensibility"]},

    {"domain_id": "newsletter-growth", "label": "Newsletter Growth Engine", "composite_score": 0.719,
     "scores": {"market_size": 0.75, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["community", "producthunt"], "related_chips": ["content", "xcontent"],
     "domain_tags": ["audience_growth", "content_quality", "distribution", "conversion", "time_leverage"]},

    {"domain_id": "security-audit", "label": "Security Audit Automation", "composite_score": 0.78,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.8, "benchmark_feasibility": 0.8,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.75},
     "evidence_sources": ["github", "community"], "related_chips": ["compliance-shield"],
     "domain_tags": ["code_quality", "infrastructure", "risk_management", "api_quality"]},

    {"domain_id": "personal-finance", "label": "Personal Finance AI", "composite_score": 0.7435,
     "scores": {"market_size": 0.85, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["community", "producthunt"], "related_chips": ["trading-crypto"],
     "domain_tags": ["roi", "portfolio_intelligence", "simplicity", "low_learning_curve"]},

    {"domain_id": "sales-closer", "label": "AI Sales Closer", "composite_score": 0.7265,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["community", "producthunt"], "related_chips": ["agentic-marketing"],
     "domain_tags": ["conversion", "campaign_roi", "attribution", "speed"]},

    {"domain_id": "devrel-community", "label": "DevRel & Community Building", "composite_score": 0.6645,
     "scores": {"market_size": 0.7, "community_demand": 0.65, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["community", "github"], "related_chips": ["open-source-maintainer"],
     "domain_tags": ["developer_adoption", "audience_growth", "engagement", "distribution"]},

    {"domain_id": "education-tutor", "label": "AI Education Tutor", "composite_score": 0.7385,
     "scores": {"market_size": 0.85, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["community", "producthunt"], "related_chips": ["prompt-engineer"],
     "domain_tags": ["low_learning_curve", "easy_start", "quick_wins", "simplicity"]},

    {"domain_id": "video-creator", "label": "AI Video Production", "composite_score": 0.686,
     "scores": {"market_size": 0.8, "community_demand": 0.65, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "x_twitter"], "related_chips": ["content", "tiktok-creator"],
     "domain_tags": ["content_quality", "creative_control", "visual_impact", "audience_growth"]},

    {"domain_id": "data-engineer", "label": "Data Engineering Pipeline", "composite_score": 0.786,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.85, "benchmark_feasibility": 0.8,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.75},
     "evidence_sources": ["github", "community"], "related_chips": ["ai-agent-builder"],
     "domain_tags": ["code_quality", "infrastructure", "productivity", "api_quality"]},

    {"domain_id": "real-estate-analyst", "label": "Real Estate AI Analyst", "composite_score": 0.698,
     "scores": {"market_size": 0.8, "community_demand": 0.65, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community"], "related_chips": ["personal-finance"],
     "domain_tags": ["deal_flow", "portfolio_intelligence", "roi", "alpha"]},

    {"domain_id": "resume-career", "label": "AI Resume & Career Coach", "composite_score": 0.7215,
     "scores": {"market_size": 0.85, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": [],
     "domain_tags": ["quick_wins", "easy_start", "outcompete", "simplicity"]},

    {"domain_id": "compliance-shield", "label": "Compliance Automation", "composite_score": 0.6765,
     "scores": {"market_size": 0.7, "community_demand": 0.6, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community"], "related_chips": ["security-audit", "legal-ops"],
     "domain_tags": ["risk_management", "infrastructure", "api_quality"]},

    {"domain_id": "legal-ops", "label": "Legal Operations AI", "composite_score": 0.6445,
     "scores": {"market_size": 0.7, "community_demand": 0.55, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community"], "related_chips": ["compliance-shield"],
     "domain_tags": ["risk_management", "time_leverage", "productivity"]},

    {"domain_id": "open-source-maintainer", "label": "Open Source Maintainer Tools", "composite_score": 0.7455,
     "scores": {"market_size": 0.7, "community_demand": 0.75, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.6, "spark_ecosystem_fit": 0.8},
     "evidence_sources": ["github", "community"], "related_chips": ["devrel-community", "github-actions"],
     "domain_tags": ["code_quality", "developer_adoption", "infrastructure", "composability"]},

    {"domain_id": "health-wellness", "label": "Health & Wellness AI", "composite_score": 0.6595,
     "scores": {"market_size": 0.8, "community_demand": 0.6, "data_availability": 0.6, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community"], "related_chips": [],
     "domain_tags": ["easy_start", "quick_wins", "simplicity"]},

    {"domain_id": "music-producer", "label": "AI Music Production", "composite_score": 0.6195,
     "scores": {"market_size": 0.7, "community_demand": 0.6, "data_availability": 0.6, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.6, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community", "producthunt"], "related_chips": ["content"],
     "domain_tags": ["creative_control", "uniqueness", "aesthetic_quality"]},

    {"domain_id": "supply-chain", "label": "Supply Chain Optimization", "composite_score": 0.618,
     "scores": {"market_size": 0.7, "community_demand": 0.5, "data_availability": 0.65, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["community"], "related_chips": [],
     "domain_tags": ["infrastructure", "roi", "time_leverage"]},
]


# =============================================================================
# VIRAL DOMAINS (20 from viral run)
# =============================================================================
VIRAL_DOMAINS = [
    {"domain_id": "meme-coin-launcher", "label": "Meme Coin Launch Strategy", "composite_score": 0.82,
     "scores": {"market_size": 0.95, "community_demand": 0.9, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.9, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["trading-crypto", "crypto-airdrop"],
     "domain_tags": ["speed", "first_mover", "trend_spotting", "early_access", "alpha"]},

    {"domain_id": "tiktok-creator", "label": "TikTok Content Strategy", "composite_score": 0.80,
     "scores": {"market_size": 0.95, "community_demand": 0.85, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["x_twitter", "community", "producthunt"], "related_chips": ["content", "video-creator"],
     "domain_tags": ["audience_growth", "content_quality", "distribution", "engagement", "creative_control", "visual_impact", "trend_spotting"]},

    {"domain_id": "mcp-server-builder", "label": "MCP Server Development", "composite_score": 0.81,
     "scores": {"market_size": 0.85, "community_demand": 0.9, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.95},
     "evidence_sources": ["github", "x_twitter", "community"], "related_chips": ["ai-agent-builder", "cursor-copilot"],
     "domain_tags": ["code_quality", "productivity", "dx", "extensibility", "infrastructure", "api_quality", "composability", "developer_adoption"]},

    {"domain_id": "cursor-copilot", "label": "AI Coding Workflow", "composite_score": 0.83,
     "scores": {"market_size": 0.9, "community_demand": 0.9, "data_availability": 0.8, "benchmark_feasibility": 0.8,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.85},
     "evidence_sources": ["github", "x_twitter", "producthunt"], "related_chips": ["mcp-server-builder", "ai-agent-builder"],
     "domain_tags": ["productivity", "code_quality", "dx", "speed", "extensibility", "quick_wins"]},

    {"domain_id": "discord-community", "label": "Discord Community Management", "composite_score": 0.76,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.75},
     "evidence_sources": ["community", "x_twitter"], "related_chips": ["devrel-community"],
     "domain_tags": ["engagement", "audience_growth", "distribution", "developer_adoption"]},

    {"domain_id": "linkedin-ghostwriter", "label": "LinkedIn Thought Leadership", "composite_score": 0.79,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["xcontent", "content"],
     "domain_tags": ["content_quality", "audience_growth", "distribution", "campaign_roi", "conversion"]},

    {"domain_id": "midjourney-art", "label": "Midjourney Art Direction", "composite_score": 0.68,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community", "x_twitter"], "related_chips": ["ai-avatar", "web-designer"],
     "domain_tags": ["aesthetic_quality", "creative_control", "uniqueness", "visual_impact"]},

    {"domain_id": "telegram-miniapp", "label": "Telegram Mini App Builder", "composite_score": 0.77,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.75},
     "evidence_sources": ["github", "x_twitter", "community"], "related_chips": ["meme-coin-launcher", "crypto-airdrop"],
     "domain_tags": ["speed_to_ship", "first_mover", "infrastructure", "developer_adoption"]},

    {"domain_id": "no-code-saas", "label": "No-Code SaaS Builder", "composite_score": 0.78,
     "scores": {"market_size": 0.9, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.75},
     "evidence_sources": ["producthunt", "community", "x_twitter"], "related_chips": ["indie-hacker", "supabase-fullstack"],
     "domain_tags": ["speed_to_ship", "low_cost", "simplicity", "all_in_one", "mvp_quality", "low_learning_curve"]},

    {"domain_id": "crypto-airdrop", "label": "Crypto Airdrop Farming", "composite_score": 0.73,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["meme-coin-launcher", "onchain-analytics"],
     "domain_tags": ["early_access", "first_mover", "alpha", "speed", "trend_spotting"]},

    {"domain_id": "ai-voice-clone", "label": "AI Voice Cloning Studio", "composite_score": 0.67,
     "scores": {"market_size": 0.75, "community_demand": 0.65, "data_availability": 0.65, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["podcast-producer", "ai-avatar"],
     "domain_tags": ["creative_control", "uniqueness", "content_quality"]},

    {"domain_id": "shopify-growth", "label": "Shopify Store Growth", "composite_score": 0.74,
     "scores": {"market_size": 0.85, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["seo-dominator", "sales-closer"],
     "domain_tags": ["conversion", "campaign_roi", "roi", "audience_targeting"]},

    {"domain_id": "supabase-fullstack", "label": "Supabase Full-Stack Development", "composite_score": 0.79,
     "scores": {"market_size": 0.8, "community_demand": 0.8, "data_availability": 0.8, "benchmark_feasibility": 0.8,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.85},
     "evidence_sources": ["github", "x_twitter", "producthunt"], "related_chips": ["mcp-server-builder", "cursor-copilot"],
     "domain_tags": ["code_quality", "productivity", "dx", "speed_to_ship", "infrastructure", "api_quality"]},

    {"domain_id": "github-actions", "label": "GitHub Actions Automation", "composite_score": 0.72,
     "scores": {"market_size": 0.75, "community_demand": 0.7, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.6, "spark_ecosystem_fit": 0.75},
     "evidence_sources": ["github", "community"], "related_chips": ["open-source-maintainer", "devops-pipeline"],
     "domain_tags": ["code_quality", "infrastructure", "productivity", "developer_adoption", "composability"]},

    {"domain_id": "seo-dominator", "label": "SEO Domination Strategy", "composite_score": 0.75,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["community", "producthunt"], "related_chips": ["content", "newsletter-growth"],
     "domain_tags": ["audience_growth", "distribution", "conversion", "campaign_roi"]},

    {"domain_id": "onchain-analytics", "label": "On-Chain Analytics", "composite_score": 0.78,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "x_twitter"], "related_chips": ["trading-crypto", "defi-architect"],
     "domain_tags": ["alpha", "portfolio_intelligence", "deal_flow", "edge", "infrastructure"]},

    {"domain_id": "podcast-producer", "label": "AI Podcast Production", "composite_score": 0.71,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["content", "ai-voice-clone"],
     "domain_tags": ["content_quality", "audience_growth", "distribution", "time_leverage"]},

    {"domain_id": "browser-extension", "label": "Browser Extension Builder", "composite_score": 0.72,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "producthunt"], "related_chips": ["cursor-copilot"],
     "domain_tags": ["productivity", "dx", "speed_to_ship", "extensibility"]},

    {"domain_id": "twitter-threads", "label": "X/Twitter Thread Mastery", "composite_score": 0.76,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.8, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["xcontent", "linkedin-ghostwriter"],
     "domain_tags": ["content_quality", "audience_growth", "engagement", "distribution", "trend_spotting"]},

    {"domain_id": "ai-avatar", "label": "AI Avatar & Digital Presence", "composite_score": 0.69,
     "scores": {"market_size": 0.75, "community_demand": 0.65, "data_availability": 0.65, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "x_twitter"], "related_chips": ["midjourney-art", "ai-voice-clone"],
     "domain_tags": ["aesthetic_quality", "creative_control", "uniqueness", "visual_impact"]},
]


# =============================================================================
# 48 NEW DOMAIN IDEAS (to reach 100 total)
# =============================================================================
NEW_48_DOMAINS = [
    # --- AI Power Users (8) ---
    {"domain_id": "rag-pipeline", "label": "RAG Pipeline Architecture", "composite_score": 0.81,
     "scores": {"market_size": 0.85, "community_demand": 0.85, "data_availability": 0.8, "benchmark_feasibility": 0.8,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.85},
     "evidence_sources": ["github", "x_twitter", "community"], "related_chips": ["ai-agent-builder", "prompt-engineer"],
     "domain_tags": ["code_quality", "productivity", "infrastructure", "extensibility", "api_quality"]},

    {"domain_id": "ai-customer-support", "label": "AI Customer Support Agent", "composite_score": 0.79,
     "scores": {"market_size": 0.9, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["ai-agent-builder", "sales-closer"],
     "domain_tags": ["conversion", "time_leverage", "all_in_one", "roi", "low_cost"]},

    {"domain_id": "llm-evaluator", "label": "LLM Benchmark & Evaluation", "composite_score": 0.77,
     "scores": {"market_size": 0.75, "community_demand": 0.8, "data_availability": 0.85, "benchmark_feasibility": 0.85,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.8},
     "evidence_sources": ["github", "arxiv", "community"], "related_chips": ["ai-agent-builder", "prompt-engineer"],
     "domain_tags": ["code_quality", "infrastructure", "api_quality", "dx"]},

    {"domain_id": "ai-code-review", "label": "AI Code Review Assistant", "composite_score": 0.78,
     "scores": {"market_size": 0.8, "community_demand": 0.8, "data_availability": 0.8, "benchmark_feasibility": 0.8,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.8},
     "evidence_sources": ["github", "producthunt"], "related_chips": ["cursor-copilot", "security-audit"],
     "domain_tags": ["code_quality", "productivity", "dx", "risk_management"]},

    {"domain_id": "fine-tuning-lab", "label": "Model Fine-Tuning Studio", "composite_score": 0.76,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.75},
     "evidence_sources": ["github", "arxiv"], "related_chips": ["llm-evaluator", "ai-agent-builder"],
     "domain_tags": ["code_quality", "infrastructure", "extensibility", "developer_adoption"]},

    {"domain_id": "ai-workflow-automation", "label": "AI Workflow Automation (n8n/Make)", "composite_score": 0.80,
     "scores": {"market_size": 0.9, "community_demand": 0.85, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.75},
     "evidence_sources": ["producthunt", "community", "x_twitter"], "related_chips": ["no-code-saas", "ai-agent-builder"],
     "domain_tags": ["time_leverage", "all_in_one", "simplicity", "low_cost", "productivity", "low_learning_curve"]},

    {"domain_id": "ai-data-analyst", "label": "AI Data Analyst (chat-with-CSV)", "composite_score": 0.78,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["producthunt", "github", "community"], "related_chips": ["data-engineer", "prompt-engineer"],
     "domain_tags": ["quick_wins", "low_learning_curve", "productivity", "easy_start", "roi"]},

    {"domain_id": "voice-ai-app", "label": "Voice AI Application Builder", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["producthunt", "github"], "related_chips": ["ai-voice-clone", "ai-customer-support"],
     "domain_tags": ["creative_control", "uniqueness", "dx", "extensibility"]},

    # --- Creator Economy (7) ---
    {"domain_id": "youtube-optimizer", "label": "YouTube Growth Optimizer", "composite_score": 0.79,
     "scores": {"market_size": 0.9, "community_demand": 0.8, "data_availability": 0.8, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["x_twitter", "community", "producthunt"], "related_chips": ["tiktok-creator", "video-creator"],
     "domain_tags": ["audience_growth", "content_quality", "distribution", "engagement", "campaign_roi"]},

    {"domain_id": "substack-writer", "label": "Substack Newsletter Writer", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["newsletter-growth", "content"],
     "domain_tags": ["content_quality", "audience_growth", "distribution", "time_leverage"]},

    {"domain_id": "course-creator", "label": "Online Course Creator", "composite_score": 0.76,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["education-tutor", "content"],
     "domain_tags": ["content_quality", "roi", "audience_growth", "time_leverage", "mvp_quality"]},

    {"domain_id": "ebook-publisher", "label": "AI eBook Publisher", "composite_score": 0.70,
     "scores": {"market_size": 0.75, "community_demand": 0.65, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community", "producthunt"], "related_chips": ["content", "substack-writer"],
     "domain_tags": ["content_quality", "time_leverage", "roi", "creative_control"]},

    {"domain_id": "twitch-streamer", "label": "Twitch Stream Optimizer", "composite_score": 0.68,
     "scores": {"market_size": 0.75, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community", "x_twitter"], "related_chips": ["discord-community", "video-creator"],
     "domain_tags": ["audience_growth", "engagement", "content_quality", "creative_control"]},

    {"domain_id": "instagram-growth", "label": "Instagram Growth Engine", "composite_score": 0.77,
     "scores": {"market_size": 0.9, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["tiktok-creator", "midjourney-art"],
     "domain_tags": ["audience_growth", "visual_impact", "engagement", "distribution", "aesthetic_quality"]},

    {"domain_id": "notion-second-brain", "label": "Notion Second Brain System", "composite_score": 0.75,
     "scores": {"market_size": 0.8, "community_demand": 0.8, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["producthunt", "community", "x_twitter"], "related_chips": ["prompt-engineer"],
     "domain_tags": ["productivity", "simplicity", "all_in_one", "time_leverage", "low_learning_curve"]},

    # --- Business & SaaS (7) ---
    {"domain_id": "saas-metrics", "label": "SaaS Metrics Dashboard", "composite_score": 0.76,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["indie-hacker", "startup-yc"],
     "domain_tags": ["roi", "attribution", "campaign_roi", "portfolio_intelligence"]},

    {"domain_id": "cold-email-outbound", "label": "AI Cold Email & Outbound", "composite_score": 0.77,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["sales-closer", "agentic-marketing"],
     "domain_tags": ["conversion", "campaign_roi", "audience_targeting", "speed", "roi"]},

    {"domain_id": "pitch-deck-builder", "label": "AI Pitch Deck Creator", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["startup-yc", "indie-hacker"],
     "domain_tags": ["speed_to_ship", "mvp_quality", "idea_validation", "visual_impact", "quick_wins"]},

    {"domain_id": "product-hunt-launcher", "label": "Product Hunt Launch Playbook", "composite_score": 0.73,
     "scores": {"market_size": 0.75, "community_demand": 0.8, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["producthunt", "community", "x_twitter"], "related_chips": ["indie-hacker", "startup-yc"],
     "domain_tags": ["first_mover", "audience_growth", "distribution", "trend_spotting", "speed"]},

    {"domain_id": "pricing-optimizer", "label": "SaaS Pricing Optimizer", "composite_score": 0.72,
     "scores": {"market_size": 0.75, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community"], "related_chips": ["saas-metrics", "startup-yc"],
     "domain_tags": ["roi", "conversion", "market_fit", "attribution"]},

    {"domain_id": "crm-builder", "label": "Custom CRM Builder", "composite_score": 0.71,
     "scores": {"market_size": 0.8, "community_demand": 0.65, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["sales-closer", "no-code-saas"],
     "domain_tags": ["all_in_one", "simplicity", "time_leverage", "conversion"]},

    {"domain_id": "customer-research", "label": "AI Customer Research", "composite_score": 0.73,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["community", "producthunt"], "related_chips": ["startup-yc", "sales-closer"],
     "domain_tags": ["idea_validation", "market_fit", "audience_targeting", "roi"]},

    # --- Crypto & Web3 (4) ---
    {"domain_id": "nft-collection", "label": "NFT Collection Launch", "composite_score": 0.71,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.65, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["midjourney-art", "meme-coin-launcher"],
     "domain_tags": ["creative_control", "first_mover", "early_access", "visual_impact", "trend_spotting"]},

    {"domain_id": "dao-governance", "label": "DAO Governance Toolkit", "composite_score": 0.69,
     "scores": {"market_size": 0.7, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["github", "x_twitter"], "related_chips": ["defi-architect", "onchain-analytics"],
     "domain_tags": ["infrastructure", "composability", "developer_adoption"]},

    {"domain_id": "token-launch", "label": "Token Launch & Tokenomics", "composite_score": 0.74,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.65, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["meme-coin-launcher", "defi-architect"],
     "domain_tags": ["first_mover", "alpha", "speed", "early_access", "roi"]},

    {"domain_id": "depin-builder", "label": "DePIN Infrastructure Builder", "composite_score": 0.70,
     "scores": {"market_size": 0.75, "community_demand": 0.7, "data_availability": 0.6, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["github", "x_twitter"], "related_chips": ["solana-dev", "defi-architect"],
     "domain_tags": ["infrastructure", "composability", "first_mover", "developer_adoption"]},

    # --- Development (5) ---
    {"domain_id": "api-monetization", "label": "API-as-Product Monetization", "composite_score": 0.75,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "producthunt"], "related_chips": ["mcp-server-builder", "ai-agent-builder"],
     "domain_tags": ["api_quality", "developer_adoption", "infrastructure", "roi", "composability"]},

    {"domain_id": "saas-boilerplate", "label": "SaaS Boilerplate Generator", "composite_score": 0.78,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.8},
     "evidence_sources": ["github", "producthunt"], "related_chips": ["supabase-fullstack", "indie-hacker"],
     "domain_tags": ["speed_to_ship", "code_quality", "productivity", "dx", "mvp_quality"]},

    {"domain_id": "mobile-app-builder", "label": "Cross-Platform Mobile App Builder", "composite_score": 0.77,
     "scores": {"market_size": 0.9, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "producthunt"], "related_chips": ["no-code-saas", "supabase-fullstack"],
     "domain_tags": ["speed_to_ship", "code_quality", "dx", "mvp_quality", "all_in_one"]},

    {"domain_id": "devops-pipeline", "label": "DevOps CI/CD Pipeline", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "community"], "related_chips": ["github-actions", "security-audit"],
     "domain_tags": ["infrastructure", "code_quality", "productivity", "developer_adoption"]},

    {"domain_id": "database-architect", "label": "Database Schema Architect", "composite_score": 0.73,
     "scores": {"market_size": 0.75, "community_demand": 0.7, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "community"], "related_chips": ["supabase-fullstack", "data-engineer"],
     "domain_tags": ["code_quality", "infrastructure", "api_quality", "extensibility"]},

    # --- Marketing & Growth (6) ---
    {"domain_id": "influencer-marketing", "label": "Influencer Marketing Manager", "composite_score": 0.76,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["agentic-marketing", "tiktok-creator"],
     "domain_tags": ["campaign_roi", "audience_targeting", "attribution", "engagement", "distribution"]},

    {"domain_id": "community-growth", "label": "Community Growth Playbook", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.75},
     "evidence_sources": ["community", "x_twitter"], "related_chips": ["discord-community", "devrel-community"],
     "domain_tags": ["audience_growth", "engagement", "distribution", "developer_adoption"]},

    {"domain_id": "email-marketing", "label": "AI Email Marketing", "composite_score": 0.75,
     "scores": {"market_size": 0.85, "community_demand": 0.7, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["cold-email-outbound", "newsletter-growth"],
     "domain_tags": ["conversion", "campaign_roi", "audience_targeting", "attribution", "time_leverage"]},

    {"domain_id": "conversion-optimizer", "label": "Conversion Rate Optimizer", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["seo-dominator", "sales-closer"],
     "domain_tags": ["conversion", "roi", "attribution", "campaign_roi"]},

    {"domain_id": "affiliate-marketing", "label": "Affiliate Marketing Automation", "composite_score": 0.73,
     "scores": {"market_size": 0.85, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community", "x_twitter"], "related_chips": ["seo-dominator", "shopify-growth"],
     "domain_tags": ["roi", "conversion", "distribution", "time_leverage"]},

    {"domain_id": "viral-growth-hacker", "label": "Viral Growth Hacking", "composite_score": 0.77,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["product-hunt-launcher", "agentic-marketing"],
     "domain_tags": ["first_mover", "trend_spotting", "audience_growth", "speed", "distribution"]},

    # --- Finance & Trading (3) ---
    {"domain_id": "quant-strategy", "label": "Quantitative Trading Strategy", "composite_score": 0.78,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.85, "benchmark_feasibility": 0.8,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "community"], "related_chips": ["trading-crypto", "data-engineer"],
     "domain_tags": ["alpha", "speed", "edge", "risk_management", "code_quality", "infrastructure"]},

    {"domain_id": "options-trader", "label": "Options Trading Intelligence", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community", "x_twitter"], "related_chips": ["trading-crypto", "quant-strategy"],
     "domain_tags": ["alpha", "risk_management", "speed", "edge", "portfolio_intelligence"]},

    {"domain_id": "stock-screener", "label": "AI Stock Screener", "composite_score": 0.76,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["community", "github"], "related_chips": ["trading-crypto", "personal-finance"],
     "domain_tags": ["alpha", "deal_flow", "portfolio_intelligence", "roi", "edge"]},

    # --- Lifestyle & Personal (5) ---
    {"domain_id": "productivity-system", "label": "AI Productivity System", "composite_score": 0.77,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["producthunt", "community", "x_twitter"], "related_chips": ["notion-second-brain"],
     "domain_tags": ["productivity", "time_leverage", "simplicity", "all_in_one", "quick_wins"]},

    {"domain_id": "habit-tracker", "label": "AI Habit & Behavior Design", "composite_score": 0.71,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["health-wellness"],
     "domain_tags": ["easy_start", "quick_wins", "simplicity", "low_learning_curve"]},

    {"domain_id": "fitness-coach", "label": "AI Fitness Coach", "composite_score": 0.72,
     "scores": {"market_size": 0.85, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["health-wellness"],
     "domain_tags": ["easy_start", "quick_wins", "outcompete", "simplicity"]},

    {"domain_id": "language-learner", "label": "AI Language Learning Tutor", "composite_score": 0.75,
     "scores": {"market_size": 0.9, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["education-tutor"],
     "domain_tags": ["easy_start", "low_learning_curve", "quick_wins", "outcompete"]},

    {"domain_id": "travel-planner", "label": "AI Travel Planner", "composite_score": 0.73,
     "scores": {"market_size": 0.85, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": [],
     "domain_tags": ["simplicity", "time_leverage", "quick_wins", "all_in_one"]},

    # --- Professional Services (3) ---
    {"domain_id": "freelance-scaler", "label": "Freelance Agency Scaler", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["community", "x_twitter"], "related_chips": ["indie-hacker", "sales-closer"],
     "domain_tags": ["time_leverage", "roi", "speed_to_ship", "conversion", "all_in_one"]},

    {"domain_id": "grant-writer", "label": "AI Grant Writer", "composite_score": 0.70,
     "scores": {"market_size": 0.7, "community_demand": 0.65, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community"], "related_chips": ["content"],
     "domain_tags": ["content_quality", "time_leverage", "roi"]},

    {"domain_id": "proposal-writer", "label": "AI Business Proposal Writer", "composite_score": 0.72,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community", "producthunt"], "related_chips": ["sales-closer", "content"],
     "domain_tags": ["content_quality", "conversion", "time_leverage", "roi", "speed"]},
]


# =============================================================================
# COMBINE ALL 100 DOMAINS
# =============================================================================
ALL_100_DOMAINS = EXISTING_CHIPS + NEW_CANDIDATES + VIRAL_DOMAINS + NEW_48_DOMAINS


# =============================================================================
# RELATIONSHIPS (cross-domain connections)
# =============================================================================
RELATIONSHIPS = [
    # Existing chip connections
    {"source": "startup-yc", "target": "agentic-marketing", "relationship": "ENABLES", "weight": 0.8},
    {"source": "startup-yc", "target": "content", "relationship": "ENABLES", "weight": 0.7},
    {"source": "trading-crypto", "target": "defi-architect", "relationship": "EXTENDS", "weight": 0.9},
    {"source": "agentic-marketing", "target": "xcontent", "relationship": "EXTENDS", "weight": 0.85},
    {"source": "agentic-marketing", "target": "content", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "roblox-development", "target": "game-balance", "relationship": "ENABLES", "weight": 0.85},

    # AI/Dev tool cluster
    {"source": "ai-agent-builder", "target": "mcp-server-builder", "relationship": "ENABLES", "weight": 0.9},
    {"source": "ai-agent-builder", "target": "prompt-engineer", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "cursor-copilot", "target": "mcp-server-builder", "relationship": "ENABLES", "weight": 0.85},
    {"source": "cursor-copilot", "target": "ai-code-review", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "mcp-server-builder", "target": "supabase-fullstack", "relationship": "ENABLES", "weight": 0.75},
    {"source": "rag-pipeline", "target": "ai-agent-builder", "relationship": "ENABLES", "weight": 0.85},
    {"source": "rag-pipeline", "target": "ai-customer-support", "relationship": "ENABLES", "weight": 0.8},
    {"source": "llm-evaluator", "target": "fine-tuning-lab", "relationship": "ENABLES", "weight": 0.8},
    {"source": "ai-workflow-automation", "target": "no-code-saas", "relationship": "EXTENDS", "weight": 0.75},
    {"source": "saas-boilerplate", "target": "supabase-fullstack", "relationship": "EXTENDS", "weight": 0.85},
    {"source": "saas-boilerplate", "target": "indie-hacker", "relationship": "ENABLES", "weight": 0.8},
    {"source": "github-actions", "target": "devops-pipeline", "relationship": "EXTENDS", "weight": 0.85},
    {"source": "database-architect", "target": "supabase-fullstack", "relationship": "ENABLES", "weight": 0.8},

    # Crypto cluster
    {"source": "meme-coin-launcher", "target": "crypto-airdrop", "relationship": "EXTENDS", "weight": 0.85},
    {"source": "meme-coin-launcher", "target": "token-launch", "relationship": "EXTENDS", "weight": 0.9},
    {"source": "defi-architect", "target": "solana-dev", "relationship": "ENABLES", "weight": 0.85},
    {"source": "defi-architect", "target": "onchain-analytics", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "defi-architect", "target": "dao-governance", "relationship": "EXTENDS", "weight": 0.7},
    {"source": "onchain-analytics", "target": "trading-crypto", "relationship": "ENABLES", "weight": 0.8},
    {"source": "telegram-miniapp", "target": "meme-coin-launcher", "relationship": "EXTENDS", "weight": 0.75},
    {"source": "nft-collection", "target": "midjourney-art", "relationship": "ENABLES", "weight": 0.75},
    {"source": "depin-builder", "target": "solana-dev", "relationship": "EXTENDS", "weight": 0.7},

    # Content & creator cluster
    {"source": "tiktok-creator", "target": "video-creator", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "tiktok-creator", "target": "youtube-optimizer", "relationship": "COMPETES_WITH", "weight": 0.6},
    {"source": "linkedin-ghostwriter", "target": "xcontent", "relationship": "COMPETES_WITH", "weight": 0.5},
    {"source": "twitter-threads", "target": "xcontent", "relationship": "EXTENDS", "weight": 0.85},
    {"source": "content", "target": "substack-writer", "relationship": "ENABLES", "weight": 0.8},
    {"source": "content", "target": "course-creator", "relationship": "ENABLES", "weight": 0.75},
    {"source": "newsletter-growth", "target": "substack-writer", "relationship": "EXTENDS", "weight": 0.85},
    {"source": "podcast-producer", "target": "ai-voice-clone", "relationship": "ENABLES", "weight": 0.7},
    {"source": "instagram-growth", "target": "tiktok-creator", "relationship": "COMPETES_WITH", "weight": 0.65},
    {"source": "midjourney-art", "target": "ai-avatar", "relationship": "ENABLES", "weight": 0.75},

    # Marketing & growth cluster
    {"source": "agentic-marketing", "target": "influencer-marketing", "relationship": "ENABLES", "weight": 0.8},
    {"source": "agentic-marketing", "target": "email-marketing", "relationship": "EXTENDS", "weight": 0.75},
    {"source": "seo-dominator", "target": "conversion-optimizer", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "seo-dominator", "target": "affiliate-marketing", "relationship": "ENABLES", "weight": 0.7},
    {"source": "cold-email-outbound", "target": "sales-closer", "relationship": "ENABLES", "weight": 0.85},
    {"source": "viral-growth-hacker", "target": "product-hunt-launcher", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "community-growth", "target": "discord-community", "relationship": "EXTENDS", "weight": 0.8},

    # Business cluster
    {"source": "indie-hacker", "target": "no-code-saas", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "indie-hacker", "target": "startup-yc", "relationship": "ENABLES", "weight": 0.7},
    {"source": "saas-metrics", "target": "pricing-optimizer", "relationship": "ENABLES", "weight": 0.75},
    {"source": "customer-research", "target": "startup-yc", "relationship": "ENABLES", "weight": 0.75},
    {"source": "pitch-deck-builder", "target": "startup-yc", "relationship": "ENABLES", "weight": 0.7},

    # Finance cluster
    {"source": "quant-strategy", "target": "trading-crypto", "relationship": "EXTENDS", "weight": 0.85},
    {"source": "options-trader", "target": "trading-crypto", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "stock-screener", "target": "personal-finance", "relationship": "EXTENDS", "weight": 0.7},

    # Lifestyle cluster
    {"source": "notion-second-brain", "target": "productivity-system", "relationship": "EXTENDS", "weight": 0.85},
    {"source": "education-tutor", "target": "language-learner", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "health-wellness", "target": "fitness-coach", "relationship": "EXTENDS", "weight": 0.8},

    # Professional services
    {"source": "freelance-scaler", "target": "proposal-writer", "relationship": "ENABLES", "weight": 0.75},
    {"source": "sales-closer", "target": "proposal-writer", "relationship": "EXTENDS", "weight": 0.7},

    # Cross-cluster bridges
    {"source": "ai-data-analyst", "target": "saas-metrics", "relationship": "ENABLES", "weight": 0.7},
    {"source": "ai-data-analyst", "target": "stock-screener", "relationship": "ENABLES", "weight": 0.65},
    {"source": "mobile-app-builder", "target": "telegram-miniapp", "relationship": "ENABLES", "weight": 0.7},
    {"source": "voice-ai-app", "target": "ai-customer-support", "relationship": "EXTENDS", "weight": 0.75},
    {"source": "browser-extension", "target": "productivity-system", "relationship": "ENABLES", "weight": 0.65},
    {"source": "devrel-community", "target": "open-source-maintainer", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "api-monetization", "target": "mcp-server-builder", "relationship": "EXTENDS", "weight": 0.75},
    {"source": "shopify-growth", "target": "conversion-optimizer", "relationship": "EXTENDS", "weight": 0.75},
]


# =============================================================================
# MAIN
# =============================================================================
def main():
    t0 = time.time()
    n = len(ALL_100_DOMAINS)
    domain_ids_set = {d["domain_id"] for d in ALL_100_DOMAINS}
    assert len(domain_ids_set) == n, f"Duplicate domain_ids found! {n} domains but {len(domain_ids_set)} unique"

    print("=" * 80)
    print(f"MIROFISH v2: 100-DOMAIN PREDICTION RUN")
    print(f"Domains: {len(EXISTING_CHIPS)} existing + {len(NEW_CANDIDATES)} candidates + {len(VIRAL_DOMAINS)} viral + {len(NEW_48_DOMAINS)} new = {n} total")
    print(f"Personas: 11 types x 125 each = 1375 agents")
    print("=" * 80)
    print()

    # Build graph
    graph = DomainGraph()
    for d in ALL_100_DOMAINS:
        graph.add_node(d["domain_id"], "domain", d.get("label", d["domain_id"]),
                       {"domain_tags": d.get("domain_tags", [])})

    # Add technology/platform nodes for graph edges
    tech_nodes = {"ai-tools", "blockchain", "web-platform", "social-media", "saas-infra"}
    for t in tech_nodes:
        graph.add_node(t, "technology", t)
    for d in ALL_100_DOMAINS:
        for src in d.get("evidence_sources", []):
            if src == "github":
                graph.add_edge("ai-tools", d["domain_id"], "ENABLES", 0.5)
            elif src == "x_twitter":
                graph.add_edge("social-media", d["domain_id"], "ENABLES", 0.4)

    graph_from_opps = build_graph_from_opportunities(ALL_100_DOMAINS)
    for node_id, node_data in graph_from_opps.nodes.items():
        if node_id not in graph.nodes:
            graph.add_node(node_id, node_data["type"], node_data["label"], node_data.get("properties", {}))
    for edge in graph_from_opps.edges:
        graph.add_edge(edge["source"], edge["target"], edge["relationship"], edge.get("weight", 0.5))

    for r in RELATIONSHIPS:
        if r["source"] in graph.nodes and r["target"] in graph.nodes:
            graph.add_edge(r["source"], r["target"], r["relationship"], r.get("weight", 0.5))

    print(f"Graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")

    # Generate signals
    domain_ids = [d["domain_id"] for d in ALL_100_DOMAINS]
    opp_signals = signals_from_opportunities(ALL_100_DOMAINS)
    graph_signals = signals_from_graph(graph)
    all_signals = opp_signals + graph_signals
    print(f"Signals: {len(opp_signals)} opportunity + {len(graph_signals)} graph = {len(all_signals)} total")

    # Generate personas
    personas = generate_personas(graph, domain_ids=domain_ids, count_per_type=125, seed=42)
    print(f"Personas: {len(personas)} agents across {len(set(p['persona_type'] for p in personas))} types")
    print()

    # --- Flagship simulation ---
    print("--- Flagship Simulation (1375 agents, 100 domains, 20 rounds) ---")
    t1 = time.time()
    result = run_simulation(graph, domain_ids, personas=personas, signals=all_signals, max_rounds=20, seed=42)
    t2 = time.time()
    evals = len(personas) * len(domain_ids) * 20
    print(f"Simulation: {t2 - t1:.1f}s ({evals:,} persona-domain-round evaluations)")
    print()

    # --- Monte Carlo ensemble ---
    print("--- Monte Carlo Ensemble (10 runs x 240 agents) ---")
    t3 = time.time()
    ensemble = run_ensemble(graph, domain_ids, n_runs=5, count_per_type=20,
                            signals=all_signals, max_rounds=20, base_seed=42)
    t4 = time.time()
    print(f"Ensemble: {t4 - t3:.1f}s")
    print()

    total_time = time.time() - t0
    print(f"Total wall time: {total_time:.1f}s")
    print()

    # ==========================================================================
    # RESULTS
    # ==========================================================================
    # Collect per-domain results
    domain_results = []
    for d in ALL_100_DOMAINS:
        d_id = d["domain_id"]
        sim_data = result["domains"].get(d_id, {})
        ens_data = ensemble["domains"].get(d_id, {})

        adoption = sim_data.get("final_adoption_rate", 0.0)
        advocacy = sim_data.get("final_advocacy_rate", 0.0)
        by_type = sim_data.get("adoption_by_persona_type", {})
        ens_mean = ens_data.get("mean_adoption", 0.0)
        ens_std = ens_data.get("std_adoption", 0.0)
        p10 = ens_data.get("p10_adoption", 0.0)
        p90 = ens_data.get("p90_adoption", 0.0)

        domain_results.append({
            "domain_id": d_id,
            "label": d.get("label", d_id),
            "status": d.get("status", "new"),
            "static_score": d.get("composite_score", 0.0),
            "adoption": adoption,
            "advocacy": advocacy,
            "ens_mean": ens_mean,
            "ens_std": ens_std,
            "p10": p10,
            "p90": p90,
            "by_type": by_type,
            "domain_tags": d.get("domain_tags", []),
        })

    domain_results.sort(key=lambda x: x["ens_mean"], reverse=True)

    # Print rankings
    print("=" * 100)
    print("TOP 20 DOMAINS (sorted by ensemble mean adoption)")
    print("=" * 100)
    print(f"{'#':>3}  {'Domain':<28} {'Ens Mean':>9} {'P10-P90':>12} {'Builder':>8} {'Advocacy':>9} {'Static':>7}")
    print("-" * 100)
    for i, dr in enumerate(domain_results[:20], 1):
        status = f" [{dr['status']}]" if dr['status'] != 'new' else ""
        print(f"{i:>3}  {dr['domain_id']:<28} {dr['ens_mean']:>8.1%} {dr['p10']:>5.0%}-{dr['p90']:<5.0%} {dr['adoption']:>8.1%} {dr['advocacy']:>8.1%} {dr['static_score']:>7.4f}{status}")

    print()
    print("=" * 100)
    print("MIDDLE 30 (ranks 21-50)")
    print("=" * 100)
    print(f"{'#':>3}  {'Domain':<28} {'Ens Mean':>9} {'P10-P90':>12} {'Builder':>8}")
    print("-" * 80)
    for i, dr in enumerate(domain_results[20:50], 21):
        print(f"{i:>3}  {dr['domain_id']:<28} {dr['ens_mean']:>8.1%} {dr['p10']:>5.0%}-{dr['p90']:<5.0%} {dr['adoption']:>8.1%}")

    print()
    print("=" * 100)
    print("BOTTOM 20 (lowest adoption signal)")
    print("=" * 100)
    print(f"{'#':>3}  {'Domain':<28} {'Ens Mean':>9} {'P10-P90':>12} {'Builder':>8}")
    print("-" * 80)
    for i, dr in enumerate(domain_results[-20:], len(domain_results) - 19):
        print(f"{i:>3}  {dr['domain_id']:<28} {dr['ens_mean']:>8.1%} {dr['p10']:>5.0%}-{dr['p90']:<5.0%} {dr['adoption']:>8.1%}")

    # ==========================================================================
    # PER-PERSONA BREAKDOWN for top 5
    # ==========================================================================
    print()
    print("=" * 100)
    print("PER-PERSONA BREAKDOWN (top 5 domains)")
    print("=" * 100)
    for dr in domain_results[:5]:
        d_id = dr["domain_id"]
        print(f"\n--- {d_id} (overall {dr['ens_mean']:.0%}) ---")
        by_type = dr["by_type"]
        sorted_types = sorted(by_type.items(), key=lambda x: x[1]["adoption_rate"], reverse=True)
        for ptype, stats in sorted_types:
            rate = stats["adoption_rate"]
            adv = stats["advocacy_rate"]
            bar = "#" * int(rate * 30)
            print(f"  {ptype:22s} {rate:5.0%} {bar}")

        # Driver summary
        summary = generate_driver_summary(personas, d_id)
        print()
        for s in summary["type_summaries"][:3]:
            vals = ", ".join(s["top_matched_values"]) if s["top_matched_values"] else "none"
            print(f"  Why {s['persona_type']}: fit={s['avg_fit_score']:.2f} values=[{vals}]")
            print(f"    {s['reason']}")

    # ==========================================================================
    # SYSTEM BUILD PRIORITY for top 5
    # ==========================================================================
    print()
    print("=" * 100)
    print("SYSTEM BUILD PRIORITY (what to build FIRST inside top domains)")
    print("=" * 100)
    for dr in domain_results[:5]:
        d_id = dr["domain_id"]
        by_type = dr["by_type"]
        ranked = compute_system_priority(d_id, by_type)
        if ranked:
            print()
            print(format_system_priority(d_id, ranked))
        else:
            print(f"\n  {d_id}: no system definitions yet (add to DOMAIN_SYSTEMS)")

    # ==========================================================================
    # CATEGORY ANALYSIS
    # ==========================================================================
    print()
    print("=" * 100)
    print("CATEGORY ANALYSIS (average adoption by category)")
    print("=" * 100)

    categories = {
        "Existing Chips": [d["domain_id"] for d in EXISTING_CHIPS],
        "Original Candidates": [d["domain_id"] for d in NEW_CANDIDATES],
        "Viral Domains": [d["domain_id"] for d in VIRAL_DOMAINS],
        "New Ideas": [d["domain_id"] for d in NEW_48_DOMAINS],
    }

    dr_map = {dr["domain_id"]: dr for dr in domain_results}
    for cat_name, cat_ids in categories.items():
        cat_results = [dr_map[d_id] for d_id in cat_ids if d_id in dr_map]
        avg_ens = sum(dr["ens_mean"] for dr in cat_results) / max(len(cat_results), 1)
        avg_adv = sum(dr["advocacy"] for dr in cat_results) / max(len(cat_results), 1)
        top = max(cat_results, key=lambda x: x["ens_mean"]) if cat_results else None
        bot = min(cat_results, key=lambda x: x["ens_mean"]) if cat_results else None
        print(f"\n  {cat_name} ({len(cat_results)} domains)")
        print(f"    Avg adoption: {avg_ens:.1%}  Avg advocacy: {avg_adv:.1%}")
        if top:
            print(f"    Best:  {top['domain_id']} ({top['ens_mean']:.1%})")
        if bot:
            print(f"    Worst: {bot['domain_id']} ({bot['ens_mean']:.1%})")

    # ==========================================================================
    # PERSONA TYPE PREFERENCES (which types love which categories)
    # ==========================================================================
    print()
    print("=" * 100)
    print("PERSONA TYPE PREFERENCES (top domain for each persona type)")
    print("=" * 100)
    for ptype in CUSTOMER_PERSONAS:
        best_domain = None
        best_rate = 0.0
        for dr in domain_results:
            rate = dr["by_type"].get(ptype, {}).get("adoption_rate", 0.0)
            if rate > best_rate:
                best_rate = rate
                best_domain = dr["domain_id"]
        if best_domain:
            print(f"  {ptype:22s} -> {best_domain:<28s} ({best_rate:.0%} adoption)")

    # ==========================================================================
    # EXPORT
    # ==========================================================================
    export = {
        "run_metadata": {
            "total_domains": n,
            "total_personas": len(personas),
            "persona_types": len(CUSTOMER_PERSONAS),
            "ensemble_runs": 10,
            "total_time_seconds": round(total_time, 1),
        },
        "rankings": [
            {
                "rank": i + 1,
                "domain_id": dr["domain_id"],
                "label": dr["label"],
                "status": dr["status"],
                "ensemble_mean": round(dr["ens_mean"], 4),
                "p10": round(dr["p10"], 4),
                "p90": round(dr["p90"], 4),
                "builder_adoption": round(dr["adoption"], 4),
                "advocacy": round(dr["advocacy"], 4),
                "static_score": dr["static_score"],
                "per_persona": {
                    ptype: {"adoption": round(stats["adoption_rate"], 4), "advocacy": round(stats["advocacy_rate"], 4)}
                    for ptype, stats in dr["by_type"].items()
                },
            }
            for i, dr in enumerate(domain_results)
        ],
    }

    output_path = os.path.join(script_dir, "..", "viz", "100_domain_predictions.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(export, f, indent=2)
    print(f"\nExported to {output_path}")

    print()
    print("=" * 100)
    print("DONE")
    print(f"100 domains evaluated by 1375 agents in {total_time:.0f}s")
    print("=" * 100)


if __name__ == "__main__":
    main()
