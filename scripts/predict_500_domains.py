"""MiroFish v4: 500-Domain Prediction with Macro Context & Retention Modeling.

The complete v4 pipeline:
- 515 domains (250 v3 + 265 new v4 categories)
- 15 persona types x 50 each = 750 agents
- 9-stage adoption funnel: unaware → aware → interested → evaluating →
  trial → adopted → committed → advocating | churned
- March 2026 macro context (AI displacement, regulatory pressure, etc.)
- Small-world network influence propagation
- Signal curve evolution (exponential, s_curve, plateau, linear)
- Monte Carlo ensemble (30 runs) with bootstrap 95% CIs
- Per-persona top-10 + cross-persona consensus
- Retention/churn tracking per domain
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
from chip_labs.mirofish.macro import MARCH_2026, MARCH_2026_EVENTS
from chip_labs.mirofish.systems import compute_system_priority, format_system_priority
from chip_labs.mirofish.report import generate_prediction_report, format_report_markdown

# =============================================================================
# IMPORT V3 DOMAINS (250)
# =============================================================================
from predict_100_domains import (
    EXISTING_CHIPS, NEW_CANDIDATES, VIRAL_DOMAINS, NEW_48_DOMAINS,
    RELATIONSHIPS,
)
from predict_250_domains import NEW_150_DOMAINS, NEW_RELATIONSHIPS

FIRST_100 = EXISTING_CHIPS + NEW_CANDIDATES + VIRAL_DOMAINS + NEW_48_DOMAINS
V3_DOMAINS = FIRST_100 + NEW_150_DOMAINS
V3_RELATIONSHIPS = RELATIONSHIPS + NEW_RELATIONSHIPS

# =============================================================================
# IMPORT V4 DOMAINS (265 new)
# =============================================================================
from domains_v4 import NEW_250_V4_DOMAINS, NEW_V4_RELATIONSHIPS

# =============================================================================
# COMBINE ALL 515 DOMAINS
# =============================================================================
ALL_DOMAINS = V3_DOMAINS + NEW_250_V4_DOMAINS
ALL_RELATIONSHIPS = V3_RELATIONSHIPS + NEW_V4_RELATIONSHIPS


def _enrich_v3_domain(d: dict) -> dict:
    """Add v4 fields to v3 domains that lack them."""
    if "retention_score" not in d:
        # Estimate retention from domain tags
        tags = set(d.get("domain_tags", []))
        if tags & {"productivity", "workflow", "dx"}:
            d["retention_score"] = 0.7
        elif tags & {"trading", "defi", "alpha"}:
            d["retention_score"] = 0.5
        elif tags & {"content_quality", "creative"}:
            d["retention_score"] = 0.6
        else:
            d["retention_score"] = 0.5
    if "urgency_score" not in d:
        tags = set(d.get("domain_tags", []))
        if tags & {"career", "reskill", "easy_start"}:
            d["urgency_score"] = 0.8
        elif tags & {"compliance", "risk_management"}:
            d["urgency_score"] = 0.7
        elif tags & {"alpha", "first_mover", "edge"}:
            d["urgency_score"] = 0.6
        else:
            d["urgency_score"] = 0.5
    return d


# V4 shock scenarios for 2026 macro context
V4_SHOCKS = [
    create_shock("mass_layoff", ["resume-ai", "career-pivot-ai", "upskill-path-ai",
                                   "ai-proof-career", "coding-bootcamp-ai",
                                   "prompt-job-skills", "interview-prep-ai"],
                 inject_at_round=3),
    create_shock("open_source_release", ["ai-agent-builder", "cursor-copilot",
                                          "fine-tuning-lab", "rag-pipeline",
                                          "multi-modal-ai", "prompt-engineer"],
                 inject_at_round=5),
    create_shock("government_subsidy", ["coding-bootcamp-ai", "upskill-path-ai",
                                         "corporate-training-ai", "ai-literacy-coach",
                                         "digital-skills-ai", "employee-onboarding-ai"],
                 inject_at_round=8),
    create_shock("security_breach", ["cybersecurity-ai", "ai-compliance-checker",
                                      "hipaa-compliance-ai", "fraud-detection-ai",
                                      "data-privacy-ai", "enterprise-search-ai"],
                 inject_at_round=10),
    create_shock("platform_ban", ["content", "faceless-youtube", "tiktok-shop",
                                   "ai-ghostwriter", "ai-music-producer",
                                   "social-media-manager"],
                 inject_at_round=12),
]


def main():
    t0 = time.time()

    # Enrich v3 domains with v4 fields
    for d in V3_DOMAINS:
        _enrich_v3_domain(d)

    n = len(ALL_DOMAINS)
    domain_ids_set = {d["domain_id"] for d in ALL_DOMAINS}
    assert len(domain_ids_set) == n, f"Duplicate domain_ids! {n} domains but {len(domain_ids_set)} unique"

    print("=" * 100)
    print("MIROFISH v4: 500-DOMAIN PREDICTION WITH MACRO CONTEXT & RETENTION")
    print(f"Domains: {n} total ({len(V3_DOMAINS)} v3 + {len(NEW_250_V4_DOMAINS)} v4)")
    print(f"Personas: {len(CUSTOMER_PERSONAS)} types x 50 each = {len(CUSTOMER_PERSONAS) * 50} agents")
    print(f"Funnel: 9-stage (unaware → advocating | churned)")
    print(f"Macro: March 2026 (displacement={MARCH_2026.ai_displacement_pressure:.1f}, "
          f"regulation={MARCH_2026.regulatory_pressure:.1f})")
    print(f"Shocks: {len(V4_SHOCKS)} scenario events")
    print("=" * 100)
    print()

    # =========================================================================
    # BUILD GRAPH
    # =========================================================================
    graph = DomainGraph()
    for d in ALL_DOMAINS:
        props = {"domain_tags": d.get("domain_tags", [])}
        if "retention_score" in d:
            props["retention_score"] = d["retention_score"]
        if "urgency_score" in d:
            props["urgency_score"] = d["urgency_score"]
        graph.add_node(d["domain_id"], "domain", d.get("label", d["domain_id"]), props)

    # Technology nodes
    tech_nodes = {"ai-tools", "blockchain", "web-platform", "social-media", "saas-infra",
                  "healthcare-tech", "govtech", "enterprise-infra", "fintech-platform",
                  "edtech-platform"}
    for t in tech_nodes:
        graph.add_node(t, "technology", t)

    # Auto-wire technology edges from evidence sources
    source_tech_map = {
        "github": "ai-tools",
        "x_twitter": "social-media",
        "producthunt": "saas-infra",
    }
    for d in ALL_DOMAINS:
        for src in d.get("evidence_sources", []):
            tech = source_tech_map.get(src)
            if tech:
                graph.add_edge(tech, d["domain_id"], "ENABLES", 0.4)

    # Build graph from opportunities (related_chips → edges)
    graph_from_opps = build_graph_from_opportunities(ALL_DOMAINS)
    for node_id, node_data in graph_from_opps.nodes.items():
        if node_id not in graph.nodes:
            graph.add_node(node_id, node_data["type"], node_data["label"],
                          node_data.get("properties", {}))
    for edge in graph_from_opps.edges:
        graph.add_edge(edge["source"], edge["target"], edge["relationship"],
                      edge.get("weight", 0.5))

    # Explicit relationships
    for r in ALL_RELATIONSHIPS:
        if r["source"] in graph.nodes and r["target"] in graph.nodes:
            graph.add_edge(r["source"], r["target"], r["relationship"],
                          r.get("weight", 0.5))

    print(f"Graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")

    # =========================================================================
    # SIGNALS
    # =========================================================================
    domain_ids = [d["domain_id"] for d in ALL_DOMAINS]
    opp_signals = signals_from_opportunities(ALL_DOMAINS)
    graph_signals = signals_from_graph(graph)
    all_signals = opp_signals + graph_signals
    print(f"Signals: {len(opp_signals)} opportunity + {len(graph_signals)} graph = "
          f"{len(all_signals)} total")

    # =========================================================================
    # PERSONAS
    # =========================================================================
    personas = generate_personas(graph, domain_ids=domain_ids, count_per_type=50, seed=42)
    print(f"Personas: {len(personas)} agents across "
          f"{len(set(p['persona_type'] for p in personas))} types")
    print()

    # =========================================================================
    # FLAGSHIP SIMULATION (full macro context)
    # =========================================================================
    agent_count = len(personas)
    evals = agent_count * n * 20
    print(f"--- Flagship Simulation ({agent_count} agents, {n} domains, 20 rounds) ---")
    print(f"    Macro: March 2026 context active")
    print(f"    Shocks: {len(V4_SHOCKS)} events injected")
    t1 = time.time()
    result = run_simulation(
        graph, domain_ids,
        personas=personas,
        signals=all_signals,
        shocks=V4_SHOCKS,
        max_rounds=20,
        seed=42,
        macro=MARCH_2026,
        macro_events=MARCH_2026_EVENTS,
    )
    t2 = time.time()
    print(f"    Simulation: {t2 - t1:.1f}s ({evals:,} persona-domain-round evaluations)")
    print()

    # =========================================================================
    # MONTE CARLO ENSEMBLE
    # =========================================================================
    ensemble_agents = len(CUSTOMER_PERSONAS) * 15  # 15 per type for ensemble speed
    print(f"--- Monte Carlo Ensemble (30 runs x {ensemble_agents} agents, bootstrap CIs) ---")
    t3 = time.time()
    ensemble = run_ensemble(
        graph, domain_ids,
        signals=all_signals,
        shocks=V4_SHOCKS,
        n_runs=30,
        count_per_type=15,
        max_rounds=20,
        base_seed=42,
        macro=MARCH_2026,
        macro_events=MARCH_2026_EVENTS,
        convergence_threshold=0.005,
        min_runs=15,
    )
    t4 = time.time()
    print(f"    Ensemble: {t4 - t3:.1f}s")
    converged = sum(1 for d in ensemble["domains"].values()
                    if d.get("converged_at_run"))
    print(f"    Converged: {converged}/{n} domains")
    print()

    total_time = time.time() - t0

    # =========================================================================
    # COLLECT RESULTS
    # =========================================================================
    domain_results = []
    for d in ALL_DOMAINS:
        d_id = d["domain_id"]
        sim_data = result["domains"].get(d_id, {})
        ens_data = ensemble["domains"].get(d_id, {})

        adoption = sim_data.get("final_adoption_rate", 0.0)
        advocacy = sim_data.get("final_advocacy_rate", 0.0)
        trial_rate = sim_data.get("final_trial_rate", 0.0)
        retention_rate = sim_data.get("final_retention_rate", 0.0)
        churn_rate = sim_data.get("final_churn_rate", 0.0)
        committed_rate = sim_data.get("final_committed_rate", 0.0)
        by_type = sim_data.get("adoption_by_persona_type", {})

        ens_mean = ens_data.get("mean_adoption", 0.0)
        ci_lo = ens_data.get("bootstrap_ci_lower", ens_data.get("p10_adoption", 0.0))
        ci_hi = ens_data.get("bootstrap_ci_upper", ens_data.get("p90_adoption", 0.0))
        cv = ens_data.get("cv", 0.0)
        mean_churn = ens_data.get("mean_churn", 0.0)

        domain_results.append({
            "domain_id": d_id,
            "label": d.get("label", d_id),
            "category": d.get("status", "candidate"),
            "static_score": d.get("composite_score", 0.0),
            "retention_score": d.get("retention_score", 0.5),
            "urgency_score": d.get("urgency_score", 0.5),
            # Flagship simulation
            "adoption": adoption,
            "advocacy": advocacy,
            "trial_rate": trial_rate,
            "retention_rate": retention_rate,
            "churn_rate": churn_rate,
            "committed_rate": committed_rate,
            # Ensemble
            "ens_mean": ens_mean,
            "ci_lower": ci_lo,
            "ci_upper": ci_hi,
            "cv": cv,
            "ens_churn": mean_churn,
            "by_type": by_type,
        })

    domain_results.sort(key=lambda x: x["ens_mean"], reverse=True)

    # =========================================================================
    # PRINT TOP 30
    # =========================================================================
    print("=" * 120)
    print("TOP 30 DOMAINS (sorted by ensemble mean adoption)")
    print("=" * 120)
    print(f"{'#':>3}  {'Domain':<35} {'Ens Mean':>9} {'95% CI':>14} "
          f"{'Trial':>7} {'Adopt':>7} {'Commit':>7} {'Churn':>7} {'Advocacy':>9}")
    print("-" * 120)
    for i, dr in enumerate(domain_results[:30], 1):
        print(f"{i:>3}  {dr['domain_id']:<35} {dr['ens_mean']:>8.1%} "
              f"[{dr['ci_lower']:>5.1%}-{dr['ci_upper']:<5.1%}] "
              f"{dr['trial_rate']:>6.1%} {dr['adoption']:>6.1%} "
              f"{dr['committed_rate']:>6.1%} {dr['churn_rate']:>6.1%} "
              f"{dr['advocacy']:>8.1%}")

    # =========================================================================
    # V4 CATEGORY ANALYSIS
    # =========================================================================
    print()
    print("=" * 100)
    print("V4 CATEGORY PERFORMANCE")
    print("=" * 100)

    # Categorize by source
    v3_results = [r for r in domain_results if r["domain_id"] in {d["domain_id"] for d in V3_DOMAINS}]
    v4_results = [r for r in domain_results if r["domain_id"] in {d["domain_id"] for d in NEW_250_V4_DOMAINS}]

    v3_mean = sum(r["ens_mean"] for r in v3_results) / max(len(v3_results), 1)
    v4_mean = sum(r["ens_mean"] for r in v4_results) / max(len(v4_results), 1)
    print(f"  V3 domains ({len(v3_results)}): avg ensemble adoption = {v3_mean:.1%}")
    print(f"  V4 domains ({len(v4_results)}): avg ensemble adoption = {v4_mean:.1%}")

    # Top v4 domains that outperform v3 median
    v3_median = sorted(r["ens_mean"] for r in v3_results)[len(v3_results) // 2] if v3_results else 0
    v4_above_v3_median = [r for r in v4_results if r["ens_mean"] > v3_median]
    print(f"  V4 domains above v3 median ({v3_median:.1%}): {len(v4_above_v3_median)}")

    # =========================================================================
    # RETENTION ANALYSIS
    # =========================================================================
    print()
    print("=" * 100)
    print("RETENTION & CHURN ANALYSIS (Top 20 by retention rate)")
    print("=" * 100)
    by_retention = sorted(domain_results, key=lambda x: x["retention_rate"], reverse=True)
    print(f"{'#':>3}  {'Domain':<35} {'Retention':>10} {'Churn':>7} {'Trial→Adopt':>12} {'Ret Score':>10}")
    print("-" * 90)
    for i, dr in enumerate(by_retention[:20], 1):
        trial_to_adopt = dr["adoption"] / max(dr["trial_rate"], 0.001)
        print(f"{i:>3}  {dr['domain_id']:<35} {dr['retention_rate']:>9.1%} "
              f"{dr['churn_rate']:>6.1%} {trial_to_adopt:>11.0%} "
              f"{dr['retention_score']:>9.2f}")

    # Highest churn
    print()
    print("HIGHEST CHURN (Top 10)")
    by_churn = sorted(domain_results, key=lambda x: x["churn_rate"], reverse=True)
    print(f"{'#':>3}  {'Domain':<35} {'Churn':>7} {'Retention':>10} {'Ret Score':>10}")
    print("-" * 75)
    for i, dr in enumerate(by_churn[:10], 1):
        print(f"{i:>3}  {dr['domain_id']:<35} {dr['churn_rate']:>6.1%} "
              f"{dr['retention_rate']:>9.1%} {dr['retention_score']:>9.2f}")

    # =========================================================================
    # PER-PERSONA TOP 10 RECOMMENDATIONS
    # =========================================================================
    print()
    print("=" * 100)
    print("EACH AI PERSONA'S TOP 10 DOMAIN RECOMMENDATIONS (v4: 15 types)")
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
        print(f"{'#':>3}  {'Domain':<35} {'Adoption':>9} {'Trial':>7} {'Churn':>7}")
        print("-" * 70)
        for i, dr in enumerate(top10, 1):
            rate = dr["by_type"].get(ptype, {}).get("adoption_rate", 0)
            trial = dr["by_type"].get(ptype, {}).get("trial_rate", 0)
            churn = dr["by_type"].get(ptype, {}).get("churn_rate", 0)
            print(f"{i:>3}  {dr['domain_id']:<35} {rate:>8.0%} {trial:>6.0%} {churn:>6.0%}")

    # =========================================================================
    # CROSS-PERSONA CONSENSUS
    # =========================================================================
    print()
    print("=" * 100)
    print("CROSS-PERSONA CONSENSUS (domains in multiple persona top-10s)")
    print("=" * 100)

    domain_appearances = {}
    for ptype, top10 in persona_top10.items():
        for dr in top10:
            d_id = dr["domain_id"]
            domain_appearances.setdefault(d_id, []).append(ptype)

    consensus = sorted(domain_appearances.items(), key=lambda x: len(x[1]), reverse=True)
    print(f"\n{'Domain':<35} {'# Personas':>10} {'Who Recommends'}")
    print("-" * 100)
    for d_id, personas_list in consensus[:25]:
        if len(personas_list) >= 2:
            print(f"{d_id:<35} {len(personas_list):>10}    {', '.join(personas_list)}")

    # =========================================================================
    # MACRO CONTEXT IMPACT ANALYSIS
    # =========================================================================
    print()
    print("=" * 100)
    print("MACRO CONTEXT IMPACT: DOMAINS BOOSTED BY 2026 CONDITIONS")
    print("=" * 100)

    # Domains with career/reskill/easy_start tags should be boosted
    macro_boosted_tags = {"career", "reskill", "easy_start", "compliance", "risk_management"}
    macro_penalized_tags = {"alpha", "defi", "edge", "first_mover", "meme", "airdrop"}

    boosted = [(r, set(d.get("domain_tags", [])) & macro_boosted_tags)
               for r in domain_results
               for d in ALL_DOMAINS if d["domain_id"] == r["domain_id"]]
    boosted = [(r, tags) for r, tags in boosted if tags]
    boosted.sort(key=lambda x: x[0]["ens_mean"], reverse=True)

    print("\nBoosted by macro context (career/reskill/compliance):")
    print(f"{'#':>3}  {'Domain':<35} {'Ens Mean':>9} {'Tags'}")
    print("-" * 80)
    for i, (dr, tags) in enumerate(boosted[:15], 1):
        print(f"{i:>3}  {dr['domain_id']:<35} {dr['ens_mean']:>8.1%}   {', '.join(tags)}")

    penalized = [(r, set(d.get("domain_tags", [])) & macro_penalized_tags)
                 for r in domain_results
                 for d in ALL_DOMAINS if d["domain_id"] == r["domain_id"]]
    penalized = [(r, tags) for r, tags in penalized if tags]
    penalized.sort(key=lambda x: x[0]["ens_mean"])

    print(f"\nPenalized by macro context (speculative/defi):")
    print(f"{'#':>3}  {'Domain':<35} {'Ens Mean':>9} {'Tags'}")
    print("-" * 80)
    for i, (dr, tags) in enumerate(penalized[:10], 1):
        print(f"{i:>3}  {dr['domain_id']:<35} {dr['ens_mean']:>8.1%}   {', '.join(tags)}")

    # =========================================================================
    # EXPORT JSON
    # =========================================================================
    export = {
        "run_metadata": {
            "version": "v4",
            "engine": "MiroFish v4 Multi-Agent Trend Prediction",
            "total_domains": n,
            "v3_domains": len(V3_DOMAINS),
            "v4_domains": len(NEW_250_V4_DOMAINS),
            "total_personas": len(personas),
            "persona_types": len(CUSTOMER_PERSONAS),
            "funnel_stages": 9,
            "ensemble_runs": 30,
            "macro_context": "march_2026",
            "shocks": len(V4_SHOCKS),
            "total_time_seconds": round(total_time, 1),
        },
        "rankings": [
            {
                "rank": i + 1,
                "domain_id": dr["domain_id"],
                "label": dr["label"],
                "category": dr["category"],
                "static_score": dr["static_score"],
                "retention_score": dr["retention_score"],
                "urgency_score": dr["urgency_score"],
                "ensemble_mean": round(dr["ens_mean"], 4),
                "ci_lower": round(dr["ci_lower"], 4),
                "ci_upper": round(dr["ci_upper"], 4),
                "cv": round(dr["cv"], 4),
                "flagship_adoption": round(dr["adoption"], 4),
                "trial_rate": round(dr["trial_rate"], 4),
                "retention_rate": round(dr["retention_rate"], 4),
                "churn_rate": round(dr["churn_rate"], 4),
                "committed_rate": round(dr["committed_rate"], 4),
                "advocacy": round(dr["advocacy"], 4),
                "per_persona": {
                    ptype: {
                        k: round(v, 4) for k, v in stats.items()
                    }
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
                    "trial_rate": round(dr["by_type"].get(ptype, {}).get("trial_rate", 0), 4),
                    "churn_rate": round(dr["by_type"].get(ptype, {}).get("churn_rate", 0), 4),
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

    output_path = os.path.join(script_dir, "..", "viz", "500_domain_predictions_v4.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(export, f, indent=2)
    print(f"\nExported to {output_path}")

    # =========================================================================
    # MARKDOWN REPORT
    # =========================================================================
    md = []
    md.append("# MiroFish v4: 500-Domain Chip Research")
    md.append("")
    md.append(f"**Generated**: March 2026")
    md.append(f"**Engine**: MiroFish v4 Multi-Agent Trend Prediction")
    md.append(f"**Agents**: {len(personas):,} ({len(CUSTOMER_PERSONAS)} persona types x 50 each)")
    md.append(f"**Domains**: {n} ({len(V3_DOMAINS)} v3 + {len(NEW_250_V4_DOMAINS)} v4)")
    md.append(f"**Funnel**: 9-stage (trial + committed + churned)")
    md.append(f"**Macro Context**: March 2026 (displacement={MARCH_2026.ai_displacement_pressure:.1f})")
    md.append(f"**Ensemble**: 30 Monte Carlo runs with bootstrap 95% CIs")
    md.append(f"**Simulation Time**: {total_time:.0f}s")
    md.append(f"**Evaluations**: {evals:,} persona-domain-round")
    md.append("")
    md.append("---")
    md.append("")

    # Top 30
    md.append("## Top 30 Domain Chips")
    md.append("")
    md.append("| Rank | Domain | Label | Ens Mean | 95% CI | Trial | Adopt | Commit | Churn | Advocacy |")
    md.append("|------|--------|-------|----------|--------|-------|-------|--------|-------|----------|")
    for i, dr in enumerate(domain_results[:30], 1):
        md.append(
            f"| {i} | `{dr['domain_id']}` | {dr['label']} | "
            f"**{dr['ens_mean']:.1%}** | {dr['ci_lower']:.1%}-{dr['ci_upper']:.1%} | "
            f"{dr['trial_rate']:.1%} | {dr['adoption']:.1%} | "
            f"{dr['committed_rate']:.1%} | {dr['churn_rate']:.1%} | {dr['advocacy']:.1%} |"
        )
    md.append("")

    # Per persona top 10
    md.append("## Each AI Persona's Top 10 Recommendations")
    md.append("")
    for ptype in CUSTOMER_PERSONAS:
        display = CUSTOMER_PERSONAS[ptype]["label"]
        desc = CUSTOMER_PERSONAS[ptype]["description"]
        md.append(f"### {display}")
        md.append(f"*{desc}*")
        md.append("")
        md.append("| # | Domain | Adoption | Trial | Churn |")
        md.append("|---|--------|----------|-------|-------|")
        for i, dr in enumerate(persona_top10[ptype], 1):
            rate = dr["by_type"].get(ptype, {}).get("adoption_rate", 0)
            trial = dr["by_type"].get(ptype, {}).get("trial_rate", 0)
            churn = dr["by_type"].get(ptype, {}).get("churn_rate", 0)
            md.append(f"| {i} | `{dr['domain_id']}` ({dr['label']}) | "
                      f"**{rate:.0%}** | {trial:.0%} | {churn:.0%} |")
        md.append("")

    # Consensus
    md.append("## Cross-Persona Consensus")
    md.append("")
    md.append("Domains that appear in multiple personas' top-10 lists:")
    md.append("")
    md.append("| Domain | # Personas | Who Recommends |")
    md.append("|--------|-----------|----------------|")
    for d_id, p_list in consensus[:25]:
        if len(p_list) >= 2:
            md.append(f"| `{d_id}` | **{len(p_list)}** | {', '.join(p_list)} |")
    md.append("")

    # Retention analysis
    md.append("## Retention & Churn Analysis")
    md.append("")
    md.append("### Top 15 by Retention Rate")
    md.append("| # | Domain | Retention | Churn | Ret Score |")
    md.append("|---|--------|-----------|-------|-----------|")
    for i, dr in enumerate(by_retention[:15], 1):
        md.append(f"| {i} | `{dr['domain_id']}` | **{dr['retention_rate']:.1%}** | "
                  f"{dr['churn_rate']:.1%} | {dr['retention_score']:.2f} |")
    md.append("")

    md.append("### Highest Churn")
    md.append("| # | Domain | Churn | Retention | Ret Score |")
    md.append("|---|--------|-------|-----------|-----------|")
    for i, dr in enumerate(by_churn[:10], 1):
        md.append(f"| {i} | `{dr['domain_id']}` | **{dr['churn_rate']:.1%}** | "
                  f"{dr['retention_rate']:.1%} | {dr['retention_score']:.2f} |")
    md.append("")

    # Full rankings
    md.append("## Full Rankings (All Domains)")
    md.append("")
    md.append("| Rank | Domain | Label | Ens Mean | Trial | Adopt | Churn |")
    md.append("|------|--------|-------|----------|-------|-------|-------|")
    for i, dr in enumerate(domain_results, 1):
        md.append(
            f"| {i} | `{dr['domain_id']}` | {dr['label']} | "
            f"{dr['ens_mean']:.1%} | {dr['trial_rate']:.1%} | "
            f"{dr['adoption']:.1%} | {dr['churn_rate']:.1%} |"
        )
    md.append("")
    md.append("---")
    md.append(f"*Generated by MiroFish v4 | {len(personas)} agents | {n} domains | {total_time:.0f}s*")

    md_path = os.path.join(script_dir, "..", "docs", "MIROFISH_500_RESEARCH.md")
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"Markdown report: {md_path}")

    print()
    print("=" * 100)
    print("DONE")
    print(f"{n} domains evaluated by {len(personas)} agents in {total_time:.0f}s")
    print(f"v4 engine: 9-stage funnel, macro context, network effects, bootstrap CIs")
    print("=" * 100)


if __name__ == "__main__":
    main()
