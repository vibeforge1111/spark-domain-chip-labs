"""Generate markdown report from existing 100-domain MiroFish predictions."""

import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "..", "viz", "100_domain_predictions.json")
output_path = os.path.join(script_dir, "..", "docs", "MIROFISH_TOP_100_RESEARCH.md")

with open(data_path) as f:
    data = json.load(f)

meta = data["run_metadata"]
rankings = data["rankings"]

lines = []
lines.append("# MiroFish Top 100 Domain Chip Research")
lines.append("")
lines.append(f"**Generated**: March 2026")
lines.append(f"**Engine**: MiroFish v2 Multi-Agent Trend Prediction")
lines.append(f"**Agents**: {meta['total_personas']:,} ({meta['persona_types']} persona types x 125 each)")
lines.append(f"**Domains**: {meta['total_domains']}")
lines.append(f"**Ensemble Runs**: {meta['ensemble_runs']} Monte Carlo")
lines.append(f"**Simulation Time**: {meta['total_time_seconds']:.0f}s")
lines.append("")
lines.append("---")
lines.append("")

# --- TOP 20 ---
lines.append("## Top 20 Domain Chips (Highest Adoption Signal)")
lines.append("")
lines.append("| Rank | Domain | Label | Status | Ens Mean | P10-P90 | Builder | Advocacy | Static |")
lines.append("|------|--------|-------|--------|----------|---------|---------|----------|--------|")
for r in rankings[:20]:
    lines.append(
        f"| {r['rank']} | `{r['domain_id']}` | {r['label']} | {r['status']} | "
        f"**{r['ensemble_mean']:.1%}** | {r['p10']:.0%}-{r['p90']:.0%} | "
        f"{r['builder_adoption']:.1%} | {r['advocacy']:.1%} | {r['static_score']:.2f} |"
    )
lines.append("")

# --- TOP 20 Persona breakdown ---
lines.append("### Per-Persona Adoption (Top 10)")
lines.append("")
persona_types = list(rankings[0]["per_persona"].keys())
header = "| Rank | Domain |"
sep = "|------|--------|"
for pt in persona_types:
    short = pt[:8]
    header += f" {short} |"
    sep += "---------|"
lines.append(header)
lines.append(sep)
for r in rankings[:10]:
    row = f"| {r['rank']} | `{r['domain_id']}` |"
    for pt in persona_types:
        val = r["per_persona"].get(pt, {}).get("adoption", 0)
        row += f" {val:.0%} |"
    lines.append(row)
lines.append("")

# --- EACH PERSONA'S TOP 10 ---
lines.append("## Each Persona Type's Top 10 Domains")
lines.append("")
lines.append("What each AI agent persona recommends as their top picks:")
lines.append("")
for pt in persona_types:
    display_name = pt.replace("_", " ").title()
    lines.append(f"### {display_name}")
    lines.append("")
    # Sort all domains by this persona's adoption
    sorted_by_persona = sorted(
        rankings,
        key=lambda x: x["per_persona"].get(pt, {}).get("adoption", 0),
        reverse=True,
    )
    lines.append("| # | Domain | Adoption | Advocacy | Why They Love It |")
    lines.append("|---|--------|----------|----------|------------------|")
    for i, r in enumerate(sorted_by_persona[:10], 1):
        adoption = r["per_persona"].get(pt, {}).get("adoption", 0)
        advocacy = r["per_persona"].get(pt, {}).get("advocacy", 0)
        lines.append(f"| {i} | `{r['domain_id']}` ({r['label']}) | **{adoption:.0%}** | {advocacy:.0%} | {r['status']} |")
    lines.append("")

# --- MIDDLE 30 ---
lines.append("## Middle Tier (Ranks 21-50)")
lines.append("")
lines.append("| Rank | Domain | Label | Ens Mean | P10-P90 | Builder | Static |")
lines.append("|------|--------|-------|----------|---------|---------|--------|")
for r in rankings[20:50]:
    lines.append(
        f"| {r['rank']} | `{r['domain_id']}` | {r['label']} | "
        f"{r['ensemble_mean']:.1%} | {r['p10']:.0%}-{r['p90']:.0%} | "
        f"{r['builder_adoption']:.1%} | {r['static_score']:.2f} |"
    )
lines.append("")

