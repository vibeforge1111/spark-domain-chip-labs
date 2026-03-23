"""Export 500-domain MiroFish v4 simulation data for the interactive graph visualization.

Produces mirofish_500_data.json in the format mirofish-500-graph.html expects.
Uses 750 agents (50 per 15 persona types) with macro context, network effects,
9-stage funnel, and staggered signal injection for dynamic curves.
"""

import json
import os
import sys
import time

sys.stdout.reconfigure(line_buffering=True)

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, "..", "src"))
sys.path.insert(0, script_dir)

from chip_labs.mirofish.graph import DomainGraph, build_graph_from_opportunities
from chip_labs.mirofish.personas import generate_personas, CUSTOMER_PERSONAS
from chip_labs.mirofish.simulation import run_simulation
from chip_labs.mirofish.signals import (
    signals_from_opportunities, signals_from_graph, create_shock,
)
from chip_labs.mirofish.macro import MARCH_2026, MARCH_2026_EVENTS

from predict_100_domains import (
    EXISTING_CHIPS, NEW_CANDIDATES, VIRAL_DOMAINS, NEW_48_DOMAINS,
    RELATIONSHIPS,
)
from predict_250_domains import NEW_150_DOMAINS, NEW_RELATIONSHIPS
from domains_v4 import NEW_250_V4_DOMAINS, NEW_V4_RELATIONSHIPS

FIRST_100 = EXISTING_CHIPS + NEW_CANDIDATES + VIRAL_DOMAINS + NEW_48_DOMAINS
V3_DOMAINS = FIRST_100 + NEW_150_DOMAINS
ALL_DOMAINS = V3_DOMAINS + NEW_250_V4_DOMAINS
ALL_RELS = RELATIONSHIPS + NEW_RELATIONSHIPS + NEW_V4_RELATIONSHIPS

# V4 domain ID sets for category coloring
V4_IDS = {d["domain_id"] for d in NEW_250_V4_DOMAINS}
EXISTING_IDS = {d["domain_id"] for d in EXISTING_CHIPS}
VIRAL_IDS = {d["domain_id"] for d in VIRAL_DOMAINS}
NEW48_IDS = {d["domain_id"] for d in NEW_48_DOMAINS}
NEW150_IDS = {d["domain_id"] for d in NEW_150_DOMAINS}


def enrich_v3_domain(d):
    """Add v4 fields to v3 domains that lack them."""
    if "retention_score" not in d:
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
        else:
            d["urgency_score"] = 0.5
    return d


def build_graph(domains, relationships):
    graph = DomainGraph()
    for d in domains:
        props = {"domain_tags": d.get("domain_tags", [])}
        if "retention_score" in d:
            props["retention_score"] = d["retention_score"]
        if "urgency_score" in d:
            props["urgency_score"] = d["urgency_score"]
        graph.add_node(d["domain_id"], "domain", d.get("label", d["domain_id"]), props)

    tech_nodes = {"ai-tools", "blockchain", "web-platform", "social-media", "saas-infra",
                  "healthcare-tech", "govtech", "enterprise-infra"}
    for t in tech_nodes:
        graph.add_node(t, "technology", t)

    source_tech = {"github": "ai-tools", "x_twitter": "social-media", "producthunt": "saas-infra"}
    for d in domains:
        for src in d.get("evidence_sources", []):
            tech = source_tech.get(src)
            if tech:
                graph.add_edge(tech, d["domain_id"], "ENABLES", 0.4)

    # Skip build_graph_from_opportunities for 500+ domains - it generates O(n^2)
    # competition edges. Use explicit relationships only + related_chips edges.
    for d in domains:
        for related in d.get("related_chips", []):
            chip_id = f"chip-{related}"
            if chip_id not in graph.nodes:
                graph.add_node(chip_id, "technology", related)
            graph.add_edge(d["domain_id"], chip_id, "EXTENDS", weight=0.7)

    for r in relationships:
        if r["source"] in graph.nodes and r["target"] in graph.nodes:
            graph.add_edge(r["source"], r["target"], r["relationship"],
                           r.get("weight", 0.5))
    return graph


