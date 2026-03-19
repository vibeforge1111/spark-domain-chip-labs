# Lab Research Packet

> Lab packet schema -- the standard unit of lab output.

---

## Overview

Everything the lab produces is a **packet**. Packets are typed, evidence-tagged, and tracked through a promotion pipeline. They are the standard unit of communication within the lab, between the lab and spark-swarm, and between the lab and human reviewers.

This document defines the five packet kinds, their schemas, and how evidence lanes map to promotion paths.

---

## Packet Base Schema

Every packet shares these common fields.

```yaml
packet:
  id: "pkt-2024-001-042"          # Unique identifier
  packet_kind: "string"           # One of 5 kinds (see below)
  evidence_lane: "string"         # research_grounded | benchmark_grounded | exploratory_frontier | realworld_validated
  created_at: "2024-01-15T10:30:00Z"
  created_by: "string"           # Workstream that produced this packet
  content: { ... }               # Kind-specific content (see below)
  promotion_status: "string"     # draft | pending | promoted | rejected | archived
  quality_score: null             # Populated by quality gate (0-100)
  cycle_id: "cycle-2024-001-042" # Which cycle produced this packet
  metadata:
    version: "1.0"
    tags: []                     # Searchable tags
    related_packets: []          # Cross-references to other packets
```

### Promotion Status Lifecycle

```
  [draft]
     |
     v
  [pending] -- submitted to quality gate
     |
  +--+--+
  |     |
  v     v
[promoted]  [rejected]
  |            |
  v            v
[archived]  [archived]
  (after     (after
   expiry)    review)
```

| Status | Meaning |
|--------|---------|
| `draft` | Being worked on by a workstream, not yet submitted |
| `pending` | Submitted to the quality gate, awaiting scoring |
| `promoted` | Passed quality gate (score >= 60), eligible for sync/memory |
| `rejected` | Failed quality gate, returned with feedback |
| `archived` | No longer active (expired, superseded, or reviewed rejection) |

---

## Packet Kind 1: methodology_doctrine

**Purpose:** Proven chip-building practices that should be followed by all chips.

**Produced by:** Methodology Researcher

**Evidence lane:** `benchmark_grounded` (must be backed by quantitative analysis)

```yaml
packet_kind: "methodology_doctrine"
content:
  doctrine_id: "doc-001"
  title: "Evaluation metrics minimum count"
  statement: "Chips should define at least 3 evaluation metrics covering different quality dimensions"
  evidence:
    - type: "cross_chip_analysis"
      data: "Chips with 3+ metrics show 40% fewer regressions (n=12, r=0.73)"
      source: "lab benchmark analysis Q1 2024"
    - type: "literature_review"
      data: "Multi-metric evaluation is standard practice in ML benchmarking"
      source: "arxiv:2301.xxxxx"
  applicability: "all chips with evaluate hooks"
  supersedes: null  # doctrine_id of any previous version
  validation_count: 5  # number of chips where this was validated
```

**Promotion path:** `draft` -> `pending` -> quality gate -> human approval -> `promoted` -> sync to spark-swarm as `mastery`

---

## Packet Kind 2: domain_opportunity

**Purpose:** Researched domain briefs describing potential new chip domains.

**Produced by:** Frontier Scout

**Evidence lane:** `exploratory_frontier` (initial discovery) or `research_grounded` (after validation)

```yaml
packet_kind: "domain_opportunity"
content:
  domain: "infrastructure-as-code"
  composite_score: 7.15
  dimension_scores:
    market_size: 7
    data_availability: 8
    benchmark_feasibility: 6
    community_demand: 9
    spark_ecosystem_fit: 7
    monetization_potential: 5
  sources_consulted:
    - type: "github"
      url: "https://github.com/trending?q=iac"
      signal: "3 new IaC tools trending in past 2 weeks"
    - type: "twitter"
      query: "#infrastructureascode pain points"
      signal: "Recurring complaints about drift detection"
    - type: "arxiv"
      papers: ["2401.xxxxx"]
      signal: "New benchmark for IaC correctness evaluation"
  validation:
    first_detected: "2024-01-01"
    first_checkpoint: "2024-01-07"
    second_checkpoint: "2024-01-14"
    sustained: true
  portfolio_gap: "No existing chip covers IaC domain"
  recommended_action: "proceed_to_architecture"
```

**Promotion path:** `draft` -> `pending` -> quality gate -> `promoted` -> triggers Chip Architect workstream

---

## Packet Kind 3: quality_assessment

**Purpose:** Portfolio-wide quality health reports.

**Produced by:** Benchmark Engineer

**Evidence lane:** `benchmark_grounded`

```yaml
packet_kind: "quality_assessment"
content:
  assessment_type: "portfolio_health"  # portfolio_health | chip_regression | rubric_calibration
  scope: "all_graduated_chips"
  timestamp: "2024-01-15T10:00:00Z"
  summary:
    total_chips: 12
    average_score: 71.5
    median_score: 73
    min_score: 52
    max_score: 91
  distribution:
    grade_a: 2  # 90-100
    grade_b: 3  # 80-89
    grade_c: 4  # 70-79
    grade_d: 2  # 60-69
    grade_f: 1  # 40-59
  regressions:
    - chip_id: "ml-ops"
      previous_score: 78
      current_score: 67
      delta: -11
      likely_cause: "Source registry staleness"
  trends:
    improving: ["data-engineering", "devops"]
    stable: ["security", "frontend"]
    degrading: ["ml-ops"]
  recommendations:
    - target: "ml-ops"
      action: "Refresh source registry, re-run benchmarks"
      priority: "high"
```

