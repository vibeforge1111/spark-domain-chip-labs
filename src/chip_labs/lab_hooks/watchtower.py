"""Lab watchtower -- generates Obsidian pages for the lab observatory."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from ..quality_rubric import score_portfolio
from ..registry import discover_chips, get_portfolio_summary


def generate_watchtower_pages(mutations: dict[str, str],
                              chip_search_dir: str | Path | None = None,
                              vault_dir: str | Path | None = None) -> list[dict[str, Any]]:
    """Generate Obsidian pages for the lab's watchtower.

    Returns a list of page specs with path and content.
    """
    vault = Path(vault_dir) if vault_dir else Path("obsidian-vault")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pages: list[dict[str, Any]] = []

    # Always generate: Lab Home
    pages.append(_lab_home_page(now, chip_search_dir))

    # Always generate: Portfolio Dashboard
    pages.append(_portfolio_dashboard_page(now, chip_search_dir))

    # Always generate: MiroFish Portfolio
    pages.append(_mirofish_portfolio_page(now))

    # Always generate: MiroFish Frontier
    pages.append(_mirofish_frontier_page(now))

    # Conditional: Agent Team Status
    pages.append(_agent_team_page(now, mutations))

    # Conditional: Graduation Pipeline
    pages.append(_graduation_pipeline_page(now, chip_search_dir))

    # Always generate: Trend Predictions
    pages.append(_trend_predictions_page(now))

    return pages


def _lab_home_page(timestamp: str, chip_search_dir: str | Path | None) -> dict[str, Any]:
    """Generate the lab home page."""
    summary = get_portfolio_summary(chip_search_dir)

    content = f"""# Spark Domain Chip Labs

> Last updated: {timestamp}

## Mission

The recursive improvement engine for the Spark domain chip ecosystem.

## Portfolio Overview

- **Total chips tracked**: {summary['total_chips']}
- **Total artifacts**: {summary['total_artifacts']:,}
- **Total vault docs**: {summary['total_vault_docs']:,}

### Maturity Distribution

| Level | Count |
|-------|-------|
| Production | {summary['maturity_distribution'].get('production', 0)} |
| Beta | {summary['maturity_distribution'].get('beta', 0)} |
| Alpha | {summary['maturity_distribution'].get('alpha', 0)} |
| Scaffold | {summary['maturity_distribution'].get('scaffold', 0)} |

## Agent Research Team

- Frontier Scout -- discovers new domain opportunities
- Methodology Researcher -- improves chip-building methodology
- Chip Architect -- designs new chip manifests
- Benchmark Engineer -- quality benchmarks
- Integration Specialist -- spark-researcher/swarm compatibility
- Growth Analyst -- ecosystem adoption tracking
- AGI Theorist -- recursive self-improvement research

## Links

- [[Portfolio Dashboard]]
- [[MiroFish Portfolio]]
- [[MiroFish Frontier]]
- [[Agent Team Status]]
- [[Graduation Pipeline]]
- [[Trend Predictions]]
"""
    return {"path": "Lab Home.md", "content": content}


def _portfolio_dashboard_page(timestamp: str, chip_search_dir: str | Path | None) -> dict[str, Any]:
    """Generate the portfolio dashboard page."""
    chips = discover_chips(chip_search_dir)
    chip_paths = [Path(c["path"]) for c in chips if c["has_manifest"]]
    portfolio = score_portfolio(chip_paths)

    rows = ""
    for chip in sorted(portfolio["chips"], key=lambda x: x["total_score"], reverse=True):
        rows += f"| {chip['chip_name']} | {chip['total_score']}/100 | {chip['verdict']} |\n"

    content = f"""# Portfolio Dashboard

> Last updated: {timestamp}

## Summary

- **Chips evaluated**: {portfolio['portfolio_size']}
- **Average quality score**: {portfolio['average_score']}/100
- **Verdict distribution**: {portfolio['verdict_distribution']}

## Chip Scores

| Chip | Score | Verdict |
|------|-------|---------|
{rows}

## Quality Trend

_Updated each watchtower pass. Track portfolio average over time._

## Action Items

- Audit chips scoring below 50/100
- Investigate chips missing evidence lane separation
- Prioritize graduation pipeline candidates

## Links

- [[Lab Home]]
- [[MiroFish Portfolio]]
- [[MiroFish Frontier]]
- [[Trend Predictions]]
"""
    return {"path": "Portfolio Dashboard.md", "content": content}


def _mirofish_portfolio_page(timestamp: str) -> dict[str, Any]:
    """Generate the current MiroFish portfolio checkpoint page."""
    export_path = _latest_meta_file("MIROFISH_PORTFOLIO_EXPORT_*.md")
    readout_path = _latest_meta_file("MIROFISH_PORTFOLIO_READOUT_*.json")

    if export_path is not None:
        export_body = export_path.read_text(encoding="utf-8").strip()
        content = f"""# MiroFish Portfolio

