"""Quick 250-domain run with progress output."""
import sys, os, time, json
sys.stdout.reconfigure(line_buffering=True)

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, "..", "src"))
sys.path.insert(0, script_dir)

print("Importing modules...", flush=True)
from predict_250_domains import ALL_250_DOMAINS, ALL_RELATIONSHIPS, NEW_RELATIONSHIPS
from chip_labs.mirofish.graph import DomainGraph, build_graph_from_opportunities
from chip_labs.mirofish.personas import generate_personas, CUSTOMER_PERSONAS
from chip_labs.mirofish.simulation import run_simulation, run_ensemble
from chip_labs.mirofish.signals import signals_from_opportunities, signals_from_graph
print(f"Loaded {len(ALL_250_DOMAINS)} domains", flush=True)

t0 = time.time()

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
for r in ALL_RELATIONSHIPS + NEW_RELATIONSHIPS:
    if r["source"] in graph.nodes and r["target"] in graph.nodes:
        graph.add_edge(r["source"], r["target"], r["relationship"], r.get("weight", 0.5))
print(f"Graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges", flush=True)

# Signals
domain_ids = [d["domain_id"] for d in ALL_250_DOMAINS]
opp_signals = signals_from_opportunities(ALL_250_DOMAINS)
graph_signals = signals_from_graph(graph)
all_signals = opp_signals + graph_signals
print(f"Signals: {len(all_signals)} total", flush=True)

# Personas - 550 agents
personas = generate_personas(graph, domain_ids=domain_ids, count_per_type=50, seed=42)
print(f"Personas: {len(personas)} agents", flush=True)

# Flagship simulation
print("Running flagship simulation...", flush=True)
t1 = time.time()
result = run_simulation(graph, domain_ids, personas=personas, signals=all_signals, max_rounds=20, seed=42)
t2 = time.time()
print(f"Flagship: {t2-t1:.1f}s", flush=True)

# Ensemble (3 runs for speed)
print("Running ensemble (3 runs)...", flush=True)
t3 = time.time()
ensemble = run_ensemble(graph, domain_ids, n_runs=3, count_per_type=10,
                        signals=all_signals, max_rounds=20, base_seed=42)
t4 = time.time()
print(f"Ensemble: {t4-t3:.1f}s", flush=True)

total_time = time.time() - t0

# Collect results
domain_results = []
for d in ALL_250_DOMAINS:
    d_id = d["domain_id"]
    sim_data = result["domains"].get(d_id, {})
    ens_data = ensemble["domains"].get(d_id, {})
    domain_results.append({
        "domain_id": d_id,
        "label": d.get("label", d_id),
        "status": d.get("status", "new"),
        "static_score": d.get("composite_score", 0.0),
        "adoption": sim_data.get("final_adoption_rate", 0.0),
        "advocacy": sim_data.get("final_advocacy_rate", 0.0),
        "ens_mean": ens_data.get("mean_adoption", 0.0),
        "p10": ens_data.get("p10_adoption", 0.0),
        "p90": ens_data.get("p90_adoption", 0.0),
        "by_type": sim_data.get("adoption_by_persona_type", {}),
    })
domain_results.sort(key=lambda x: x["ens_mean"], reverse=True)

# Print top 25
print(f"\n{'='*90}", flush=True)
print("TOP 25 DOMAINS", flush=True)
print(f"{'='*90}", flush=True)
for i, dr in enumerate(domain_results[:25], 1):
    print(f"{i:>3}  {dr['domain_id']:<30} {dr['ens_mean']:>8.1%} {dr['adoption']:>8.1%}", flush=True)

# Per-persona top 10
persona_top10 = {}
for ptype in CUSTOMER_PERSONAS:
    sorted_by = sorted(domain_results, key=lambda x: x["by_type"].get(ptype, {}).get("adoption_rate", 0), reverse=True)
    persona_top10[ptype] = sorted_by[:10]
    display = CUSTOMER_PERSONAS[ptype]["label"]
    print(f"\n--- {display} Top 10 ---", flush=True)
    for i, dr in enumerate(sorted_by[:10], 1):
        rate = dr["by_type"].get(ptype, {}).get("adoption_rate", 0)
        print(f"  {i:>2}  {dr['domain_id']:<30} {rate:.0%}", flush=True)

# Consensus
domain_appearances = {}
for ptype, top10 in persona_top10.items():
    for dr in top10:
        d_id = dr["domain_id"]
        if d_id not in domain_appearances:
            domain_appearances[d_id] = []
        domain_appearances[d_id].append(ptype)
consensus = sorted(domain_appearances.items(), key=lambda x: len(x[1]), reverse=True)

print(f"\n{'='*90}", flush=True)
print("CONSENSUS (in multiple top-10s)", flush=True)
for d_id, p_list in consensus[:15]:
    print(f"  {d_id:<30} {len(p_list)} personas: {', '.join(p_list)}", flush=True)

