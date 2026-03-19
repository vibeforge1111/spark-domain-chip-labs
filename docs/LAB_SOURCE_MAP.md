# Lab Source Map

> The lab's source registry -- where intelligence comes from and how it flows back.

---

## Overview

The lab's source registry declares every source of information the lab consumes, how frequently it is refreshed, and how findings flow back as feedback. Sources are organized into primary (directly consumed every cycle), secondary (consulted on demand), and feedback loops (information flowing back from the lab's outputs).

---

## Primary Sources

These sources are consulted during every research refresh (always-on stage).

### spark-researcher Documentation

| Field | Value |
|-------|-------|
| Source ID | `src-spark-researcher` |
| Location | `spark-researcher/` repo docs |
| Refresh Cadence | Every cycle |
| Retrieval Path | Git pull, file read |

**What the lab extracts:**

| Document | What It Provides |
|----------|-----------------|
| Architecture docs | How chips are structured, lifecycle stages |
| Intelligence contract | Required hooks, evidence lanes, memory tiers |
| Chip manifest schema | Field definitions, validation rules |
| Evaluation methodology | How chips self-evaluate, metric requirements |

### spark-swarm Contracts and Architecture

| Field | Value |
|-------|-------|
| Source ID | `src-spark-swarm` |
| Location | `spark-swarm/` repo docs and contracts |
| Refresh Cadence | Every cycle |
| Retrieval Path | Git pull, file read |

**What the lab extracts:**

| Document | What It Provides |
|----------|-----------------|
| Collective sync protocol | How chips share insights |
| Evolution modes | Governance constraints per repo |
| Contradiction resolution | How disagreements are handled |
| Memory promotion paths | How insights move between tiers |
| Alpha validation | Stage gating and verdict systems |

### Existing Chip Manifests and Code

| Field | Value |
|-------|-------|
| Source ID | `src-chip-manifests` |
| Location | All graduated chip directories |
| Refresh Cadence | Every cycle |
| Retrieval Path | File system scan, manifest parsing |

**What the lab extracts:**

| Artifact | What It Provides |
|----------|-----------------|
| Chip manifests (YAML) | Structural patterns, field usage, hook implementations |
| Evaluate hooks | Evaluation approaches across domains |
| Source registries | What sources different domains use |
| Benchmark packs | How quality is measured per chip |
| Quality scores (historical) | Trends in chip quality over time |

---

## Secondary Sources

These sources are consulted on demand by specific workstreams.

### AI Research Papers

| Field | Value |
|-------|-------|
| Source ID | `src-ai-research` |
| Location | arxiv, conference proceedings |
| Refresh Cadence | Weekly (Frontier Scout), on demand (Methodology Researcher) |
| Retrieval Path | API query, PDF download |

**What the lab extracts:**

| Paper Type | What It Provides |
|-----------|-----------------|
| Survey papers | Domain landscape maps, key players, open problems |
| Benchmark papers | Evaluation methodologies, metric definitions, baselines |
| Methodology papers | Research approaches, experimental design patterns |
| Tool papers | Implementation patterns, architecture decisions |

### Evaluation Methodology Literature

| Field | Value |
|-------|-------|
| Source ID | `src-eval-methodology` |
| Location | ML evaluation research, testing literature |
| Refresh Cadence | Monthly (Methodology Researcher) |
| Retrieval Path | Literature search, citation following |

**What the lab extracts:**

| Topic | What It Provides |
|-------|-----------------|
| Metric design | How to choose and design evaluation metrics |
| Baseline construction | How to establish meaningful baselines |
| Statistical validity | How many trials, confidence intervals, significance |
| Grader agreement | How to validate that automated graders match human judgment |

### Community Signals

| Field | Value |
|-------|-------|
| Source ID | `src-community` |
| Location | GitHub, Product Hunt, X/Twitter, forums |
| Refresh Cadence | Daily (Frontier Scout), monthly (Growth Analyst) |
| Retrieval Path | API query, web scraping, manual monitoring |

**What the lab extracts:**

| Signal Type | What It Provides |
|------------|-----------------|
| Domain demand | Which domains practitioners are asking for help with |
| Pain points | Specific problems that could be addressed by chips |
| Tool landscape | What tools already exist in each domain |
| Adoption indicators | How existing chips are being received |

---

## Feedback Loops