**Promotion path:** `draft` -> `pending` -> quality gate -> `promoted` -> sync to spark-swarm as `insight` (if cross-chip relevant)

---

## Packet Kind 4: transfer_pattern

**Purpose:** Cross-chip findings -- patterns that transfer between domains.

**Produced by:** AGI Theorist

**Evidence lane:** `research_grounded` or `benchmark_grounded`

```yaml
packet_kind: "transfer_pattern"
content:
  pattern_id: "xfer-001"
  title: "Source freshness correlates with evaluation reliability"
  pattern_type: "methodology_transfer"  # methodology | source | evaluation | architecture | failure
  description: "Chips with source registries refreshed within 7 days show 2x more reliable evaluation scores compared to chips with 30+ day stale sources"
  evidence:
    - type: "cross_chip_correlation"
      chips_analyzed: ["data-engineering", "ml-ops", "devops", "security"]
      correlation: 0.68
      confidence: "medium"
      source: "lab benchmark analysis, 15 cycles"
  transferable_to: "all chips with source registries"
  actionable_recommendation: "Set source refresh cadence to weekly or more frequent"
  safety_note: "Pattern observed in 4 chips; may not generalize to all domains"
  related_patterns: []
```

**Promotion path:** `draft` -> `pending` -> quality gate -> human review (for safety note) -> `promoted` -> sync to spark-swarm as `insight`

---

## Packet Kind 5: graduation_candidate

**Purpose:** Prototypes ready for graduation review.

**Produced by:** Chip Architect (design) + Benchmark Engineer (validation)

**Evidence lane:** `realworld_validated` (must have trial results)

```yaml
packet_kind: "graduation_candidate"
content:
  chip_id: "infrastructure-as-code"
  chip_name: "Infrastructure as Code"
  version: "0.1.0"
  graduation_criteria:
    working_cli: true
    benchmark_pack: true
    output_contract: true
    quality_score: 72
    quality_threshold_met: true  # >= 60
    evidence_lanes_used: ["research_grounded", "benchmark_grounded"]
    evidence_lanes_met: true    # >= 2 lanes
    trial_count: 4
    trials_met: true            # >= 3 trials
    human_approval: false       # pending
  trial_results:
    - trial_id: "trial-001"
      timestamp: "2024-01-10T10:00:00Z"
      primary_metric: 0.78
      passed: true
    - trial_id: "trial-002"
      timestamp: "2024-01-12T14:00:00Z"
      primary_metric: 0.81
      passed: true
    - trial_id: "trial-003"
      timestamp: "2024-01-13T09:00:00Z"
      primary_metric: 0.75
      passed: true
    - trial_id: "trial-004"
      timestamp: "2024-01-14T16:00:00Z"
      primary_metric: 0.83
      passed: true
  rubric_breakdown:
    manifest_validity: 13
    evidence_separation: 15
    evaluation_depth: 14
    memory_knowledge: 11
    integration_health: 10
    documentation: 9
  blockers: []
  reviewer_notes: "Documentation score is low; recommend improving before graduation"
```

**Promotion path:** `draft` -> `pending` -> quality gate (score >= 60) -> human graduation review -> `promoted` (becomes a production chip)

---

## Evidence Lanes and Promotion Paths

Each evidence lane has different rules for what can be promoted and how.

| Evidence Lane | Can Be Promoted? | Promotion Requires | Typical Destination |
|---------------|-----------------|--------------------|--------------------|
| `research_grounded` | Yes | Source citations, retrieval paths | Memory tier: seasonal |
| `benchmark_grounded` | Yes | Quantitative data, reproducible methodology | Memory tier: seasonal or identity |
| `exploratory_frontier` | Conditionally | Must be validated first (move to another lane) | Memory tier: situational (temporary) |
| `realworld_validated` | Yes | Real usage context, outcome documentation | Memory tier: identity |

### The Frontier-to-Grounded Transition

Exploratory frontier packets cannot be directly promoted to high-tier memory. They must first be validated and re-tagged:

```
[exploratory_frontier packet]
       |
       v
  [Validation activity]
  (benchmark, real-world trial, source confirmation)
       |
   +---+---+
   |       |
Validated  Not validated
   |       |
   v       v
Re-tag as  Remains
grounded   exploratory
lane       (or archived)
```

---

## Packet Storage and Retrieval

### Storage

Packets are stored in the lab's memory backend:

| Tier | What Goes Here | Retention |
|------|---------------|-----------|
| Immediate | Draft packets, in-progress work | 7 days |
| Situational | Pending and recently promoted packets | 30 days |
| Seasonal | Promoted packets with ongoing relevance | 1 year |
| Identity | Methodology doctrines, core transfer patterns | Indefinite |

### Retrieval

Packets can be retrieved by:
- `packet_kind` -- get all packets of a specific kind
- `evidence_lane` -- get all packets in a specific lane
- `promotion_status` -- get pending, promoted, or rejected packets
- `created_by` -- get all packets from a specific workstream
- `cycle_id` -- get all packets from a specific cycle
- `tags` -- full-text search across packet tags
- `related_packets` -- follow cross-references

### Packet Lifecycle Metrics

| Metric | What It Measures |
|--------|-----------------|
| Time to promotion | How long from draft to promoted |
| Rejection rate | % of pending packets rejected by quality gate |
| Promotion rate | % of pending packets promoted |
| Sync rate | % of promoted packets synced to spark-swarm |
| Citation count | How many other packets reference this one |
| Archival rate | % of packets archived before expiry (superseded) |
