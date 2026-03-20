# Evaluation Methodology: V1 → V2 → V3

## Overview

The domain chip quality evaluation system has evolved through three rubric versions, each designed to address fundamental flaws discovered in its predecessor. This document captures the methodology, scoring mechanics, and lessons learned at each stage.

## V1: Binary File-Existence Rubric (Original)

**Module**: `src/chip_labs/quality_rubric.py`
**Dimensions**: 6 | **Total Points**: 100 | **Portfolio Average**: 93.8

### How It Worked

V1 scored chips with binary pass/fail checks: does the file exist? Is the directory non-empty? Does the manifest parse?

| Dimension | Points | What It Checked |
|-----------|--------|-----------------|
| Manifest Validity | 15 | spark-chip.json parses, has schema_version, io_protocol, 4 hooks, frontier |
| Evidence Separation | 15 | 4 research lanes have files > 50 bytes |
| Evaluation Depth | 15 | project.json has metrics, scoring function exists, candidate trials |
| Memory & Beliefs | 10 | Beliefs directory, source registry, watchtower pages |
| Integration Quality | 10 | project.json valid, self-edit config, DSPy config |
| Documentation | 10 | README, chip_skill.md, mission docs |

### Fatal Flaw

Any file larger than 50 bytes passed. A research directory with a single file containing "placeholder text here" scored the same as one with 104 genuine research files averaging 336 words each. The rubric measured *structure* not *substance*.

**Result**: Portfolio inflated to 93.8/100 average. Every chip with proper scaffolding scored 80+.

---

## V2: Hardened Check Rubric (Upgraded)

**Module**: `src/chip_labs/quality_rubric_v2.py`
**Dimensions**: 7 | **Checks**: 37 | **Total Points**: 100 | **Portfolio Average**: 60.9 (raw) → 91.5 (gamed)

### Improvements Over V1

V2 added a 7th dimension (Flywheel Health, 25 pts) and hardened existing checks with minimum content thresholds.

| Dimension | Points | New/Changed Checks |
|-----------|--------|--------------------|
| Manifest Validity | 15 | Same as V1 |
| Evidence Separation | 15 | Same files > 50 bytes checks |
| Evaluation Depth | 15 | Added: multiple_metrics (3+), candidate_trials (3+) |
| Memory & Beliefs | 10 | Added: watchtower_pages (vault files), source_registry_urls |
| Integration Quality | 10 | Added: self_edit_config, hooks_wired |
| Documentation | 10 | Added: mission_docs (150+ chars) |
| **Flywheel Health** | **25** | **NEW**: has_run_history, contradiction_handling, metric_trajectory, belief_promotion, suggest_output |

### The Gaming Experiment

The `improve_all_chips.py` bridge script proved V2 was still gameable:

1. Created minimal files that satisfied every binary check
2. Added 50+ character contradiction docs (generic text)
3. Added 2 ascending score_history entries (synthetic)
4. Added stub belief promotion evidence
5. **Result**: Portfolio jumped from 60.9 → 91.5 without adding genuine intelligence

### Fatal Flaw

34 of 100 points still came from file-existence checks. V2 added *more* checks but not *deeper* checks. A chip with 2 synthetic ascending scores in score_history.jsonl scored the same as one with 785 genuine evaluation runs showing real improvement.

**Key lesson**: Adding more binary checks is an arms race. The rubric must measure content quality, not content existence.

---

## V3: Deep Content Analysis Rubric (Current)

**Module**: `src/chip_labs/deep_eval.py`
**Dimensions**: 8 | **Total Points**: 100 | **Portfolio Average**: 51.0

### Core Principle: Continuous Depth, Not Binary Existence

Every checker returns a continuous float (0.0 to max_points) based on content analysis. A file that exists but is hollow scores near 0. A rich artifact scores near max. There are no binary pass/fail checks.

### 8 Dimensions

#### 1. Manifest & Structure (10 pts)
- Manifest schema validity (3 pts)
- project.json completeness: eval_metric, 3+ metrics, candidate_trials (3 pts)
- Scoring function detection: regex for `def score/evaluate` + `return` in src/ (2 pts)
- Frontier bonus for populated mutation axes (2 pts)