# Export JSON
export = {
    "run_metadata": {"total_domains": len(ALL_250_DOMAINS), "total_personas": len(personas),
                      "persona_types": len(CUSTOMER_PERSONAS), "ensemble_runs": 3,
                      "total_time_seconds": round(total_time, 1)},
    "rankings": [
        {"rank": i+1, "domain_id": dr["domain_id"], "label": dr["label"], "status": dr["status"],
         "ensemble_mean": round(dr["ens_mean"], 4), "p10": round(dr["p10"], 4), "p90": round(dr["p90"], 4),
         "builder_adoption": round(dr["adoption"], 4), "advocacy": round(dr["advocacy"], 4),
         "static_score": dr["static_score"],
         "per_persona": {pt: {"adoption": round(s["adoption_rate"], 4), "advocacy": round(s["advocacy_rate"], 4)}
                         for pt, s in dr["by_type"].items()}}
        for i, dr in enumerate(domain_results)
    ],
    "persona_top10": {
        ptype: [{"rank": i+1, "domain_id": dr["domain_id"],
                 "adoption": round(dr["by_type"].get(ptype, {}).get("adoption_rate", 0), 4)}
                for i, dr in enumerate(top10)]
        for ptype, top10 in persona_top10.items()
    },
    "consensus": [{"domain_id": d_id, "persona_count": len(p_list), "personas": p_list}
                   for d_id, p_list in consensus],
}
out = os.path.join(script_dir, "..", "viz", "250_domain_predictions.json")
with open(out, "w") as f:
    json.dump(export, f, indent=2)
print(f"\nJSON: {out}", flush=True)

# Generate MD report
md = []
md.append("# MiroFish v3: 250-Domain Chip Research")
md.append("")
md.append(f"**Generated**: March 2026  ")
md.append(f"**Engine**: MiroFish v3 Multi-Agent Trend Prediction  ")
md.append(f"**Agents**: {len(personas)} ({len(CUSTOMER_PERSONAS)} persona types x 50 each)  ")
md.append(f"**Domains**: {len(ALL_250_DOMAINS)}  ")
md.append(f"**Ensemble Runs**: 3 Monte Carlo  ")
md.append(f"**Simulation Time**: {total_time:.0f}s  ")
md.append("")
md.append("---")
md.append("")
md.append("## Top 25 Domain Chips")
md.append("")
md.append("| Rank | Domain | Label | Ens Mean | P10-P90 | Builder | Advocacy |")
md.append("|------|--------|-------|----------|---------|---------|----------|")
for i, dr in enumerate(domain_results[:25], 1):
    md.append(f"| {i} | `{dr['domain_id']}` | {dr['label']} | **{dr['ens_mean']:.1%}** | {dr['p10']:.0%}-{dr['p90']:.0%} | {dr['adoption']:.1%} | {dr['advocacy']:.1%} |")
md.append("")

md.append("## Each AI Persona's Top 10 Recommendations")
md.append("")
for ptype in CUSTOMER_PERSONAS:
    display = CUSTOMER_PERSONAS[ptype]["label"]
    desc = CUSTOMER_PERSONAS[ptype]["description"]
    md.append(f"### {display}")
    md.append(f"*{desc}*")
    md.append("")
    md.append("| # | Domain | Label | Adoption | Advocacy |")
    md.append("|---|--------|-------|----------|----------|")
    for i, dr in enumerate(persona_top10[ptype], 1):
        rate = dr["by_type"].get(ptype, {}).get("adoption_rate", 0)
        adv = dr["by_type"].get(ptype, {}).get("advocacy_rate", 0)
        md.append(f"| {i} | `{dr['domain_id']}` | {dr['label']} | **{rate:.0%}** | {adv:.0%} |")
    md.append("")

md.append("## Cross-Persona Consensus")
md.append("")
md.append("Domains appearing in multiple personas' top-10 lists:")
md.append("")
md.append("| Domain | Label | # Personas | Who Recommends |")
md.append("|--------|-------|-----------|----------------|")
for d_id, p_list in consensus:
    if len(p_list) >= 2:
        label = next((dr["label"] for dr in domain_results if dr["domain_id"] == d_id), d_id)
        md.append(f"| `{d_id}` | {label} | **{len(p_list)}** | {', '.join(p_list)} |")
md.append("")

md.append("## Full Rankings (All 250)")
md.append("")
md.append("| Rank | Domain | Label | Ens Mean | Builder | Status |")
md.append("|------|--------|-------|----------|---------|--------|")
for i, dr in enumerate(domain_results, 1):
    md.append(f"| {i} | `{dr['domain_id']}` | {dr['label']} | {dr['ens_mean']:.1%} | {dr['adoption']:.1%} | {dr['status']} |")
md.append("")
md.append("---")
md.append(f"*Generated by MiroFish v3 | {len(personas)} agents | {len(ALL_250_DOMAINS)} domains | {total_time:.0f}s*")

md_path = os.path.join(script_dir, "..", "docs", "MIROFISH_250_RESEARCH.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print(f"MD: {md_path}", flush=True)
print(f"\nDONE in {total_time:.0f}s", flush=True)
