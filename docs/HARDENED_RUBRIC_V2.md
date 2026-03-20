# Hardened Quality Rubric V2

**Date**: 2026-03-20
**Module**: `src/chip_labs/quality_rubric_v2.py`

---

## Why V2?

The v1 rubric (30 checks, 100 pts across 6 dimensions) was **surface-level**. A chip could score 100/100 while producing zero intelligence:

- Evidence lanes passed if the word "source" appeared anywhere in text
- Scoring logic passed if any Python file contained "score" and "def"
- Source registry passed if "source" and "registry" keywords existed
- Documentation passed if files existed (regardless of content length)

V2 fixes this by:
1. **Hardening existing checks** with real validation (file existence in subdirs, URL patterns, minimum content lengths)
2. **Adding a new Flywheel Intelligence dimension** (25 pts) that verifies the chip is actually producing intelligence

---

## Point Distribution

| Dimension | V1 | V2 | Change |
|-----------|---:|---:|--------|
| Manifest Validity | 15 | 15 | Same |
| Evidence Separation | 20 | 15 | -5, checks hardened |
| Evaluation Depth | 20 | 15 | -5, checks hardened |
| Memory & Knowledge | 15 | 10 | -5, checks hardened |
| Integration Health | 15 | 10 | -5, checks hardened |
| Documentation | 15 | 10 | -5, checks hardened |
| **Flywheel Intelligence** | -- | **25** | **NEW** |
| **Total** | **100** | **100** | |

---

## Hardened Checks (Existing Dimensions)

### Evidence Separation (15 pts)
- `has_research_grounded` (4 pts): Actual files in `research/research_grounded/` (not just keyword matching)
- `has_benchmark_grounded` (4 pts): Actual files in `research/benchmark_grounded/`
- `has_exploratory_frontier` (4 pts): Actual files in `research/exploratory_frontier/`
- `has_realworld_validated` (3 pts): Actual files in `research/realworld_validated/`

### Evaluation Depth (15 pts)
- `primary_metric` (3 pts): Unchanged
- `baseline_trial` (3 pts): Unchanged
- `multiple_metrics` (3 pts): Unchanged
- `scoring_logic` (3 pts): Now verifies function contains `return` with numeric expression, not just "score" keyword
- `source_registry_urls` (3 pts): Now requires actual URL patterns (`https://`, `doi:`, `arxiv:`)

### Memory & Knowledge (10 pts)
- `source_registry` (3 pts): Unchanged (downweighted from 5)
- `obsidian_vault` (4 pts): Now requires 3+ pages with >100 chars each
- `memory_backend` (3 pts): Unchanged (downweighted from 5)

### Documentation (10 pts)
- `readme_exists` (2 pts): Now requires minimum 200 chars of content
- `mission_docs` (3 pts): Now requires minimum 150 chars of real content
- `architecture_docs` (2 pts): Now requires minimum 150 chars
- `docs_directory` (1 pt): Unchanged (downweighted)
- `pyproject_valid` (2 pts): Unchanged

---

## New Dimension: Flywheel Intelligence (25 pts)

This is the core v2 innovation. It measures whether the chip's autoloop flywheel is **actually producing intelligence**.

| Check | Points | What It Verifies |
|-------|-------:|------------------|
| `has_run_history` | 4 | Non-empty `score_history.jsonl` or `loop_telemetry.json` |
| `belief_promotion` | 5 | Score improved over time OR belief files marked "durable"/"promoted" |
| `metric_trajectory` | 4 | 3+ score entries with 2+ ascending transitions |
| `contradiction_handling` | 4 | Substantive contradiction docs (>50 chars beyond headers) |
| `packet_quality_real` | 3 | Packets with structured claim/mechanism/boundary fields |
| `has_dspy_integration` | 3 | DSPy scripts or config detected in chip |
| `has_skill_file` | 2 | `chip_skill.md` with >200 chars of real content |

---

## V1 vs V2 Scoring: Real Portfolio

| Chip | V1 Score | V2 Score | Delta | V2 Flywheel |
|------|----------|----------|-------|-------------|
| domain-chip-startup-yc | 100 | 73 | -27 | 10/25 |
| domain-chip-agentic-marketing | 100 | 68 | -32 | 5/25 |
| domain-chip-spark-private | 100 | 68 | -32 | 5/25 |
| domain-chip-roblox-development | 97 | 66 | -31 | 5/25 |
| domain-chip-pokemon-red | 97 | 63 | -34 | 5/25 |
| domain-chip-spark-private-main | 97 | 61 | -36 | 0/25 |
| domain-chip-xcontent | 94 | 60 | -34 | 5/25 |
| domain-chip-content | 95 | 57 | -38 | 4/25 |
| domain-chip-trading-crypto | 91 | 57 | -34 | 5/25 |
| domain-chip-web-designer | 92 | 57 | -35 | 0/25 |
| domain-chip-predictive-worlds-lab | 69 | 40 | -29 | 4/25 |
| **Portfolio Average** | **93.8** | **60.9** | **-32.9** | **4.4/25** |

### Key Takeaways

1. **Average dropped 33 points** -- the v1 scores were inflated by surface-level checks
2. **Zero chips are production_ready on v2** -- all need flywheel work
3. **startup-yc leads at 73** because it has the most real intelligence (DSPy, beliefs, run history)
4. **Flywheel averages 4.4/25** -- most chips have minimal intelligence production
5. **Evidence Separation collapsed** -- most chips have no actual files in research subdirs
6. **This is working as intended** -- the rubric now reflects actual intelligence, not file existence

---

## Gap Analyzer V2 Auto-Fixes

Four new auto-fix functions for flywheel checks:

| Check | Fix Function | What It Does |
|-------|-------------|--------------|
| `has_run_history` | `_fix_has_run_history` | Scores the chip and persists result to `score_history.jsonl` |
| `contradiction_handling` | `_fix_contradiction_handling` | Creates substantive `CONTRADICTIONS.md` with real content |
| `packet_quality_real` | `_fix_packet_quality_real` | Creates structured packets with claim/mechanism/boundary |
| `has_skill_file` | `_fix_has_skill_file` | Generates `chip_skill.md` via intelligence_server |

The remaining 3 flywheel checks (`belief_promotion`, `metric_trajectory`, `has_dspy_integration`) are **not auto-fixable** -- they require actual intelligence accumulation through the autoloop.

---

## CLI Usage

```bash
# Score against v2 rubric
chip-labs score-v2 <chip-path>

# Score with v1 rubric (unchanged)
chip-labs score <chip-path>

# Run doctor with v2-aware fixes
chip-labs doctor <chip-path>
```

---

## Verdict Thresholds (Same as V1)

| Score | Verdict |
|-------|---------|
| >= 80 | `production_ready` |
| 60-79 | `beta` |
| 35-59 | `alpha` |
| < 35 | `scaffold` |