> Last updated: {timestamp}
> Canonical export: `{export_path.relative_to(_repo_root())}`

## Current Checkpoint

The page below is sourced from the latest saved MiroFish portfolio export artifact.

{export_body}

## Links

- [[Lab Home]]
- [[Portfolio Dashboard]]
- [[MiroFish Frontier]]
- [[Trend Predictions]]
"""
        return {"path": "MiroFish Portfolio.md", "content": content}

    if readout_path is not None:
        from ..mirofish.portfolio import format_portfolio_readout_markdown

        readout_packet = json.loads(readout_path.read_text(encoding="utf-8"))
        export_body = format_portfolio_readout_markdown(
            readout_packet,
            title="MiroFish Portfolio Readout",
        )
        content = f"""# MiroFish Portfolio

> Last updated: {timestamp}
> Canonical readout: `{readout_path.relative_to(_repo_root())}`

## Current Checkpoint

No saved markdown export was found, so this page was rendered directly from the latest portfolio readout packet.

{export_body}

## Links

- [[Lab Home]]
- [[Portfolio Dashboard]]
- [[MiroFish Frontier]]
- [[Trend Predictions]]
"""
        return {"path": "MiroFish Portfolio.md", "content": content}

    content = f"""# MiroFish Portfolio

> Last updated: {timestamp}

## Current Checkpoint

No saved MiroFish portfolio export or readout artifact was found under `research/meta/`.

## Next Step

- Generate a saved portfolio readout or export artifact before treating this page as the canonical MiroFish dashboard surface.

## Links

- [[Lab Home]]
- [[Portfolio Dashboard]]
- [[MiroFish Frontier]]
- [[Trend Predictions]]
"""
    return {"path": "MiroFish Portfolio.md", "content": content}


def _mirofish_frontier_page(timestamp: str) -> dict[str, Any]:
    """Generate the current MiroFish frontier checkpoint page."""
    shortlist_path = _latest_meta_file("MIROFISH_FRONTIER_SHORTLIST_*.md")
    if shortlist_path is not None and "_NOTE_" in shortlist_path.name:
        shortlist_candidates = [
            path
            for path in (_repo_root() / "research" / "meta").glob("MIROFISH_FRONTIER_SHORTLIST_*.md")
            if "_NOTE_" not in path.name
        ]
        shortlist_path = max(shortlist_candidates, key=lambda path: path.stat().st_mtime_ns) if shortlist_candidates else None
    export_path = _latest_meta_file("MIROFISH_FRONTIER_EXPORT_*.md")
    readout_path = _latest_meta_file("MIROFISH_FRONTIER_READOUT_*.json")
    compare_path = _latest_meta_file("MIROFISH_FRONTIER_CHECKPOINTS_*.html")

    compare_line = (
        f"> Local comparison page: `{compare_path.relative_to(_repo_root())}`"
        if compare_path is not None
        else "> Local comparison page: not generated yet"
    )
    shortlist_line = (
        f"> Canonical shortlist: `{shortlist_path.relative_to(_repo_root())}`"
        if shortlist_path is not None
        else "> Canonical shortlist: not generated yet"
    )

    if shortlist_path is not None and export_path is not None:
        shortlist_body = shortlist_path.read_text(encoding="utf-8").strip()
        export_body = export_path.read_text(encoding="utf-8").strip()
        content = f"""# MiroFish Frontier

> Last updated: {timestamp}
{shortlist_line}
> Canonical export: `{export_path.relative_to(_repo_root())}`
{compare_line}

## Current Frontier Shortlist

The page below is sourced from the latest saved MiroFish frontier shortlist artifact.

{shortlist_body}

## Full Frontier Checkpoint

The broader ranked frontier export is kept below for comparison and deeper review.

{export_body}

## Links

- [[Lab Home]]
- [[Portfolio Dashboard]]
- [[MiroFish Portfolio]]
- [[Trend Predictions]]
"""
        return {"path": "MiroFish Frontier.md", "content": content}

    if export_path is not None:
        export_body = export_path.read_text(encoding="utf-8").strip()
        content = f"""# MiroFish Frontier

> Last updated: {timestamp}
{shortlist_line}
> Canonical export: `{export_path.relative_to(_repo_root())}`
{compare_line}

## Current Frontier Checkpoint

The page below is sourced from the latest saved MiroFish frontier export artifact.

{export_body}

## Links

- [[Lab Home]]
- [[Portfolio Dashboard]]
- [[MiroFish Portfolio]]
- [[Trend Predictions]]
"""
        return {"path": "MiroFish Frontier.md", "content": content}

    if readout_path is not None:
        from ..mirofish.hybrid import format_frontier_readout_markdown

        readout_packet = json.loads(readout_path.read_text(encoding="utf-8"))
        export_body = format_frontier_readout_markdown(
            readout_packet,
            title="MiroFish Frontier Readout",
        )
        content = f"""# MiroFish Frontier