#### 2. Empirical Velocity (18 pts) -- THE KEY DIFFERENTIATOR
- **Run volume** (5 pts): Logarithmic tiers -- 0 runs=0, 1-9=1, 10-49=2, 50-199=3, 200-499=4, 500+=5
- **Trajectory quality** (5 pts): Spearman rank correlation of scores over time. r<0=0, r<0.3=1, r<0.5=2, r<0.7=3, r<0.85=4, r>=0.85=5. Requires 5+ data points; fewer caps at 2.
- **Verdict diversity** (4 pts): Count of unique verdicts (improved, regressed, baseline, deferred, etc.)
- **Recency** (4 pts): Days since last run. >90=0, 60-90=1, 30-60=2, 7-30=3, <7=4

#### 3. Doctrine Quality (15 pts)
- **Causal density** (5 pts): Causal markers per 100 words ("because", "therefore", "leads to", "prioritize", "optimize", "tradeoff", etc.)
- **Boundary specificity** (5 pts): Fraction of doctrines with boundary markers ("only when", "does not apply", "limited to", numbers, percentages)
- **Uniqueness** (5 pts): Average pairwise Jaccard distance between doctrines. <0.3=0 (too similar), 0.5-0.7=3, 0.7+=5. Requires 3+ doctrines.

#### 4. Evidence Integrity (12 pts)
- **Lane balance** (4 pts): Gini coefficient across 4 evidence lanes. <0.3=4 (well balanced), 0.3-0.5=3, 0.5-0.7=2, 0.7+=1
- **Content density** (4 pts): Average words per file. <50=0, 50-100=1, 100-200=2, 200-500=3, 500+=4
- **Structured packets** (4 pts): Count of packets with claim+mechanism+boundary fields. 0=0, 1-2=1, 3-9=2, 10-29=3, 30+=4

#### 5. Contradiction Rigor (12 pts)
- **Contradiction count** (4 pts): Absolute count (5+ = full credit), multiplied by healthy-ratio factor (0.005-0.3 ratio = 1.0x). Zero contradictions with 50+ runs is suspicious (0 pts).
- **Specificity** (4 pts): Named entity density -- numbers, percentages, metric names, dates per 100 words
- **Resolution quality** (4 pts): Patterns like "resolved by", "fixed in", "root cause" referencing specific runs

#### 6. Flywheel Health (15 pts)
- **Loop activity frequency** (5 pts): Average interval between runs. >30 days=1, 7-30=2, 1-7=3, multiple/day=4, sustained daily 7+ days=5
- **Delta per iteration** (5 pts): Average score improvement per run (rolling window of 10). Penalizes identical scores.
- **Coverage awareness** (5 pts): GAPS.md existence (2), explicit limitations (1), suggest hook references actual gaps (2)

#### 7. Watchtower Depth (8 pts)
- **Page count** (3 pts): Logarithmic -- 0=0, 1-2=1, 3-9=2, 10+=3
- **Substance per page** (3 pts): Average words. <50=0, 50-150=1, 150-400=2, 400+=3
- **Cross-references** (2 pts): Internal wikilinks [[...]] connecting vault pages

#### 8. Integration Maturity (10 pts)
- **DSPy purposefulness** (4 pts): Config exists=1, real module paths=2, DSPy imports with signatures=3, chip-specific metrics=4
- **Scoring model complexity** (3 pts): Simple threshold=1, multi-metric weighted=2, conditional/domain-specific=3
- **Hook wiring** (3 pts): 0-1 hooks=0, 2 hooks=1, 3 hooks=2, all 4 hooks=3

### Anti-Gaming Mechanisms

| Flag | Detection | Meaning |
|------|-----------|---------|
| `identical_scores` | All scores in history are the same value | Gaming: fake run data with no variation |
| `single_day_batch` | All runs have timestamps within 24 hours | Suspect: batch generation, not organic learning |
| `high_structure_low_velocity` | Manifest score >= 50% but velocity score < 10% | Scaffolded structure with no real evaluation activity |
| `high_doctrine_count_low_substance` | 5+ doctrines but causal density < 0.5/100w | Quantity without quality: boilerplate doctrines |

