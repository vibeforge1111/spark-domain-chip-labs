# Analysis: Template System & Recursive Improvement Loops

**Date**: 2026-03-20
**Source**: spark-domain-chip-labs, spark-growth, quality rubric deep analysis
**Method**: Code inspection, rubric simulation, pattern extraction

---

## Current Template System: State of Affairs

### What Exists

1. **3 blank markdown forms** in `research/domains/_template/`:
   - `DOMAIN_BRIEF.md` — Empty form with section headers
   - `EVIDENCE.md` — Empty evidence lane tables
   - `GRADUATION_ASSESSMENT.md` — 7-criterion checklist

2. **12-step creation checklist** in `methodology.py` (lines 103-116) — Data only, nothing automated

3. **Proven patterns** in `methodology.py` — Knowledge base, not applied during creation

### What Does NOT Exist

- No `scaffold_chip()` function
- No CLI command for chip creation
- No code generator (no cookiecutter/yeoman/etc.)
- No category-specific templates
- No auto-scoring during scaffold
- No auto-fix capability

### Result

Every new chip is built by hand from scratch. Developers copy files from existing chips, manually adapt them, and discover missing pieces through trial-and-error rubric runs.

---

## The Broken Feedback Loop

### Current Architecture (Disconnected)

```
evaluate.py ──► returns score ──► watchtower shows it ──► human reads it
                                                              │
suggest.py  ──► returns candidates ──► researcher picks one   │
     │                                                        │
     └── independently discovers chips, scores them ◄─────────┘
                    NO DATA BRIDGE
```

### The Gap

- `evaluate` returns `{total_score, dimension_scores, failed_checks}` but this data goes nowhere except watchtower markdown
- `suggest` independently re-discovers and re-scores chips — it doesn't receive evaluate's output
- There is no function that converts `failed_checks` into `improvement_tasks`
- There is no automated fix execution for structural failures
- There is no score persistence over time

### What Should Exist

```
evaluate.py ──► gap_analyzer() ──► prioritized fix list ──► auto_fixer()
                     │                                           │
                     ▼                                           ▼
              suggest.py receives                         re-evaluate
              specific gaps as input                      (closed loop)
```

---

## Quality Rubric Deep Analysis

### The 30 Checks

| # | Dimension | Check | Points | Automatable? |
|---|-----------|-------|--------|-------------|
| 1 | Manifest (15) | schema_version = spark-chip.v1 | 2 | Yes |
| 2 | | io_protocol = spark-hook-io.v1 | 3 | Yes |
| 3 | | all 4 hooks in capabilities | 3 | Yes |
| 4 | | frontier enabled | 3 | Yes |
| 5 | | required_fields present | 2 | Yes |
| 6 | | field_patterns defined | 2 | Yes |
| 7 | Evidence (20) | research_grounded lane | 5 | Partial |
| 8 | | benchmark_grounded lane | 5 | Partial |
| 9 | | exploratory_frontier lane | 5 | Partial |
| 10 | | realworld_validated lane | 5 | Partial |
| 11 | Evaluation (20) | primary metric defined | 4 | Yes |
| 12 | | 3+ metrics | 4 | Partial |
| 13 | | scoring logic exists | 4 | Yes (skeleton) |
| 14 | | 3+ candidate trials | 4 | Partial |
| 15 | | baseline trial | 4 | Yes |
| 16 | Memory (15) | source registry | 3 | Yes (stub) |
| 17 | | packet schema | 3 | Partial |
| 18 | | watchtower pages | 3 | Yes (skeleton) |
| 19 | | obsidian vault | 3 | Yes |
| 20 | | memory backend | 3 | Yes |
| 21 | Integration (15) | project.json valid | 3 | Yes |
| 22 | | chip path set | 3 | Yes |
| 23 | | commands defined | 3 | Yes |
| 24 | | guardrails set | 3 | Yes |
| 25 | | self_edit config | 3 | Yes |
| 26 | Documentation (15) | README exists | 3 | Yes |
| 27 | | mission docs | 3 | Yes |
| 28 | | architecture docs | 3 | Yes |
| 29 | | docs/ directory | 3 | Yes |
| 30 | | pyproject.toml | 3 | Yes |

### Automation Summary

