"""Run 1000-agent MiroFish simulation across existing + new domain candidates.

Predicts which domains will be trendy and popular in spark-swarm,
both among what we've already built and new opportunities.
"""

import time
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
from chip_labs.mirofish.calibration import replay_calibration
from chip_labs.mirofish.report import generate_prediction_report
from chip_labs.trend_scanner import rank_opportunities, score_opportunity

# ============================================================================
# DOMAIN UNIVERSE: Existing chips + New candidates
# ============================================================================

# --- Already built (12 existing chips) ---
EXISTING_CHIPS = [
    {
        "domain_id": "startup-yc",
        "label": "YC Startup Evaluation",
        "description": "Startup scoring, pitch evaluation, YC-style factor analysis.",
        "scores": {"market_size": 0.85, "data_availability": 0.90, "benchmark_feasibility": 0.88, "community_demand": 0.82, "spark_ecosystem_fit": 0.95, "monetization_potential": 0.75},
        "rationale": "Reference implementation. v0.3.0 production chip.",
        "related_chips": [],
        "evidence_sources": ["github", "community", "spark_ecosystem"],
        "status": "production",
    },
    {
        "domain_id": "trading-crypto",
        "label": "Crypto Trading Strategy",
        "description": "Trading signals, doctrine/strategy separation, market regime detection.",
        "scores": {"market_size": 0.92, "data_availability": 0.88, "benchmark_feasibility": 0.85, "community_demand": 0.90, "spark_ecosystem_fit": 0.90, "monetization_potential": 0.92},
        "rationale": "Second production chip. Doctrine + strategy pattern.",
        "related_chips": ["startup-yc"],
        "evidence_sources": ["github", "x_twitter", "community"],
        "status": "production",
    },
    {
        "domain_id": "agentic-marketing",
        "label": "AI Marketing Automation",
        "description": "Content marketing, campaign optimization, audience analysis.",
        "scores": {"market_size": 0.80, "data_availability": 0.75, "benchmark_feasibility": 0.72, "community_demand": 0.78, "spark_ecosystem_fit": 0.82, "monetization_potential": 0.80},
        "rationale": "Beta chip with strong growth trajectory.",
        "related_chips": ["startup-yc"],
        "evidence_sources": ["producthunt", "x_twitter", "community"],
        "status": "beta",
    },
    {
        "domain_id": "web-designer",
        "label": "Web Design Patterns",
        "description": "UI/UX patterns, component architecture, design systems.",
        "scores": {"market_size": 0.78, "data_availability": 0.72, "benchmark_feasibility": 0.68, "community_demand": 0.75, "spark_ecosystem_fit": 0.70, "monetization_potential": 0.65},
        "rationale": "Alpha chip. Visual design is high-demand but hard to benchmark.",
        "related_chips": [],
        "evidence_sources": ["github", "producthunt"],
        "status": "alpha",
    },
    {
        "domain_id": "xcontent",
        "label": "X/Twitter Content Strategy",
        "description": "Thread writing, engagement optimization, audience growth.",
        "scores": {"market_size": 0.72, "data_availability": 0.80, "benchmark_feasibility": 0.65, "community_demand": 0.82, "spark_ecosystem_fit": 0.75, "monetization_potential": 0.70},
        "rationale": "Alpha chip. High virality potential.",
        "related_chips": ["agentic-marketing"],
        "evidence_sources": ["x_twitter", "community"],
        "status": "alpha",
    },
    {
        "domain_id": "pokemon-red",
        "label": "Pokemon Game AI",
        "description": "Game AI, battle strategy, team building optimization.",
        "scores": {"market_size": 0.55, "data_availability": 0.70, "benchmark_feasibility": 0.75, "community_demand": 0.68, "spark_ecosystem_fit": 0.65, "monetization_potential": 0.40},
        "rationale": "Niche but passionate community. Proof of concept for game chips.",
        "related_chips": [],
        "evidence_sources": ["github", "community"],
        "status": "alpha",
    },
    {
        "domain_id": "roblox-development",
        "label": "Roblox Game Development",
        "description": "Roblox Lua scripting, game design, monetization.",
        "scores": {"market_size": 0.70, "data_availability": 0.68, "benchmark_feasibility": 0.72, "community_demand": 0.72, "spark_ecosystem_fit": 0.65, "monetization_potential": 0.60},
        "rationale": "Large addressable market. 97% of game studios using AI tools.",
        "related_chips": ["pokemon-red"],
        "evidence_sources": ["github", "community"],
        "status": "alpha",
    },
    {
        "domain_id": "vibe-incubator",
        "label": "Vibe Coding Incubator",
        "description": "Project scaffolding, vibe-coded prototyping, rapid iteration.",
        "scores": {"market_size": 0.65, "data_availability": 0.60, "benchmark_feasibility": 0.58, "community_demand": 0.70, "spark_ecosystem_fit": 0.88, "monetization_potential": 0.55},
        "rationale": "Meta-chip for the chip ecosystem itself.",
        "related_chips": ["startup-yc"],
        "evidence_sources": ["spark_ecosystem", "community"],
        "status": "alpha",
    },
    {
        "domain_id": "content",
        "label": "Content Strategy",
        "description": "Blog writing, SEO, content calendar management.",
        "scores": {"market_size": 0.70, "data_availability": 0.65, "benchmark_feasibility": 0.55, "community_demand": 0.60, "spark_ecosystem_fit": 0.58, "monetization_potential": 0.62},
        "rationale": "Weakest chip (74/100). Needs quality audit.",
        "related_chips": ["agentic-marketing"],
        "evidence_sources": ["community"],
        "status": "alpha",
    },
    {
        "domain_id": "predictive-worlds-lab",
        "label": "Prediction & Simulation Research",
        "description": "MiroFish analysis, OASIS study, prediction calibration.",
        "scores": {"market_size": 0.50, "data_availability": 0.55, "benchmark_feasibility": 0.60, "community_demand": 0.45, "spark_ecosystem_fit": 0.80, "monetization_potential": 0.40},
        "rationale": "Research chip. Informed MiroFish integration in chip-labs.",
        "related_chips": [],
        "evidence_sources": ["arxiv", "github"],
        "status": "alpha",
    },
]

