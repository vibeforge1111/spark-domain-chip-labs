"""Compare MiroFish simulation results: 550 agents vs 1001 agents.

Runs lightweight simulations (10 rounds) to measure how agent count
affects adoption rates, tipping points, and persona distribution.
"""

import os
import sys
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, "..", "src"))

from chip_labs.mirofish.graph import DomainGraph, build_graph_from_opportunities
from chip_labs.mirofish.personas import generate_personas, PERSONA_TYPES
from chip_labs.mirofish.simulation import run_simulation
from chip_labs.mirofish.signals import signals_from_opportunities, signals_from_graph, create_shock

from predict_100_domains import ALL_100_DOMAINS, RELATIONSHIPS


def build_graph(domains, relationships):
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


def run_comparison(graph, domain_ids, domains, count_per_type, label, seed=42):
    t0 = time.time()
    total = count_per_type * len(PERSONA_TYPES)
    print(f"\n{'='*60}")
    print(f"  {label}: {count_per_type} per type = {total} agents")
    print(f"{'='*60}")

    opp_signals = signals_from_opportunities(domains)
    graph_signals = signals_from_graph(graph)

    # Stagger signals (same as export script)
    domain_scores = {d["domain_id"]: d.get("composite_score", 0.5) for d in domains}
    for sig in opp_signals:
        affected = sig.get("affects_domains", [])
        if affected:
            avg = sum(domain_scores.get(d, 0.5) for d in affected) / len(affected)
            sig["inject_at_round"] = min(int((1.0 - avg) * 14), 12)
    for sig in graph_signals:
        affected = sig.get("affects_domains", [])
        if affected:
            avg = sum(domain_scores.get(d, 0.5) for d in affected) / len(affected)
            sig["inject_at_round"] = min(int((1.0 - avg) * 14) + 2, 14)

    all_signals = opp_signals + graph_signals

    shocks = [
        create_shock("breakout_tool", ["ai-agent-builder", "prompt-engineer", "cursor-copilot"], inject_at_round=3),
        create_shock("viral_adoption", ["solana-dev", "defi-architect", "meme-coin-launcher"], inject_at_round=5),
        create_shock("market_crash", ["trading-crypto", "defi-architect", "solana-dev"], inject_at_round=8),
        create_shock("ecosystem_integration", ["mcp-server-builder", "ai-agent-builder"], inject_at_round=4),
    ]

    personas = generate_personas(graph, domain_ids, count_per_type=count_per_type, seed=seed)
    result = run_simulation(
        graph, domain_ids, personas=list(personas),
        signals=all_signals, shocks=shocks,
        max_rounds=20, seed=seed, context="builder_community",
    )

    elapsed = time.time() - t0
    print(f"  Completed in {elapsed:.1f}s")

    return result, elapsed


