"""MiroFish viral domain prediction for Spark Swarm / Spark Researcher growth.

20 NEW domain chips selected for maximum virality:
- Large, active online communities
- Shareable output (social proof loops)
- Trending in March 2026
- Natural "show your work" moments that drive discovery of Spark
"""

import time
import json
import sys
sys.path.insert(0, "src")

from chip_labs.mirofish.graph import build_graph_from_opportunities
from chip_labs.mirofish.personas import generate_personas
from chip_labs.mirofish.simulation import (
    run_simulation, run_dual_context, run_ensemble, run_sensitivity,
)
from chip_labs.mirofish.signals import (
    signals_from_opportunities, signals_from_graph,
    create_signal, create_shock,
)
from chip_labs.trend_scanner import score_opportunity

# ============================================================================
# 20 VIRAL DOMAIN CHIPS -- selected for Spark ecosystem growth
# ============================================================================

VIRAL_DOMAINS = [
    # --- TIER 1: Maximum virality (huge communities + shareable output) ---
    {
        "domain_id": "meme-coin-launcher",
        "label": "Meme Coin Launch Strategy",
        "description": "Token creation on pump.fun/moonshot, bonding curves, community building, launch timing, anti-rug patterns.",
        "scores": {"market_size": 0.92, "data_availability": 0.88, "benchmark_feasibility": 0.70, "community_demand": 0.95, "spark_ecosystem_fit": 0.80, "monetization_potential": 0.95},
        "rationale": "Pump.fun did $500M+ in fees. Every launch is a shareable event. Massive X/Twitter virality loop.",
        "related_chips": ["trading-crypto", "solana-dev"],
        "evidence_sources": ["x_twitter", "github", "community"],
    },
    {
        "domain_id": "tiktok-creator",
        "label": "TikTok Content Strategy",
        "description": "Hook writing, trend surfing, sound selection, posting cadence, duet strategy, shop integration.",
        "scores": {"market_size": 0.95, "data_availability": 0.80, "benchmark_feasibility": 0.65, "community_demand": 0.92, "spark_ecosystem_fit": 0.70, "monetization_potential": 0.85},
        "rationale": "1.5B MAU. Every creator wants growth. AI-assisted content creation is #1 request. Viral by definition.",
        "related_chips": ["xcontent", "video-creator"],
        "evidence_sources": ["x_twitter", "producthunt", "community"],
    },
    {
        "domain_id": "mcp-server-builder",
        "label": "MCP Server Development",
        "description": "Build Model Context Protocol servers for Claude/AI tools. Tool definition, resource management, transport patterns.",
        "scores": {"market_size": 0.82, "data_availability": 0.90, "benchmark_feasibility": 0.88, "community_demand": 0.95, "spark_ecosystem_fit": 0.98, "monetization_potential": 0.72},
        "rationale": "10,000+ MCP servers. Every AI dev building them. Anthropic ecosystem = perfect Spark fit. GitHub repos go viral.",
        "related_chips": ["ai-agent-builder", "prompt-engineer"],
        "evidence_sources": ["github", "producthunt", "community"],
    },
    {
        "domain_id": "cursor-copilot",
        "label": "AI Coding Workflow",
        "description": "Cursor/Copilot/Windsurf patterns, .cursorrules design, AI-assisted refactoring, code review automation.",
        "scores": {"market_size": 0.90, "data_availability": 0.85, "benchmark_feasibility": 0.82, "community_demand": 0.92, "spark_ecosystem_fit": 0.92, "monetization_potential": 0.78},
        "rationale": "Every dev uses AI coding tools. Cursor has 1M+ users. .cursorrules files shared virally on X/GitHub.",
        "related_chips": ["ai-agent-builder", "prompt-engineer"],
        "evidence_sources": ["github", "x_twitter", "community"],
    },
    {
        "domain_id": "discord-community",
        "label": "Discord Server & Bot Building",
        "description": "Server architecture, bot development, engagement loops, moderation AI, community gamification.",
        "scores": {"market_size": 0.85, "data_availability": 0.82, "benchmark_feasibility": 0.78, "community_demand": 0.88, "spark_ecosystem_fit": 0.82, "monetization_potential": 0.72},
        "rationale": "200M+ MAU. Every crypto/AI/gaming project needs Discord. Bot repos get thousands of stars.",
        "related_chips": ["devrel-community"],
        "evidence_sources": ["github", "community"],
    },
    # --- TIER 2: High virality (trending + natural share loops) ---
    {
        "domain_id": "linkedin-ghostwriter",
        "label": "LinkedIn Thought Leadership",
        "description": "Post writing, carousel design, engagement optimization, personal brand strategy, lead generation.",
        "scores": {"market_size": 0.85, "data_availability": 0.78, "benchmark_feasibility": 0.72, "community_demand": 0.88, "spark_ecosystem_fit": 0.68, "monetization_potential": 0.82},
        "rationale": "1B users. LinkedIn ghostwriting is a $100M+ industry. Every post is free advertising for the tool that wrote it.",
        "related_chips": ["xcontent", "agentic-marketing", "content"],
        "evidence_sources": ["x_twitter", "producthunt", "community"],
    },
    {
        "domain_id": "midjourney-art",
        "label": "AI Art Direction",
        "description": "Prompt engineering for Midjourney/DALL-E/Flux, style consistency, brand asset generation, upscaling workflow.",
        "scores": {"market_size": 0.88, "data_availability": 0.75, "benchmark_feasibility": 0.60, "community_demand": 0.90, "spark_ecosystem_fit": 0.58, "monetization_potential": 0.78},
        "rationale": "Every image shared is a viral moment. AI art communities are massive. Prompt libraries get millions of views.",
        "related_chips": [],
        "evidence_sources": ["x_twitter", "producthunt", "community"],
    },
    {
        "domain_id": "telegram-miniapp",
        "label": "Telegram Mini App Development",
        "description": "TON blockchain mini-apps, Telegram Bot API, in-app payments, viral mechanics (tap-to-earn, referrals).",
        "scores": {"market_size": 0.88, "data_availability": 0.78, "benchmark_feasibility": 0.75, "community_demand": 0.90, "spark_ecosystem_fit": 0.75, "monetization_potential": 0.90},
        "rationale": "900M Telegram users. Hamster Kombat got 300M users. TON ecosystem exploding. Built-in viral referral loops.",
        "related_chips": ["solana-dev", "defi-architect"],
        "evidence_sources": ["github", "x_twitter", "community"],
    },
    {
        "domain_id": "no-code-saas",
        "label": "No-Code SaaS Builder",
        "description": "Bubble/v0/Bolt patterns, rapid prototyping, template marketplaces, deployment without coding.",
        "scores": {"market_size": 0.88, "data_availability": 0.72, "benchmark_feasibility": 0.68, "community_demand": 0.90, "spark_ecosystem_fit": 0.78, "monetization_potential": 0.82},
        "rationale": "Non-technical founders are the biggest market. 'I built this without code' posts go mega-viral. Massive TAM.",
        "related_chips": ["indie-hacker", "vibe-incubator"],
        "evidence_sources": ["x_twitter", "producthunt", "community"],
    },
    {
        "domain_id": "crypto-airdrop",
        "label": "Airdrop Farming Strategy",
        "description": "Protocol interaction optimization, wallet management, eligibility criteria analysis, anti-sybil patterns.",
        "scores": {"market_size": 0.85, "data_availability": 0.82, "benchmark_feasibility": 0.72, "community_demand": 0.95, "spark_ecosystem_fit": 0.68, "monetization_potential": 0.92},
        "rationale": "$10B+ distributed via airdrops in 2024-25. 'Free money' narrative is maximum virality. Every airdrop is a share event.",
        "related_chips": ["trading-crypto", "defi-architect", "solana-dev"],
        "evidence_sources": ["x_twitter", "community"],
    },
    # --- TIER 3: Strong virality (large communities + clear value prop) ---
    {
        "domain_id": "ai-voice-clone",
        "label": "AI Voice Cloning & TTS",
        "description": "Voice cloning with ElevenLabs/PlayHT, podcast dubbing, audiobook narration, voice-first content.",
        "scores": {"market_size": 0.82, "data_availability": 0.70, "benchmark_feasibility": 0.65, "community_demand": 0.85, "spark_ecosystem_fit": 0.55, "monetization_potential": 0.80},
        "rationale": "Voice demos go viral instantly. 'Clone my voice' content gets millions of views. ElevenLabs API is accessible.",
        "related_chips": [],
        "evidence_sources": ["producthunt", "x_twitter", "community"],
    },
    {
        "domain_id": "shopify-growth",
        "label": "Shopify Store Optimization",
        "description": "Conversion optimization, product page design, ad creative, email flows, upsell funnels.",
        "scores": {"market_size": 0.90, "data_availability": 0.75, "benchmark_feasibility": 0.72, "community_demand": 0.82, "spark_ecosystem_fit": 0.58, "monetization_potential": 0.92},
        "rationale": "4.6M Shopify stores. Revenue screenshots go viral. Every merchant seeking AI-powered growth. High willingness to pay.",
        "related_chips": ["agentic-marketing", "sales-closer"],
        "evidence_sources": ["producthunt", "community"],
    },
    {
        "domain_id": "supabase-fullstack",
        "label": "Supabase Full-Stack Patterns",
        "description": "Auth, RLS, Edge Functions, real-time subscriptions, Next.js integration, migration patterns.",
        "scores": {"market_size": 0.82, "data_availability": 0.90, "benchmark_feasibility": 0.85, "community_demand": 0.88, "spark_ecosystem_fit": 0.88, "monetization_potential": 0.68},
        "rationale": "Fastest-growing BaaS. 'Built with Supabase' is a badge of honor. Massive GitHub presence. Perfect dev tool fit.",
        "related_chips": ["ai-agent-builder", "indie-hacker"],
        "evidence_sources": ["github", "producthunt", "community"],
    },
    {
        "domain_id": "github-actions",
        "label": "GitHub Actions & CI/CD",
        "description": "Workflow automation, custom actions, matrix builds, deployment pipelines, DevOps patterns.",
        "scores": {"market_size": 0.85, "data_availability": 0.92, "benchmark_feasibility": 0.88, "community_demand": 0.80, "spark_ecosystem_fit": 0.85, "monetization_potential": 0.62},
        "rationale": "100M+ GitHub devs. Actions marketplace is viral distribution. Every workflow shared = discovery. Natural Spark integration.",
        "related_chips": ["open-source-maintainer"],
        "evidence_sources": ["github", "community"],
    },
    {
        "domain_id": "seo-dominator",
        "label": "AI-Powered SEO Strategy",
        "description": "Programmatic SEO, keyword clustering, content generation, SERP analysis, backlink strategy.",
        "scores": {"market_size": 0.88, "data_availability": 0.78, "benchmark_feasibility": 0.72, "community_demand": 0.85, "spark_ecosystem_fit": 0.65, "monetization_potential": 0.90},
        "rationale": "SEO revenue screenshots are the most viral content on X. AI-SEO tools are top on Product Hunt. High ROI = shareability.",
        "related_chips": ["content", "agentic-marketing", "newsletter-growth"],
        "evidence_sources": ["x_twitter", "producthunt", "community"],
    },
    {
        "domain_id": "onchain-analytics",
        "label": "On-Chain Data Analytics",
        "description": "Dune queries, wallet analysis, whale tracking, token flow visualization, smart money signals.",
        "scores": {"market_size": 0.80, "data_availability": 0.90, "benchmark_feasibility": 0.82, "community_demand": 0.88, "spark_ecosystem_fit": 0.75, "monetization_potential": 0.85},
        "rationale": "Dune dashboards go viral daily on Crypto Twitter. Data-driven alpha = massive engagement. Nansen has $100M+ valuation.",
        "related_chips": ["trading-crypto", "defi-architect", "data-engineer"],
        "evidence_sources": ["x_twitter", "github", "community"],
    },
    {
        "domain_id": "podcast-producer",
        "label": "AI Podcast Production",
        "description": "Show notes, clip extraction, guest research, distribution strategy, sponsorship matching.",
        "scores": {"market_size": 0.78, "data_availability": 0.72, "benchmark_feasibility": 0.65, "community_demand": 0.80, "spark_ecosystem_fit": 0.60, "monetization_potential": 0.75},
        "rationale": "4M+ podcasts, growing 20% YoY. Every episode is shareable content. AI editing saves hours. Clips go viral on social.",
        "related_chips": ["content", "ai-voice-clone"],
        "evidence_sources": ["producthunt", "community"],
    },
    {
        "domain_id": "browser-extension",
        "label": "Chrome Extension Development",
        "description": "Extension architecture, manifest v3, content scripts, popup UI, Chrome Web Store optimization.",
        "scores": {"market_size": 0.82, "data_availability": 0.85, "benchmark_feasibility": 0.80, "community_demand": 0.78, "spark_ecosystem_fit": 0.72, "monetization_potential": 0.78},
        "rationale": "Chrome Web Store has 200K+ extensions, billions of installs. Extensions are viral distribution machines. Low barrier to ship.",
        "related_chips": ["indie-hacker"],
        "evidence_sources": ["github", "producthunt", "community"],
    },
    {
        "domain_id": "twitter-threads",
        "label": "X/Twitter Thread Craft",
        "description": "Thread architecture, hook patterns, engagement bait, quote-tweet strategy, algorithm optimization.",
        "scores": {"market_size": 0.82, "data_availability": 0.85, "benchmark_feasibility": 0.68, "community_demand": 0.92, "spark_ecosystem_fit": 0.75, "monetization_potential": 0.70},
        "rationale": "Threads are the #1 content format on X. 'This thread went viral' is a meta-viral moment. Every thread credits tools used.",
        "related_chips": ["xcontent", "agentic-marketing"],
        "evidence_sources": ["x_twitter", "community"],
    },
    {
        "domain_id": "ai-avatar",
        "label": "AI Avatar & Digital Identity",
        "description": "Profile photo generation, consistent character design, virtual influencer creation, brand mascots.",
        "scores": {"market_size": 0.80, "data_availability": 0.68, "benchmark_feasibility": 0.62, "community_demand": 0.88, "spark_ecosystem_fit": 0.55, "monetization_potential": 0.80},
        "rationale": "AI-generated profile pics go viral. Virtual influencers have millions of followers. Identity is deeply shareable.",
        "related_chips": ["midjourney-art"],
        "evidence_sources": ["x_twitter", "producthunt", "community"],
    },
]