# --- New candidates (not yet built) ---
NEW_CANDIDATES = [
    # Tier 1: High signal from trend_scanner
    {
        "domain_id": "defi-architect",
        "label": "DeFi Architecture",
        "description": "Smart contract patterns, MEV protection, liquidity strategies, gas optimization.",
        "scores": {"market_size": 0.90, "data_availability": 0.85, "benchmark_feasibility": 0.80, "community_demand": 0.92, "spark_ecosystem_fit": 0.85, "monetization_potential": 0.95},
        "rationale": "AI agent token market cap at $7.7B. Natural extension of trading-crypto.",
        "related_chips": ["trading-crypto"],
        "evidence_sources": ["github", "x_twitter", "community"],
    },
    {
        "domain_id": "ai-agent-builder",
        "label": "AI Agent Architecture",
        "description": "Agent patterns, tool selection, prompt engineering, eval frameworks, MCP integration.",
        "scores": {"market_size": 0.88, "data_availability": 0.82, "benchmark_feasibility": 0.75, "community_demand": 0.90, "spark_ecosystem_fit": 0.80, "monetization_potential": 0.78},
        "rationale": "AI agents are #1 category on Product Hunt 2026. MCP has 10,000+ servers.",
        "related_chips": [],
        "evidence_sources": ["producthunt", "github", "arxiv"],
    },
    {
        "domain_id": "indie-hacker",
        "label": "Indie Hacker / Micro SaaS",
        "description": "Micro SaaS validation, pricing strategy, launch playbook, distribution channels.",
        "scores": {"market_size": 0.82, "data_availability": 0.78, "benchmark_feasibility": 0.72, "community_demand": 0.85, "spark_ecosystem_fit": 0.82, "monetization_potential": 0.80},
        "rationale": "Micro SaaS market growing 30% annually. Solo founders are most active sharers.",
        "related_chips": ["startup-yc", "agentic-marketing"],
        "evidence_sources": ["community", "x_twitter", "producthunt"],
    },
    # Tier 2: Niche but strong signal
    {
        "domain_id": "game-balance",
        "label": "Game Balance & Economy Design",
        "description": "Game economy, difficulty curves, player progression, monetization balance.",
        "scores": {"market_size": 0.72, "data_availability": 0.70, "benchmark_feasibility": 0.78, "community_demand": 0.74, "spark_ecosystem_fit": 0.75, "monetization_potential": 0.65},
        "rationale": "97% of game studios use AI tools. Extends pokemon-red + roblox.",
        "related_chips": ["pokemon-red", "roblox-development"],
        "evidence_sources": ["github", "community"],
    },
    {
        "domain_id": "compliance-shield",
        "label": "Compliance Automation",
        "description": "SOX, GDPR, SOC2, HIPAA automated checks and evidence collection.",
        "scores": {"market_size": 0.75, "data_availability": 0.60, "benchmark_feasibility": 0.65, "community_demand": 0.68, "spark_ecosystem_fit": 0.55, "monetization_potential": 0.88},
        "rationale": "Enterprise AI is 'Year of 2026'. High willingness to pay.",
        "related_chips": [],
        "evidence_sources": ["vc_landscape", "community"],
    },
    {
        "domain_id": "legal-ops",
        "label": "Legal Operations AI",
        "description": "Contract analysis, clause identification, risk scoring, due diligence.",
        "scores": {"market_size": 0.78, "data_availability": 0.55, "benchmark_feasibility": 0.58, "community_demand": 0.65, "spark_ecosystem_fit": 0.50, "monetization_potential": 0.85},
        "rationale": "Harvey raised $100M+. Vertical AI poster child.",
        "related_chips": [],
        "evidence_sources": ["vc_landscape"],
    },
    # --- NEW: Fresh candidates beyond what trend_scanner has ---
    {
        "domain_id": "data-engineer",
        "label": "Data Engineering Patterns",
        "description": "ETL/ELT pipelines, data quality, dbt patterns, Spark/Flink optimization, data mesh.",
        "scores": {"market_size": 0.85, "data_availability": 0.80, "benchmark_feasibility": 0.75, "community_demand": 0.78, "spark_ecosystem_fit": 0.72, "monetization_potential": 0.82},
        "rationale": "Every company needs data infra. dbt has 50K+ companies using it. Massive GitHub ecosystem.",
        "related_chips": [],
        "evidence_sources": ["github", "community", "producthunt"],
    },
    {
        "domain_id": "personal-finance",
        "label": "Personal Finance AI",
        "description": "Budgeting optimization, tax strategy, investment allocation, debt payoff planning.",
        "scores": {"market_size": 0.88, "data_availability": 0.65, "benchmark_feasibility": 0.60, "community_demand": 0.85, "spark_ecosystem_fit": 0.60, "monetization_potential": 0.90},
        "rationale": "Everyone needs it. Mint shutdown left a gap. AI finance advisors are hot on TikTok/X.",
        "related_chips": ["trading-crypto"],
        "evidence_sources": ["x_twitter", "producthunt", "community"],
    },
    {
        "domain_id": "open-source-maintainer",
        "label": "Open Source Project Management",
        "description": "Issue triage, PR review, release management, community health, contributor onboarding.",
        "scores": {"market_size": 0.65, "data_availability": 0.90, "benchmark_feasibility": 0.82, "community_demand": 0.72, "spark_ecosystem_fit": 0.85, "monetization_potential": 0.45},
        "rationale": "GitHub has 100M+ devs. OSS maintainer burnout is real. AI triage saves hours/week.",
        "related_chips": [],
        "evidence_sources": ["github", "community"],
    },
    {
        "domain_id": "newsletter-growth",
        "label": "Newsletter & Audience Growth",
        "description": "Newsletter writing, subscriber growth, monetization, referral programs, Substack/Beehiiv.",
        "scores": {"market_size": 0.72, "data_availability": 0.70, "benchmark_feasibility": 0.65, "community_demand": 0.80, "spark_ecosystem_fit": 0.68, "monetization_potential": 0.78},
        "rationale": "Creator economy booming. Newsletter is the new blog. Beehiiv growing 200% YoY.",
        "related_chips": ["xcontent", "agentic-marketing", "content"],
        "evidence_sources": ["x_twitter", "producthunt", "community"],
    },
    {
        "domain_id": "solana-dev",
        "label": "Solana Development",
        "description": "Anchor framework, SPL tokens, Solana program optimization, Metaplex NFTs.",
        "scores": {"market_size": 0.82, "data_availability": 0.78, "benchmark_feasibility": 0.72, "community_demand": 0.88, "spark_ecosystem_fit": 0.75, "monetization_potential": 0.88},
        "rationale": "Solana is #2 L1. Pump.fun alone did $500M in fees. Massive builder community.",
        "related_chips": ["trading-crypto", "defi-architect"],
        "evidence_sources": ["github", "x_twitter", "community"],
    },
    {
        "domain_id": "prompt-engineer",
        "label": "Prompt Engineering Mastery",
        "description": "System prompt design, chain-of-thought patterns, eval-driven prompt iteration, jailbreak defense.",
        "scores": {"market_size": 0.80, "data_availability": 0.85, "benchmark_feasibility": 0.80, "community_demand": 0.88, "spark_ecosystem_fit": 0.90, "monetization_potential": 0.65},
        "rationale": "Every AI builder needs this. Anthropic/OpenAI prompt guides get millions of views.",
        "related_chips": ["ai-agent-builder"],
        "evidence_sources": ["github", "arxiv", "community"],
    },
    {
        "domain_id": "devrel-community",
        "label": "Developer Relations & Community",
        "description": "DevRel strategy, community building, developer experience, docs-as-code, hackathon design.",
        "scores": {"market_size": 0.68, "data_availability": 0.65, "benchmark_feasibility": 0.55, "community_demand": 0.72, "spark_ecosystem_fit": 0.78, "monetization_potential": 0.60},
        "rationale": "Every dev tool company needs DevRel. Community-led growth is the new playbook.",
        "related_chips": ["agentic-marketing", "open-source-maintainer"],
        "evidence_sources": ["x_twitter", "community"],
    },
    {
        "domain_id": "security-audit",
        "label": "Security Audit & Pentesting",
        "description": "Code audit patterns, vulnerability detection, OWASP coverage, smart contract security.",
        "scores": {"market_size": 0.80, "data_availability": 0.75, "benchmark_feasibility": 0.78, "community_demand": 0.82, "spark_ecosystem_fit": 0.65, "monetization_potential": 0.90},
        "rationale": "Every deploy needs security review. AI-assisted audits reduce cost 10x. Bug bounty market at $100M+.",
        "related_chips": ["defi-architect", "compliance-shield"],
        "evidence_sources": ["github", "community", "vc_landscape"],
    },
    {
        "domain_id": "music-producer",
        "label": "AI Music Production",
        "description": "Beat making, mixing/mastering, sample selection, genre-aware composition.",
        "scores": {"market_size": 0.70, "data_availability": 0.60, "benchmark_feasibility": 0.50, "community_demand": 0.75, "spark_ecosystem_fit": 0.45, "monetization_potential": 0.72},
        "rationale": "Suno/Udio exploded. AI music tools are top trending. But benchmark feasibility is hard.",
        "related_chips": [],
        "evidence_sources": ["producthunt", "x_twitter"],
    },
    {
        "domain_id": "sales-closer",
        "label": "AI Sales & Closing",
        "description": "Sales call analysis, objection handling, pipeline management, CRM automation.",
        "scores": {"market_size": 0.85, "data_availability": 0.68, "benchmark_feasibility": 0.62, "community_demand": 0.78, "spark_ecosystem_fit": 0.55, "monetization_potential": 0.92},
        "rationale": "AI SDR tools raised $500M+ in 2025. Every B2B company needs this.",
        "related_chips": ["agentic-marketing"],
        "evidence_sources": ["producthunt", "vc_landscape"],
    },
    {
        "domain_id": "health-wellness",
        "label": "Health & Wellness AI",
        "description": "Fitness programming, nutrition planning, sleep optimization, biomarker analysis.",
        "scores": {"market_size": 0.88, "data_availability": 0.55, "benchmark_feasibility": 0.48, "community_demand": 0.80, "spark_ecosystem_fit": 0.40, "monetization_potential": 0.85},
        "rationale": "Huge TAM but data privacy concerns. Whoop/Oura creating data access. Hard to benchmark.",
        "related_chips": [],
        "evidence_sources": ["producthunt", "community"],
    },
    {
        "domain_id": "real-estate-analyst",
        "label": "Real Estate Analysis AI",
        "description": "Property valuation, market analysis, investment thesis, rental yield optimization.",
        "scores": {"market_size": 0.82, "data_availability": 0.70, "benchmark_feasibility": 0.65, "community_demand": 0.68, "spark_ecosystem_fit": 0.50, "monetization_potential": 0.88},
        "rationale": "Zillow, Redfin APIs exist. High willingness to pay. Data availability improving.",
        "related_chips": ["personal-finance"],
        "evidence_sources": ["community", "vc_landscape"],
    },
    {
        "domain_id": "education-tutor",
        "label": "AI Tutoring & Learning",
        "description": "Personalized learning paths, Socratic questioning, knowledge gap detection, exam prep.",
        "scores": {"market_size": 0.85, "data_availability": 0.72, "benchmark_feasibility": 0.68, "community_demand": 0.82, "spark_ecosystem_fit": 0.55, "monetization_potential": 0.78},
        "rationale": "Khan Academy + GPT proved the model. Duolingo Max crushing it. Parents pay.",
        "related_chips": [],
        "evidence_sources": ["producthunt", "community", "arxiv"],
    },
    {
        "domain_id": "supply-chain",
        "label": "Supply Chain Optimization",
        "description": "Inventory optimization, demand forecasting, logistics routing, supplier risk scoring.",
        "scores": {"market_size": 0.80, "data_availability": 0.58, "benchmark_feasibility": 0.55, "community_demand": 0.55, "spark_ecosystem_fit": 0.42, "monetization_potential": 0.88},
        "rationale": "Enterprise goldmine but low community demand. Hard to get benchmark data.",
        "related_chips": [],
        "evidence_sources": ["vc_landscape"],
    },
    {
        "domain_id": "video-creator",
        "label": "AI Video Production",
        "description": "Script-to-video, editing automation, thumbnail generation, shorts optimization.",
        "scores": {"market_size": 0.82, "data_availability": 0.62, "benchmark_feasibility": 0.52, "community_demand": 0.85, "spark_ecosystem_fit": 0.50, "monetization_potential": 0.80},
        "rationale": "YouTube Shorts, TikTok, Reels. Runway/Pika proving AI video works. Massive demand.",
        "related_chips": ["xcontent"],
        "evidence_sources": ["producthunt", "x_twitter", "community"],
    },
    {
        "domain_id": "resume-career",
        "label": "Resume & Career AI",
        "description": "Resume optimization, interview prep, salary negotiation, career path planning.",
        "scores": {"market_size": 0.78, "data_availability": 0.72, "benchmark_feasibility": 0.70, "community_demand": 0.80, "spark_ecosystem_fit": 0.55, "monetization_potential": 0.75},
        "rationale": "Everyone needs a job. AI resume tools are top on Product Hunt. High personal ROI.",
        "related_chips": [],
        "evidence_sources": ["producthunt", "community"],
    },
]

