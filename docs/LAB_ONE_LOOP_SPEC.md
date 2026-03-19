# Lab One Loop Spec

> The lab's governing flywheel. One loop that routes to the right workstream based on the current bottleneck.

---

## Design Principle

The lab runs **one loop**, not seven. Every iteration of the loop executes a fixed set of always-on stages, then conditionally routes to the workstream that addresses the most pressing bottleneck.

This is not a cron job. It is a bottleneck-driven flywheel.

```
  +---> [ Always-On Stages ] ---+
  |                              |
  |    [ Bottleneck Detection ]  |
  |              |               |
  |    [ Conditional Stage ]     |
  |              |               |
  +--- [ Memory Update ] <------+
```

---

## Always-On Stages

These stages execute **every iteration**, regardless of which workstream is active.

### Stage 1: Research Refresh

| Field | Value |
|-------|-------|
| Purpose | Pull latest data from source registry |
| Duration | 30-60 seconds |
| Inputs | Source registry manifest, last refresh timestamp |
| Outputs | Updated source cache, change delta |
| Failure Mode | Stale data warning, continue with cached |

Activities:
- Check each registered source for updates since last refresh
- Pull new data into the local source cache
- Compute change delta for downstream stages
- Log refresh metrics (sources checked, data pulled, failures)

### Stage 2: Packet Quality Gate

| Field | Value |
|-------|-------|
| Purpose | Validate all pending packets against the quality rubric |
| Duration | 15-45 seconds |
| Inputs | Pending packets from previous cycle, quality rubric |
| Outputs | Scored packets, promotion/rejection decisions |
| Failure Mode | Packets held in pending, flagged for review |

Activities:
- Score each pending packet against the 100-point rubric
- Promote packets that meet threshold (>= 60/100)
- Reject packets with critical failures (evidence lane violations)
- Queue promoted packets for memory update

### Stage 3: Memory Update

| Field | Value |
|-------|-------|
| Purpose | Persist promoted packets and cycle state |
| Duration | 10-20 seconds |
| Inputs | Promoted packets, cycle metrics |
| Outputs | Updated memory store, cycle record |
| Failure Mode | Retry with backoff, alert on persistent failure |

Activities:
- Write promoted packets to the appropriate memory tier
- Update cycle counter and metrics
- Persist bottleneck detection state for next iteration
- Prune expired immediate-tier memories

### Stage 4: Watchtower Update

| Field | Value |
|-------|-------|
| Purpose | Update the lab's situational awareness dashboard |
| Duration | 5-10 seconds |
| Inputs | Cycle metrics, packet statuses, bottleneck state |
| Outputs | Updated watchtower state |
| Failure Mode | Stale watchtower, non-blocking |

Activities:
- Refresh portfolio coverage metrics
- Update quality trend indicators
- Flag anomalies (score drops, integration failures)
- Emit watchtower state for external consumers (spark-swarm)

---

## Bottleneck Detection

After always-on stages complete, the loop determines which conditional stage to execute.

### Detection Logic

```
priority_order = [
    ("portfolio_coverage_gap",   -> Domain Discovery),
    ("methodology_gap",          -> Methodology Research),
    ("design_gap",               -> Chip Architecture),
    ("quality_regression",       -> Quality Benchmarking),
    ("integration_drift",        -> Integration Check),
    ("demand_signal_gap",        -> Growth Analysis),
    ("periodic_15_pass",         -> Meta-Research),
]

for (signal, stage) in priority_order:
    if detected(signal):
        execute(stage)
        break
else:
    execute(Domain Discovery)  # default: look for new opportunities
```

### Signal Definitions

