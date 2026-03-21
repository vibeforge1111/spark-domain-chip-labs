"""Lab watchtower -- generates Obsidian pages for the lab observatory."""

from __future__ import annotations

from datetime import datetime, timezone
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
"""
    return {"path": "Portfolio Dashboard.md", "content": content}


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
"""
    return {"path": "Trend Predictions.md", "content": content}