def compare_results(result_small, result_large, label_small, label_large):
    print(f"\n{'='*70}")
    print(f"  COMPARISON: {label_small} vs {label_large}")
    print(f"{'='*70}")

    # Gather domain results
    all_domains = set(result_small["domains"].keys()) | set(result_large["domains"].keys())

    rows = []
    for d_id in sorted(all_domains):
        s = result_small["domains"].get(d_id, {})
        l = result_large["domains"].get(d_id, {})
        s_adopt = s.get("final_adoption_rate", 0)
        l_adopt = l.get("final_adoption_rate", 0)
        s_adv = s.get("final_advocacy_rate", 0)
        l_adv = l.get("final_advocacy_rate", 0)
        s_tp = s.get("tipping_point_round")
        l_tp = l.get("tipping_point_round")
        delta = l_adopt - s_adopt
        rows.append((d_id, s_adopt, l_adopt, delta, s_adv, l_adv, s_tp, l_tp))

    # Sort by absolute delta (biggest changes first)
    rows.sort(key=lambda r: abs(r[3]), reverse=True)

    # Summary stats
    s_adoptions = [r[1] for r in rows]
    l_adoptions = [r[2] for r in rows]
    deltas = [r[3] for r in rows]
    s_avg = sum(s_adoptions) / len(s_adoptions)
    l_avg = sum(l_adoptions) / len(l_adoptions)

    print(f"\n  Average adoption:  {label_small}={s_avg*100:.2f}%  {label_large}={l_avg*100:.2f}%  delta={((l_avg-s_avg)*100):+.2f}%")
    print(f"  Domains with >5% adoption: {label_small}={sum(1 for a in s_adoptions if a > 0.05)}  {label_large}={sum(1 for a in l_adoptions if a > 0.05)}")
    print(f"  Tipping points reached: {label_small}={sum(1 for r in rows if r[6] is not None)}  {label_large}={sum(1 for r in rows if r[7] is not None)}")

    # Biggest gainers
    print(f"\n  Top 15 domains with BIGGEST CHANGE ({label_large} vs {label_small}):")
    print(f"  {'Domain':<28} {'550 agents':>10} {'1001 agents':>12} {'Delta':>8}  {'Direction'}")
    print(f"  {'-'*72}")
    for d_id, s_a, l_a, delta, s_adv, l_adv, s_tp, l_tp in rows[:15]:
        direction = "UP" if delta > 0 else "DOWN" if delta < 0 else "SAME"
        print(f"  {d_id:<28} {s_a*100:>9.1f}% {l_a*100:>11.1f}% {delta*100:>+7.1f}%  {direction}")

    # Per-persona-type comparison for top 5 domains
    print(f"\n  Per-persona breakdown for top 5 changed domains:")
    for d_id, s_a, l_a, delta, _, _, _, _ in rows[:5]:
        s_dom = result_small["domains"].get(d_id, {})
        l_dom = result_large["domains"].get(d_id, {})
        s_pt = s_dom.get("adoption_by_persona_type", {})
        l_pt = l_dom.get("adoption_by_persona_type", {})
        print(f"\n  {d_id}: {s_a*100:.1f}% -> {l_a*100:.1f}% ({delta*100:+.1f}%)")
        for ptype in sorted(PERSONA_TYPES.keys()):
            s_rate = s_pt.get(ptype, {}).get("adoption_rate", 0)
            l_rate = l_pt.get(ptype, {}).get("adoption_rate", 0)
            p_delta = l_rate - s_rate
            if abs(p_delta) > 0.01 or s_rate > 0.01 or l_rate > 0.01:
                bar = "#" * int(l_rate * 30)
                print(f"    {ptype:<20} {s_rate*100:>5.1f}% -> {l_rate*100:>5.1f}% ({p_delta*100:+5.1f}%)  {bar}")

    # Statistical summary
    up = sum(1 for d in deltas if d > 0.005)
    down = sum(1 for d in deltas if d < -0.005)
    same = len(deltas) - up - down
    print(f"\n  Summary: {up} domains UP, {down} domains DOWN, {same} roughly SAME")
    print(f"  Max increase: {max(deltas)*100:+.1f}%  Max decrease: {min(deltas)*100:+.1f}%")
    print(f"  Median delta: {sorted(deltas)[len(deltas)//2]*100:+.2f}%")


def main():
    print("Building graph for 100 domains...")
    graph = build_graph(ALL_100_DOMAINS, RELATIONSHIPS)
    domain_ids = [d["domain_id"] for d in ALL_100_DOMAINS]

    # Run 550 agents (50 per type)
    result_550, time_550 = run_comparison(graph, domain_ids, ALL_100_DOMAINS, 50, "550 agents")

    # Run 1001 agents (91 per type)
    result_1001, time_1001 = run_comparison(graph, domain_ids, ALL_100_DOMAINS, 91, "1001 agents")

    compare_results(result_550, result_1001, "550 agents", "1001 agents")

    print(f"\n  Time: 550 agents={time_550:.0f}s, 1001 agents={time_1001:.0f}s")
    print(f"  Slowdown: {time_1001/time_550:.1f}x")


if __name__ == "__main__":
    main()
