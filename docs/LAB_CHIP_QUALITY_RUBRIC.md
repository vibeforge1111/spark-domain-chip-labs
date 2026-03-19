# Lab Chip Quality Rubric

> Complete 100-point rubric for evaluating domain chip quality.

---

## Overview

Every chip produced by or evaluated by the lab is scored against this rubric. The rubric measures six dimensions of chip quality, totaling 100 points. A chip must score **>= 60** to pass the quality gate.

| Dimension | Points | Weight |
|-----------|--------|--------|
| Manifest Validity | 15 | 15% |
| Evidence Separation | 20 | 20% |
| Evaluation Depth | 20 | 20% |
| Memory & Knowledge | 15 | 15% |
| Integration Health | 15 | 15% |
| Documentation | 15 | 15% |
| **Total** | **100** | **100%** |

---

## Dimension 1: Manifest Validity (15 points)

Does the chip have a valid, complete manifest that follows the protocol?

| Criterion | Points | Pass | Fail |
|-----------|--------|------|------|
| Schema compliance | 3 | Manifest parses against chip schema without errors | Parse errors or missing required fields |
| Protocol hooks | 3 | All required protocol hooks defined (init, evaluate, report) | Missing hooks or stub-only implementations |
| Frontier definition | 2 | Clear frontier boundary: what the chip knows vs. explores | No frontier defined or frontier is trivially broad |
| Required fields | 3 | All required fields present: id, name, domain, version, sources | Missing any required field |
| Pattern declarations | 2 | Declares which patterns the chip implements | No pattern declarations |
| Hook signatures | 2 | Hook signatures match the intelligence contract | Signature mismatches |

### Scoring Guide

| Score Range | Interpretation |
|-------------|---------------|
| 13-15 | Production-ready manifest |
| 10-12 | Minor issues, fixable without redesign |
| 7-9 | Structural problems requiring revision |
| 0-6 | Fundamental manifest issues |

---

## Dimension 2: Evidence Separation (20 points)

Does the chip properly separate evidence by lane?

| Criterion | Points | Pass | Fail |
|-----------|--------|------|------|
| `research_grounded` lane | 5 | Claims backed by cited sources with retrieval paths | Unsourced claims in research lane |
| `benchmark_grounded` lane | 5 | Quantitative results from reproducible evaluations | Qualitative-only or unreproducible results |
| `exploratory_frontier` lane | 5 | Clearly labeled as exploratory, not presented as proven | Frontier claims mixed with grounded evidence |
| `realworld_validated` lane | 5 | Evidence from production use or user feedback | No real-world validation attempted |

### Evidence Lane Rules

```
research_grounded:
  - Must cite source (URL, paper, dataset)
  - Must have retrieval path (how to re-find this)
  - Must not mix with exploratory claims

benchmark_grounded:
  - Must include methodology (how measured)
  - Must include baseline (compared against what)
  - Must be reproducible (same inputs -> same outputs)

exploratory_frontier:
  - Must be labeled "exploratory" or "frontier"
  - Must not be promoted to memory without validation
  - Must include confidence level (low/medium/high)

realworld_validated:
  - Must reference real usage context
  - Must include outcome (what happened)
  - Must note sample size or scope
```

### Scoring Guide

| Score Range | Interpretation |
|-------------|---------------|
| 17-20 | Rigorous evidence separation across all lanes |
| 13-16 | Good separation with minor lane mixing |
| 8-12 | Evidence exists but lanes are poorly separated |
| 0-7 | No meaningful evidence separation |

---

## Dimension 3: Evaluation Depth (20 points)

Does the chip evaluate its own outputs meaningfully?

| Criterion | Points | Pass | Fail |
|-----------|--------|------|------|
| Primary metric defined | 4 | One clear primary metric with measurement method | No primary metric or vague definition |
| Multiple metrics | 4 | 3+ metrics covering different quality dimensions | Single metric or fewer than 3 |
| Scoring logic | 4 | Deterministic scoring function, not subjective | "Looks good" or purely human judgment |
| Candidate trials | 4 | 3+ trial runs with recorded results | Fewer than 3 trials or unrecorded results |
| Baseline comparison | 4 | Results compared against a defined baseline | No baseline or comparison against nothing |

### Evaluation Requirements