| Category | Checks | Fully Automatable | Partially | Domain-Only |
|----------|--------|-------------------|-----------|-------------|
| Manifest | 6 | 6 | 0 | 0 |
| Evidence | 4 | 0 | 4 | 0 |
| Evaluation | 5 | 3 | 2 | 0 |
| Memory | 5 | 3 | 2 | 0 |
| Integration | 5 | 5 | 0 | 0 |
| Documentation | 5 | 5 | 0 | 0 |
| **Total** | **30** | **22** | **8** | **0** |

**Key insight**: There are zero checks that are purely domain-specific and cannot be partially automated. Even evidence lanes can be seeded with stubs.

### Score Projections for Auto-Scaffold

| Scenario | Score | Verdict |
|----------|-------|---------|
| Empty directory | 0 | scaffold |
| Current 3-template system | ~10-15 | scaffold |
| Full structural scaffold | 45-50 | alpha |
| Scaffold + evidence stubs | 55-60 | alpha/beta |
| Scaffold + auto-fix pass | 65-70 | beta |
| Scaffold + domain research | 75-80 | beta/production |

---

## Recursive Improvement: What Works and What Doesn't

### What Works (Evidence from Mature Chips)

1. **Real data as evaluation ground truth** (trading-crypto: walk-forward on candle data)
2. **External benchmarks** (startup-yc: startup-bench as independent truth surface)
3. **Variety enforcement** (trading-crypto: variety backlog; startup-yc: anchor retirement)
4. **Cadenced review** (startup-yc: doctrine review every 15 runs)
5. **Progressive promotion gates** (trading-crypto: learning → backtest → paper-trade)
6. **Contradiction detection** (startup-yc: tag-based penalties)

### What Doesn't Work or Is Missing

1. **No score persistence** — Can't track improvement trends
2. **No automatic gap-to-fix pipeline** — Humans must interpret scores and decide fixes
3. **No stall detection in most chips** — Only startup-yc has agent cooldown
4. **No cross-chip learning** — Each chip is a complete silo
5. **Human approval gates** — Required for all self-edits, blocking autonomous loops
6. **Unbounded candidate growth** — project.json candidate_trials only grows, never prunes
7. **Watchtower is write-only** — No programmatic query API for chip state
8. **Testing is optional** — Most mature chips have zero tests

### Ideal Recursive Loop Properties

Based on analysis of what works across all chips:

1. **Closed feedback**: evaluate output feeds directly into gap analysis and suggestion
2. **Score tracking**: Every evaluation persisted with timestamp and context
3. **Auto-structural-fix**: Structural rubric failures fixed without human intervention
4. **Stall detection**: If score doesn't improve for N iterations, change strategy
5. **Variety enforcement**: Prevent same mutations from being retried
6. **Progressive autonomy**: Start gated, reduce gates as chip proves reliable
7. **External validation**: At least one benchmark that the chip doesn't control
8. **Cross-chip transfer**: Patterns from production chips automatically applied to new ones
9. **Pruning**: Retired candidates archived, not kept in active trials
10. **Regression detection**: Tests + score comparison catch regressions

---

## spark-growth Connection

### Current State: Zero Technical Integration

spark-growth is a marketing/content repository with no code, no tests, and no chip integration.

### Potential Integration Points

| Growth Activity | Chip System Equivalent | Integration Opportunity |
|----------------|----------------------|------------------------|
| Market scanning (HN, Reddit, X) | Frontier Scout domain discovery | Growth signals as domain opportunity inputs |
| Community mentions tracking | MiroFish adoption signals | Community data as simulation inputs |
| Content research | Domain brief research | Content research byproduct as domain brief seed |
| Growth analytics | Loop telemetry | Adoption metrics as evaluation evidence |

### Recommendation

Growth analytics should feed the MiroFish simulation as real-world validation signals. The Frontier Scout workstream should consume growth channel data for domain discovery. This requires a simple signal ingestion API, not a deep integration.

---

## The Meta-Chip Recursion Insight

spark-domain-chip-labs is itself a chip that evaluates chips. This creates a unique recursive opportunity:

1. **The lab can evaluate itself** against its own rubric
2. **The lab can improve itself** using the same gap-to-fix pipeline it builds for other chips
3. **The lab's quality rubric improvements propagate** to all chips in the portfolio
4. **The lab's template improvements** accelerate all future chip creation

This is the highest-leverage point in the entire system: improvements to the meta-chip multiply across every chip in the portfolio.
