"""Generate markdown report from existing 100-domain MiroFish predictions."""

import argparse
import json
import os


def main():
    parser = argparse.ArgumentParser(description="Generate top 100 report")
    parser.add_argument("--data-path",
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "viz", "100_domain_predictions.json"),
                        help="Input predictions JSON file")
    parser.add_argument("--output-path",
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "MIROFISH_TOP_100_RESEARCH.md"),
                        help="Output markdown file path")
    args = parser.parse_args()

    data_path = args.data_path
    output_path = args.output_path

    with open(data_path) as f:
        data = json.load(f)

    meta = data["run_metadata"]
    rankings = data["rankings"]

    # Build persona type list from top domain's per_persona data
    persona_types = list(rankings[0]["per_persona"].keys())
    n_persona_types = len(persona_types)

    # Sort by ensemble_mean descending
    rankings.sort(key=lambda r: r["ensemble_mean"], reverse=True)

    lines = []
    lines.append("# MiroFish Top 100 Domain Predictions")
    lines.append("")
    lines.append(f"**Generated**: {meta['timestamp']}")
    lines.append(f"**Agents**: {meta['total_personas']} ({n_persona_types} persona types)")
    lines.append(f"**Domains**: {meta['total_domains']}")
    lines.append(f"**Ensemble runs**: {meta['ensemble_runs']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Top 10 Domains")
    lines.append("")

    # Build top-10 table
    header = "| Rank | Domain | Advocacy Rate | Adoption | TAM | Signal |"
    sep = "|------|--------|-------------|----------|-----|--------|"
    lines.append(header)
    lines.append(sep)
    for i, r in enumerate(rankings[:10]):
        tam_label = r.get("tam", {}).get("label", "auto")
        lines.append(
            f"| {i+1} | `{r['domain_id']}` | {r['advocacy']:.1%} | {r['ensemble_mean']:.1%} | {tam_label} | {r['signal_strength']} |"
        )
    lines.append("")
    lines.append(f"*(Full rankings below)*")
    lines.append("")

    # Full rankings
    lines.append("## Full Rankings")
    lines.append("")
    lines.append("| Rank | Domain | Advocacy Rate | Adoption | Signal | Avg Persona Matches |")
    lines.append("|------|--------|-------------|----------|--------|-------------------|")
    for i, r in enumerate(rankings):
        # Count how many persona types have >0 advocacy for this domain
        advocating_types = sum(
            1 for pt in persona_types
            if r["per_persona"].get(pt, {}).get("advocacy", 0) > 0
        )
        lines.append(
            f"| {i+1} | `{r['domain_id']}` | {r['advocacy']:.1%} | {r['ensemble_mean']:.1%} | {r['signal_strength']} | {advocating_types}/{n_persona_types} |"
        )
    lines.append("")

    # Advocacy analysis
    lines.append("## Advocacy Analysis")
    lines.append("")
    lines.append("Domains with strongest advocacy (top 15):")
    lines.append("")
    lines.append("| Domain | Advocacy Rate | Adoption | Who Advocates |")
    lines.append("|--------|-------------|----------|---------------|")
    advocacy_sorted = sorted(rankings, key=lambda r: r["advocacy"], reverse=True)
    for r in advocacy_sorted[:15]:
        advocates = [
            pt for pt in persona_types
            if r["per_persona"].get(pt, {}).get("advocacy", 0) > 0
        ]
        lines.append(
            f"| `{r['domain_id']}` | **{r['advocacy']:.1%}** | {r['ensemble_mean']:.1%} | {', '.join(advocates) if advocates else 'none'} |"
        )
    lines.append("")

    # Tier-based analysis
    lines.append("## Tier Breakdown")
    lines.append("")
    tier1 = [r for r in rankings if r["ensemble_mean"] > 0.25]
    tier2 = [r for r in rankings if 0.15 <= r["ensemble_mean"] <= 0.25]
    tier3 = [r for r in rankings if 0.10 <= r["ensemble_mean"] < 0.15]
    tier4 = [r for r in rankings if r["ensemble_mean"] < 0.10]

    lines.append(f"- **Tier 1 (>25%)**: {len(tier1)} domains with strong adoption signal")
    lines.append(f"- **Tier 2 (15-25%)**: {len(tier2)} domains")
    lines.append(f"- **Tier 3 (10-15%)**: {len(tier3)} domains")
    lines.append(f"- **Tier 4 (<10%)**: {len(tier4)} domains with low adoption signal")
    lines.append("")

    lines.append("### Tier 1: High Signal (Ens Mean > 25%)")
    for r in tier1:
        lines.append(f"- `{r['domain_id']}` - {r['label']} ({r['ensemble_mean']:.1%})")
    lines.append("")

    lines.append("### Tier 2: Strong Signal (Ens Mean 15-25%)")
    for r in tier2:
        lines.append(f"- `{r['domain_id']}` - {r['label']} ({r['ensemble_mean']:.1%})")
    lines.append("")

    lines.append("### Tier 3: Watch List (Ens Mean 10-15%)")
    for r in tier3:
        lines.append(f"- `{r['domain_id']}` - {r['label']} ({r['ensemble_mean']:.1%})")
    lines.append("")

    lines.append("### Tier 4: Low Signal (Ens Mean < 10%)")
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


if __name__ == "__main__":
    main()