### Statistical Utilities (Zero Dependencies)

All implemented inline without scipy/numpy:

- **Spearman rank correlation**: Rank both arrays, compute Pearson on ranks. Handles ties via average rank.
- **Gini coefficient**: `G = Σ Σ |xi - xj| / (2n²μ)`. Measures inequality of evidence lane file counts.
- **Jaccard distance**: `1 - |A ∩ B| / |A ∪ B|`. Measures doctrine uniqueness (higher = more different).
- **Causal density**: Regex count of causal/knowledge markers per 100 words.
- **Boundary specificity**: Fraction of sentences containing boundary markers.

### Depth Levels

Each dimension produces a depth level based on score percentage:

| Level | Score % | Meaning |
|-------|---------|---------|
| absent | 0% | No meaningful content |
| surface | 1-25% | Minimal/scaffolded content |
| moderate | 26-50% | Some genuine content but gaps |
| deep | 51-75% | Substantial genuine content |
| expert | 76-100% | Rich, deep, well-connected content |

---

## Version Comparison

| Feature | V1 | V2 | V3 |
|---------|----|----|-----|
| Scoring type | Binary per check | Binary per check | Continuous 0.0-max per dimension |
| File assessment | "exists?" | "exists + min size?" | "content density + causal quality?" |
| Run assessment | "non-empty?" | "2+ ascending?" | "Spearman correlation + volume tiers + recency" |
| Doctrine check | none | "has file?" | "causal density + boundary specificity + Jaccard uniqueness" |
| Evidence check | "has dir?" | "has 4 lanes?" | "Gini balance + content density + structured packets" |
| Contradiction | none | ">50 chars?" | "count-ratio + named entities + resolution quality" |
| Flywheel | none | "has run history?" | "frequency + delta/iteration + coverage awareness" |
| Anti-gaming | none | none | 4 flag detectors |
| Dep. count | 0 | 0 | 0 |
| Portfolio avg | 93.8 | 91.5 (gamed) / 60.9 (raw) | 51.0 |
| Verdict dist. | 10 prod, 1 beta | 10 prod, 1 beta | 0 prod, 6 beta, 5 alpha |

## Portfolio Results (V3, March 2026)

| Rank | Chip | Score | Verdict | Key Strength |
|------|------|-------|---------|-------------|
| 1 | startup-yc | 64.0 | beta | 785 runs, 276 vault pages, expert velocity+watchtower |
| 2 | xcontent | 61.6 | beta | Best trajectory (r=0.729), best evidence balance |
| 3 | pokemon-red | 60.8 | beta | 776 runs, 1666 words/vault page |
| 4 | content | 57.0 | beta | Highest causal density (1.92/100w) |
| 5 | agentic-marketing | 55.0 | beta | 11 contradictions with high specificity |
| 6 | spark-private | 53.0 | beta | 198 vault pages |
| 7 | roblox-development | 48.0 | alpha | 41 vault pages |
| 8 | web-designer | 48.0 | alpha | Best flywheel delta (+0.1/run) |
| 9 | spark-private-main | 43.0 | alpha | Flywheel starting |
| 10 | trading-crypto | 39.0 | alpha | 61 vault pages, 437 words each |
| 11 | predictive-worlds-lab | 32.0 | alpha | Best trajectory (r=0.882) |

## Lessons Learned

1. **Binary checks are an arms race**: For every "exists?" check, a scaffolding script can create a minimal valid file. Content analysis is the only defense.
2. **Run count reveals truth**: The single most powerful differentiator between genuine and scaffolded chips is empirical velocity. startup-yc's 785 runs vs content's 10 runs tells the real story.
3. **Contradictions signal health**: A chip with 500+ runs and zero contradictions is suspicious, not perfect. Real learning always encounters regressions.
4. **Causal reasoning proves understanding**: "Prioritize X" is a statement. "Because X correlates with Y across N runs, prioritize X when Z" is intelligence. Causal density separates knowledge from boilerplate.
5. **Zero deps is non-negotiable**: All three rubric versions use stdlib only. This ensures any chip on any machine can be evaluated without installing packages.