```yaml
evaluate_hook:
  primary_metric:
    name: "string"          # e.g., "accuracy", "relevance_score"
    measurement: "string"   # How to compute it
    threshold: "number"     # Minimum acceptable value

  secondary_metrics:        # At least 2 additional
    - name: "string"
      measurement: "string"

  scoring:
    function: "deterministic"  # Must be reproducible
    inputs: ["defined"]        # All inputs specified
    output: "numeric"          # Numeric score, not pass/fail only

  trials:
    minimum: 3
    recorded: true             # Results persisted
    reproducible: true         # Same inputs -> same score

  baseline:
    type: "string"             # "previous_version" | "null_model" | "human_expert"
    value: "number"            # Baseline score to beat
```

### Scoring Guide

| Score Range | Interpretation |
|-------------|---------------|
| 17-20 | Rigorous self-evaluation with strong baselines |
| 13-16 | Good evaluation, minor gaps in trials or metrics |
| 8-12 | Basic evaluation present but shallow |
| 0-7 | No meaningful self-evaluation |

---

## Dimension 4: Memory & Knowledge (15 points)

Does the chip manage knowledge properly?

| Criterion | Points | Pass | Fail |
|-----------|--------|------|------|
| Source registry | 3 | Declared sources with refresh cadence and retrieval paths | No source registry or sources without paths |
| Packet schema | 3 | Outputs conform to a typed packet schema | Unstructured or untyped outputs |
| Watchtower integration | 3 | Emits watchtower-compatible state updates | No watchtower integration |
| Obsidian vault compatibility | 3 | Knowledge exportable to Obsidian-compatible markdown | Proprietary format only |
| Memory backend | 3 | Uses tiered memory (immediate/situational/seasonal/identity) | Flat memory or no persistence |

### Scoring Guide

| Score Range | Interpretation |
|-------------|---------------|
| 13-15 | Full knowledge management pipeline |
| 10-12 | Good knowledge management with minor gaps |
| 6-9 | Partial knowledge management |
| 0-5 | No structured knowledge management |

---

## Dimension 5: Integration Health (15 points)

Does the chip integrate properly with the ecosystem?

| Criterion | Points | Pass | Fail |
|-----------|--------|------|------|
| project.json presence | 3 | Valid project.json with chip metadata | Missing or invalid project.json |
| Chip path resolution | 3 | Chip loadable from standard path conventions | Custom paths or hardcoded locations |
| CLI commands | 3 | Standard commands work (init, evaluate, report) | Missing or broken commands |
| Guardrails | 3 | Input/output validation, error handling, bounds checking | No guardrails or uncaught errors |
| Self-edit protocol | 3 | Follows proposal-first self-modification | Direct self-edit or no self-edit capability |

### Scoring Guide

| Score Range | Interpretation |
|-------------|---------------|
| 13-15 | Seamless ecosystem integration |
| 10-12 | Minor integration issues, functional |
| 6-9 | Integration works but fragile |
| 0-5 | Significant integration problems |

---

## Dimension 6: Documentation (15 points)

Is the chip documented for humans and machines?

| Criterion | Points | Pass | Fail |
|-----------|--------|------|------|
| README | 3 | Clear README with purpose, usage, and examples | Missing or stub README |
| Mission statement | 3 | Why this chip exists, what problem it solves | No mission or generic description |
| Architecture description | 3 | How the chip works internally, key design decisions | No architecture docs |
| Docs directory | 3 | Organized docs/ with structured documentation | No docs directory |
| pyproject/package config | 3 | Valid build configuration with dependencies declared | Missing or incomplete build config |

### Scoring Guide

| Score Range | Interpretation |
|-------------|---------------|
| 13-15 | Excellent documentation for all audiences |
| 10-12 | Good docs with minor gaps |
| 6-9 | Basic docs present but incomplete |
| 0-5 | Poorly documented or undocumented |

---

## Overall Score Interpretation

| Total Score | Grade | Status | Action |
|-------------|-------|--------|--------|
| 90-100 | A | Exemplary | Reference chip for methodology |
| 80-89 | B | Strong | Production ready |
| 70-79 | C | Acceptable | Minor improvements recommended |
| 60-69 | D | Minimum viable | Passes gate, improvements needed |
| 40-59 | F | Below threshold | Blocked from graduation |
| 0-39 | X | Critical | Requires fundamental rework |

---

## Rubric Evolution

This rubric is not static. The Methodology Researcher workstream proposes updates based on:

- Patterns in chip failures (new criteria needed)
- Criterion redundancy (criteria that always co-occur)
- Scoring calibration (criteria that are too easy/hard)

All rubric changes require human approval before taking effect. Changes are versioned and documented in the methodology evolution log.
