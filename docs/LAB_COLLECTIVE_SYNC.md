# Lab Collective Sync

> How lab intelligence flows to spark-swarm.

---

## Overview

The lab participates in spark-swarm as a specialized chip -- specifically, a "chip-research" specialization. It does not have elevated privileges. It follows the same collective sync protocol as every other chip in the swarm.

What makes the lab different is not its authority but its focus: it researches how to build better chips, while other chips research their own domains.

---

## The Lab as a Chip Specialization

### Identity in spark-swarm

```yaml
specialization:
  id: "chip-research"
  type: "meta-research"
  domain: "chip building methodology"
  evolution_mode: "guarded"  # lab proposes, owner approves
  memory_policy: "selective"  # not everything the lab learns goes to the swarm
```

### Selective Memory Policy

The lab produces a lot of internal state: cycle records, bottleneck signals, intermediate scores, draft packets. Most of this is internal noise that would pollute the swarm's collective memory.

The selective memory policy means:
- Only **promoted packets** (those passing the quality gate) are eligible for sync
- Only packets relevant to **other chips** are actually synced
- Internal methodology debates stay internal until resolved
- Cycle metrics are available for querying but not actively pushed

---

## What Gets Synced

The lab emits four types of content to spark-swarm.

### 1. Insights (Methodology Discoveries)

**What:** Proven practices discovered through methodology research.

**When synced:** After human approval of a methodology change.

**Format:**
```yaml
sync_type: "insight"
content:
  discovery: "Chips with 3+ evaluation metrics have 40% fewer regressions"
  evidence_lane: "benchmark_grounded"
  evidence:
    - source: "cross-chip regression analysis, Q1 2024"
      data: "12 chips analyzed, correlation r=0.73"
  applicability: "all chips with evaluate hooks"
  promotion_status: "promoted"
```

**Consumed by:** All chips during their evaluate hook design.

### 2. Masteries (Proven Chip-Building Practices)

**What:** Chip-building practices that have been validated across multiple graduations.

**When synced:** After a practice contributes to 3+ successful graduations.

**Format:**
```yaml
sync_type: "mastery"
content:
  practice: "Source registry with declared refresh cadence"
  validation_count: 5
  graduation_ids: ["grad-001", "grad-002", "grad-003", "grad-004", "grad-005"]
  impact: "Chips with refresh cadence have 60% fresher data"
  evidence_lane: "realworld_validated"
  promotion_status: "promoted"
```

**Consumed by:** Chip Architect workstream and any chip undergoing redesign.

### 3. Contradictions (Disagreements Between Chips)

**What:** Cases where two chips or the lab and a chip disagree on something.

**When synced:** Immediately upon detection of a warning or critical contradiction.

**Format:**
```yaml
sync_type: "contradiction"
content:
  severity: "warning"  # advisory | warning | critical
  domain_a: "chip-research"
  claim_a: "Evaluation baselines should use null models"
  domain_b: "ml-ops"
  claim_b: "Evaluation baselines should use previous version"
  resolution_status: "unresolved"
  evidence:
    - lane: "benchmark_grounded"
      data: "Both approaches have merit in different contexts"
```

**Consumed by:** The affected chips and human reviewers.

### 4. Upgrades (Improvements to Chip Standards)

**What:** Proposed changes to chip standards, contracts, or interfaces.

**When synced:** After human approval, before execution.

**Format:**
```yaml
sync_type: "upgrade"
content:
  target: "intelligence_contract"
  change: "Add required 'refresh_cadence' field to source_registry schema"
  rationale: "Analysis shows chips without refresh cadence have 3x stale data rate"
  evidence_lane: "benchmark_grounded"
  breaking: false  # does this break existing chips?
  migration_path: "Add field with default value 'weekly'"
  approval_status: "approved"
  approved_by: "human_reviewer_id"
```

**Consumed by:** All chips, via spark-swarm upgrade propagation.

---

## Compatibility with Existing Specializations

