# Lab Agent Team

> 7 researcher workstreams -- not separate processes, but routing within one flywheel.

---

## Architecture: One Loop, Many Workstreams

The lab does not run 7 independent agents. It runs **one loop** that routes to the right workstream based on the current bottleneck. Each workstream is a specialization of attention, not a separate process.

Think of it as one researcher who wears 7 hats, switching based on what the ecosystem needs most right now.

```
[ Bottleneck Detection ]
        |
        v
  +-----+-----+-----+-----+-----+-----+-----+
  | FS  | MR  | CA  | BE  | IS  | GA  | AT  |
  +-----+-----+-----+-----+-----+-----+-----+
        |
        v
  [ Packet Output -> Memory -> Next Cycle ]
```

---

## Workstream 1: Frontier Scout

**Purpose:** Discovers new domain opportunities before they become obvious.

| Field | Value |
|-------|-------|
| Trigger | `portfolio_coverage_gap` -- when the chip portfolio has blind spots |
| Sources | GitHub trending, Product Hunt launches, X/Twitter communities, arxiv preprints |
| Output | **Domain briefs** -- structured assessments of domain viability |
| Evidence Lane | `exploratory_frontier` |
| Cadence | Continuous scan, deep dive on signal |

**Key Activities:**
- Scan source channels for emerging domain signals
- Score opportunities using the trend methodology framework
- Filter hype from sustained demand (2+ week signal rule)
- Produce domain briefs with market size, data availability, and ecosystem fit

**Hands Off To:** Chip Architect (when a domain brief reaches `research_grounded`)

---

## Workstream 2: Methodology Researcher

**Purpose:** Improves the chip-building methodology itself -- the meta-research function.

| Field | Value |
|-------|-------|
| Trigger | `methodology_gap` -- when chip validation failures reveal process issues |
| Sources | Chip validation failures, cross-chip analysis, quality score trends |
| Output | **Rubric updates** -- improvements to evaluation criteria and building practices |
| Evidence Lane | `benchmark_grounded` |
| Cadence | Triggered by failure patterns or periodic review |

**Key Activities:**
- Analyze patterns in chip quality scores over time
- Identify systematic weaknesses in the chip-building process
- Propose rubric updates with evidence from failure analysis
- Cross-reference methodology against AI evaluation research

**Hands Off To:** Benchmark Engineer (to validate rubric changes against existing chips)

---

## Workstream 3: Chip Architect

**Purpose:** Designs new chip manifests from researched domain briefs.

| Field | Value |
|-------|-------|
| Trigger | Domain brief reaches `research_grounded` status |
| Sources | Existing chip manifests, master chip architect prompt, domain brief |
| Output | **Architecture packets** -- complete chip design specifications |
| Evidence Lane | `research_grounded` |
| Cadence | On demand, driven by Frontier Scout output |

**Key Activities:**
- Translate domain briefs into chip manifest structures
- Define source registries, evaluate hooks, and memory schemas
- Ensure consistency with existing chip patterns
- Produce scaffold-ready architecture packets

**Hands Off To:** Benchmark Engineer (to create quality benchmarks for the new chip)

---

## Workstream 4: Benchmark Engineer

**Purpose:** Creates and maintains quality benchmarks for chips.

| Field | Value |
|-------|-------|
| Trigger | Periodic schedule + regression detection |
| Sources | Chip outputs, quality rubric, historical benchmark data |
| Output | **Benchmark packs** -- test suites; **Regression reports** -- quality trend analysis |
| Evidence Lane | `benchmark_grounded` |
| Cadence | Periodic (weekly) + event-driven (new chip, rubric change) |

**Key Activities:**
- Design benchmark test cases for each chip domain
- Run quality assessments against the rubric
- Detect regressions in chip performance over time
- Produce benchmark packs that chips can self-evaluate against

**Hands Off To:** Integration Specialist (when benchmarks reveal compatibility issues)

---

## Workstream 5: Integration Specialist

**Purpose:** Ensures compatibility between the lab, spark-researcher, and spark-swarm.

| Field | Value |
|-------|-------|
| Trigger | `integration_gap` -- when contracts or interfaces drift |
| Sources | spark-researcher contracts, spark-swarm architecture, chip manifests |
| Output | **Health reports** -- integration status; **Contract fixes** -- proposed updates |
| Evidence Lane | `realworld_validated` |
| Cadence | After every collective sync + on contract change |

**Key Activities:**
- Monitor spark-researcher intelligence contract compliance
- Verify spark-swarm collective sync compatibility
- Detect interface drift between lab outputs and consumer expectations
- Propose contract fixes that maintain backward compatibility

**Hands Off To:** Methodology Researcher (when integration issues reveal methodology gaps)

---

## Workstream 6: Growth Analyst

**Purpose:** Tracks ecosystem adoption and prioritizes chip development by demand.

| Field | Value |
|-------|-------|
| Trigger | `growth_signal_gap` -- when adoption data is stale or missing |
| Sources | Chip usage metrics, community feedback, market signals |
| Output | **ROI assessments** -- domain investment analysis; **Priority rankings** -- ordered backlog |
| Evidence Lane | `realworld_validated` |
| Cadence | Monthly review + event-driven (new market signal) |

**Key Activities:**
- Track which chips are being adopted and how
- Assess ROI of chip development investment per domain
- Rank domain opportunities by demand-weighted priority
- Identify underserved domains with high community demand

**Hands Off To:** Frontier Scout (to investigate high-priority domains)

---

## Workstream 7: AGI Theorist

**Purpose:** Studies recursive self-improvement patterns and transfer learning across chips.

| Field | Value |
|-------|-------|
| Trigger | Every 15 passes through the flywheel + transfer events |
| Sources | Cross-chip performance data, methodology evolution history, transfer patterns |
| Output | **Transfer patterns** -- cross-domain insights; **Safety reports** -- recursive improvement analysis |
| Evidence Lane | `exploratory_frontier` |
| Cadence | Every 15 loop iterations + on significant transfer events |

**Key Activities:**
- Analyze how improvements in one chip domain transfer to others
- Study the lab's own improvement trajectory over time
- Document recursive improvement patterns with evidence
- Produce safety reports on self-modification scope and bounds
- Ensure human oversight gates remain intact

**Hands Off To:** Methodology Researcher (when transfer patterns suggest methodology updates)

---

## Workstream Routing Summary

| Bottleneck Detected | Routes To | Primary Output |
|---------------------|-----------|----------------|
| Portfolio coverage gap | Frontier Scout | Domain briefs |
| Methodology gap | Methodology Researcher | Rubric updates |
| Design gap | Chip Architect | Architecture packets |
| Quality regression | Benchmark Engineer | Benchmark packs |
| Integration drift | Integration Specialist | Health reports |
| Demand signal gap | Growth Analyst | Priority rankings |
| Periodic (every 15) | AGI Theorist | Transfer patterns |

---

## Collaboration Pattern

Workstreams are not siloed. They hand off to each other through the flywheel:

```
Frontier Scout -> Chip Architect -> Benchmark Engineer
                                         |
Growth Analyst <-- Integration Specialist <-+
       |
       v
Frontier Scout (next cycle)

Methodology Researcher <-> AGI Theorist (cross-cutting)
```

Every handoff produces a typed packet. Every packet flows through the memory system. The flywheel never stops -- it just changes which workstream gets attention.