Information flows not just into the lab but back out, creating closed loops that enable improvement.

### Chip Graduation Success/Failure

```
Lab produces chip prototype
       |
       v
  [Graduation Pipeline]
       |
   +---+---+
   |       |
Success  Failure
   |       |
   v       v
Positive   Failure analysis
signal     |
   |       v
   +-->  [Root cause identification]
              |
              v
         [Methodology update proposal]
              |
              v
         [Next chip benefits from fix]
```

| Feedback | Source | Consumer | Cadence |
|----------|--------|----------|---------|
| Graduation success | Graduation Review records | Methodology Researcher, Growth Analyst | Per graduation event |
| Graduation failure | Graduation Review records | Methodology Researcher, Benchmark Engineer | Per graduation event |
| Failure root causes | Failure analysis records | Chip Architect, Methodology Researcher | Per failure analysis |

### Quality Score Trends

```
Lab scores chips each cycle
       |
       v
  [Quality score time series]
       |
       v
  [Trend analysis]
       |
   +---+---+
   |       |
Improving  Degrading
   |       |
   v       v
Validate   Regression
method     investigation
   |       |
   v       v
  [Reinforce   [Fix root cause]
   practice]
```

| Feedback | Source | Consumer | Cadence |
|----------|--------|----------|---------|
| Score trends | Quality gate records | Benchmark Engineer, Watchtower | Per cycle |
| Regressions | Score drop detection | Benchmark Engineer, Methodology Researcher | On detection |
| Calibration data | Score-to-outcome correlation | Methodology Researcher | Quarterly |

### Collective Sync Health

```
Lab syncs with spark-swarm
       |
       v
  [Sync success/failure records]
       |
       v
  [Health analysis]
       |
   +---+---+
   |       |
Healthy  Unhealthy
   |       |
   v       v
Continue  Integration
as-is     investigation
              |
              v
         [Contract fix proposal]
```

| Feedback | Source | Consumer | Cadence |
|----------|--------|----------|---------|
| Sync health | Collective sync records | Integration Specialist | Per sync |
| Contract drift | Schema validation results | Integration Specialist | Per cycle |
| Adoption metrics | Sync consumption data | Growth Analyst | Monthly |

---

## Source Quality Assessment

Not all sources are equal. The lab tracks source quality over time.

| Quality Dimension | Measurement | Acceptable Threshold |
|-------------------|-------------|---------------------|
| Freshness | Days since last update | < 30 days for primary, < 90 days for secondary |
| Reliability | Retrieval success rate | > 95% for primary, > 80% for secondary |
| Relevance | Citation rate in promoted packets | > 10% of promoted packets cite this source |
| Coverage | % of chip domains covered | > 80% for primary, best-effort for secondary |

### Source Lifecycle

```
New source discovered
       |
       v
  [Candidate] -- evaluated for quality
       |
       v
  [Active] -- consulted per refresh cadence
       |
       v
  [Stale] -- quality drops below threshold
       |
   +---+---+
   |       |
Refresh   Retire
   |       |
   v       v
[Active]  [Archived]
```

---

## Source Registry Schema

```yaml
source_registry:
  version: "1.0"
  sources:
    - id: "src-spark-researcher"
      type: "primary"
      location: "spark-researcher/"
      refresh_cadence: "every_cycle"
      retrieval_method: "git_pull"
      quality:
        freshness_days: 0
        reliability_pct: 99
        relevance_pct: 85
      consumed_by: ["all_workstreams"]
      last_refreshed: "2024-01-15T10:00:00Z"

    - id: "src-ai-research"
      type: "secondary"
      location: "arxiv.org"
      refresh_cadence: "weekly"
      retrieval_method: "api_query"
      quality:
        freshness_days: 7
        reliability_pct: 90
        relevance_pct: 30
      consumed_by: ["frontier_scout", "methodology_researcher"]
      last_refreshed: "2024-01-14T10:00:00Z"
```

---

## Adding New Sources

New sources are added through the Frontier Scout workstream:

1. Scout identifies a potentially valuable source
2. Source is added as a candidate with quality metrics TBD
3. After 2 refresh cycles, quality metrics are computed
4. If quality meets thresholds, source is promoted to active
5. Source is registered in the source registry manifest

Removing sources follows the staleness detection process: if a source drops below quality thresholds for 3 consecutive checks, it is flagged for retirement and archived.