The lab's chip-research specialization is designed to coexist with all existing chip specializations. It does not conflict because:

| Property | Lab Specialization | Other Specializations |
|----------|-------------------|----------------------|
| Domain | Chip building methodology | Their specific domain |
| Output type | Methodology packets | Domain insights |
| Memory scope | Cross-chip patterns | Domain-specific knowledge |
| Authority | Same as any chip | Same as any chip |
| Sync protocol | Standard collective sync | Standard collective sync |

### No Special Privileges

The lab uses the exact same collective sync API as every other chip. It cannot:
- Force other chips to accept its insights
- Override another chip's memory
- Bypass evolution mode constraints
- Push upgrades without going through the standard approval flow

---

## AUTORESEARCH.md Manifest Design

The lab's integration with spark-swarm is configured through an `AUTORESEARCH.md` manifest that declares the lab's research parameters.

### Manifest Structure

```markdown
# AUTORESEARCH.md

## Research Identity
- specialization: chip-research
- domain: chip building methodology
- evolution_mode: guarded

## Source Registry
- spark-researcher: architecture docs, intelligence contract
- spark-swarm: collective sync protocol, evolution modes
- chip-manifests: all graduated chip manifests

## Sync Policy
- emit: insights, masteries, contradictions, upgrades
- receive: chip performance data, integration health, domain signals
- frequency: per-cycle (always-on stages) + on-demand (conditional stages)

## Memory Policy
- promote: packets scoring >= 60/100
- sync: promoted packets with cross-chip relevance
- retain: all cycle records internally
- prune: immediate-tier memories after 7 days

## Quality Gate
- minimum_score: 60/100
- evidence_lanes_required: 2
- human_gate: graduation, methodology changes, upgrades

## Bounds
- max_iterations: 8
- max_stage_duration: 10m
- self_edit: proposal-first
```

### How Other Chips Discover the Lab

Other chips can discover the lab through spark-swarm's standard discovery mechanism:

1. Query the swarm registry for specialization `chip-research`
2. Read the lab's AUTORESEARCH.md for sync policy
3. Subscribe to relevant sync types (insights, masteries, upgrades)
4. Receive updates through standard collective sync channels

---

## Sync Protocol Details

### Outbound Sync (Lab -> Swarm)

```
Lab produces packet
       |
       v
  [Quality Gate]
  Score >= 60? Evidence lanes valid?
       |
   +---+---+
   |       |
  Yes      No
   |       |
   v       v
  [Cross-chip    [Internal only]
   relevance?]
       |
   +---+---+
   |       |
  Yes      No
   |       |
   v       v
  [Sync to    [Internal only]
   swarm]
```

### Inbound Sync (Swarm -> Lab)

The lab receives from the swarm:

| Data Type | Used By | Purpose |
|-----------|---------|---------|
| Chip performance data | Benchmark Engineer | Track quality trends |
| Integration health | Integration Specialist | Detect contract drift |
| Domain signals | Frontier Scout | Discover new opportunities |
| Contradiction reports | Methodology Researcher | Identify methodology gaps |
| Evolution mode changes | All workstreams | Adjust behavior constraints |

### Sync Frequency

| Sync Type | Frequency |
|-----------|-----------|
| Outbound insights/masteries | Per cycle (when produced) |
| Outbound contradictions | Immediate (on detection) |
| Outbound upgrades | On human approval |
| Inbound performance data | Per cycle (research refresh) |
| Inbound health data | Per cycle (watchtower update) |
| Inbound evolution changes | On change (event-driven) |

---

## Failure Handling

| Failure | Response |
|---------|----------|
| Swarm unreachable | Queue outbound syncs locally, retry on next cycle |
| Inbound data stale | Use cached data, log staleness warning |
| Contradiction during sync | Block the conflicting packet, surface for review |
| Schema mismatch | Log integration drift, trigger Integration Specialist |
| Evolution mode conflict | Respect the more restrictive mode, log the conflict |
