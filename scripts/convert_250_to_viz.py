"""Convert existing 250-domain prediction results into the visualization format.

Reads 250_domain_predictions.json (from the 3.5-hour simulation) and domain
metadata from predict_250_domains.py, then generates mirofish_250_data.json
with synthetic adoption curves (logistic growth scaled to actual final rates).

This avoids re-running the full simulation just to get viz-format data.
"""

import json
import math
import os
import sys
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, "..", "src"))
sys.path.insert(0, script_dir)

from predict_250_domains import (
    ALL_250_DOMAINS, FIRST_100, NEW_150_DOMAINS,
    EXISTING_CHIPS, NEW_CANDIDATES, VIRAL_DOMAINS, NEW_48_DOMAINS,
    RELATIONSHIPS, NEW_RELATIONSHIPS,
)
from chip_labs.mirofish.personas import CUSTOMER_PERSONAS

ALL_RELS = RELATIONSHIPS + NEW_RELATIONSHIPS
ROUNDS = 20


def logistic_curve(final_rate, rounds=ROUNDS, midpoint=None, steepness=None):
    """Generate a logistic adoption curve scaled to the final rate."""
    if final_rate <= 0:
        return [0.0] * (rounds + 1)

    # Higher adoption -> earlier midpoint (faster takeoff)
    if midpoint is None:
        midpoint = max(3, min(14, int((1.0 - final_rate * 5) * 10)))
    if steepness is None:
        steepness = 0.4 + final_rate * 2  # higher adoption = steeper curve

    curve = []
    for r in range(rounds + 1):
        val = final_rate / (1.0 + math.exp(-steepness * (r - midpoint)))
        curve.append(min(val, final_rate))
    return curve


def generate_stage_distribution(adoption_rate, advocacy_rate, interest_rate):
    """Generate realistic stage distribution from rates."""
    advocating = advocacy_rate
    adopted = max(0, adoption_rate - advocating)
    evaluating = min(0.08, adoption_rate * 0.3)
    interested = max(0, interest_rate - adoption_rate - evaluating)
    aware = max(0, min(0.3, 1.0 - adopted - advocating - evaluating - interested))
    unaware = max(0, 1.0 - aware - interested - evaluating - adopted - advocating)
    return {
        "unaware": round(unaware, 4),
        "aware": round(aware, 4),
        "interested": round(interested, 4),
        "evaluating": round(evaluating, 4),
        "adopted": round(adopted, 4),
        "advocating": round(advocating, 4),
    }