| Signal | Detection Rule | Priority |
|--------|---------------|----------|
| `portfolio_coverage_gap` | Domains with demand but no chip | 1 (highest) |
| `methodology_gap` | 3+ chip failures with shared root cause | 2 |
| `design_gap` | Domain brief at `research_grounded` with no architecture packet | 3 |
| `quality_regression` | Quality score drop > 10 points in any chip | 4 |
| `integration_drift` | Contract mismatch between lab and spark-researcher/swarm | 5 |
| `demand_signal_gap` | Adoption data older than 30 days | 6 |
| `periodic_15_pass` | 15 loop iterations since last meta-research | 7 (lowest) |

---

## Conditional Stages

Only **one** conditional stage executes per loop iteration.

### Domain Discovery

| Field | Value |
|-------|-------|
| Trigger | `portfolio_coverage_gap` |
| Workstream | Frontier Scout |
| Max Duration | 5 minutes |
| Output | Domain briefs (evidence lane: `exploratory_frontier`) |

### Methodology Research

| Field | Value |
|-------|-------|
| Trigger | `methodology_gap` |
| Workstream | Methodology Researcher |
| Max Duration | 10 minutes |
| Output | Rubric updates (evidence lane: `benchmark_grounded`) |

### Chip Architecture

| Field | Value |
|-------|-------|
| Trigger | `design_gap` |
| Workstream | Chip Architect |
| Max Duration | 10 minutes |
| Output | Architecture packets (evidence lane: `research_grounded`) |

### Quality Benchmarking

| Field | Value |
|-------|-------|
| Trigger | `quality_regression` |
| Workstream | Benchmark Engineer |
| Max Duration | 8 minutes |
| Output | Benchmark packs, regression reports |

### Integration Check

| Field | Value |
|-------|-------|
| Trigger | `integration_drift` |
| Workstream | Integration Specialist |
| Max Duration | 5 minutes |
| Output | Health reports, contract fixes |

### Growth Analysis

| Field | Value |
|-------|-------|
| Trigger | `demand_signal_gap` |
| Workstream | Growth Analyst |
| Max Duration | 5 minutes |
| Output | ROI assessments, priority rankings |

### Meta-Research

| Field | Value |
|-------|-------|
| Trigger | `periodic_15_pass` |
| Workstream | AGI Theorist |
| Max Duration | 10 minutes |
| Output | Transfer patterns, safety reports |

---

## Loop Constraints

| Constraint | Value | Rationale |
|------------|-------|-----------|
| Max iterations per pass | 8 | Bounded autonomy -- prevents runaway loops |
| Max conditional stage duration | 10 minutes | Prevents any single workstream from monopolizing |
| Always-on stage timeout | 2 minutes each | Ensures forward progress even with failures |
| Minimum cycle interval | 30 seconds | Prevents tight-loop resource exhaustion |
| Memory write retry limit | 3 | Fail fast on persistent storage issues |

---

## Cycle Record Schema

Every loop iteration produces a cycle record:

```yaml
cycle:
  id: "cycle-2024-001-042"
  iteration: 42
  started_at: "2024-01-15T10:30:00Z"
  completed_at: "2024-01-15T10:31:45Z"
  always_on:
    research_refresh: { sources_checked: 5, updates_found: 2, status: "ok" }
    packet_quality_gate: { pending: 3, promoted: 2, rejected: 1, status: "ok" }
    memory_update: { writes: 2, prunes: 0, status: "ok" }
    watchtower_update: { anomalies: 0, status: "ok" }
  bottleneck_detected: "design_gap"
  conditional_stage: "chip_architecture"
  conditional_output:
    packets_produced: 1
    evidence_lane: "research_grounded"
  next_bottleneck_hint: "quality_regression"
```

---

## Integration Points

| System | How the Loop Interacts |
|--------|----------------------|
| spark-researcher | Consumes architecture packets and methodology updates via source registry |
| spark-swarm | Receives watchtower updates and promoted packets via collective sync |
| Quality rubric | Used by Packet Quality Gate (always-on) and Benchmark Engineer (conditional) |
| Source registry | Read by Research Refresh (always-on) and Frontier Scout (conditional) |
| Memory backend | Written by Memory Update (always-on), read by all workstreams |
