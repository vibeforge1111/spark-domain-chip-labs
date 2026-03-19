# Lab Graduation Criteria

> When a lab prototype becomes a real chip.

---

## Overview

Graduation is the gate between "lab prototype" and "production chip." Not every prototype graduates. The criteria exist to ensure that only chips with demonstrated quality, evidence, and integration readiness enter the ecosystem.

Graduation requires **all 7 criteria** to pass. There are no partial graduations.

---

## The 7 Graduation Criteria

### Criterion 1: Working CLI

| Field | Value |
|-------|-------|
| Requirement | Chip has a functional CLI with init, evaluate, and report commands |
| Verification | Run each command with test inputs; all must complete without errors |
| Rationale | A chip that cannot be invoked is not a chip |

**What "working" means:**
- `init` -- initializes chip state from source registry
- `evaluate` -- runs the evaluate hook against provided inputs
- `report` -- produces a structured output report
- All commands handle errors gracefully (no unhandled exceptions)
- Commands respond within documented timeout bounds

---

### Criterion 2: Benchmark Pack

| Field | Value |
|-------|-------|
| Requirement | Chip ships with a benchmark pack containing test cases and expected baselines |
| Verification | Run benchmark pack; all test cases execute; results are within baseline bounds |
| Rationale | A chip without benchmarks cannot demonstrate or maintain quality |

**Benchmark pack structure:**
```yaml
benchmark_pack:
  version: "1.0"
  test_cases:
    - id: "tc-001"
      input: { ... }
      expected_baseline: { metric: "value" }
      tolerance: 0.05
  baseline_source: "description of how baseline was established"
  last_validated: "2024-01-15"
```

---

### Criterion 3: Output Contract

| Field | Value |
|-------|-------|
| Requirement | Chip defines a typed output contract that downstream consumers can rely on |
| Verification | Output schema validates against all benchmark pack outputs |
| Rationale | Chips in the ecosystem must have predictable interfaces |

**Contract requirements:**
- Schema definition (JSON Schema or equivalent)
- All fields typed and documented
- Required vs. optional fields declared
- Versioned (contract changes require version bump)
- Compatible with spark-swarm collective sync format

---

### Criterion 4: Quality Score >= 60

| Field | Value |
|-------|-------|
| Requirement | Chip scores at least 60/100 on the Lab Chip Quality Rubric |
| Verification | Run full rubric evaluation; total score must be >= 60 |
| Rationale | Minimum viable quality threshold for ecosystem participation |

**Score breakdown must show:**
- No dimension scoring 0 (every dimension must have some implementation)
- No critical failures in Manifest Validity or Integration Health
- Evidence Separation score >= 10/20 (must demonstrate evidence lane usage)

---

### Criterion 5: Evidence Lanes

| Field | Value |
|-------|-------|
| Requirement | Chip uses at least 2 of 4 evidence lanes with proper separation |
| Verification | Audit chip outputs; verify lane labels and source citations |
| Rationale | Evidence separation is the foundation of chip trustworthiness |

**Minimum evidence lane requirements:**

| Lane | Required? | Notes |
|------|-----------|-------|
| `research_grounded` | Yes | Must cite at least one source |
| `benchmark_grounded` | Yes | Must have at least one quantitative result |
| `exploratory_frontier` | Optional | If used, must be clearly labeled |
| `realworld_validated` | Optional | If used, must reference real usage |

---

### Criterion 6: 3+ Trials

| Field | Value |
|-------|-------|
| Requirement | Chip has been run through at least 3 evaluation trials with recorded results |
| Verification | Trial records exist with timestamps, inputs, outputs, and scores |
| Rationale | A single run proves nothing; consistency requires repeated trials |

**Trial record schema:**
```yaml
trial:
  id: "trial-001"
  timestamp: "2024-01-15T10:30:00Z"
  inputs: { ... }
  outputs: { ... }
  scores:
    primary_metric: 0.82
    secondary_metrics: { ... }
  notes: "string"
```

**Trial requirements:**
- Minimum 3 trials, not all on the same day
- At least 2 trials must pass the primary metric threshold
- Trial results must be persisted (not ephemeral)

---

### Criterion 7: Human Approval

| Field | Value |
|-------|-------|
| Requirement | A human reviewer has explicitly approved the chip for graduation |
| Verification | Approval record exists with reviewer identity and timestamp |
| Rationale | The lab cannot graduate chips autonomously -- this is a safety invariant |

**Approval record:**
```yaml
graduation_approval:
  reviewer: "human_identifier"
  approved_at: "2024-01-15T14:00:00Z"
  quality_score: 72
  notes: "Approved with recommendation to improve documentation"
  conditions: []  # Optional conditions for post-graduation improvement
```

**Human approval is non-negotiable.** No automation, no bypass, no exception. This is the lab's primary safety gate.

---

## Graduation Pipeline

A chip prototype moves through these stages on the path to graduation:

```
Domain Brief -> Evidence -> Architecture Packet -> Scaffold -> Quality Gate -> Graduation Review
```

### Stage Details

| Stage | Input | Output | Gate |
|-------|-------|--------|------|
| **Domain Brief** | Frontier Scout research | Structured domain assessment | Viability score > threshold |
| **Evidence** | Domain brief + source research | Populated evidence lanes | At least 2 lanes with content |
| **Architecture Packet** | Evidence + existing manifests | Complete chip design spec | Chip Architect review |
| **Scaffold** | Architecture packet | Working code with CLI | CLI commands execute |
| **Quality Gate** | Scaffolded chip | Rubric score + benchmark results | Score >= 60, all criteria met |
| **Graduation Review** | Quality gate report | Graduation approval/rejection | Human reviewer approval |

### Stage Transitions

```
Domain Brief ----[viability_check]----> Evidence
Evidence --------[lane_coverage]------> Architecture Packet
Architecture ----[design_review]------> Scaffold
Scaffold --------[cli_functional]-----> Quality Gate
Quality Gate ----[score_threshold]----> Graduation Review
Graduation ------[human_approval]----> Production Chip
```

### Failure Handling

| Stage | Failure | Recovery |
|-------|---------|----------|
| Domain Brief | Low viability score | Return to Frontier Scout for more research |
| Evidence | Insufficient sources | Expand source registry, re-research |
| Architecture | Design inconsistencies | Revise with Chip Architect |
| Scaffold | CLI failures | Fix implementation, re-test |
| Quality Gate | Score < 60 | Identify weakest dimensions, iterate |
| Graduation Review | Human rejection | Address reviewer feedback, re-submit |

---

## Post-Graduation

Graduation is not the end. Graduated chips are:

- Added to the chip portfolio monitored by the lab
- Subject to ongoing quality benchmarking (regression detection)
- Eligible for collective sync with spark-swarm
- Tracked by the Growth Analyst for adoption metrics

A graduated chip can be **demoted** if:
- Quality score drops below 50 in two consecutive benchmarks
- Critical integration failures are detected
- Evidence lane violations are discovered post-graduation

Demotion requires human approval, just like graduation.