ALL_DOMAINS = EXISTING_CHIPS + NEW_CANDIDATES

# ============================================================================
# RUN 1000-AGENT SIMULATION
# ============================================================================

def main():
    print("=" * 80)
    print("MIROFISH 1000-AGENT TREND PREDICTION")
    print(f"Domains: {len(EXISTING_CHIPS)} existing + {len(NEW_CANDIDATES)} new = {len(ALL_DOMAINS)} total")
    print("=" * 80)

    # Score all domains
    for d in ALL_DOMAINS:
        d["composite_score"] = score_opportunity(d)

    # Build graph
    t0 = time.perf_counter()
    graph = build_graph_from_opportunities(ALL_DOMAINS)
    t_graph = time.perf_counter() - t0
    print(f"\nGraph: {graph.node_count} nodes, {graph.edge_count} edges (built in {t_graph:.3f}s)")

    # Generate 1000 personas (125 per type * 8 types)
    t0 = time.perf_counter()
    domain_ids = [d["domain_id"] for d in ALL_DOMAINS]
    personas = generate_personas(graph, domain_ids, count_per_type=125, seed=42)
    t_personas = time.perf_counter() - t0
    print(f"Personas: {len(personas)} agents (generated in {t_personas:.3f}s)")

    # Generate signals
    t0 = time.perf_counter()
    opp_signals = signals_from_opportunities(ALL_DOMAINS)
    graph_signals = signals_from_graph(graph)
    all_signals = opp_signals + graph_signals
    t_signals = time.perf_counter() - t0
    print(f"Signals: {len(opp_signals)} opportunity + {len(graph_signals)} graph = {len(all_signals)} total ({t_signals:.3f}s)")

    # Add shocks for realism
    shocks = [
        create_shock("breakout_tool", ["ai-agent-builder", "prompt-engineer"], inject_at_round=3),
        create_shock("viral_adoption", ["solana-dev", "defi-architect"], inject_at_round=5),
        create_shock("market_crash", ["trading-crypto", "defi-architect", "solana-dev", "personal-finance"], inject_at_round=8),
        create_shock("ecosystem_integration", ["open-source-maintainer", "ai-agent-builder"], inject_at_round=4),
        create_shock("regulatory_ban", ["health-wellness", "compliance-shield"], inject_at_round=10),
    ]

    # Run builder community simulation
    print(f"\nRunning simulation with {len(personas)} agents, {len(domain_ids)} domains, 20 rounds...")
    t0 = time.perf_counter()
    builder_result = run_simulation(
        graph, domain_ids, personas=personas,
        signals=all_signals, shocks=shocks,
        max_rounds=20, seed=42, context="builder_community",
    )
    t_sim = time.perf_counter() - t0
    print(f"Simulation completed in {t_sim:.3f}s")
    print(f"Performance: {len(personas) * len(domain_ids) * 20:,} persona-domain-round evaluations")

    # Run enterprise simulation with fresh personas
    t0 = time.perf_counter()
    enterprise_personas = generate_personas(graph, domain_ids, count_per_type=125, seed=42)
    enterprise_result = run_simulation(
        graph, domain_ids, personas=enterprise_personas,
        signals=all_signals, shocks=shocks,
        max_rounds=20, seed=42, context="enterprise_market",
    )
    t_ent = time.perf_counter() - t0
    print(f"Enterprise simulation: {t_ent:.3f}s")

    total_time = t_graph + t_personas + t_signals + t_sim + t_ent
    print(f"\nTotal wall time (flagship): {total_time:.3f}s")

    # ========================================================================
    # MONTE CARLO ENSEMBLE (10 runs x 240 agents for confidence intervals)
    # ========================================================================

    print("\n" + "=" * 80)
    print("MONTE CARLO ENSEMBLE (10 runs x 240 agents)")
    print("=" * 80)

    t0 = time.perf_counter()
    ensemble_result = run_ensemble(
        graph, domain_ids, signals=all_signals, shocks=shocks,
        max_rounds=20, n_runs=10, base_seed=42,
        context="builder_community", count_per_type=30,
    )
    t_ensemble = time.perf_counter() - t0
    print(f"Ensemble completed in {t_ensemble:.3f}s ({10 * 240 * len(domain_ids) * 20:,} agent-domain-round evals)")

    # ========================================================================
    # SENSITIVITY ANALYSIS (4 factors, lightweight agents)
    # ========================================================================

    print("\n" + "=" * 80)
    print("SENSITIVITY ANALYSIS (signal strength, thresholds, persona count, shock timing)")
    print("=" * 80)

    t0 = time.perf_counter()
    sensitivity_result = run_sensitivity(
        graph, domain_ids, signals=all_signals, shocks=shocks,
        max_rounds=20, seed=42, context="builder_community",
        count_per_type=2,
    )
    t_sensitivity = time.perf_counter() - t0
    print(f"Sensitivity analysis completed in {t_sensitivity:.3f}s")

    total_time += t_ensemble + t_sensitivity
    print(f"\nTotal wall time (all analyses): {total_time:.3f}s")

    # ========================================================================
    # RESULTS
    # ========================================================================

    print("\n" + "=" * 80)
    print("PREDICTIONS: AMONG EXISTING CHIPS (what to evolve)")
    print("=" * 80)

    existing_ids = {d["domain_id"] for d in EXISTING_CHIPS}
    existing_results = []
    for d_id in sorted(existing_ids):
        b = builder_result["domains"].get(d_id, {})
        e = enterprise_result["domains"].get(d_id, {})
        ens = ensemble_result["domains"].get(d_id, {})
        existing_results.append({
            "domain_id": d_id,
            "builder": b.get("final_adoption_rate", 0),
            "enterprise": e.get("final_adoption_rate", 0),
            "advocacy": b.get("final_advocacy_rate", 0),
            "tipping": b.get("tipping_point_round"),
            "consensus": b.get("final_consensus", 0),
            "disagreement": b.get("disagreement_score", 0),
            "status": next((c.get("status", "") for c in EXISTING_CHIPS if c["domain_id"] == d_id), ""),
            "static": next((c.get("composite_score", 0) for c in ALL_DOMAINS if c["domain_id"] == d_id), 0),
            "ens_mean": ens.get("mean_adoption", 0),
            "ens_p10": ens.get("p10_adoption", 0),
            "ens_p90": ens.get("p90_adoption", 0),
            "ens_std": ens.get("std_adoption", 0),
        })

    existing_results.sort(key=lambda x: x["builder"], reverse=True)
    print(f"\n{'Domain':<25s} {'Status':<12s} {'Builder':>8s} {'Ent':>6s} {'Advocacy':>9s} {'Tip':>5s} {'Ens Mean':>9s} {'P10-P90':>12s}")
    print("-" * 95)
    for r in existing_results:
        tp = f"R{r['tipping']:d}" if r["tipping"] is not None else "-"
        ci = f"{r['ens_p10']:.0%}-{r['ens_p90']:.0%}"
        print(f"{r['domain_id']:<25s} {r['status']:<12s} {r['builder']:7.1%} {r['enterprise']:5.1%} {r['advocacy']:8.1%} {tp:>5s} {r['ens_mean']:8.1%} {ci:>12s}")

    print("\n" + "=" * 80)
    print("PREDICTIONS: NEW DOMAIN CHIPS (what to build next)")
    print("=" * 80)

    new_ids = {d["domain_id"] for d in NEW_CANDIDATES} - existing_ids
    new_results = []
    for d_id in sorted(new_ids):
        b = builder_result["domains"].get(d_id, {})
        e = enterprise_result["domains"].get(d_id, {})
        ens = ensemble_result["domains"].get(d_id, {})
        static = next((c.get("composite_score", 0) for c in ALL_DOMAINS if c["domain_id"] == d_id), 0)
        new_results.append({
            "domain_id": d_id,
            "builder": b.get("final_adoption_rate", 0),
            "enterprise": e.get("final_adoption_rate", 0),
            "advocacy": b.get("final_advocacy_rate", 0),
            "tipping": b.get("tipping_point_round"),
            "consensus": b.get("final_consensus", 0),
            "disagreement": b.get("disagreement_score", 0),
            "static": static,
            "delta": round(b.get("final_adoption_rate", 0) - static, 4),
            "ens_mean": ens.get("mean_adoption", 0),
            "ens_p10": ens.get("p10_adoption", 0),
            "ens_p90": ens.get("p90_adoption", 0),
            "ens_std": ens.get("std_adoption", 0),
        })

    new_results.sort(key=lambda x: x["builder"], reverse=True)
    print(f"\n{'Domain':<25s} {'Builder':>8s} {'Ent':>6s} {'Ens Mean':>9s} {'P10-P90':>12s} {'Static':>7s} {'Delta':>7s} {'Signal'}")
    print("-" * 100)
    for r in new_results:
        ci = f"{r['ens_p10']:.0%}-{r['ens_p90']:.0%}"
        if r["delta"] > 0.05:
            signal = "SIM HIGHER"
        elif r["delta"] < -0.05:
            signal = "SIM LOWER"
        else:
            signal = "ALIGNED"
        print(f"{r['domain_id']:<25s} {r['builder']:7.1%} {r['enterprise']:5.1%} {r['ens_mean']:8.1%} {ci:>12s} {r['static']:6.4f} {r['delta']:+6.4f}  {signal}")

    # Top picks
    print("\n" + "=" * 80)
    print("TOP 10 OVERALL (existing + new combined)")
    print("=" * 80)

    all_results = existing_results + new_results
    all_results.sort(key=lambda x: (x["ens_mean"], x["builder"]), reverse=True)

    print(f"\n{'#':<4s} {'Domain':<25s} {'Ens Mean':>9s} {'P10-P90':>12s} {'Builder':>8s} {'Ent':>6s} {'Gap':>6s}")
    print("-" * 80)
    for i, r in enumerate(all_results[:10], 1):
        gap = r["builder"] - r["enterprise"]
        ci = f"{r['ens_p10']:.0%}-{r['ens_p90']:.0%}"
        tag = " *NEW*" if r["domain_id"] in new_ids else f" [{r.get('status', '')}]"
        print(f"{i:<4d} {r['domain_id']:<25s} {r['ens_mean']:8.1%} {ci:>12s} {r['builder']:7.1%} {r['enterprise']:5.1%} {gap:+5.1%}{tag}")

    # Bottom 5 (avoid these)
    print(f"\n{'BOTTOM 5 (low adoption signal)':}")
    print("-" * 75)
    for r in all_results[-5:]:
        tp = f"R{r['tipping']:d}" if r["tipping"] is not None else "None"
        tag = " *NEW*" if r["domain_id"] in new_ids else f" [{r.get('status', '')}]"
        print(f"     {r['domain_id']:<25s} {r['builder']:7.1%} {r['enterprise']:10.1%} {r.get('advocacy', 0):8.1%} {tp:>8s}{tag}")

    # Biggest surprises (where sim differs most from static)
    print("\n" + "=" * 80)
    print("BIGGEST SURPRISES (sim vs static delta)")
    print("=" * 80)
    surprises = [r for r in all_results if "delta" in r]
    surprises.sort(key=lambda x: abs(x["delta"]), reverse=True)
    print(f"\n{'Domain':<25s} {'Sim':>8s} {'Static':>7s} {'Delta':>7s} {'Direction'}")
    print("-" * 60)
    for r in surprises[:8]:
        direction = "SIM HIGHER (undervalued by static)" if r["delta"] > 0 else "SIM LOWER (overvalued by static)"
        print(f"{r['domain_id']:<25s} {r['builder']:7.1%} {r['static']:6.4f} {r['delta']:+6.4f}  {direction}")

    # ========================================================================
    # ENSEMBLE CONFIDENCE ANALYSIS
    # ========================================================================

    print("\n" + "=" * 80)
    print("ENSEMBLE CONFIDENCE ANALYSIS (10 Monte Carlo runs)")
    print("=" * 80)

    # Sort by confidence width (uncertainty) -- most uncertain first
    uncertainty_ranked = sorted(all_results, key=lambda x: x.get("ens_std", 0), reverse=True)
    print(f"\n{'Domain':<25s} {'Ens Mean':>9s} {'Std':>6s} {'P10':>6s} {'P90':>6s} {'Width':>7s} {'Certainty'}")
    print("-" * 80)
    for r in uncertainty_ranked:
        width = r["ens_p90"] - r["ens_p10"]
        if width < 0.05:
            certainty = "HIGH"
        elif width < 0.15:
            certainty = "MEDIUM"
        else:
            certainty = "LOW"
        print(f"{r['domain_id']:<25s} {r['ens_mean']:8.1%} {r['ens_std']:5.3f} {r['ens_p10']:5.1%} {r['ens_p90']:5.1%} {width:6.1%}  {certainty}")

    # ========================================================================
    # SENSITIVITY ANALYSIS
    # ========================================================================

    print("\n" + "=" * 80)
    print("SENSITIVITY ANALYSIS (what factors drive adoption?)")
    print("=" * 80)

    factor_importance = sensitivity_result.get("factor_importance", {})
    most_sensitive = sensitivity_result.get("most_sensitive_factor", {})

    # Show per-domain most sensitive factor
    print(f"\n{'Domain':<25s} {'Most Sensitive Factor':<22s} {'Impact':>8s} {'Signal':>9s} {'Threshold':>10s} {'Count':>7s} {'Timing':>8s}")
    print("-" * 100)
    for r in all_results[:15]:
        d_id = r["domain_id"]
        importance = factor_importance.get(d_id, {})
        top_factor = most_sensitive.get(d_id, "?")
        sig_imp = importance.get("signal_strength", 0)
        thr_imp = importance.get("adoption_threshold", 0)
        cnt_imp = importance.get("persona_count", 0)
        tim_imp = importance.get("shock_timing", 0)
        print(f"{d_id:<25s} {top_factor:<22s} {max(importance.values(), default=0):7.3f} {sig_imp:8.3f} {thr_imp:9.3f} {cnt_imp:6.3f} {tim_imp:7.3f}")

    # Summary
    print("\n" + "=" * 80)
    print("ACTIONABLE SUMMARY")
    print("=" * 80)

    high_confidence_winners = [
        r for r in all_results
        if r["ens_mean"] > 0.3 and r.get("ens_std", 1) < 0.1
    ]
    high_upside_uncertain = [
        r for r in all_results
        if r["ens_mean"] > 0.2 and r.get("ens_std", 0) > 0.08
    ]
    low_adoption = [
        r for r in all_results
        if r["ens_mean"] < 0.1
    ]

    print(f"\nHigh-confidence picks (mean > 30%, std < 10%):")
    for r in sorted(high_confidence_winners, key=lambda x: x["ens_mean"], reverse=True)[:5]:
        tag = " *NEW*" if r["domain_id"] in new_ids else f" [{r.get('status', '')}]"
        print(f"  {r['domain_id']:<25s} {r['ens_mean']:5.1%} (p10={r['ens_p10']:.0%}, p90={r['ens_p90']:.0%}){tag}")

    print(f"\nHigh-upside / uncertain (mean > 20%, std > 8%):")
    for r in sorted(high_upside_uncertain, key=lambda x: x["ens_mean"], reverse=True)[:5]:
        tag = " *NEW*" if r["domain_id"] in new_ids else f" [{r.get('status', '')}]"
        print(f"  {r['domain_id']:<25s} {r['ens_mean']:5.1%} (p10={r['ens_p10']:.0%}, p90={r['ens_p90']:.0%}){tag}")

    print(f"\nLow adoption signal (mean < 10%) -- avoid or deprioritize:")
    for r in sorted(low_adoption, key=lambda x: x["ens_mean"])[:5]:
        tag = " *NEW*" if r["domain_id"] in new_ids else f" [{r.get('status', '')}]"
        most = most_sensitive.get(r["domain_id"], "?")
        print(f"  {r['domain_id']:<25s} {r['ens_mean']:5.1%} (most sensitive to: {most}){tag}")


if __name__ == "__main__":
    main()
