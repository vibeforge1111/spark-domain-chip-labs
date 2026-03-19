"""Export MiroFish simulation data as JSON for the knowledge graph visualization."""

import json
import sys
import time

sys.path.insert(0, "src")

from chip_labs.mirofish.graph import build_graph_from_opportunities
from chip_labs.mirofish.personas import generate_personas, PERSONA_TYPES
from chip_labs.mirofish.simulation import run_simulation
from chip_labs.mirofish.signals import (
    signals_from_opportunities, signals_from_graph,
    create_shock, SIGNAL_TYPES, SHOCK_TEMPLATES,
)
from chip_labs.trend_scanner import score_opportunity

# Import domain data
from predict_1000_agents import EXISTING_CHIPS, NEW_CANDIDATES, ALL_DOMAINS


def main():
    # Score all domains
    for d in ALL_DOMAINS:
        d["composite_score"] = score_opportunity(d)

    # Build graph
    graph = build_graph_from_opportunities(ALL_DOMAINS)

    # Generate 1000 personas
    domain_ids = [d["domain_id"] for d in ALL_DOMAINS]
    personas = generate_personas(graph, domain_ids, count_per_type=125, seed=42)

    # Generate signals
    opp_signals = signals_from_opportunities(ALL_DOMAINS)
    graph_signals = signals_from_graph(graph)
    all_signals = opp_signals + graph_signals

    # Shocks
    shocks = [
        create_shock("breakout_tool", ["ai-agent-builder", "prompt-engineer"], inject_at_round=3),
        create_shock("viral_adoption", ["solana-dev", "defi-architect"], inject_at_round=5),
        create_shock("market_crash", ["trading-crypto", "defi-architect", "solana-dev", "personal-finance"], inject_at_round=8),
        create_shock("ecosystem_integration", ["open-source-maintainer", "ai-agent-builder"], inject_at_round=4),
        create_shock("regulatory_ban", ["health-wellness", "compliance-shield"], inject_at_round=10),
    ]

    # Run builder simulation
    builder_result = run_simulation(
        graph, domain_ids, personas=list(personas),
        signals=all_signals, shocks=shocks,
        max_rounds=20, seed=42, context="builder_community",
    )

    # Run enterprise simulation with fresh personas
    enterprise_personas = generate_personas(graph, domain_ids, count_per_type=125, seed=42)
    enterprise_result = run_simulation(
        graph, domain_ids, personas=enterprise_personas,
        signals=all_signals, shocks=shocks,
        max_rounds=20, seed=42, context="enterprise_market",
    )

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
    domains_data = []
    for d in ALL_DOMAINS:
        d_id = d["domain_id"]
        b = builder_result["domains"].get(d_id, {})
        e = enterprise_result["domains"].get(d_id, {})

        # Get adoption curve (per-round data)
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

        domains_data.append({
            "domain_id": d_id,
            "label": d.get("label", d_id),
            "description": d.get("description", ""),
            "is_existing": d_id in existing_ids,
            "status": d.get("status", "candidate"),
            "composite_score": d.get("composite_score", 0),
            "scores": d.get("scores", {}),
            "related_chips": d.get("related_chips", []),
            "evidence_sources": d.get("evidence_sources", []),
            "builder_adoption": b.get("final_adoption_rate", 0),
            "enterprise_adoption": e.get("final_adoption_rate", 0),
            "advocacy_rate": b.get("final_advocacy_rate", 0),
            "tipping_point": b.get("tipping_point_round"),
            "consensus": b.get("final_consensus", 0),
            "disagreement": b.get("disagreement_score", 0),
            "builder_curve": builder_curve,
            "enterprise_curve": enterprise_curve,
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
            "title": "MiroFish 1000-Agent Trend Prediction",
            "agent_count": len(personas),
            "domain_count": len(domain_ids),
            "existing_count": len(EXISTING_CHIPS),
            "candidate_count": len(NEW_CANDIDATES),
            "total_signals": len(all_signals),
            "graph_nodes": len(graph_nodes),
            "graph_edges": len(graph_edges),
            "rounds": 20,
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
    output_path = "viz/mirofish_data.json"
    with open(output_path, "w") as f:
        json.dump(export, f, indent=2)
    print(f"Exported to {output_path} ({len(json.dumps(export)):,} bytes)")
    return export


if __name__ == "__main__":
    main()
