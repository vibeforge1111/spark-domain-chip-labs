"""MiroFish v3: 250-Domain Prediction with Per-Persona Top-10 Recommendations.

Expands the domain universe from 100 to 250 chips across 15+ verticals.
Each of the 11 persona types recommends their personal top 10.

Runs the full MiroFish v2 pipeline:
- 1375 agents (11 customer persona types x 125 each)
- 20-round simulation with probabilistic adoption
- Monte Carlo ensemble (5 runs) for confidence intervals
- Per-persona-type top-10 picks
- Cross-persona consensus analysis
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
# IMPORT ALL 100 EXISTING DOMAINS FROM predict_100_domains.py
# =============================================================================
from predict_100_domains import (
    EXISTING_CHIPS, NEW_CANDIDATES, VIRAL_DOMAINS, NEW_48_DOMAINS,
    RELATIONSHIPS,
)

FIRST_100 = EXISTING_CHIPS + NEW_CANDIDATES + VIRAL_DOMAINS + NEW_48_DOMAINS


# =============================================================================
# 150 NEW DOMAINS (to reach 250 total)
# =============================================================================
NEW_150_DOMAINS = [
    # --- AI Infrastructure & DevTools (15) ---
    {"domain_id": "vector-db-ops", "label": "Vector Database Operations", "composite_score": 0.79,
     "scores": {"market_size": 0.8, "community_demand": 0.8, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.8},
     "evidence_sources": ["github", "community"], "related_chips": ["rag-pipeline", "ai-agent-builder"],
     "domain_tags": ["infrastructure", "code_quality", "dx", "extensibility"]},

    {"domain_id": "ai-testing-qa", "label": "AI-Powered QA & Testing", "composite_score": 0.77,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.8, "benchmark_feasibility": 0.8,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.75},
     "evidence_sources": ["github", "producthunt"], "related_chips": ["ai-code-review", "cursor-copilot"],
     "domain_tags": ["code_quality", "productivity", "dx", "infrastructure"]},

    {"domain_id": "edge-ai-deploy", "label": "Edge AI Deployment", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["github", "arxiv"], "related_chips": ["ai-agent-builder", "mobile-app-builder"],
     "domain_tags": ["infrastructure", "speed", "code_quality", "developer_adoption"]},

    {"domain_id": "ai-observability", "label": "AI Observability & Monitoring", "composite_score": 0.78,
     "scores": {"market_size": 0.8, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.75},
     "evidence_sources": ["github", "producthunt"], "related_chips": ["llm-evaluator", "devops-pipeline"],
     "domain_tags": ["infrastructure", "code_quality", "risk_management", "api_quality"]},

    {"domain_id": "multi-modal-ai", "label": "Multi-Modal AI Applications", "composite_score": 0.80,
     "scores": {"market_size": 0.85, "community_demand": 0.85, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.8},
     "evidence_sources": ["github", "arxiv", "x_twitter"], "related_chips": ["ai-agent-builder", "rag-pipeline"],
     "domain_tags": ["code_quality", "extensibility", "infrastructure", "composability"]},

    {"domain_id": "ai-safety-alignment", "label": "AI Safety & Alignment", "composite_score": 0.72,
     "scores": {"market_size": 0.7, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.6, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["arxiv", "github", "community"], "related_chips": ["llm-evaluator", "prompt-engineer"],
     "domain_tags": ["risk_management", "infrastructure", "code_quality"]},

    {"domain_id": "synthetic-data-gen", "label": "Synthetic Data Generation", "composite_score": 0.76,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "arxiv"], "related_chips": ["fine-tuning-lab", "llm-evaluator"],
     "domain_tags": ["code_quality", "infrastructure", "extensibility"]},

    {"domain_id": "ai-gateway-proxy", "label": "AI Gateway & Proxy Router", "composite_score": 0.77,
     "scores": {"market_size": 0.8, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.75},
     "evidence_sources": ["github", "producthunt"], "related_chips": ["ai-agent-builder", "api-monetization"],
     "domain_tags": ["infrastructure", "api_quality", "composability", "dx"]},

    {"domain_id": "ai-docs-writer", "label": "AI Documentation Writer", "composite_score": 0.75,
     "scores": {"market_size": 0.75, "community_demand": 0.75, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.75},
     "evidence_sources": ["github", "community"], "related_chips": ["cursor-copilot", "devrel-community"],
     "domain_tags": ["content_quality", "productivity", "dx", "developer_adoption"]},

    {"domain_id": "cli-tool-builder", "label": "CLI Tool Builder", "composite_score": 0.73,
     "scores": {"market_size": 0.7, "community_demand": 0.75, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.75},
     "evidence_sources": ["github", "community"], "related_chips": ["cursor-copilot", "mcp-server-builder"],
     "domain_tags": ["code_quality", "dx", "productivity", "extensibility"]},

    {"domain_id": "kubernetes-ops", "label": "Kubernetes Operations AI", "composite_score": 0.75,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["github", "community"], "related_chips": ["devops-pipeline", "database-architect"],
     "domain_tags": ["infrastructure", "code_quality", "risk_management"]},

    {"domain_id": "terraform-iac", "label": "Terraform Infrastructure-as-Code", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.75, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "community"], "related_chips": ["devops-pipeline", "kubernetes-ops"],
     "domain_tags": ["infrastructure", "code_quality", "extensibility"]},

    {"domain_id": "graphql-api", "label": "GraphQL API Design", "composite_score": 0.73,
     "scores": {"market_size": 0.75, "community_demand": 0.7, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "community"], "related_chips": ["api-monetization", "supabase-fullstack"],
     "domain_tags": ["code_quality", "api_quality", "dx", "extensibility"]},

    {"domain_id": "websocket-realtime", "label": "Real-Time WebSocket Apps", "composite_score": 0.72,
     "scores": {"market_size": 0.75, "community_demand": 0.7, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "community"], "related_chips": ["supabase-fullstack", "discord-community"],
     "domain_tags": ["infrastructure", "speed", "dx", "developer_adoption"]},

    {"domain_id": "rust-systems", "label": "Rust Systems Programming", "composite_score": 0.74,
     "scores": {"market_size": 0.75, "community_demand": 0.75, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "community"], "related_chips": ["solana-dev", "cli-tool-builder"],
     "domain_tags": ["code_quality", "speed", "infrastructure", "developer_adoption"]},

    # --- Web3 & DeFi Expanded (12) ---
    {"domain_id": "base-l2-dev", "label": "Base L2 Development", "composite_score": 0.78,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "x_twitter"], "related_chips": ["defi-architect", "solana-dev"],
     "domain_tags": ["code_quality", "infrastructure", "developer_adoption", "speed"]},

    {"domain_id": "cross-chain-bridge", "label": "Cross-Chain Bridge Builder", "composite_score": 0.73,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["github", "x_twitter"], "related_chips": ["defi-architect", "solana-dev"],
     "domain_tags": ["infrastructure", "code_quality", "composability", "risk_management"]},

    {"domain_id": "wallet-ux", "label": "Crypto Wallet UX Design", "composite_score": 0.75,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["web-designer", "telegram-miniapp"],
     "domain_tags": ["simplicity", "low_learning_curve", "aesthetic_quality", "dx"]},

    {"domain_id": "mev-protection", "label": "MEV Protection Strategies", "composite_score": 0.76,
     "scores": {"market_size": 0.75, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "x_twitter"], "related_chips": ["defi-architect", "trading-crypto"],
     "domain_tags": ["alpha", "edge", "risk_management", "speed"]},

    {"domain_id": "staking-yield", "label": "Staking & Yield Optimization", "composite_score": 0.77,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["defi-architect", "trading-crypto"],
     "domain_tags": ["roi", "portfolio_intelligence", "alpha", "risk_management"]},

    {"domain_id": "social-fi", "label": "Social-Fi Applications", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["meme-coin-launcher", "discord-community"],
     "domain_tags": ["audience_growth", "first_mover", "engagement", "trend_spotting"]},

    {"domain_id": "prediction-market", "label": "Prediction Market Builder", "composite_score": 0.76,
     "scores": {"market_size": 0.8, "community_demand": 0.8, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["x_twitter", "community", "github"], "related_chips": ["defi-architect", "onchain-analytics"],
     "domain_tags": ["alpha", "deal_flow", "roi", "trend_spotting"]},

    {"domain_id": "rwa-tokenization", "label": "Real World Asset Tokenization", "composite_score": 0.75,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["x_twitter", "vc_landscape"], "related_chips": ["defi-architect", "real-estate-analyst"],
     "domain_tags": ["infrastructure", "roi", "deal_flow", "first_mover"]},

    {"domain_id": "zk-proof-dev", "label": "Zero-Knowledge Proof Development", "composite_score": 0.72,
     "scores": {"market_size": 0.75, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["github", "arxiv"], "related_chips": ["solana-dev", "defi-architect"],
     "domain_tags": ["code_quality", "infrastructure", "developer_adoption"]},

    {"domain_id": "gaming-nft", "label": "Gaming NFT Economy", "composite_score": 0.71,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["nft-collection", "game-balance"],
     "domain_tags": ["creative_control", "first_mover", "audience_growth", "trend_spotting"]},

    {"domain_id": "ai-agent-token", "label": "AI Agent Token Launch", "composite_score": 0.79,
     "scores": {"market_size": 0.9, "community_demand": 0.85, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.9, "spark_ecosystem_fit": 0.75},
     "evidence_sources": ["x_twitter", "community", "github"], "related_chips": ["ai-agent-builder", "token-launch"],
     "domain_tags": ["first_mover", "alpha", "trend_spotting", "speed", "early_access"]},

    {"domain_id": "perpetuals-trading", "label": "Perpetual Futures Trading", "composite_score": 0.77,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.8, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["trading-crypto", "options-trader"],
     "domain_tags": ["alpha", "speed", "edge", "risk_management"]},

    # --- Creator Economy Expanded (12) ---
    {"domain_id": "ai-ghostwriter", "label": "AI Ghostwriting Service", "composite_score": 0.76,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["content", "linkedin-ghostwriter"],
     "domain_tags": ["content_quality", "time_leverage", "roi", "conversion"]},

    {"domain_id": "podcast-clipper", "label": "Podcast to Short-Form Clipper", "composite_score": 0.75,
     "scores": {"market_size": 0.8, "community_demand": 0.8, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "x_twitter"], "related_chips": ["podcast-producer", "tiktok-creator"],
     "domain_tags": ["content_quality", "distribution", "time_leverage", "audience_growth"]},

    {"domain_id": "thumbnail-designer", "label": "AI Thumbnail Designer", "composite_score": 0.73,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["youtube-optimizer", "midjourney-art"],
     "domain_tags": ["visual_impact", "aesthetic_quality", "engagement", "conversion"]},

    {"domain_id": "social-media-scheduler", "label": "AI Social Media Scheduler", "composite_score": 0.76,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["xcontent", "instagram-growth"],
     "domain_tags": ["time_leverage", "distribution", "productivity", "all_in_one"]},

    {"domain_id": "brand-voice-ai", "label": "AI Brand Voice Creator", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["content", "ai-ghostwriter"],
     "domain_tags": ["content_quality", "uniqueness", "creative_control", "aesthetic_quality"]},

    {"domain_id": "meme-generator", "label": "AI Meme Generator", "composite_score": 0.71,
     "scores": {"market_size": 0.75, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["midjourney-art", "xcontent"],
     "domain_tags": ["engagement", "trend_spotting", "creative_control", "audience_growth"]},

    {"domain_id": "faceless-youtube", "label": "Faceless YouTube Channel", "composite_score": 0.75,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["x_twitter", "community", "producthunt"], "related_chips": ["youtube-optimizer", "video-creator"],
     "domain_tags": ["roi", "time_leverage", "audience_growth", "low_cost"]},

    {"domain_id": "whatsapp-bot", "label": "WhatsApp Business Bot", "composite_score": 0.74,
     "scores": {"market_size": 0.85, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community", "producthunt"], "related_chips": ["ai-customer-support", "telegram-miniapp"],
     "domain_tags": ["conversion", "audience_targeting", "simplicity", "roi"]},

    {"domain_id": "community-course", "label": "Cohort-Based Course Builder", "composite_score": 0.73,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community", "producthunt"], "related_chips": ["course-creator", "discord-community"],
     "domain_tags": ["roi", "audience_growth", "engagement", "content_quality"]},

    {"domain_id": "digital-products", "label": "Digital Product Store Builder", "composite_score": 0.74,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community", "producthunt"], "related_chips": ["indie-hacker", "shopify-growth"],
     "domain_tags": ["roi", "speed_to_ship", "low_cost", "time_leverage"]},

    {"domain_id": "reddit-marketing", "label": "Reddit Marketing Strategy", "composite_score": 0.72,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community", "x_twitter"], "related_chips": ["agentic-marketing", "seo-dominator"],
     "domain_tags": ["audience_growth", "distribution", "engagement", "audience_targeting"]},

    {"domain_id": "twitter-ads", "label": "X/Twitter Ads Optimizer", "composite_score": 0.74,
     "scores": {"market_size": 0.85, "community_demand": 0.7, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["x_twitter", "community"], "related_chips": ["xcontent", "agentic-marketing"],
     "domain_tags": ["campaign_roi", "conversion", "audience_targeting", "attribution"]},

    # --- Business & Enterprise (15) ---
    {"domain_id": "hr-recruiter", "label": "AI HR & Recruiting", "composite_score": 0.76,
     "scores": {"market_size": 0.85, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["resume-career", "sales-closer"],
     "domain_tags": ["time_leverage", "roi", "productivity", "conversion"]},

    {"domain_id": "meeting-assistant", "label": "AI Meeting Assistant", "composite_score": 0.77,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["productivity-system", "sales-closer"],
     "domain_tags": ["time_leverage", "productivity", "quick_wins", "all_in_one"]},

    {"domain_id": "invoice-payments", "label": "AI Invoicing & Payments", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["freelance-scaler", "saas-metrics"],
     "domain_tags": ["time_leverage", "roi", "simplicity", "all_in_one"]},

    {"domain_id": "competitive-intel", "label": "Competitive Intelligence AI", "composite_score": 0.76,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["startup-yc", "customer-research"],
     "domain_tags": ["alpha", "market_fit", "deal_flow", "edge"]},

    {"domain_id": "contract-drafter", "label": "AI Contract Drafter", "composite_score": 0.73,
     "scores": {"market_size": 0.8, "community_demand": 0.65, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["legal-ops", "proposal-writer"],
     "domain_tags": ["time_leverage", "risk_management", "roi", "productivity"]},

    {"domain_id": "accounting-bookkeeper", "label": "AI Bookkeeping", "composite_score": 0.75,
     "scores": {"market_size": 0.85, "community_demand": 0.7, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["personal-finance", "invoice-payments"],
     "domain_tags": ["time_leverage", "roi", "simplicity", "productivity"]},

    {"domain_id": "inventory-manager", "label": "AI Inventory Management", "composite_score": 0.72,
     "scores": {"market_size": 0.8, "community_demand": 0.65, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community"], "related_chips": ["supply-chain", "shopify-growth"],
     "domain_tags": ["roi", "time_leverage", "productivity"]},

    {"domain_id": "market-research-ai", "label": "AI Market Research", "composite_score": 0.76,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["customer-research", "competitive-intel"],
     "domain_tags": ["idea_validation", "market_fit", "roi", "deal_flow"]},

    {"domain_id": "support-ticket-ai", "label": "Support Ticket Automation", "composite_score": 0.76,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["ai-customer-support", "crm-builder"],
     "domain_tags": ["time_leverage", "roi", "low_cost", "productivity"]},

    {"domain_id": "ecommerce-analytics", "label": "E-Commerce Analytics AI", "composite_score": 0.75,
     "scores": {"market_size": 0.85, "community_demand": 0.7, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["shopify-growth", "saas-metrics"],
     "domain_tags": ["roi", "attribution", "campaign_roi", "conversion"]},

    {"domain_id": "event-planner", "label": "AI Event Planning", "composite_score": 0.70,
     "scores": {"market_size": 0.75, "community_demand": 0.65, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community"], "related_chips": ["community-growth", "product-hunt-launcher"],
     "domain_tags": ["time_leverage", "all_in_one", "simplicity"]},

    {"domain_id": "b2b-lead-gen", "label": "B2B Lead Generation AI", "composite_score": 0.77,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["cold-email-outbound", "sales-closer"],
     "domain_tags": ["conversion", "deal_flow", "roi", "audience_targeting"]},

    {"domain_id": "ad-creative-gen", "label": "AI Ad Creative Generator", "composite_score": 0.76,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "x_twitter"], "related_chips": ["agentic-marketing", "midjourney-art"],
     "domain_tags": ["visual_impact", "campaign_roi", "conversion", "creative_control"]},

    {"domain_id": "churn-predictor", "label": "Churn Prediction AI", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.75, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community", "github"], "related_chips": ["saas-metrics", "ai-data-analyst"],
     "domain_tags": ["roi", "risk_management", "attribution", "portfolio_intelligence"]},

    {"domain_id": "loyalty-rewards", "label": "AI Loyalty & Rewards Program", "composite_score": 0.71,
     "scores": {"market_size": 0.8, "community_demand": 0.65, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community"], "related_chips": ["shopify-growth", "community-growth"],
     "domain_tags": ["engagement", "conversion", "audience_growth", "roi"]},

    # --- Education & Knowledge (10) ---
    {"domain_id": "flashcard-ai", "label": "AI Flashcard & Spaced Repetition", "composite_score": 0.73,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["education-tutor", "language-learner"],
     "domain_tags": ["easy_start", "low_learning_curve", "quick_wins"]},

    {"domain_id": "research-assistant", "label": "AI Research Paper Assistant", "composite_score": 0.76,
     "scores": {"market_size": 0.8, "community_demand": 0.8, "data_availability": 0.8, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "arxiv", "community"], "related_chips": ["rag-pipeline", "prompt-engineer"],
     "domain_tags": ["productivity", "content_quality", "time_leverage", "quick_wins"]},

    {"domain_id": "exam-prep", "label": "AI Exam Preparation", "composite_score": 0.74,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["education-tutor", "flashcard-ai"],
     "domain_tags": ["quick_wins", "easy_start", "outcompete"]},

    {"domain_id": "knowledge-graph", "label": "Personal Knowledge Graph Builder", "composite_score": 0.73,
     "scores": {"market_size": 0.75, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "community"], "related_chips": ["notion-second-brain", "rag-pipeline"],
     "domain_tags": ["productivity", "extensibility", "infrastructure"]},

    {"domain_id": "coding-tutor", "label": "AI Coding Bootcamp Tutor", "composite_score": 0.75,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "github", "community"], "related_chips": ["education-tutor", "cursor-copilot"],
     "domain_tags": ["easy_start", "low_learning_curve", "code_quality", "quick_wins"]},

    {"domain_id": "book-summarizer", "label": "AI Book Summarizer", "composite_score": 0.72,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["content", "research-assistant"],
     "domain_tags": ["time_leverage", "quick_wins", "content_quality"]},

    {"domain_id": "debate-coach", "label": "AI Debate & Argumentation Coach", "composite_score": 0.68,
     "scores": {"market_size": 0.65, "community_demand": 0.65, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.6, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community"], "related_chips": ["education-tutor", "prompt-engineer"],
     "domain_tags": ["quick_wins", "outcompete", "content_quality"]},

    {"domain_id": "math-solver", "label": "AI Math & Science Solver", "composite_score": 0.75,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["education-tutor", "exam-prep"],
     "domain_tags": ["quick_wins", "easy_start", "outcompete", "low_learning_curve"]},

    {"domain_id": "writing-coach", "label": "AI Creative Writing Coach", "composite_score": 0.73,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["content", "ebook-publisher"],
     "domain_tags": ["content_quality", "creative_control", "quick_wins"]},

    {"domain_id": "certification-prep", "label": "IT Certification Prep AI", "composite_score": 0.72,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community"], "related_chips": ["exam-prep", "coding-tutor"],
     "domain_tags": ["quick_wins", "outcompete", "easy_start"]},

    # --- Lifestyle & Wellness (10) ---
    {"domain_id": "meal-planner", "label": "AI Meal Planning & Recipes", "composite_score": 0.73,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["health-wellness", "fitness-coach"],
     "domain_tags": ["simplicity", "easy_start", "quick_wins"]},

    {"domain_id": "meditation-mindfulness", "label": "AI Meditation & Mindfulness", "composite_score": 0.68,
     "scores": {"market_size": 0.75, "community_demand": 0.65, "data_availability": 0.6, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["health-wellness"],
     "domain_tags": ["easy_start", "simplicity", "quick_wins"]},

    {"domain_id": "fashion-stylist", "label": "AI Fashion & Style Advisor", "composite_score": 0.71,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["midjourney-art"],
     "domain_tags": ["aesthetic_quality", "creative_control", "simplicity"]},

    {"domain_id": "pet-care-ai", "label": "AI Pet Care & Training", "composite_score": 0.68,
     "scores": {"market_size": 0.75, "community_demand": 0.65, "data_availability": 0.6, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.45},
     "evidence_sources": ["community"], "related_chips": ["health-wellness"],
     "domain_tags": ["easy_start", "simplicity", "quick_wins"]},

    {"domain_id": "dating-coach", "label": "AI Dating & Relationship Coach", "composite_score": 0.70,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.6, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.45},
     "evidence_sources": ["community"], "related_chips": [],
     "domain_tags": ["quick_wins", "outcompete", "simplicity"]},

    {"domain_id": "home-decorator", "label": "AI Interior Design", "composite_score": 0.72,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["web-designer", "midjourney-art"],
     "domain_tags": ["aesthetic_quality", "visual_impact", "creative_control"]},

    {"domain_id": "sleep-optimizer", "label": "AI Sleep Optimization", "composite_score": 0.67,
     "scores": {"market_size": 0.75, "community_demand": 0.65, "data_availability": 0.6, "benchmark_feasibility": 0.55,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.45},
     "evidence_sources": ["community"], "related_chips": ["health-wellness", "habit-tracker"],
     "domain_tags": ["quick_wins", "easy_start", "simplicity"]},

    {"domain_id": "astrology-ai", "label": "AI Astrology & Horoscope", "composite_score": 0.66,
     "scores": {"market_size": 0.75, "community_demand": 0.7, "data_availability": 0.6, "benchmark_feasibility": 0.55,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.4},
     "evidence_sources": ["community"], "related_chips": [],
     "domain_tags": ["engagement", "audience_growth", "quick_wins"]},

    {"domain_id": "garden-planner", "label": "AI Garden & Plant Care", "composite_score": 0.66,
     "scores": {"market_size": 0.7, "community_demand": 0.65, "data_availability": 0.6, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.6, "spark_ecosystem_fit": 0.45},
     "evidence_sources": ["community"], "related_chips": [],
     "domain_tags": ["easy_start", "simplicity", "quick_wins"]},

    {"domain_id": "parenting-ai", "label": "AI Parenting Guide", "composite_score": 0.70,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.6, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.45},
     "evidence_sources": ["community"], "related_chips": ["education-tutor"],
     "domain_tags": ["easy_start", "simplicity", "quick_wins"]},

    # --- Gaming & Entertainment (10) ---
    {"domain_id": "unity-gamedev", "label": "Unity Game Development AI", "composite_score": 0.75,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["github", "community"], "related_chips": ["roblox-development", "game-balance"],
     "domain_tags": ["code_quality", "creative_control", "easy_start"]},

    {"domain_id": "unreal-gamedev", "label": "Unreal Engine AI Toolkit", "composite_score": 0.73,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["github", "community"], "related_chips": ["unity-gamedev", "game-balance"],
     "domain_tags": ["code_quality", "creative_control", "visual_impact"]},

    {"domain_id": "tabletop-rpg", "label": "AI Tabletop RPG Game Master", "composite_score": 0.70,
     "scores": {"market_size": 0.7, "community_demand": 0.75, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community", "producthunt"], "related_chips": ["game-balance", "ai-voice-clone"],
     "domain_tags": ["creative_control", "engagement", "uniqueness"]},

    {"domain_id": "esports-analytics", "label": "Esports Analytics AI", "composite_score": 0.72,
     "scores": {"market_size": 0.75, "community_demand": 0.7, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community", "x_twitter"], "related_chips": ["game-balance", "twitch-streamer"],
     "domain_tags": ["alpha", "edge", "portfolio_intelligence"]},

    {"domain_id": "game-modding", "label": "AI Game Modding Toolkit", "composite_score": 0.70,
     "scores": {"market_size": 0.7, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.6, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["github", "community"], "related_chips": ["roblox-development", "unity-gamedev"],
     "domain_tags": ["creative_control", "easy_start", "uniqueness"]},

    {"domain_id": "interactive-fiction", "label": "AI Interactive Fiction Writer", "composite_score": 0.69,
     "scores": {"market_size": 0.65, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.6, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["community", "producthunt"], "related_chips": ["writing-coach", "tabletop-rpg"],
     "domain_tags": ["creative_control", "content_quality", "uniqueness"]},

    {"domain_id": "sports-betting", "label": "Sports Betting Analytics", "composite_score": 0.75,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.8, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community", "x_twitter"], "related_chips": ["trading-crypto", "prediction-market"],
     "domain_tags": ["alpha", "edge", "roi", "speed"]},

    {"domain_id": "music-playlist", "label": "AI Music Playlist Curator", "composite_score": 0.68,
     "scores": {"market_size": 0.75, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.6, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["community"], "related_chips": ["music-producer"],
     "domain_tags": ["easy_start", "simplicity", "aesthetic_quality"]},

    {"domain_id": "trivia-quiz", "label": "AI Trivia & Quiz Generator", "composite_score": 0.67,
     "scores": {"market_size": 0.7, "community_demand": 0.65, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.55, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community"], "related_chips": ["education-tutor", "discord-community"],
     "domain_tags": ["engagement", "easy_start", "quick_wins"]},

    {"domain_id": "fan-fiction", "label": "AI Fan Fiction Generator", "composite_score": 0.65,
     "scores": {"market_size": 0.65, "community_demand": 0.7, "data_availability": 0.6, "benchmark_feasibility": 0.55,
                "monetization_potential": 0.55, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["community"], "related_chips": ["writing-coach", "interactive-fiction"],
     "domain_tags": ["creative_control", "engagement", "content_quality"]},

    # --- Science & Engineering (8) ---
    {"domain_id": "biotech-lab", "label": "AI Biotech Lab Assistant", "composite_score": 0.72,
     "scores": {"market_size": 0.75, "community_demand": 0.65, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["arxiv", "github"], "related_chips": ["research-assistant"],
     "domain_tags": ["infrastructure", "code_quality", "productivity"]},

    {"domain_id": "cad-3d-design", "label": "AI 3D CAD Design", "composite_score": 0.71,
     "scores": {"market_size": 0.75, "community_demand": 0.65, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["github", "community"], "related_chips": ["web-designer"],
     "domain_tags": ["creative_control", "visual_impact", "productivity"]},

    {"domain_id": "climate-analytics", "label": "Climate Data Analytics", "composite_score": 0.69,
     "scores": {"market_size": 0.7, "community_demand": 0.65, "data_availability": 0.75, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.6, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["arxiv", "github"], "related_chips": ["data-engineer", "ai-data-analyst"],
     "domain_tags": ["infrastructure", "code_quality"]},

    {"domain_id": "robotics-controller", "label": "AI Robotics Controller", "composite_score": 0.70,
     "scores": {"market_size": 0.75, "community_demand": 0.65, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["arxiv", "github"], "related_chips": ["edge-ai-deploy"],
     "domain_tags": ["infrastructure", "code_quality", "speed"]},

    {"domain_id": "drug-discovery", "label": "AI Drug Discovery", "composite_score": 0.71,
     "scores": {"market_size": 0.8, "community_demand": 0.6, "data_availability": 0.65, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.45},
     "evidence_sources": ["arxiv"], "related_chips": ["biotech-lab"],
     "domain_tags": ["infrastructure", "roi"]},

    {"domain_id": "materials-science", "label": "AI Materials Science", "composite_score": 0.67,
     "scores": {"market_size": 0.7, "community_demand": 0.55, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.45},
     "evidence_sources": ["arxiv"], "related_chips": ["biotech-lab"],
     "domain_tags": ["infrastructure"]},

    {"domain_id": "satellite-data", "label": "Satellite & Geospatial AI", "composite_score": 0.70,
     "scores": {"market_size": 0.75, "community_demand": 0.6, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["github", "arxiv"], "related_chips": ["data-engineer", "climate-analytics"],
     "domain_tags": ["infrastructure", "code_quality"]},

    {"domain_id": "energy-optimization", "label": "Energy & Grid Optimization AI", "composite_score": 0.68,
     "scores": {"market_size": 0.75, "community_demand": 0.55, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.45},
     "evidence_sources": ["arxiv", "community"], "related_chips": ["supply-chain"],
     "domain_tags": ["infrastructure", "roi"]},

    # --- Niche / Emerging (15) ---
    {"domain_id": "ai-recruiter-screen", "label": "AI Candidate Screening", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["hr-recruiter", "resume-career"],
     "domain_tags": ["time_leverage", "roi", "productivity"]},

    {"domain_id": "translation-ai", "label": "AI Real-Time Translation", "composite_score": 0.75,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community", "github"], "related_chips": ["language-learner"],
     "domain_tags": ["quick_wins", "simplicity", "productivity"]},

    {"domain_id": "legal-discovery", "label": "AI Legal E-Discovery", "composite_score": 0.72,
     "scores": {"market_size": 0.75, "community_demand": 0.6, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["community"], "related_chips": ["legal-ops", "contract-drafter"],
     "domain_tags": ["time_leverage", "roi", "risk_management"]},

    {"domain_id": "insurance-underwrite", "label": "AI Insurance Underwriting", "composite_score": 0.71,
     "scores": {"market_size": 0.8, "community_demand": 0.6, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.45},
     "evidence_sources": ["vc_landscape"], "related_chips": ["compliance-shield"],
     "domain_tags": ["risk_management", "roi", "infrastructure"]},

    {"domain_id": "real-estate-listing", "label": "AI Real Estate Listing Writer", "composite_score": 0.72,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community", "producthunt"], "related_chips": ["real-estate-analyst", "content"],
     "domain_tags": ["content_quality", "conversion", "time_leverage"]},

    {"domain_id": "tax-optimizer", "label": "AI Tax Optimization", "composite_score": 0.73,
     "scores": {"market_size": 0.85, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["community"], "related_chips": ["personal-finance", "accounting-bookkeeper"],
     "domain_tags": ["roi", "simplicity", "time_leverage"]},

    {"domain_id": "patent-writer", "label": "AI Patent Drafting", "composite_score": 0.70,
     "scores": {"market_size": 0.7, "community_demand": 0.6, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["community"], "related_chips": ["legal-ops", "grant-writer"],
     "domain_tags": ["content_quality", "time_leverage", "roi"]},

    {"domain_id": "wedding-planner", "label": "AI Wedding Planner", "composite_score": 0.67,
     "scores": {"market_size": 0.75, "community_demand": 0.65, "data_availability": 0.6, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.4},
     "evidence_sources": ["community"], "related_chips": ["event-planner"],
     "domain_tags": ["all_in_one", "simplicity", "time_leverage"]},

    {"domain_id": "podcast-discovery", "label": "AI Podcast Discovery & Curation", "composite_score": 0.69,
     "scores": {"market_size": 0.75, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community"], "related_chips": ["podcast-producer", "content"],
     "domain_tags": ["content_quality", "time_leverage", "quick_wins"]},

    {"domain_id": "charity-nonprofit", "label": "AI Nonprofit & Fundraising", "composite_score": 0.68,
     "scores": {"market_size": 0.7, "community_demand": 0.6, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["community"], "related_chips": ["grant-writer", "email-marketing"],
     "domain_tags": ["roi", "time_leverage", "conversion"]},

    {"domain_id": "vintage-collector", "label": "AI Vintage & Collectibles Appraiser", "composite_score": 0.65,
     "scores": {"market_size": 0.65, "community_demand": 0.6, "data_availability": 0.6, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.4},
     "evidence_sources": ["community"], "related_chips": [],
     "domain_tags": ["deal_flow", "alpha", "uniqueness"]},

    {"domain_id": "car-buying", "label": "AI Car Buying Advisor", "composite_score": 0.69,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.45},
     "evidence_sources": ["community"], "related_chips": ["personal-finance"],
     "domain_tags": ["deal_flow", "roi", "simplicity"]},

    {"domain_id": "drone-pilot", "label": "AI Drone Operations & FPV", "composite_score": 0.68,
     "scores": {"market_size": 0.7, "community_demand": 0.65, "data_availability": 0.6, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.45},
     "evidence_sources": ["github", "community"], "related_chips": ["robotics-controller", "satellite-data"],
     "domain_tags": ["creative_control", "infrastructure"]},

    {"domain_id": "3d-printing", "label": "AI 3D Printing Optimizer", "composite_score": 0.68,
     "scores": {"market_size": 0.7, "community_demand": 0.65, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["github", "community"], "related_chips": ["cad-3d-design"],
     "domain_tags": ["creative_control", "quick_wins", "productivity"]},

    # --- Regional / Locale-specific (8) ---
    {"domain_id": "china-wechat-mini", "label": "WeChat Mini Program Builder", "composite_score": 0.74,
     "scores": {"market_size": 0.9, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community"], "related_chips": ["telegram-miniapp", "mobile-app-builder"],
     "domain_tags": ["speed_to_ship", "first_mover", "infrastructure"]},

    {"domain_id": "japan-line-bot", "label": "LINE Bot Builder (Japan/TW)", "composite_score": 0.71,
     "scores": {"market_size": 0.8, "community_demand": 0.65, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["community"], "related_chips": ["telegram-miniapp", "whatsapp-bot"],
     "domain_tags": ["speed_to_ship", "first_mover"]},

    {"domain_id": "india-upi-payments", "label": "India UPI Payments Integration", "composite_score": 0.73,
     "scores": {"market_size": 0.9, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["community"], "related_chips": ["invoice-payments"],
     "domain_tags": ["infrastructure", "speed_to_ship", "roi"]},

    {"domain_id": "latam-pix-fintech", "label": "LatAm PIX & Fintech", "composite_score": 0.72,
     "scores": {"market_size": 0.85, "community_demand": 0.65, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["community"], "related_chips": ["personal-finance", "invoice-payments"],
     "domain_tags": ["infrastructure", "roi", "first_mover"]},

    {"domain_id": "arabic-nlp", "label": "Arabic NLP & Content", "composite_score": 0.69,
     "scores": {"market_size": 0.8, "community_demand": 0.6, "data_availability": 0.6, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["community", "arxiv"], "related_chips": ["translation-ai", "content"],
     "domain_tags": ["content_quality", "first_mover"]},

    {"domain_id": "korea-naver-seo", "label": "Korea Naver SEO & Marketing", "composite_score": 0.70,
     "scores": {"market_size": 0.8, "community_demand": 0.65, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["community"], "related_chips": ["seo-dominator", "agentic-marketing"],
     "domain_tags": ["audience_growth", "distribution", "first_mover"]},

    {"domain_id": "africa-mobile-money", "label": "Africa Mobile Money & Fintech", "composite_score": 0.71,
     "scores": {"market_size": 0.85, "community_demand": 0.6, "data_availability": 0.6, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.45},
     "evidence_sources": ["community"], "related_chips": ["personal-finance"],
     "domain_tags": ["first_mover", "roi", "infrastructure"]},

    {"domain_id": "eu-gdpr-tool", "label": "EU GDPR Compliance Tool", "composite_score": 0.72,
     "scores": {"market_size": 0.8, "community_demand": 0.65, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community"], "related_chips": ["compliance-shield", "legal-ops"],
     "domain_tags": ["risk_management", "infrastructure", "roi"]},

    # --- Misc trending (15) ---
    {"domain_id": "ai-personal-assistant", "label": "AI Personal Life Assistant", "composite_score": 0.77,
     "scores": {"market_size": 0.9, "community_demand": 0.8, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["producthunt", "x_twitter", "community"], "related_chips": ["productivity-system", "notion-second-brain"],
     "domain_tags": ["all_in_one", "simplicity", "time_leverage", "quick_wins"]},

    {"domain_id": "ai-cover-letter", "label": "AI Cover Letter Writer", "composite_score": 0.72,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["resume-career", "content"],
     "domain_tags": ["quick_wins", "easy_start", "conversion"]},

    {"domain_id": "ai-photo-editor", "label": "AI Photo Editor", "composite_score": 0.74,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["midjourney-art", "instagram-growth"],
     "domain_tags": ["aesthetic_quality", "visual_impact", "creative_control"]},

    {"domain_id": "ai-logo-maker", "label": "AI Logo & Brand Identity", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["web-designer", "brand-voice-ai"],
     "domain_tags": ["aesthetic_quality", "visual_impact", "speed_to_ship"]},

    {"domain_id": "ai-presentation", "label": "AI Presentation Builder", "composite_score": 0.75,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["pitch-deck-builder", "content"],
     "domain_tags": ["visual_impact", "speed_to_ship", "productivity", "quick_wins"]},

    {"domain_id": "ai-spreadsheet", "label": "AI Spreadsheet Automation", "composite_score": 0.76,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["ai-data-analyst", "productivity-system"],
     "domain_tags": ["productivity", "time_leverage", "quick_wins", "low_learning_curve"]},

    {"domain_id": "ai-calendar", "label": "AI Calendar & Scheduling", "composite_score": 0.74,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["meeting-assistant", "productivity-system"],
     "domain_tags": ["time_leverage", "productivity", "simplicity"]},

    {"domain_id": "ai-crm-outreach", "label": "AI CRM & Smart Outreach", "composite_score": 0.76,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["crm-builder", "cold-email-outbound"],
     "domain_tags": ["conversion", "deal_flow", "roi", "audience_targeting"]},

    {"domain_id": "ai-form-builder", "label": "AI Smart Form Builder", "composite_score": 0.73,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["no-code-saas", "customer-research"],
     "domain_tags": ["speed_to_ship", "simplicity", "conversion"]},

    {"domain_id": "ai-chatbot-no-code", "label": "No-Code AI Chatbot Builder", "composite_score": 0.77,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["producthunt", "community", "x_twitter"], "related_chips": ["ai-customer-support", "no-code-saas"],
     "domain_tags": ["low_learning_curve", "speed_to_ship", "simplicity", "conversion"]},

    {"domain_id": "ai-inventory-photo", "label": "AI Product Photography", "composite_score": 0.73,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["shopify-growth", "midjourney-art"],
     "domain_tags": ["visual_impact", "roi", "conversion", "aesthetic_quality"]},

    {"domain_id": "ai-competitor-monitor", "label": "AI Competitor Monitoring", "composite_score": 0.75,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["competitive-intel", "market-research-ai"],
     "domain_tags": ["alpha", "edge", "deal_flow", "market_fit"]},

    {"domain_id": "ai-changelog", "label": "AI Changelog & Release Notes", "composite_score": 0.71,
     "scores": {"market_size": 0.7, "community_demand": 0.7, "data_availability": 0.75, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.6, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "community"], "related_chips": ["open-source-maintainer", "ai-docs-writer"],
     "domain_tags": ["productivity", "dx", "content_quality"]},

    {"domain_id": "ai-onboarding-flow", "label": "AI User Onboarding Designer", "composite_score": 0.74,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["web-designer", "conversion-optimizer"],
     "domain_tags": ["conversion", "low_learning_curve", "dx", "engagement"]},

    {"domain_id": "ai-waitlist", "label": "AI Waitlist & Launch Builder", "composite_score": 0.73,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["product-hunt-launcher", "viral-growth-hacker"],
     "domain_tags": ["audience_growth", "distribution", "first_mover", "speed"]},

    # --- Additional domains to reach 250 (21 more) ---
    {"domain_id": "ai-transcription", "label": "AI Transcription & Captioning", "composite_score": 0.76,
     "scores": {"market_size": 0.85, "community_demand": 0.8, "data_availability": 0.75, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["podcast-producer", "video-creator"],
     "domain_tags": ["productivity", "time_leverage", "quick_wins"]},

    {"domain_id": "ai-dubbing", "label": "AI Video Dubbing & Localization", "composite_score": 0.73,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["ai-voice-clone", "translation-ai"],
     "domain_tags": ["content_quality", "audience_growth", "creative_control"]},

    {"domain_id": "marketplace-builder", "label": "AI Marketplace Builder", "composite_score": 0.76,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.85, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["shopify-growth", "no-code-saas"],
     "domain_tags": ["speed_to_ship", "roi", "mvp_quality", "conversion"]},

    {"domain_id": "subscription-box", "label": "AI Subscription Box Optimizer", "composite_score": 0.71,
     "scores": {"market_size": 0.75, "community_demand": 0.65, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community"], "related_chips": ["shopify-growth", "ecommerce-analytics"],
     "domain_tags": ["roi", "conversion", "audience_targeting"]},

    {"domain_id": "podcast-guest-match", "label": "AI Podcast Guest Matching", "composite_score": 0.70,
     "scores": {"market_size": 0.7, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community"], "related_chips": ["podcast-producer", "influencer-marketing"],
     "domain_tags": ["deal_flow", "audience_growth", "distribution"]},

    {"domain_id": "gig-economy", "label": "Gig Economy Optimizer", "composite_score": 0.72,
     "scores": {"market_size": 0.85, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["community"], "related_chips": ["freelance-scaler"],
     "domain_tags": ["roi", "time_leverage", "speed"]},

    {"domain_id": "dropshipping-ai", "label": "AI Dropshipping Automation", "composite_score": 0.73,
     "scores": {"market_size": 0.85, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["shopify-growth", "ecommerce-analytics"],
     "domain_tags": ["roi", "low_cost", "speed_to_ship"]},

    {"domain_id": "print-on-demand", "label": "AI Print-on-Demand Designer", "composite_score": 0.71,
     "scores": {"market_size": 0.75, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["midjourney-art", "shopify-growth"],
     "domain_tags": ["creative_control", "roi", "low_cost"]},

    {"domain_id": "amazon-fba", "label": "Amazon FBA Intelligence", "composite_score": 0.75,
     "scores": {"market_size": 0.9, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["ecommerce-analytics", "shopify-growth"],
     "domain_tags": ["roi", "deal_flow", "alpha", "speed"]},

    {"domain_id": "ai-hiring-manager", "label": "AI Hiring Decision Support", "composite_score": 0.73,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["hr-recruiter", "ai-recruiter-screen"],
     "domain_tags": ["time_leverage", "roi", "risk_management"]},

    {"domain_id": "ai-survey-builder", "label": "AI Survey & Feedback Collector", "composite_score": 0.73,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["customer-research", "ai-form-builder"],
     "domain_tags": ["idea_validation", "market_fit", "quick_wins"]},

    {"domain_id": "ai-whiteboard", "label": "AI Collaborative Whiteboard", "composite_score": 0.72,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["ai-presentation", "meeting-assistant"],
     "domain_tags": ["productivity", "creative_control", "simplicity"]},

    {"domain_id": "ai-annotation", "label": "AI Data Annotation & Labeling", "composite_score": 0.75,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.8, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.7},
     "evidence_sources": ["github", "community"], "related_chips": ["fine-tuning-lab", "synthetic-data-gen"],
     "domain_tags": ["infrastructure", "productivity", "code_quality"]},

    {"domain_id": "ai-ab-testing", "label": "AI A/B Testing Optimizer", "composite_score": 0.75,
     "scores": {"market_size": 0.8, "community_demand": 0.75, "data_availability": 0.75, "benchmark_feasibility": 0.75,
                "monetization_potential": 0.75, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["conversion-optimizer", "saas-metrics"],
     "domain_tags": ["roi", "attribution", "conversion"]},

    {"domain_id": "ai-sitemap-gen", "label": "AI Website & Sitemap Generator", "composite_score": 0.73,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["web-designer", "seo-dominator"],
     "domain_tags": ["speed_to_ship", "productivity", "distribution"]},

    {"domain_id": "ai-contract-review", "label": "AI Contract Review Assistant", "composite_score": 0.73,
     "scores": {"market_size": 0.8, "community_demand": 0.65, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.8, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["community"], "related_chips": ["legal-ops", "contract-drafter"],
     "domain_tags": ["risk_management", "time_leverage", "roi"]},

    {"domain_id": "ai-receipt-scanner", "label": "AI Receipt & Expense Tracker", "composite_score": 0.72,
     "scores": {"market_size": 0.8, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.5},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["accounting-bookkeeper", "personal-finance"],
     "domain_tags": ["time_leverage", "simplicity", "quick_wins"]},

    {"domain_id": "ai-color-palette", "label": "AI Color Palette & Design System", "composite_score": 0.71,
     "scores": {"market_size": 0.75, "community_demand": 0.7, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.6},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["web-designer", "ai-logo-maker"],
     "domain_tags": ["aesthetic_quality", "creative_control", "visual_impact"]},

    {"domain_id": "ai-music-video", "label": "AI Music Video Generator", "composite_score": 0.70,
     "scores": {"market_size": 0.75, "community_demand": 0.7, "data_availability": 0.6, "benchmark_feasibility": 0.6,
                "monetization_potential": 0.7, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["producthunt", "community"], "related_chips": ["music-producer", "video-creator"],
     "domain_tags": ["creative_control", "visual_impact", "uniqueness"]},

    {"domain_id": "ai-npc-dialog", "label": "AI NPC Dialogue Generator", "composite_score": 0.71,
     "scores": {"market_size": 0.7, "community_demand": 0.75, "data_availability": 0.7, "benchmark_feasibility": 0.7,
                "monetization_potential": 0.65, "spark_ecosystem_fit": 0.65},
     "evidence_sources": ["github", "community"], "related_chips": ["game-balance", "interactive-fiction"],
     "domain_tags": ["creative_control", "content_quality", "engagement"]},

    {"domain_id": "ai-pixel-art", "label": "AI Pixel Art Generator", "composite_score": 0.69,
     "scores": {"market_size": 0.65, "community_demand": 0.7, "data_availability": 0.65, "benchmark_feasibility": 0.65,
                "monetization_potential": 0.6, "spark_ecosystem_fit": 0.55},
     "evidence_sources": ["github", "community"], "related_chips": ["midjourney-art", "roblox-development"],
     "domain_tags": ["aesthetic_quality", "creative_control", "uniqueness"]},
]


# =============================================================================
# COMBINE ALL 250 DOMAINS
# =============================================================================
ALL_250_DOMAINS = FIRST_100 + NEW_150_DOMAINS


# =============================================================================
# NEW RELATIONSHIPS (for the 150 new domains)
# =============================================================================
NEW_RELATIONSHIPS = [
    # AI Infra cluster
    {"source": "vector-db-ops", "target": "rag-pipeline", "relationship": "ENABLES", "weight": 0.85},
    {"source": "ai-observability", "target": "llm-evaluator", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "multi-modal-ai", "target": "ai-agent-builder", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "synthetic-data-gen", "target": "fine-tuning-lab", "relationship": "ENABLES", "weight": 0.85},
    {"source": "ai-gateway-proxy", "target": "api-monetization", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "kubernetes-ops", "target": "devops-pipeline", "relationship": "EXTENDS", "weight": 0.8},

    # Web3 expanded
    {"source": "base-l2-dev", "target": "defi-architect", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "ai-agent-token", "target": "token-launch", "relationship": "EXTENDS", "weight": 0.85},
    {"source": "ai-agent-token", "target": "ai-agent-builder", "relationship": "ENABLES", "weight": 0.8},
    {"source": "perpetuals-trading", "target": "trading-crypto", "relationship": "EXTENDS", "weight": 0.85},
    {"source": "staking-yield", "target": "defi-architect", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "prediction-market", "target": "onchain-analytics", "relationship": "ENABLES", "weight": 0.75},
    {"source": "rwa-tokenization", "target": "real-estate-analyst", "relationship": "EXTENDS", "weight": 0.7},

    # Creator expanded
    {"source": "faceless-youtube", "target": "youtube-optimizer", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "podcast-clipper", "target": "podcast-producer", "relationship": "EXTENDS", "weight": 0.85},
    {"source": "ai-ghostwriter", "target": "content", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "brand-voice-ai", "target": "content", "relationship": "EXTENDS", "weight": 0.75},

    # Business
    {"source": "b2b-lead-gen", "target": "cold-email-outbound", "relationship": "ENABLES", "weight": 0.85},
    {"source": "meeting-assistant", "target": "productivity-system", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "ai-chatbot-no-code", "target": "ai-customer-support", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "ai-personal-assistant", "target": "productivity-system", "relationship": "EXTENDS", "weight": 0.85},
    {"source": "ai-spreadsheet", "target": "ai-data-analyst", "relationship": "EXTENDS", "weight": 0.8},

    # Education
    {"source": "coding-tutor", "target": "education-tutor", "relationship": "EXTENDS", "weight": 0.8},
    {"source": "research-assistant", "target": "rag-pipeline", "relationship": "ENABLES", "weight": 0.8},
    {"source": "math-solver", "target": "education-tutor", "relationship": "EXTENDS", "weight": 0.8},
]

ALL_RELATIONSHIPS = RELATIONSHIPS + NEW_RELATIONSHIPS


# =============================================================================
# MAIN
# =============================================================================
def main():
    t0 = time.time()
    n = len(ALL_250_DOMAINS)
    domain_ids_set = {d["domain_id"] for d in ALL_250_DOMAINS}
    assert len(domain_ids_set) == n, f"Duplicate domain_ids! {n} domains but {len(domain_ids_set)} unique"

    print("=" * 90)
    print(f"MIROFISH v3: 250-DOMAIN PREDICTION WITH PER-PERSONA TOP-10")
    print(f"Domains: {n} total")
    print(f"Personas: 11 types x 50 each = 550 agents")
    print("=" * 90)
    print()

    # Build graph
    graph = DomainGraph()
    for d in ALL_250_DOMAINS:
        graph.add_node(d["domain_id"], "domain", d.get("label", d["domain_id"]),
                       {"domain_tags": d.get("domain_tags", [])})

    tech_nodes = {"ai-tools", "blockchain", "web-platform", "social-media", "saas-infra"}
    for t in tech_nodes:
        graph.add_node(t, "technology", t)
    for d in ALL_250_DOMAINS:
        for src in d.get("evidence_sources", []):
            if src == "github":
                graph.add_edge("ai-tools", d["domain_id"], "ENABLES", 0.5)
            elif src == "x_twitter":
                graph.add_edge("social-media", d["domain_id"], "ENABLES", 0.4)

    graph_from_opps = build_graph_from_opportunities(ALL_250_DOMAINS)
    for node_id, node_data in graph_from_opps.nodes.items():
        if node_id not in graph.nodes:
            graph.add_node(node_id, node_data["type"], node_data["label"], node_data.get("properties", {}))
    for edge in graph_from_opps.edges:
        graph.add_edge(edge["source"], edge["target"], edge["relationship"], edge.get("weight", 0.5))

    for r in ALL_RELATIONSHIPS:
        if r["source"] in graph.nodes and r["target"] in graph.nodes:
            graph.add_edge(r["source"], r["target"], r["relationship"], r.get("weight", 0.5))

    print(f"Graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")

    # Signals
    domain_ids = [d["domain_id"] for d in ALL_250_DOMAINS]
    opp_signals = signals_from_opportunities(ALL_250_DOMAINS)
    graph_signals = signals_from_graph(graph)
    all_signals = opp_signals + graph_signals
    print(f"Signals: {len(opp_signals)} opportunity + {len(graph_signals)} graph = {len(all_signals)} total")

    # Personas
    personas = generate_personas(graph, domain_ids=domain_ids, count_per_type=50, seed=42)
    print(f"Personas: {len(personas)} agents across {len(set(p['persona_type'] for p in personas))} types")
    print()

    # --- Flagship simulation ---
    print("--- Flagship Simulation (1375 agents, 250 domains, 20 rounds) ---")
    t1 = time.time()
    result = run_simulation(graph, domain_ids, personas=personas, signals=all_signals, max_rounds=20, seed=42)
    t2 = time.time()
    evals = len(personas) * len(domain_ids) * 20
    print(f"Simulation: {t2 - t1:.1f}s ({evals:,} persona-domain-round evaluations)")
    print()

    # --- Monte Carlo ensemble ---
    print("--- Monte Carlo Ensemble (5 runs x 220 agents) ---")
    t3 = time.time()
    ensemble = run_ensemble(graph, domain_ids, n_runs=5, count_per_type=20,
                            signals=all_signals, max_rounds=20, base_seed=42)
    t4 = time.time()
    print(f"Ensemble: {t4 - t3:.1f}s")
    print()

    total_time = time.time() - t0

    # ==========================================================================
    # COLLECT RESULTS
    # ==========================================================================
    domain_results = []
    for d in ALL_250_DOMAINS:
        d_id = d["domain_id"]
        sim_data = result["domains"].get(d_id, {})
        ens_data = ensemble["domains"].get(d_id, {})

        adoption = sim_data.get("final_adoption_rate", 0.0)
        advocacy = sim_data.get("final_advocacy_rate", 0.0)
        by_type = sim_data.get("adoption_by_persona_type", {})
        ens_mean = ens_data.get("mean_adoption", 0.0)
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
            "p10": p10,
            "p90": p90,
            "by_type": by_type,
        })

    domain_results.sort(key=lambda x: x["ens_mean"], reverse=True)

    # ==========================================================================
    # PRINT TOP 25
    # ==========================================================================
    print("=" * 100)
    print("TOP 25 DOMAINS (sorted by ensemble mean adoption)")
    print("=" * 100)
    print(f"{'#':>3}  {'Domain':<30} {'Ens Mean':>9} {'P10-P90':>12} {'Builder':>8} {'Advocacy':>9}")
    print("-" * 90)
    for i, dr in enumerate(domain_results[:25], 1):
        status = f" [{dr['status']}]" if dr['status'] != 'new' else ""
        print(f"{i:>3}  {dr['domain_id']:<30} {dr['ens_mean']:>8.1%} {dr['p10']:>5.0%}-{dr['p90']:<5.0%} {dr['adoption']:>8.1%} {dr['advocacy']:>8.1%}{status}")

    # ==========================================================================
    # PER-PERSONA TOP 10 RECOMMENDATIONS
    # ==========================================================================
    print()
    print("=" * 100)
    print("EACH AI PERSONA'S TOP 10 DOMAIN RECOMMENDATIONS")
    print("=" * 100)

    persona_top10 = {}
    for ptype in CUSTOMER_PERSONAS:
        sorted_by_persona = sorted(
            domain_results,
            key=lambda x: x["by_type"].get(ptype, {}).get("adoption_rate", 0),
            reverse=True,
        )
        top10 = sorted_by_persona[:10]
        persona_top10[ptype] = top10

        display_name = CUSTOMER_PERSONAS[ptype]["label"]
        print(f"\n--- {display_name} (Top 10) ---")
        print(f"{'#':>3}  {'Domain':<30} {'Adoption':>9} {'Advocacy':>9}")
        print("-" * 60)
        for i, dr in enumerate(top10, 1):
            rate = dr["by_type"].get(ptype, {}).get("adoption_rate", 0)
            adv = dr["by_type"].get(ptype, {}).get("advocacy_rate", 0)
            print(f"{i:>3}  {dr['domain_id']:<30} {rate:>8.0%} {adv:>8.0%}")

    # ==========================================================================
    # CROSS-PERSONA CONSENSUS
    # ==========================================================================
    print()
    print("=" * 100)
    print("CROSS-PERSONA CONSENSUS (domains in multiple persona top-10s)")
    print("=" * 100)

    domain_appearances = {}
    for ptype, top10 in persona_top10.items():
        for dr in top10:
            d_id = dr["domain_id"]
            if d_id not in domain_appearances:
                domain_appearances[d_id] = []
            domain_appearances[d_id].append(ptype)

    consensus = sorted(domain_appearances.items(), key=lambda x: len(x[1]), reverse=True)
    print(f"\n{'Domain':<30} {'# Personas':>10} {'Who Recommends'}")
    print("-" * 90)
    for d_id, personas_list in consensus[:20]:
        print(f"{d_id:<30} {len(personas_list):>10}    {', '.join(personas_list)}")

    # ==========================================================================
    # EXPORT
    # ==========================================================================
    export = {
        "run_metadata": {
            "total_domains": n,
            "total_personas": len(personas),
            "persona_types": len(CUSTOMER_PERSONAS),
            "ensemble_runs": 5,
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
        "persona_top10": {
            ptype: [
                {
                    "rank": i + 1,
                    "domain_id": dr["domain_id"],
                    "adoption": round(dr["by_type"].get(ptype, {}).get("adoption_rate", 0), 4),
                    "advocacy": round(dr["by_type"].get(ptype, {}).get("advocacy_rate", 0), 4),
                }
                for i, dr in enumerate(top10)
            ]
            for ptype, top10 in persona_top10.items()
        },
        "consensus": [
            {"domain_id": d_id, "persona_count": len(p_list), "personas": p_list}
            for d_id, p_list in consensus
        ],
    }

    output_path = os.path.join(script_dir, "..", "viz", "250_domain_predictions.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(export, f, indent=2)
    print(f"\nExported to {output_path}")

    # ==========================================================================
    # GENERATE MARKDOWN REPORT
    # ==========================================================================
    md_lines = []
    md_lines.append("# MiroFish v3: 250-Domain Chip Research")
    md_lines.append("")
    md_lines.append(f"**Generated**: March 2026")
    md_lines.append(f"**Engine**: MiroFish v3 Multi-Agent Trend Prediction")
    md_lines.append(f"**Agents**: {len(personas):,} ({len(CUSTOMER_PERSONAS)} persona types x 125 each)")
    md_lines.append(f"**Domains**: {n}")
    md_lines.append(f"**Ensemble Runs**: 5 Monte Carlo")
    md_lines.append(f"**Simulation Time**: {total_time:.0f}s")
    md_lines.append(f"**Evaluations**: {evals:,} persona-domain-round")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    # Top 25
    md_lines.append("## Top 25 Domain Chips")
    md_lines.append("")
    md_lines.append("| Rank | Domain | Label | Ens Mean | P10-P90 | Builder | Advocacy |")
    md_lines.append("|------|--------|-------|----------|---------|---------|----------|")
    for i, dr in enumerate(domain_results[:25], 1):
        md_lines.append(
            f"| {i} | `{dr['domain_id']}` | {dr['label']} | "
            f"**{dr['ens_mean']:.1%}** | {dr['p10']:.0%}-{dr['p90']:.0%} | "
            f"{dr['adoption']:.1%} | {dr['advocacy']:.1%} |"
        )
    md_lines.append("")

    # Per persona top 10
    md_lines.append("## Each AI Persona's Top 10 Recommendations")
    md_lines.append("")
    for ptype in CUSTOMER_PERSONAS:
        display = CUSTOMER_PERSONAS[ptype]["label"]
        desc = CUSTOMER_PERSONAS[ptype]["description"]
        md_lines.append(f"### {display}")
        md_lines.append(f"*{desc}*")
        md_lines.append("")
        md_lines.append("| # | Domain | Adoption | Advocacy |")
        md_lines.append("|---|--------|----------|----------|")
        for i, dr in enumerate(persona_top10[ptype], 1):
            rate = dr["by_type"].get(ptype, {}).get("adoption_rate", 0)
            adv = dr["by_type"].get(ptype, {}).get("advocacy_rate", 0)
            md_lines.append(f"| {i} | `{dr['domain_id']}` ({dr['label']}) | **{rate:.0%}** | {adv:.0%} |")
        md_lines.append("")

    # Consensus
    md_lines.append("## Cross-Persona Consensus")
    md_lines.append("")
    md_lines.append("Domains that appear in multiple personas' top-10 lists:")
    md_lines.append("")
    md_lines.append("| Domain | # Personas | Who Recommends |")
    md_lines.append("|--------|-----------|----------------|")
    for d_id, p_list in consensus[:25]:
        if len(p_list) >= 2:
            md_lines.append(f"| `{d_id}` | **{len(p_list)}** | {', '.join(p_list)} |")
    md_lines.append("")

    # Full rankings
    md_lines.append("## Full Rankings (All 250 Domains)")
    md_lines.append("")
    md_lines.append("| Rank | Domain | Label | Ens Mean | Builder | Status |")
    md_lines.append("|------|--------|-------|----------|---------|--------|")
    for i, dr in enumerate(domain_results, 1):
        md_lines.append(
            f"| {i} | `{dr['domain_id']}` | {dr['label']} | "
            f"{dr['ens_mean']:.1%} | {dr['adoption']:.1%} | {dr['status']} |"
        )
    md_lines.append("")
    md_lines.append("---")
    md_lines.append(f"*Generated by MiroFish v3 | {len(personas)} agents | {n} domains | {total_time:.0f}s*")

    md_path = os.path.join(script_dir, "..", "docs", "MIROFISH_250_RESEARCH.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Markdown report: {md_path}")

    print()
    print("=" * 100)
    print("DONE")
    print(f"250 domains evaluated by {len(personas)} agents in {total_time:.0f}s")
    print("=" * 100)


if __name__ == "__main__":
    main()