# --- BOTTOM 30 ---
lines.append("## Lower Tier (Ranks 51-100)")
lines.append("")
lines.append("| Rank | Domain | Label | Ens Mean | P10-P90 | Builder | Static |")
lines.append("|------|--------|-------|----------|---------|---------|--------|")
for r in rankings[50:]:
    lines.append(
        f"| {r['rank']} | `{r['domain_id']}` | {r['label']} | "
        f"{r['ensemble_mean']:.1%} | {r['p10']:.0%}-{r['p90']:.0%} | "
        f"{r['builder_adoption']:.1%} | {r['static_score']:.2f} |"
    )
lines.append("")

# --- CONSENSUS PICKS (all persona types agree) ---
lines.append("## Consensus Analysis")
lines.append("")
lines.append("### Universal Picks (adopted by 8+ persona types at >20%)")
lines.append("")
for r in rankings:
    count = sum(1 for pt in persona_types if r["per_persona"].get(pt, {}).get("adoption", 0) > 0.20)
    if count >= 8:
        lines.append(f"- **`{r['domain_id']}`** ({r['label']}): {count}/{len(persona_types)} persona types at >20% adoption")
lines.append("")

lines.append("### Polarizing Picks (loved by some, ignored by others)")
lines.append("")
for r in rankings[:30]:
    adoptions = [r["per_persona"].get(pt, {}).get("adoption", 0) for pt in persona_types]
    max_a = max(adoptions)
    min_a = min(adoptions)
    if max_a - min_a > 0.6:
        top_persona = max(persona_types, key=lambda pt: r["per_persona"].get(pt, {}).get("adoption", 0))
        bot_persona = min(persona_types, key=lambda pt: r["per_persona"].get(pt, {}).get("adoption", 0))
        lines.append(
            f"- **`{r['domain_id']}`**: {top_persona} loves it ({max_a:.0%}) but {bot_persona} ignores it ({min_a:.0%})"
        )
lines.append("")

# --- ADVOCACY LEADERS ---
lines.append("### Advocacy Leaders (highest word-of-mouth signal)")
lines.append("")
advocacy_sorted = sorted(rankings, key=lambda x: x["advocacy"], reverse=True)
lines.append("| Domain | Advocacy Rate | Adoption | Who Advocates |")
lines.append("|--------|-------------|----------|---------------|")
for r in advocacy_sorted[:15]:
    advocates = [
        pt for pt in persona_types
        if r["per_persona"].get(pt, {}).get("advocacy", 0) > 0
    ]
    lines.append(
        f"| `{r['domain_id']}` | **{r['advocacy']:.1%}** | {r['ensemble_mean']:.1%} | {', '.join(advocates) if advocates else 'none'} |"
    )
lines.append("")

# --- SUMMARY ---
lines.append("## Key Takeaways")
lines.append("")
lines.append("### Tier 1: Build Now (Ens Mean > 25%)")
tier1 = [r for r in rankings if r["ensemble_mean"] > 0.25]
for r in tier1:
    lines.append(f"- **`{r['domain_id']}`** - {r['label']} ({r['ensemble_mean']:.1%})")
lines.append("")

lines.append("### Tier 2: Strong Signal (Ens Mean 15-25%)")
tier2 = [r for r in rankings if 0.15 <= r["ensemble_mean"] <= 0.25]
for r in tier2:
    lines.append(f"- `{r['domain_id']}` - {r['label']} ({r['ensemble_mean']:.1%})")
lines.append("")

lines.append("### Tier 3: Watch List (Ens Mean 10-15%)")
tier3 = [r for r in rankings if 0.10 <= r["ensemble_mean"] < 0.15]
for r in tier3:
    lines.append(f"- `{r['domain_id']}` - {r['label']} ({r['ensemble_mean']:.1%})")
lines.append("")

lines.append("### Tier 4: Low Signal (Ens Mean < 10%)")
tier4 = [r for r in rankings if r["ensemble_mean"] < 0.10]
for r in tier4:
    lines.append(f"- `{r['domain_id']}` - {r['label']} ({r['ensemble_mean']:.1%})")
lines.append("")

lines.append("---")
lines.append("")
lines.append("*Generated by MiroFish v2 Multi-Agent Trend Prediction Engine*")
lines.append(f"*{meta['total_personas']} agents, {meta['total_domains']} domains, {meta['ensemble_runs']} Monte Carlo runs*")

content = "\n".join(lines)
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Report written to {output_path}")
print(f"Total lines: {len(lines)}")
print(f"Tier 1 (>25%): {len(tier1)} domains")
print(f"Tier 2 (15-25%): {len(tier2)} domains")
print(f"Tier 3 (10-15%): {len(tier3)} domains")
print(f"Tier 4 (<10%): {len(tier4)} domains")
