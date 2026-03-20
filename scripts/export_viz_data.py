"""Export MiroFish simulation data as JSON for the knowledge graph visualization.

Uses all 100 domains from predict_100_domains.py.
Runs lightweight simulations (550 agents) to generate adoption curves
for the interactive graph visualization.
"""

import json
import os
import sys
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, "..", "src"))

from chip_labs.mirofish.graph import DomainGraph, build_graph_from_opportunities
from chip_labs.mirofish.personas import generate_personas, PERSONA_TYPES
from chip_labs.mirofish.simulation import run_simulation
from chip_labs.mirofish.signals import (
    signals_from_opportunities, signals_from_graph,
    create_shock,
)

# Import all 100 domains and relationships
from predict_100_domains import (
    ALL_100_DOMAINS, EXISTING_CHIPS, NEW_CANDIDATES,
    VIRAL_DOMAINS, NEW_48_DOMAINS, RELATIONSHIPS,
)


def build_graph(domains, relationships):
    """Build the domain graph (same logic as predict_100_domains.py)."""
    graph = DomainGraph()
    for d in domains:
        graph.add_node(d["domain_id"], "domain", d.get("label", d["domain_id"]),
                       {"domain_tags": d.get("domain_tags", [])})

    tech_nodes = {"ai-tools", "blockchain", "web-platform", "social-media", "saas-infra"}
    for t in tech_nodes:
        graph.add_node(t, "technology", t)
    for d in domains:
        for src in d.get("evidence_sources", []):
            if src == "github":
                graph.add_edge("ai-tools", d["domain_id"], "ENABLES", 0.5)
            elif src == "x_twitter":
                graph.add_edge("social-media", d["domain_id"], "ENABLES", 0.4)

    graph_from_opps = build_graph_from_opportunities(domains)
    for node_id, node_data in graph_from_opps.nodes.items():
        if node_id not in graph.nodes:
            graph.add_node(node_id, node_data["type"], node_data["label"],
                           node_data.get("properties", {}))
    for edge in graph_from_opps.edges:
        graph.add_edge(edge["source"], edge["target"], edge["relationship"],
                       edge.get("weight", 0.5))

    for r in relationships:
        if r["source"] in graph.nodes and r["target"] in graph.nodes:
            graph.add_edge(r["source"], r["target"], r["relationship"],
                           r.get("weight", 0.5))

    return graph