def main():
    t0 = time.time()

    # Enrich v3 domains
    for d in V3_DOMAINS:
        enrich_v3_domain(d)

    print(f"Building graph for {len(ALL_DOMAINS)} domains...", flush=True)
    graph = build_graph(ALL_DOMAINS, ALL_RELS)
    domain_ids = [d["domain_id"] for d in ALL_DOMAINS]
    print(f"Graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges", flush=True)

    # Generate signals with staggered injection
    opp_signals = signals_from_opportunities(ALL_DOMAINS)
    graph_signals = signals_from_graph(graph)

    # Filter to only strong signals to keep runtime manageable
    # (515 domains generates 200K+ signals otherwise)
    opp_signals = [s for s in opp_signals if s.get("strength", 0) >= 0.4]
    graph_signals = [s for s in graph_signals if s.get("strength", 0) >= 0.3]

    domain_scores = {d["domain_id"]: d.get("composite_score", 0.5) for d in ALL_DOMAINS}
    for sig in opp_signals:
        domains_affected = sig.get("affects_domains", [])
        if domains_affected:
            avg_score = sum(domain_scores.get(d, 0.5) for d in domains_affected) / len(domains_affected)
            sig["inject_at_round"] = min(int((1.0 - avg_score) * 14), 12)
    for sig in graph_signals:
        domains_affected = sig.get("affects_domains", [])
        if domains_affected:
            avg_score = sum(domain_scores.get(d, 0.5) for d in domains_affected) / len(domains_affected)
            sig["inject_at_round"] = min(int((1.0 - avg_score) * 14) + 2, 14)

    all_signals = opp_signals + graph_signals
    print(f"Signals: {len(all_signals)} total (filtered from raw)", flush=True)

    # V4 shocks
    shocks = [
        create_shock("breakout_tool", ["ai-agent-builder", "prompt-engineer", "cursor-copilot", "mcp-server-builder"], inject_at_round=3),
        create_shock("mass_layoff", ["resume-ai", "career-pivot-ai", "upskill-path-ai", "ai-proof-career", "coding-bootcamp-ai"], inject_at_round=4),
        create_shock("open_source_release", ["ai-agent-builder", "cursor-copilot", "fine-tuning-lab", "rag-pipeline"], inject_at_round=5),
        create_shock("viral_adoption", ["tiktok-creator", "faceless-youtube", "ai-personal-assistant"], inject_at_round=6),
        create_shock("ecosystem_integration", ["mcp-server-builder", "ai-agent-builder", "supabase-fullstack"], inject_at_round=7),
        create_shock("government_subsidy", ["coding-bootcamp-ai", "upskill-path-ai", "corporate-training-ai"], inject_at_round=8),
        create_shock("market_crash", ["trading-crypto", "defi-architect", "solana-dev"], inject_at_round=9),
        create_shock("security_breach", ["cybersecurity-ai", "ai-compliance-checker", "fraud-detection-ai"], inject_at_round=10),
        create_shock("platform_ban", ["content", "faceless-youtube", "ai-ghostwriter"], inject_at_round=12),
    ]

    # 450 agents (30 per 15 types) for viz export speed
    count_per_type = 30
    print(f"Generating {count_per_type * len(CUSTOMER_PERSONAS)} personas...", flush=True)
    personas = generate_personas(graph, domain_ids, count_per_type=count_per_type, seed=42)

    # v4 simulation with macro context
    print("Running v4 simulation with macro context...", flush=True)
    result = run_simulation(
        graph, domain_ids, personas=list(personas),
        signals=all_signals, shocks=shocks,
        max_rounds=20, seed=42, context="builder_community",
        macro=MARCH_2026, macro_events=MARCH_2026_EVENTS,
    )
    t1 = time.time()
    print(f"  Simulation: {t1 - t0:.1f}s", flush=True)

    # --- Export graph nodes ---
    graph_nodes = [{"id": nid, "label": n.get("label", nid), "type": n.get("type", "unknown")}
                   for nid, n in graph.nodes.items()]

    # --- Export graph edges (domain-domain only to limit size) ---
    domain_id_set = set(domain_ids)
    graph_edges = [{"source": e["source"], "target": e["target"],
                    "relationship": e["relationship"], "weight": e.get("weight", 0.5)}
                   for e in graph.edges
                   if e["source"] in domain_id_set or e["target"] in domain_id_set]

    # --- Export domain results ---
    domains_data = []
    for d in ALL_DOMAINS:
        d_id = d["domain_id"]
        b = result["domains"].get(d_id, {})

        builder_curve = [
            {"round": s["round"], "adoption_rate": s["adoption_rate"],
             "advocacy_rate": s["advocacy_rate"],
             "interest_rate": s.get("interest_rate", 0),
             "stage_distribution": s.get("stage_distribution", {})}
            for s in b.get("adoption_curve", [])
        ]

        # Determine category for viz coloring
        if d_id in EXISTING_IDS:
            category = "existing"
        elif d_id in VIRAL_IDS:
            category = "viral"
        elif d_id in V4_IDS:
            # Sub-categorize v4 domains by tags
            tags = set(d.get("domain_tags", []))
            if tags & {"career", "reskill", "easy_start"}:
                category = "v4_survival"
            elif tags & {"compliance", "hipaa"}:
                category = "v4_health"
            elif tags & {"workflow", "productivity"}:
                category = "v4_enterprise"
            else:
                category = "v4_other"
        else:
            category = "candidate"

        domains_data.append({
            "domain_id": d_id,
            "label": d.get("label", d_id),
            "description": d.get("description", ""),
            "is_existing": d_id in EXISTING_IDS,
            "is_viral": d_id in VIRAL_IDS,
            "is_v4": d_id in V4_IDS,
            "category": category,
            "status": d.get("status", "candidate"),
            "composite_score": d.get("composite_score", 0),
            "retention_score": d.get("retention_score", 0.5),
            "urgency_score": d.get("urgency_score", 0.5),
            "scores": d.get("scores", {}),
            "related_chips": d.get("related_chips", []),
            "evidence_sources": d.get("evidence_sources", []),
            "domain_tags": d.get("domain_tags", []),
            "builder_adoption": b.get("final_adoption_rate", 0),
            "trial_rate": b.get("final_trial_rate", 0),
            "retention_rate": b.get("final_retention_rate", 0),
            "churn_rate": b.get("final_churn_rate", 0),
            "committed_rate": b.get("final_committed_rate", 0),
            "advocacy_rate": b.get("final_advocacy_rate", 0),
            "tipping_point": b.get("tipping_point_round"),
            "consensus": b.get("final_consensus", 0),
            "disagreement": b.get("disagreement_score", 0),
            "builder_curve": builder_curve,
            "adoption_by_persona_type": b.get("adoption_by_persona_type", {}),
        })

    # --- Export persona types ---
    persona_types = []
    for ptype, traits in CUSTOMER_PERSONAS.items():
        count = sum(1 for p in personas if p["persona_type"] == ptype)
        persona_types.append({
            "type": ptype, "label": traits["label"], "count": count,
            "influence_score": traits["influence_score"],
            "adoption_threshold": traits["adoption_threshold"],
            "risk_tolerance": traits["risk_tolerance"],
            "network_reach": traits["network_reach"],
        })

    # --- Signal summary ---
    signal_summary = {
        "opportunity_signals": len(opp_signals),
        "graph_signals": len(graph_signals),
        "total_signals": len(all_signals),
        "signal_types": {},
    }
    for s in all_signals:
        st = s.get("signal_type", "unknown")
        signal_summary["signal_types"][st] = signal_summary["signal_types"].get(st, 0) + 1

    # --- Shocks data ---
    shocks_data = [
        {"shock_id": s.get("shock_id", ""), "label": s.get("label", ""),
         "template": s.get("template", ""), "inject_at_round": s.get("inject_at_round", 0),
         "strength": s.get("strength", 0), "effect": s.get("effect", "neutral"),
         "affects_domains": s.get("affects_domains", []),
         "affected_persona_types": s.get("affected_persona_types", [])}
        for s in shocks
    ]

    # --- Macro timeline ---
    macro_timeline = result.get("macro_timeline", [])

    # --- Macro events for feed ---
    macro_events_data = [
        {"label": e.get("label", ""), "inject_at_round": e.get("inject_at_round", 0),
         "description": e.get("description", "")}
        for e in (MARCH_2026_EVENTS or [])
    ]

    # --- Assemble export ---
    export = {
        "meta": {
            "title": f"MiroFish v4: {len(ALL_DOMAINS)}-Domain Trend Prediction",
            "version": "v4",
            "agent_count": len(personas),
            "domain_count": len(domain_ids),
            "v3_domains": len(V3_DOMAINS),
            "v4_domains": len(NEW_250_V4_DOMAINS),
            "total_signals": len(all_signals),
            "graph_nodes": len(graph_nodes),
            "graph_edges": len(graph_edges),
            "rounds": 20,
            "persona_types": len(CUSTOMER_PERSONAS),
            "funnel_stages": 9,
            "macro_context": "march_2026",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "graph_nodes": graph_nodes,
        "graph_edges": graph_edges,
        "domains": domains_data,
        "persona_types": persona_types,
        "signal_summary": signal_summary,
        "shocks": shocks_data,
        "macro_timeline": macro_timeline,
        "macro_events": macro_events_data,
    }

    output_path = os.path.join(script_dir, "..", "viz", "mirofish_500_data.json")
    with open(output_path, "w") as f:
        json.dump(export, f, indent=2)
    size = os.path.getsize(output_path)
    print(f"\nExported to {output_path} ({size:,} bytes)", flush=True)
    print(f"  {len(graph_nodes)} graph nodes, {len(graph_edges)} graph edges", flush=True)
    print(f"  {len(domains_data)} domains with adoption curves", flush=True)
    print(f"  {len(persona_types)} persona types", flush=True)
    print(f"  {len(macro_timeline)} macro timeline entries", flush=True)
    print(f"Total time: {time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