# ============================================================================
# Relationships that drive viral network effects
# ============================================================================

VIRAL_RELATIONSHIPS = [
    # Content creation cluster
    ("tiktok-creator", "twitter-threads", "EXTENDS"),
    ("twitter-threads", "linkedin-ghostwriter", "EXTENDS"),
    ("linkedin-ghostwriter", "seo-dominator", "ENABLES"),
    ("seo-dominator", "podcast-producer", "ENABLES"),

    # Crypto viral cluster
    ("meme-coin-launcher", "crypto-airdrop", "EXTENDS"),
    ("crypto-airdrop", "onchain-analytics", "ENABLES"),
    ("onchain-analytics", "meme-coin-launcher", "ENABLES"),
    ("telegram-miniapp", "meme-coin-launcher", "EXTENDS"),

    # Dev tools cluster
    ("mcp-server-builder", "cursor-copilot", "EXTENDS"),
    ("cursor-copilot", "github-actions", "ENABLES"),
    ("supabase-fullstack", "no-code-saas", "ENABLES"),
    ("github-actions", "browser-extension", "ENABLES"),

    # Creative cluster
    ("midjourney-art", "ai-avatar", "EXTENDS"),
    ("ai-voice-clone", "podcast-producer", "ENABLES"),
    ("ai-avatar", "tiktok-creator", "ENABLES"),

    # Competition
    ("tiktok-creator", "linkedin-ghostwriter", "COMPETES_WITH"),
    ("no-code-saas", "supabase-fullstack", "COMPETES_WITH"),
    ("twitter-threads", "tiktok-creator", "COMPETES_WITH"),
    ("meme-coin-launcher", "shopify-growth", "COMPETES_WITH"),
]