def main():
    t0 = time.time()
    print(f"Building graph for {len(ALL_100_DOMAINS)} domains...")

    graph = build_graph(ALL_100_DOMAINS, RELATIONSHIPS)
    domain_ids = [d["domain_id"] for d in ALL_100_DOMAINS]

    # Generate signals with staggered injection for dynamic adoption curves.
    # Without staggering, all signals start at round 0 and personas blast
    # through all stages by round 3, creating flat curves.
    opp_signals = signals_from_opportunities(ALL_100_DOMAINS)
    graph_signals = signals_from_graph(graph)

    # Stagger opportunity signals: stronger domains get signals earlier,
    # weaker domains "emerge" in later rounds. This creates realistic
    # adoption dynamics where the viz shows gradual growth.
    domain_scores = {d["domain_id"]: d.get("composite_score", 0.5) for d in ALL_100_DOMAINS}
    for sig in opp_signals:
        domains_affected = sig.get("affects_domains", [])
        if domains_affected:
            avg_score = sum(domain_scores.get(d, 0.5) for d in domains_affected) / len(domains_affected)
            # Top domains (score > 0.8) get signals at rounds 0-2
            # Mid domains (0.6-0.8) get signals at rounds 3-6
            # Low domains (< 0.6) get signals at rounds 7-12
            inject_round = int((1.0 - avg_score) * 14)
            sig["inject_at_round"] = min(inject_round, 12)

    # Stagger graph signals similarly but with a slight delay
    for sig in graph_signals:
        domains_affected = sig.get("affects_domains", [])
        if domains_affected:
            avg_score = sum(domain_scores.get(d, 0.5) for d in domains_affected) / len(domains_affected)
            inject_round = int((1.0 - avg_score) * 14) + 2
            sig["inject_at_round"] = min(inject_round, 14)

    all_signals = opp_signals + graph_signals

    # Shocks
    shocks = [
        create_shock("breakout_tool", ["ai-agent-builder", "prompt-engineer", "cursor-copilot"], inject_at_round=3),
        create_shock("viral_adoption", ["solana-dev", "defi-architect", "meme-coin-launcher"], inject_at_round=5),
        create_shock("market_crash", ["trading-crypto", "defi-architect", "solana-dev", "options-trader", "quant-strategy"], inject_at_round=8),
        create_shock("ecosystem_integration", ["mcp-server-builder", "ai-agent-builder", "supabase-fullstack"], inject_at_round=4),
        create_shock("regulatory_ban", ["health-wellness", "compliance-shield", "crypto-airdrop"], inject_at_round=10),
        create_shock("viral_adoption", ["tiktok-creator", "meme-coin-launcher", "telegram-miniapp"], inject_at_round=6),
        create_shock("breakout_tool", ["no-code-saas", "ai-workflow-automation"], inject_at_round=7),
    ]

    # Use 50 per type = 550 agents for fast viz export (vs 125 = 1375 for full run)
    count_per_type = 50
    print(f"Generating personas ({count_per_type} per type = {count_per_type * 11} agents)...")
    personas = generate_personas(graph, domain_ids, count_per_type=count_per_type, seed=42)

    # Run builder simulation
    print("Running builder simulation...")
    builder_result = run_simulation(
        graph, domain_ids, personas=list(personas),
        signals=all_signals, shocks=shocks,
        max_rounds=20, seed=42, context="builder_community",
    )
    t1 = time.time()
    print(f"  Builder sim: {t1 - t0:.1f}s")

    # Run enterprise simulation with fresh personas
    print("Running enterprise simulation...")
    enterprise_personas = generate_personas(graph, domain_ids, count_per_type=count_per_type, seed=99)
    enterprise_result = run_simulation(
        graph, domain_ids, personas=enterprise_personas,
        signals=all_signals, shocks=shocks,
        max_rounds=20, seed=99, context="enterprise_market",
    )
    t2 = time.time()
    print(f"  Enterprise sim: {t2 - t1:.1f}s")

    # --- Export graph nodes ---
    graph_nodes = []
    for node_id, node in graph.nodes.items():
        graph_nodes.append({
            "id": node_id,
            "label": node.get("label", node_id),
            "type": node.get("type", "unknown"),
        })

    # --- Export graph edges ---
    graph_edges = []
    for edge in graph.edges:
        graph_edges.append({
            "source": edge["source"],
            "target": edge["target"],
            "relationship": edge["relationship"],
            "weight": edge.get("weight", 0.5),
        })

    # --- Export domain results ---
    existing_ids = {d["domain_id"] for d in EXISTING_CHIPS}
    viral_ids = {d["domain_id"] for d in VIRAL_DOMAINS}
    new_ids = {d["domain_id"] for d in NEW_48_DOMAINS}
    domains_data = []
    for d in ALL_100_DOMAINS:
        d_id = d["domain_id"]
        b = builder_result["domains"].get(d_id, {})
        e = enterprise_result["domains"].get(d_id, {})

        builder_curve = []
        for snapshot in b.get("adoption_curve", []):
            builder_curve.append({
                "round": snapshot["round"],
                "adoption_rate": snapshot["adoption_rate"],
                "advocacy_rate": snapshot["advocacy_rate"],
                "interest_rate": snapshot["interest_rate"],
                "stage_distribution": snapshot["stage_distribution"],
            })

        enterprise_curve = []
        for snapshot in e.get("adoption_curve", []):
            enterprise_curve.append({
                "round": snapshot["round"],
                "adoption_rate": snapshot["adoption_rate"],
                "advocacy_rate": snapshot["advocacy_rate"],
                "interest_rate": snapshot["interest_rate"],
            })

        category = "existing" if d_id in existing_ids else \
                   "viral" if d_id in viral_ids else \
                   "new" if d_id in new_ids else "candidate"

        domains_data.append({
            "domain_id": d_id,
            "label": d.get("label", d_id),
            "description": d.get("description", ""),
            "is_existing": d_id in existing_ids,
            "is_viral": d_id in viral_ids,
            "category": category,
            "status": d.get("status", "candidate"),
            "composite_score": d.get("composite_score", 0),
            "scores": d.get("scores", {}),
            "related_chips": d.get("related_chips", []),
            "evidence_sources": d.get("evidence_sources", []),
            "domain_tags": d.get("domain_tags", []),
            "builder_adoption": b.get("final_adoption_rate", 0),
            "enterprise_adoption": e.get("final_adoption_rate", 0),
            "advocacy_rate": b.get("final_advocacy_rate", 0),
            "tipping_point": b.get("tipping_point_round"),
            "consensus": b.get("final_consensus", 0),
            "disagreement": b.get("disagreement_score", 0),
            "builder_curve": builder_curve,
            "enterprise_curve": enterprise_curve,
            "adoption_by_persona_type": b.get("adoption_by_persona_type", {}),
        })

    # --- Export persona type distribution ---
    persona_types = []
    for ptype, traits in PERSONA_TYPES.items():
        count = sum(1 for p in personas if p["persona_type"] == ptype)
        persona_types.append({
            "type": ptype,
            "label": traits["label"],
            "count": count,
            "influence_score": traits["influence_score"],
            "adoption_threshold": traits["adoption_threshold"],
            "risk_tolerance": traits["risk_tolerance"],
            "network_reach": traits["network_reach"],
        })

    # --- Export signals summary ---
    signal_summary = {
        "opportunity_signals": len(opp_signals),
        "graph_signals": len(graph_signals),
        "total_signals": len(all_signals),
        "signal_types": {},
    }
    for s in all_signals:
        st = s.get("signal_type", "unknown")
        signal_summary["signal_types"][st] = signal_summary["signal_types"].get(st, 0) + 1

    # --- Export shocks ---
    shocks_data = []
    for s in shocks:
        shocks_data.append({
            "shock_id": s.get("shock_id", ""),
            "label": s.get("label", ""),
            "template": s.get("template", ""),
            "inject_at_round": s.get("inject_at_round", 0),
            "strength": s.get("strength", 0),
            "effect": s.get("effect", "neutral"),
            "affects_domains": s.get("affects_domains", []),
            "affected_persona_types": s.get("affected_persona_types", []),
        })

    # --- Assemble full export ---
    export = {
        "meta": {
            "title": f"MiroFish v2: {len(ALL_100_DOMAINS)}-Domain Trend Prediction",
            "agent_count": len(personas),
            "domain_count": len(domain_ids),
            "existing_count": len(EXISTING_CHIPS),
            "candidate_count": len(NEW_CANDIDATES),
            "viral_count": len(VIRAL_DOMAINS),
            "new_count": len(NEW_48_DOMAINS),
            "total_signals": len(all_signals),
            "graph_nodes": len(graph_nodes),
            "graph_edges": len(graph_edges),
            "rounds": 20,
            "persona_types": 11,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "graph_nodes": graph_nodes,
        "graph_edges": graph_edges,
        "domains": domains_data,
        "persona_types": persona_types,
        "signal_summary": signal_summary,
        "shocks": shocks_data,
    }

    # Write to file
    output_path = os.path.join(script_dir, "..", "viz", "mirofish_data.json")
    with open(output_path, "w") as f:
        json.dump(export, f, indent=2)
    size = os.path.getsize(output_path)
    print(f"\nExported to {output_path} ({size:,} bytes)")
    print(f"  {len(graph_nodes)} graph nodes, {len(graph_edges)} graph edges")
    print(f"  {len(domains_data)} domains with adoption curves")
    print(f"Total time: {time.time() - t0:.1f}s")
    return export


if __name__ == "__main__":
    main()