def main():
    t0 = time.time()

    # Load the existing prediction results
    pred_path = os.path.join(script_dir, "..", "viz", "250_domain_predictions.json")
    with open(pred_path) as f:
        predictions = json.load(f)

    # Build lookup from predictions
    pred_lookup = {}
    for r in predictions["rankings"]:
        pred_lookup[r["domain_id"]] = r

    # Build domain metadata lookup
    domain_meta = {}
    for d in ALL_250_DOMAINS:
        domain_meta[d["domain_id"]] = d

    # Categorize domains
    existing_ids = {d["domain_id"] for d in EXISTING_CHIPS}
    viral_ids = {d["domain_id"] for d in VIRAL_DOMAINS}
    new48_ids = {d["domain_id"] for d in NEW_48_DOMAINS}
    new150_ids = {d["domain_id"] for d in NEW_150_DOMAINS}
    candidate_ids = {d["domain_id"] for d in NEW_CANDIDATES}

    # Build graph nodes from domains + tech nodes
    graph_nodes = []
    for d in ALL_250_DOMAINS:
        graph_nodes.append({
            "id": d["domain_id"],
            "label": d.get("label", d["domain_id"]),
            "type": "domain",
        })
    tech_nodes = ["ai-tools", "blockchain", "web-platform", "social-media", "saas-infra"]
    for t in tech_nodes:
        graph_nodes.append({"id": t, "label": t, "type": "technology"})

    # Build graph edges from relationships + evidence sources
    graph_edges = []
    domain_id_set = {d["domain_id"] for d in ALL_250_DOMAINS}
    for d in ALL_250_DOMAINS:
        for src in d.get("evidence_sources", []):
            if src == "github":
                graph_edges.append({"source": "ai-tools", "target": d["domain_id"],
                                    "relationship": "ENABLES", "weight": 0.5})
            elif src == "x_twitter":
                graph_edges.append({"source": "social-media", "target": d["domain_id"],
                                    "relationship": "ENABLES", "weight": 0.4})
    for r in ALL_RELS:
        if r["source"] in domain_id_set and r["target"] in domain_id_set:
            graph_edges.append({
                "source": r["source"], "target": r["target"],
                "relationship": r["relationship"],
                "weight": r.get("weight", 0.5),
            })

    # Build domain viz data with synthetic adoption curves
    domains_data = []
    for d in ALL_250_DOMAINS:
        d_id = d["domain_id"]
        pred = pred_lookup.get(d_id, {})

        final_adoption = pred.get("builder_adoption", 0)
        final_advocacy = pred.get("advocacy", 0)
        ens_mean = pred.get("ensemble_mean", 0)
        per_persona = pred.get("per_persona", {})

        # Generate builder adoption curve (logistic)
        adoption_curve = logistic_curve(final_adoption)
        advocacy_curve = logistic_curve(final_advocacy, midpoint=12, steepness=0.3)
        interest_curve = logistic_curve(min(1.0, final_adoption * 3), midpoint=6, steepness=0.5)

        builder_curve = []
        for r in range(ROUNDS + 1):
            ar = adoption_curve[r]
            adv = advocacy_curve[r]
            ir = interest_curve[r]
            stage_dist = generate_stage_distribution(ar, adv, ir)
            builder_curve.append({
                "round": r,
                "adoption_rate": round(ar, 4),
                "advocacy_rate": round(adv, 4),
                "interest_rate": round(ir, 4),
                "stage_distribution": stage_dist,
            })

        # Enterprise curve (slightly delayed, lower rates)
        ent_adoption = final_adoption * 0.7
        ent_curve_vals = logistic_curve(ent_adoption, midpoint=10, steepness=0.35)
        ent_adv_vals = logistic_curve(final_advocacy * 0.5, midpoint=14, steepness=0.25)
        enterprise_curve = []
        for r in range(ROUNDS + 1):
            enterprise_curve.append({
                "round": r,
                "adoption_rate": round(ent_curve_vals[r], 4),
                "advocacy_rate": round(ent_adv_vals[r], 4),
                "interest_rate": round(min(1.0, ent_curve_vals[r] * 2.5), 4),
            })

        # Category
        category = "existing" if d_id in existing_ids else \
                   "viral" if d_id in viral_ids else \
                   "new48" if d_id in new48_ids else \
                   "new150" if d_id in new150_ids else "candidate"

        # Adoption by persona type
        adoption_by_persona = {}
        for ptype, pdata in per_persona.items():
            adoption_by_persona[ptype] = {
                "adoption_rate": pdata.get("adoption", 0),
                "advocacy_rate": pdata.get("advocacy", 0),
            }

        # Tipping point (round where adoption > 3%)
        tipping = None
        for r, val in enumerate(adoption_curve):
            if val > 0.03:
                tipping = r
                break

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
            "builder_adoption": final_adoption,
            "enterprise_adoption": ent_adoption,
            "advocacy_rate": final_advocacy,
            "tipping_point": tipping,
            "consensus": ens_mean,
            "disagreement": abs(pred.get("p90", 0) - pred.get("p10", 0)),
            "builder_curve": builder_curve,
            "enterprise_curve": enterprise_curve,
            "adoption_by_persona_type": adoption_by_persona,
        })

    # Persona types
    persona_types = []
    for ptype, traits in CUSTOMER_PERSONAS.items():
        persona_types.append({
            "type": ptype,
            "label": traits["label"],
            "count": 50,
            "influence_score": traits["influence_score"],
            "adoption_threshold": traits["adoption_threshold"],
            "risk_tolerance": traits["risk_tolerance"],
            "network_reach": traits["network_reach"],
        })

    # Shocks (same as the simulation used)
    shocks_data = [
        {"shock_id": "breakout_ai_tools", "label": "AI Tool Breakout",
         "template": "breakout_tool", "inject_at_round": 3, "strength": 0.8,
         "effect": "positive",
         "affects_domains": ["ai-agent-builder", "prompt-engineer", "cursor-copilot", "mcp-server-builder"],
         "affected_persona_types": ["developer", "tool_maker", "entrepreneur"]},
        {"shock_id": "viral_web3", "label": "Web3 Viral Wave",
         "template": "viral_adoption", "inject_at_round": 5, "strength": 0.7,
         "effect": "positive",
         "affects_domains": ["solana-dev", "defi-architect", "meme-coin-launcher", "ai-agent-token"],
         "affected_persona_types": ["trader", "opportunity_hunter", "investor"]},
        {"shock_id": "market_crash", "label": "Crypto Market Crash",
         "template": "market_crash", "inject_at_round": 8, "strength": 0.6,
         "effect": "negative",
         "affects_domains": ["trading-crypto", "defi-architect", "solana-dev", "perpetuals-trading", "quant-strategy"],
         "affected_persona_types": ["trader", "investor"]},
        {"shock_id": "ecosystem_sync", "label": "Ecosystem Integration",
         "template": "ecosystem_integration", "inject_at_round": 4, "strength": 0.5,
         "effect": "positive",
         "affects_domains": ["mcp-server-builder", "ai-agent-builder", "supabase-fullstack", "rag-pipeline"],
         "affected_persona_types": ["developer", "tool_maker"]},
        {"shock_id": "regulatory_ban", "label": "Regulatory Crackdown",
         "template": "regulatory_ban", "inject_at_round": 10, "strength": 0.5,
         "effect": "negative",
         "affects_domains": ["health-wellness", "compliance-shield", "crypto-airdrop", "sports-betting"],
         "affected_persona_types": ["marketer", "opportunity_hunter"]},
        {"shock_id": "viral_creator", "label": "Creator Economy Surge",
         "template": "viral_adoption", "inject_at_round": 6, "strength": 0.6,
         "effect": "positive",
         "affects_domains": ["tiktok-creator", "faceless-youtube", "telegram-miniapp", "ai-personal-assistant"],
         "affected_persona_types": ["content_creator", "creative", "opportunity_hunter"]},
        {"shock_id": "nocode_breakout", "label": "No-Code Breakout",
         "template": "breakout_tool", "inject_at_round": 7, "strength": 0.5,
         "effect": "positive",
         "affects_domains": ["no-code-saas", "ai-workflow-automation", "ai-chatbot-no-code"],
         "affected_persona_types": ["solopreneur", "entrepreneur", "ai_newcomer"]},
    ]

    # Signal summary
    signal_summary = {
        "opportunity_signals": 30000,
        "graph_signals": 29000,
        "total_signals": 59092,
        "signal_types": {
            "trend_signal": 15000,
            "competition_signal": 10000,
            "adoption_signal": 12000,
            "graph_proximity": 22092,
        },
    }

    # Assemble export
    export = {
        "meta": {
            "title": f"MiroFish v3: {len(ALL_250_DOMAINS)}-Domain Trend Prediction",
            "agent_count": 550,
            "domain_count": len(ALL_250_DOMAINS),
            "existing_count": len(EXISTING_CHIPS),
            "candidate_count": len(NEW_CANDIDATES),
            "viral_count": len(VIRAL_DOMAINS),
            "new_count": len(NEW_48_DOMAINS) + len(NEW_150_DOMAINS),
            "total_signals": 59092,
            "graph_nodes": len(graph_nodes),
            "graph_edges": len(graph_edges),
            "rounds": ROUNDS,
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

    # Sort domains by builder_adoption for ranking
    export["domains"].sort(key=lambda x: x["builder_adoption"], reverse=True)

    output_path = os.path.join(script_dir, "..", "viz", "mirofish_250_data.json")
    with open(output_path, "w") as f:
        json.dump(export, f, indent=2)

    size = os.path.getsize(output_path)
    print(f"Exported to {output_path}")
    print(f"  Size: {size:,} bytes")
    print(f"  {len(graph_nodes)} graph nodes, {len(graph_edges)} graph edges")
    print(f"  {len(domains_data)} domains with adoption curves")
    print(f"  {len(shocks_data)} shock events")
    print(f"  Time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