def main():
    print("=" * 80)
    print("MIROFISH VIRAL DOMAIN PREDICTION")
    print("Which 20 new domain chips will make Spark Swarm go viral?")
    print("=" * 80)

    # Score all domains
    for d in VIRAL_DOMAINS:
        d["composite_score"] = score_opportunity(d)

    # Build graph
    t0 = time.perf_counter()
    graph = build_graph_from_opportunities(VIRAL_DOMAINS)

    # Add custom viral relationship edges
    for source, target, rel in VIRAL_RELATIONSHIPS:
        if source in graph.nodes and target in graph.nodes:
            weight = 0.85 if rel == "EXTENDS" else 0.75 if rel == "ENABLES" else 0.80
            graph.add_edge(source, target, rel, weight=weight)

    t_graph = time.perf_counter() - t0
    domain_ids = [d["domain_id"] for d in VIRAL_DOMAINS]
    print(f"\nGraph: {graph.node_count} nodes, {graph.edge_count} edges (built in {t_graph:.3f}s)")

    # Generate signals
    opp_signals = signals_from_opportunities(VIRAL_DOMAINS)
    graph_signals = signals_from_graph(graph)

    # Add viral-specific signals
    viral_signals = [
        # Pump.fun/meme coin mania
        create_signal("memecoin-mania", "viral_tweet", ["meme-coin-launcher", "crypto-airdrop"], strength=0.95),
        create_signal("pumpfun-revenue", "vc_funding", ["meme-coin-launcher", "telegram-miniapp"], strength=0.90),
        # AI tools explosion
        create_signal("mcp-10k-servers", "github_trending", ["mcp-server-builder", "cursor-copilot"], strength=0.92),
        create_signal("cursor-1m-users", "producthunt_launch", ["cursor-copilot"], strength=0.88),
        # Creator economy surge
        create_signal("creator-economy-2026", "community_request",
                     ["tiktok-creator", "linkedin-ghostwriter", "twitter-threads", "podcast-producer"], strength=0.85),
        # Supabase Series C
        create_signal("supabase-funding", "vc_funding", ["supabase-fullstack"], strength=0.88),
        # TON ecosystem growth
        create_signal("ton-ecosystem", "viral_tweet", ["telegram-miniapp"], strength=0.90),
        # AI art mainstream
        create_signal("ai-art-mainstream", "producthunt_launch", ["midjourney-art", "ai-avatar"], strength=0.82),
        # SEO revenue screenshots going viral
        create_signal("seo-revenue-viral", "viral_tweet", ["seo-dominator", "shopify-growth"], strength=0.80),
        # Voice AI breakthrough
        create_signal("voice-ai-breakthrough", "github_trending", ["ai-voice-clone"], strength=0.78),
    ]

    all_signals = opp_signals + graph_signals + viral_signals
    print(f"Signals: {len(opp_signals)} opportunity + {len(graph_signals)} graph + {len(viral_signals)} viral = {len(all_signals)} total")

    # Shocks: viral events that could happen
    shocks = [
        create_shock("viral_adoption", ["meme-coin-launcher", "tiktok-creator"], inject_at_round=2),
        create_shock("breakout_tool", ["mcp-server-builder", "cursor-copilot", "supabase-fullstack"], inject_at_round=4),
        create_shock("ecosystem_integration", ["github-actions", "mcp-server-builder"], inject_at_round=6),
        create_shock("viral_adoption", ["telegram-miniapp", "crypto-airdrop"], inject_at_round=5),
        create_shock("market_crash", ["meme-coin-launcher", "crypto-airdrop", "onchain-analytics"], inject_at_round=12),
        create_shock("regulatory_ban", ["ai-voice-clone", "ai-avatar"], inject_at_round=14),
    ]

    # ========================================================================
    # FLAGSHIP: 1000-agent simulation
    # ========================================================================

    print(f"\n--- Flagship Simulation (1000 agents) ---")
    personas = generate_personas(graph, domain_ids, count_per_type=125, seed=42)
    print(f"Personas: {len(personas)} agents")

    t0 = time.perf_counter()
    builder_result = run_simulation(
        graph, domain_ids, personas=list(personas),
        signals=all_signals, shocks=shocks,
        max_rounds=20, seed=42, context="builder_community",
    )
    t_sim = time.perf_counter() - t0
    print(f"Builder simulation: {t_sim:.3f}s")

    t0 = time.perf_counter()
    enterprise_personas = generate_personas(graph, domain_ids, count_per_type=125, seed=42)
    enterprise_result = run_simulation(
        graph, domain_ids, personas=enterprise_personas,
        signals=all_signals, shocks=shocks,
        max_rounds=20, seed=42, context="enterprise_market",
    )
    t_ent = time.perf_counter() - t0
    print(f"Enterprise simulation: {t_ent:.3f}s")

    # ========================================================================
    # MONTE CARLO ENSEMBLE (20 runs x 240 agents)
    # ========================================================================

    print(f"\n--- Monte Carlo Ensemble (20 runs x 240 agents) ---")
    t0 = time.perf_counter()
    ensemble_result = run_ensemble(
        graph, domain_ids, signals=all_signals, shocks=shocks,
        max_rounds=20, n_runs=20, base_seed=42,
        context="builder_community", count_per_type=30,
    )
    t_ensemble = time.perf_counter() - t0
    print(f"Ensemble: {t_ensemble:.3f}s")

    # ========================================================================
    # SENSITIVITY ANALYSIS
    # ========================================================================

    print(f"\n--- Sensitivity Analysis ---")
    t0 = time.perf_counter()
    sensitivity_result = run_sensitivity(
        graph, domain_ids, signals=all_signals, shocks=shocks,
        max_rounds=20, seed=42, count_per_type=2,
    )
    t_sens = time.perf_counter() - t0
    print(f"Sensitivity: {t_sens:.3f}s")

    total_time = t_graph + t_sim + t_ent + t_ensemble + t_sens
    print(f"\nTotal: {total_time:.1f}s")

    # ========================================================================
    # RESULTS
    # ========================================================================

    print("\n" + "=" * 80)
    print("VIRAL DOMAIN RANKINGS (sorted by ensemble mean adoption)")
    print("=" * 80)

    results = []
    for d in VIRAL_DOMAINS:
        d_id = d["domain_id"]
        b = builder_result["domains"].get(d_id, {})
        e = enterprise_result["domains"].get(d_id, {})
        ens = ensemble_result["domains"].get(d_id, {})
        sens = sensitivity_result.get("most_sensitive_factor", {}).get(d_id, "?")
        importance = sensitivity_result.get("factor_importance", {}).get(d_id, {})

        results.append({
            "domain_id": d_id,
            "label": d["label"],
            "builder": b.get("final_adoption_rate", 0),
            "enterprise": e.get("final_adoption_rate", 0),
            "advocacy": b.get("final_advocacy_rate", 0),
            "tipping": b.get("tipping_point_round"),
            "consensus": b.get("final_consensus", 0),
            "static": d.get("composite_score", 0),
            "ens_mean": ens.get("mean_adoption", 0),
            "ens_p10": ens.get("p10_adoption", 0),
            "ens_p90": ens.get("p90_adoption", 0),
            "ens_std": ens.get("std_adoption", 0),
            "tipping_rate": ens.get("tipping_rate", 0),
            "most_sensitive": sens,
            "max_impact": max(importance.values(), default=0),
        })

    results.sort(key=lambda x: x["ens_mean"], reverse=True)

    print(f"\n{'#':<4s} {'Domain':<24s} {'Ens Mean':>9s} {'P10-P90':>12s} {'Builder':>8s} {'Ent':>6s} {'Advocacy':>9s} {'Tip':>5s} {'Sensitive To'}")
    print("-" * 110)
    for i, r in enumerate(results, 1):
        tp = f"R{r['tipping']:d}" if r["tipping"] is not None else "-"
        ci = f"{r['ens_p10']:.0%}-{r['ens_p90']:.0%}"
        print(f"{i:<4d} {r['domain_id']:<24s} {r['ens_mean']:8.1%} {ci:>12s} {r['builder']:7.1%} {r['enterprise']:5.1%} {r['advocacy']:8.1%} {tp:>5s}  {r['most_sensitive']}")

    # ========================================================================
    # VIRALITY TIERS
    # ========================================================================

    print("\n" + "=" * 80)
    print("VIRALITY TIERS (build priority for Spark growth)")
    print("=" * 80)

    tier1 = [r for r in results if r["ens_mean"] > 0.5]
    tier2 = [r for r in results if 0.25 <= r["ens_mean"] <= 0.5]
    tier3 = [r for r in results if 0.10 <= r["ens_mean"] < 0.25]
    tier4 = [r for r in results if r["ens_mean"] < 0.10]

    print(f"\nTIER 1 -- BUILD NOW (adoption > 50%, high viral potential)")
    for r in tier1:
        gap = r["builder"] - r["enterprise"]
        width = r["ens_p90"] - r["ens_p10"]
        certainty = "HIGH" if width < 0.05 else "MED" if width < 0.15 else "LOW"
        print(f"  {r['domain_id']:<24s} {r['ens_mean']:5.1%} [{certainty}]  gap={gap:+.0%}  advocacy={r['advocacy']:.0%}  why: {r['label']}")

    print(f"\nTIER 2 -- BUILD SOON (adoption 25-50%, strong signal)")
    for r in tier2:
        print(f"  {r['domain_id']:<24s} {r['ens_mean']:5.1%}  sensitive to: {r['most_sensitive']}")

    print(f"\nTIER 3 -- MONITOR (adoption 10-25%, uncertain)")
    for r in tier3:
        print(f"  {r['domain_id']:<24s} {r['ens_mean']:5.1%}  needs: stronger signal")

    print(f"\nTIER 4 -- SKIP FOR NOW (adoption < 10%)")
    for r in tier4:
        print(f"  {r['domain_id']:<24s} {r['ens_mean']:5.1%}  blocker: {r['most_sensitive']}")

    # ========================================================================
    # CLUSTER ANALYSIS
    # ========================================================================

    print("\n" + "=" * 80)
    print("VIRAL CLUSTER ANALYSIS (which clusters amplify each other?)")
    print("=" * 80)

    clusters = {
        "Crypto Viral Loop": ["meme-coin-launcher", "crypto-airdrop", "onchain-analytics", "telegram-miniapp"],
        "Content Creator Engine": ["tiktok-creator", "twitter-threads", "linkedin-ghostwriter", "podcast-producer"],
        "Dev Tools Ecosystem": ["mcp-server-builder", "cursor-copilot", "github-actions", "supabase-fullstack"],
        "Visual/Creative": ["midjourney-art", "ai-avatar", "ai-voice-clone"],
        "Commerce/Growth": ["shopify-growth", "seo-dominator", "no-code-saas", "browser-extension"],
    }

    result_map = {r["domain_id"]: r for r in results}
    for cluster_name, members in clusters.items():
        member_results = [result_map[m] for m in members if m in result_map]
        if not member_results:
            continue
        avg_adoption = sum(r["ens_mean"] for r in member_results) / len(member_results)
        avg_advocacy = sum(r["advocacy"] for r in member_results) / len(member_results)
        tipping_count = sum(1 for r in member_results if r["tipping"] is not None)

        print(f"\n  {cluster_name}")
        print(f"    Avg adoption: {avg_adoption:.1%}  |  Avg advocacy: {avg_advocacy:.1%}  |  Tipping: {tipping_count}/{len(member_results)}")
        for r in sorted(member_results, key=lambda x: x["ens_mean"], reverse=True):
            tp = f"R{r['tipping']}" if r["tipping"] is not None else "-"
            print(f"      {r['domain_id']:<22s} {r['ens_mean']:5.1%}  tip={tp:>4s}  adv={r['advocacy']:.0%}")

    # ========================================================================
    # SPARK GROWTH RECOMMENDATIONS
    # ========================================================================

    print("\n" + "=" * 80)
    print("SPARK GROWTH STRATEGY")
    print("=" * 80)

    print(f"""
Based on the simulation of {len(VIRAL_DOMAINS)} viral domains with {len(personas)} agents:

IMMEDIATE ACTIONS (build these domain chips first):""")

    for i, r in enumerate(results[:5], 1):
        print(f"  {i}. {r['label']} ({r['domain_id']})")
        print(f"     Adoption: {r['ens_mean']:.0%} | Advocacy: {r['advocacy']:.0%} | Builder-Enterprise gap: {r['builder'] - r['enterprise']:+.0%}")

    print(f"""
VIRAL AMPLIFICATION STRATEGY:
  - Crypto cluster drives discovery (meme coins -> airdrop -> analytics)
  - Dev tools cluster drives retention (MCP -> Cursor -> GitHub Actions)
  - Content cluster drives brand awareness (TikTok -> Threads -> LinkedIn)
  - Each chip user becomes Spark evangelist through shareable output

NETWORK EFFECTS:
  - {sum(1 for r in results if r['ens_mean'] > 0.5)} domains above 50% adoption = critical mass
  - {sum(1 for r in results if r['tipping'] is not None)} domains reached tipping point within 20 rounds
  - Average advocacy rate: {sum(r['advocacy'] for r in results) / len(results):.1%}
""")

    # ========================================================================
    # EXPORT DATA
    # ========================================================================

    export = {
        "meta": {
            "title": "MiroFish Viral Domain Prediction",
            "domain_count": len(VIRAL_DOMAINS),
            "agent_count": len(personas),
            "ensemble_runs": 20,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "results": [{
            "domain_id": r["domain_id"],
            "label": r["label"],
            "ensemble_mean": r["ens_mean"],
            "ensemble_p10": r["ens_p10"],
            "ensemble_p90": r["ens_p90"],
            "builder_adoption": r["builder"],
            "enterprise_adoption": r["enterprise"],
            "advocacy_rate": r["advocacy"],
            "tipping_point": r["tipping"],
            "static_score": r["static"],
            "most_sensitive_factor": r["most_sensitive"],
        } for r in results],
        "clusters": {name: {
            "members": members,
            "avg_adoption": sum(result_map[m]["ens_mean"] for m in members if m in result_map) / len(members),
        } for name, members in clusters.items()},
    }

    output_path = "viz/viral_predictions.json"
    with open(output_path, "w") as f:
        json.dump(export, f, indent=2)
    print(f"Exported to {output_path}")


if __name__ == "__main__":
    main()