> Last updated: {timestamp}
> Canonical readout: `{readout_path.relative_to(_repo_root())}`
{compare_line}

## Current Frontier Checkpoint

No saved markdown export was found, so this page was rendered directly from the latest frontier readout packet.

{export_body}

## Links

- [[Lab Home]]
- [[Portfolio Dashboard]]
- [[MiroFish Portfolio]]
- [[Trend Predictions]]
"""
        return {"path": "MiroFish Frontier.md", "content": content}

    content = f"""# MiroFish Frontier

> Last updated: {timestamp}
{compare_line}

## Current Frontier Checkpoint

No saved MiroFish frontier export or readout artifact was found under `research/meta/`.

## Next Step

- Generate a saved frontier readout or export artifact before treating this page as the canonical MiroFish frontier surface.

## Links

- [[Lab Home]]
- [[Portfolio Dashboard]]
- [[MiroFish Portfolio]]
- [[Trend Predictions]]
"""
    return {"path": "MiroFish Frontier.md", "content": content}


def _agent_team_page(timestamp: str, mutations: dict[str, str]) -> dict[str, Any]:
    """Generate the agent team status page."""
    active_workstream = mutations.get("agent_workstream", "none")
    research_focus = mutations.get("research_focus", "none")

    content = f"""# Agent Team Status

> Last updated: {timestamp}

## Active Workstream

- **Current focus**: {research_focus}
- **Active agent**: {active_workstream}

## Workstream Status

| Agent | Status | Last Output |
|-------|--------|-------------|
| Frontier Scout | {"active" if active_workstream == "frontier_scout" else "standby"} | -- |
| Methodology Researcher | {"active" if active_workstream == "methodology_researcher" else "standby"} | -- |
| Chip Architect | {"active" if active_workstream == "chip_architect" else "standby"} | -- |
| Benchmark Engineer | {"active" if active_workstream == "benchmark_engineer" else "standby"} | -- |
| Integration Specialist | {"active" if active_workstream == "integration_specialist" else "standby"} | -- |
| Growth Analyst | {"active" if active_workstream == "growth_analyst" else "standby"} | -- |
| AGI Theorist | {"active" if active_workstream == "agi_theorist" else "standby"} | -- |

## Bottleneck Priority

_Updated by the suggest hook each pass._
"""
    return {"path": "Agent Team Status.md", "content": content}


def _graduation_pipeline_page(timestamp: str, chip_search_dir: str | Path | None) -> dict[str, Any]:
    """Generate the graduation pipeline page."""
    content = f"""# Graduation Pipeline

> Last updated: {timestamp}

## Graduation Criteria

- [ ] Working CLI with all 4 hooks (evaluate, suggest, packets, watchtower)
- [ ] One successful benchmark pack
- [ ] Output contract (schema + templates)
- [ ] Quality rubric score >= 60/100
- [ ] Evidence lane separation implemented
- [ ] At least 3 candidate trials defined
- [ ] Human approval obtained

## Current Candidates

_No graduation candidates yet. Lab prototypes will appear here when they meet initial criteria._

## Graduated Chips

_None yet. The first chip graduated from the lab will be tracked here._

## Pipeline Stages

```
Domain Brief -> Evidence Gathering -> Architecture Packet -> Scaffold -> Quality Gate -> Graduation Review
```
"""
    return {"path": "Graduation Pipeline.md", "content": content}


def _trend_predictions_page(timestamp: str) -> dict[str, Any]:
    """Generate the trend predictions page with MiroFish simulation data."""
    from ..trend_scanner import simulate_opportunities, SEED_OPPORTUNITIES
    from ..mirofish.report import format_report_markdown

    sim = simulate_opportunities(SEED_OPPORTUNITIES, seed=42)
    report = sim.get("simulation_report", {})
    report_md = format_report_markdown(report)

    content = f"""# Trend Predictions

> Last updated: {timestamp}
> Engine: MiroFish-inspired multi-agent simulation
> Evidence lane: exploratory_frontier

{report_md}

## How To Use This

1. **Do NOT auto-promote** these predictions to doctrine
2. Predictions are `exploratory_frontier` until replay-benchmarked
3. Use as input to the **suggest** hook for domain discovery candidates
4. Cross-reference with static scoring from trend_scanner for calibration

## Links

- [[Lab Home]]
- [[Portfolio Dashboard]]
- [[MiroFish Portfolio]]
- [[MiroFish Frontier]]
"""
    return {"path": "Trend Predictions.md", "content": content}


def _repo_root() -> Path:
    """Return the repository root from the watchtower module location."""
    return Path(__file__).resolve().parents[3]


def _latest_meta_file(pattern: str) -> Path | None:
    """Return the most recent matching research/meta artifact by modification time."""
    research_meta = _repo_root() / "research" / "meta"
    matches = list(research_meta.glob(pattern))
    if not matches:
        return None
    return max(matches, key=lambda path: path.stat().st_mtime_ns)
