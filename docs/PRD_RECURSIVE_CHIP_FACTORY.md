# PRD: Recursive Chip Factory — Self-Improving Domain Intelligence at Scale

**Version**: 0.1.0
**Date**: 2026-03-20
**Status**: DRAFT — Awaiting validation through experimental runs
**Owner**: spark-domain-chip-labs

---

## Problem Statement

Creating a domain chip currently takes **10-20 hours** of manual work, of which **50-55% is structural boilerplate**. Converting a chip into a self-improving recursive loop requires even more effort — wiring evaluation feedback to suggestion engines, building promotion gates, and designing evidence pipelines. Only 1 of 12 chips (startup-yc) has reached production maturity (v0.3.0), and it took weeks of focused effort.

**The core bottleneck**: There is no automated scaffold, no closed feedback loop between evaluate and suggest, and no shared infrastructure for the patterns that are identical across every domain.

### Evidence Base (from cross-repo analysis of 8 repositories)

| Finding | Source |
|---------|--------|
| 50-55% of chip work is boilerplate | Comparative analysis of trading-crypto, web-designer, startup-yc |
| `evaluate` and `suggest` hooks share no data pipeline | chip-labs source analysis (evaluate.py, suggest.py) |
| 22 of 30 rubric checks are automatable with structural fixes | quality_rubric.py analysis |
| A chip at score 45 can reach 60+ with 6 structural additions (no domain logic) | Rubric gap analysis |
| 0 of 12 chips have both tests AND production maturity | Portfolio audit |
| No code scaffold generator exists — only 3 blank markdown templates | research/domains/_template/ inspection |
| CLI monolith problem: startup-yc cli.py = 8,886 lines | Direct measurement |
| No cross-chip learning protocol exists | Architecture review |
| Human approval gates block autonomous improvement | spark-researcher.project.json guardrails |
| predictive-worlds-lab (best test coverage) does NOT follow chip contract | Manifest comparison |

---

## Vision

**A system where creating a new domain chip takes 15 minutes of human input (a domain brief), and the chip autonomously reaches beta quality (60+ score) within hours through recursive self-improvement loops.**

```
Human writes domain brief (15 min)
         │
         ▼
┌─────────────────────┐
│   CHIP FACTORY       │
│                      │
│  scaffold_chip()     │──► Working v0.0.1 chip (score ~45)
│  gap_analyzer()      │──► Prioritized fix list
│  auto_fix()          │──► Structural fixes applied
│  research_seeder()   │──► Initial evidence gathered
│  recursive_loop()    │──► evaluate→gap→fix→re-score cycle
│                      │
└─────────────────────┘
         │
         ▼
  v0.1.0 alpha (score 60+) in hours
  v0.2.0 beta (score 75+) in days
  v0.3.0 production (score 85+) in 1-2 weeks
```

---

## Architecture

### Layer 1: Chip Scaffold Engine

Generates a complete, functional chip from a domain brief.

#### Input: Domain Brief (human-authored, ~15 min)

```yaml
domain_id: "quantum-computing"
domain_name: "Quantum Computing Research"
category: "technology"  # technology | finance | creative | gaming | science | business
description: "Evaluate quantum computing approaches, algorithms, and hardware"
mutation_axes:
  - name: "algorithm_class"
    values: ["variational", "grover", "shor", "qaoa", "vqe"]
  - name: "hardware_platform"
    values: ["superconducting", "trapped_ion", "photonic", "topological"]
  - name: "error_correction"
    values: ["surface_code", "repetition", "concatenated", "none"]
primary_metric: "quantum_advantage_score"
research_sources:
  - type: "arxiv"
    query: "quantum computing algorithms"
  - type: "web"
    urls: ["https://quantum-journal.org"]
evidence_lanes:
  - "research_grounded"
  - "benchmark_grounded"
  - "exploratory_frontier"
```

#### Output: Complete Chip Directory

```
domain-chip-quantum-computing/
├── spark-chip.json              # Full manifest with mutations
├── spark-researcher.project.json # Loop config with trials
├── pyproject.toml               # Zero-dep package
├── README.md                    # Generated from brief
├── src/quantum_computing/
│   ├── __init__.py
│   ├── cli.py                   # Hook routing (100% boilerplate)
│   ├── evaluate.py              # Scoring skeleton with mutation engine
│   ├── suggest.py               # Gap-driven suggestion engine
│   ├── packets.py               # Evidence-lane-tagged emitter
│   ├── watchtower.py            # Obsidian page generator
│   └── scoring_engine.py        # Shared additive scoring model
├── docs/
│   ├── MISSION.md
│   ├── ARCHITECTURE.md
│   ├── SOURCE_REGISTRY.md
│   └── ONE_LOOP_SPEC.md
├── research/
│   ├── packets/
│   └── sources/
├── obsidian-vault/
│   └── README.md
├── tests/
│   ├── test_evaluate.py         # Smoke tests for evaluate hook
│   ├── test_suggest.py          # Smoke tests for suggest hook
│   ├── test_packets.py          # Smoke tests for packets hook
│   └── test_watchtower.py       # Smoke tests for watchtower hook
└── data/
    └── README.md
```

**Design target**: Scaffold scores 45-50 on quality rubric immediately (passes 15+ of 30 checks).

### Layer 2: Shared Scoring Library (spark-chip-core)

Extract the additive mutation scoring pattern that ALL chips reimplemented independently:

```python
# spark_chip_core/scoring.py

class MutationScoringEngine:
    """Shared scoring engine used by all domain chips.

    Pattern extracted from:
    - trading-crypto: doctrine/strategy/regime/timeframe scoring
    - web-designer: 7-axis design scoring with pair bonuses
    - startup-yc: factor catalog with family priors and uplift
    """

    def __init__(self, config: ScoringConfig):
        self.base_score = config.base_score  # typically 50
        self.dimensions = config.dimensions   # {name: {value: delta}}
        self.pair_bonuses = config.pair_bonuses  # {(dim_a_val, dim_b_val): bonus}
        self.system_bonuses = config.system_bonuses  # [{condition, bonus}]
        self.clamp = config.clamp  # (min, max) typically (0, 100)

    def score(self, mutations: dict) -> ScoringResult:
        """Score a mutation combination."""
        score = self.base_score
        breakdown = {}

        # Dimension deltas
        for dim_name, dim_values in self.dimensions.items():
            val = mutations.get(dim_name)
            delta = dim_values.get(val, 0)
            score += delta
            breakdown[dim_name] = {"value": val, "delta": delta}

        # Pair synergies
        for (dim_a, val_a, dim_b, val_b), bonus in self.pair_bonuses.items():
            if mutations.get(dim_a) == val_a and mutations.get(dim_b) == val_b:
                score += bonus
                breakdown[f"pair_{dim_a}_{dim_b}"] = bonus

        # System bonuses
        for system_bonus in self.system_bonuses:
            if system_bonus.condition(mutations):
                score += system_bonus.bonus

        score = max(self.clamp[0], min(self.clamp[1], score))

        return ScoringResult(
            total=score,
            breakdown=breakdown,
            verdict=self._verdict(score),
            evidence_lane=self._classify_lane(mutations)
        )
```

### Layer 3: Gap Analyzer & Auto-Fixer

Closes the broken `evaluate → suggest` feedback loop.

```python
# chip_labs/gap_analyzer.py

def analyze_gaps(score_result: dict) -> list[GapFix]:
    """Convert failed rubric checks into prioritized, actionable fixes."""
    fixes = []
    for check in score_result["failed_checks"]:
        fix = FIX_REGISTRY.get(check["check_id"])
        if fix:
            fixes.append(GapFix(
                check_id=check["check_id"],
                dimension=check["dimension"],
                points_recoverable=check["max_points"] - check["scored_points"],
                fix_type=fix.fix_type,  # "structural" | "content" | "domain_specific"
                auto_fixable=fix.auto_fixable,
                fix_fn=fix.apply,
                description=fix.description
            ))

    # Sort by points recoverable (highest impact first)
    fixes.sort(key=lambda f: f.points_recoverable, reverse=True)
    return fixes


# Automated fix registry for structural checks
FIX_REGISTRY = {
    # Manifest (15 pts, 6 checks — all automatable)
    "schema_version": StructuralFix("Set schema to spark-chip.v1"),
    "io_protocol": StructuralFix("Set protocol to spark-hook-io.v1"),
    "all_four_hooks": StructuralFix("Add missing hook entries to capabilities"),
    "frontier_enabled": StructuralFix("Add frontier block with web_search and model"),
    "required_fields": StructuralFix("Add required_fields from mutation axes"),
    "field_patterns": StructuralFix("Generate regex patterns for mutation values"),

    # Documentation (15 pts, 5 checks — 4 automatable)
    "readme_exists": StructuralFix("Generate README from domain brief"),
    "mission_docs": StructuralFix("Generate MISSION.md from brief"),
    "architecture_docs": StructuralFix("Generate ARCHITECTURE.md skeleton"),
    "docs_directory": StructuralFix("Create docs/ directory"),
    "pyproject_exists": StructuralFix("Generate pyproject.toml"),

    # Integration (15 pts, 5 checks — all automatable)
    "project_json_valid": StructuralFix("Generate spark-researcher.project.json"),
    "chip_path_set": StructuralFix("Set chip path in project.json"),
    "commands_defined": StructuralFix("Generate commands from manifest capabilities"),
    "guardrails_set": StructuralFix("Apply standard guardrails template"),
    "self_edit_config": StructuralFix("Apply standard self-edit template"),

    # Memory (15 pts, 5 checks — 3 automatable)
    "source_registry": StructuralFix("Generate source registry from brief"),
    "obsidian_vault": StructuralFix("Create obsidian-vault/ with README"),
    "memory_backend": StructuralFix("Add memory backend config to project.json"),
    # packet_schema and watchtower_pages require content

    # Evidence (20 pts) and Evaluation (20 pts) — mostly domain-specific
    # But baseline trial and metric definition are templatable
    "primary_metric": StructuralFix("Define primary metric from brief"),
    "baseline_trial": StructuralFix("Generate baseline candidate trial"),
}
# Total automatable: 22 of 30 checks = up to 73 points recoverable automatically
```

### Layer 4: Recursive Improvement Orchestrator

The autonomous score→fix→re-score cycle.

```python
# chip_labs/improve.py

def improve_chip(
    chip_path: Path,
    target_score: int = 60,
    max_iterations: int = 20,
    auto_fix_only: bool = True
) -> ImprovementReport:
    """Run autonomous improvement cycle on a chip.

    Phase 1 (structural): Apply auto-fixable structural improvements
    Phase 2 (content): Generate content stubs for content-dependent checks
    Phase 3 (domain): Queue domain-specific improvements for human/LLM review
    """
    history = []

    for iteration in range(max_iterations):
        # Score
        result = score_chip(chip_path)
        history.append(ScoreSnapshot(
            iteration=iteration,
            score=result["total_score"],
            verdict=result["verdict"],
            failed_checks=result["failed_checks"]
        ))

        # Check target
        if result["total_score"] >= target_score:
            break

        # Analyze gaps
        gaps = analyze_gaps(result)
        fixable = [g for g in gaps if g.auto_fixable] if auto_fix_only else gaps

        if not fixable:
            break  # Only domain-specific gaps remain

        # Apply highest-impact fix
        fix = fixable[0]
        fix.fix_fn(chip_path)

    return ImprovementReport(
        chip_path=chip_path,
        initial_score=history[0].score,
        final_score=history[-1].score,
        iterations=len(history),
        fixes_applied=[h for h in history if h.score > (history[history.index(h)-1].score if history.index(h) > 0 else 0)],
        remaining_gaps=[g for g in analyze_gaps(score_chip(chip_path)) if not g.auto_fixable]
    )
```

### Layer 5: Cross-Chip Intelligence Transfer

Currently missing entirely. Each chip is a silo.

```python
# chip_labs/transfer.py

def extract_transfer_patterns(portfolio: list[ChipScore]) -> list[TransferPattern]:
    """Extract patterns from high-scoring chips that could help lower-scoring ones.

    Pattern types:
    - scoring_model: How the evaluation logic works
    - loop_design: How the recursive improvement is structured
    - evidence_strategy: How research sources are organized
    - promotion_gates: How candidates graduate to higher evidence lanes
    """
    patterns = []

    # Find what production chips do that scaffold chips don't
    production = [c for c in portfolio if c.verdict == "production_ready"]
    struggling = [c for c in portfolio if c.score < 60]

    for prod_chip in production:
        for dimension in prod_chip.dimension_scores:
            if dimension.score >= 18:  # Near-perfect dimension
                # Extract the pattern
                patterns.append(TransferPattern(
                    source_chip=prod_chip.name,
                    dimension=dimension.name,
                    technique=dimension.implementation_summary,
                    applicable_to=[s.name for s in struggling
                                  if s.dimension_scores[dimension.name].score < 12]
                ))

    return patterns
```

### Layer 6: Domain Category Templates

Pre-built configurations for common domain categories that accelerate chip creation beyond generic scaffolding.

```yaml
# templates/categories/finance.yaml
category: finance
default_mutation_axes:
  - name: "risk_model"
    values: ["var_95", "var_99", "cvar", "stress_test"]
  - name: "time_horizon"
    values: ["intraday", "daily", "weekly", "monthly"]
  - name: "data_regime"
    values: ["bull", "bear", "sideways", "volatile", "crisis"]
default_evidence_lanes:
  - research_grounded
  - benchmark_grounded
  - realworld_validated
  - backtest_benchmark
scoring_template: "additive_with_regime_gates"
research_source_types:
  - academic_papers
  - market_data
  - regulatory_filings
promotion_gates:
  - type: "backtest"
    threshold: 0.6
  - type: "paper_trade"
    threshold: 0.7
  - type: "live_validation"
    threshold: 0.8
watchtower_pages:
  - "Leaderboard"
  - "Regime Analysis"
  - "Risk Dashboard"
  - "Promotion Pipeline"

# templates/categories/creative.yaml
category: creative
default_mutation_axes:
  - name: "style_direction"
    values: ["minimal", "expressive", "brutalist", "organic", "systematic"]
  - name: "medium"
    values: ["web", "print", "motion", "interactive"]
  - name: "audience"
    values: ["consumer", "enterprise", "developer", "luxury"]
default_evidence_lanes:
  - research_grounded
  - exploratory_frontier
  - heuristic_frontier
  - realworld_validated
scoring_template: "multi_axis_with_pair_bonuses"
research_source_types:
  - award_sites
  - case_studies
  - design_systems
  - user_research
watchtower_pages:
  - "Reference Library"
  - "Critique Queue"
  - "Style Doctrine"
  - "Benchmark Gallery"

# templates/categories/technology.yaml
# templates/categories/gaming.yaml
# templates/categories/science.yaml
# templates/categories/business.yaml
```

---

## Implementation Plan

### Phase 1: Scaffold Engine (Week 1)

**Goal**: `scaffold_chip(brief) → working chip directory scoring 45+`

| Task | Effort | Impact |
|------|--------|--------|
| Define DomainBrief schema (YAML) | 2 hrs | Foundation for everything |
| Build scaffold_chip() generator | 8 hrs | Eliminates 50% of chip creation time |
| Generate all boilerplate files from brief | 4 hrs | pyproject, manifest, project.json, CLI |
| Generate skeleton hooks (evaluate, suggest, packets, watchtower) | 4 hrs | Working hooks out of the box |
| Generate test scaffolds | 2 hrs | Prevent the zero-test problem |
| Build 6 category templates (finance, creative, tech, gaming, science, business) | 6 hrs | Category-specific acceleration |
| Validate: scaffold 3 new chips, verify score >= 45 | 2 hrs | Proof it works |

**Deliverable**: `python -m chip_labs scaffold --brief quantum-computing.yaml` → complete chip

### Phase 2: Gap Analyzer + Auto-Fixer (Week 2)

**Goal**: `improve_chip(path) → score jumps from 45 to 65+ automatically`

| Task | Effort | Impact |
|------|--------|--------|
| Build gap_analyzer() from rubric | 4 hrs | Maps failures to fixes |
| Implement 22 structural fix functions | 8 hrs | Auto-fix 73% of rubric checks |
| Build improve_chip() orchestrator | 4 hrs | Autonomous score→fix→rescore cycle |
| Wire gap analysis into suggest hook | 2 hrs | Close the evaluate→suggest feedback loop |
| Add score persistence (JSONL ledger per chip) | 2 hrs | Track improvement over time |
| Build `chip_doctor` CLI command | 2 hrs | One-command portfolio health improvement |
| Validate: run chip_doctor on 5 weakest portfolio chips | 2 hrs | Prove score improvements |

**Deliverable**: `python -m chip_labs doctor domain-chip-content` → score improves from 74 to 85+

### Phase 3: Shared Scoring Library (Week 2-3)

**Goal**: Extract the additive mutation scoring pattern into a shared library

| Task | Effort | Impact |
|------|--------|--------|
| Design ScoringConfig schema | 2 hrs | Unified scoring model |
| Extract MutationScoringEngine from 3 chips | 6 hrs | Remove 200-400 lines per chip |
| Build ScoringResult with verdict + evidence lane | 2 hrs | Standard output contract |
| Migrate trading-crypto to use shared engine | 4 hrs | Validation |
| Migrate web-designer to use shared engine | 4 hrs | Validation |
| Migrate startup-yc to use shared engine | 4 hrs | Validation |
| Benchmark: verify identical scores before/after migration | 2 hrs | No regression |

**Deliverable**: `from spark_chip_core import MutationScoringEngine` usable by all chips

### Phase 4: Recursive Loop Automation (Week 3-4)

**Goal**: A chip can run evaluate→gap→fix→rescore→suggest→research→repeat autonomously

| Task | Effort | Impact |
|------|--------|--------|
| Build RecursiveLoopController | 8 hrs | Orchestrates the full cycle |
| Integrate gap_analyzer into loop controller | 2 hrs | Auto-fix within loop |
| Add research seeder (generates initial evidence from web sources) | 6 hrs | Chips start researching immediately |
| Build promotion gates for auto-discovered evidence | 4 hrs | Quality control on auto-research |
| Add loop telemetry (iterations, score trajectory, fixes applied) | 2 hrs | Visibility into loop health |
| Configurable autonomy levels (full-auto, semi-auto, human-gated) | 4 hrs | Progressive trust |
| Validate: scaffold + auto-improve a chip from 0 to 60+ unattended | 4 hrs | End-to-end proof |

**Deliverable**: `python -m chip_labs autoloop --brief domain.yaml --target-score 60` runs unattended

### Phase 5: Cross-Chip Intelligence (Week 4+)

**Goal**: Chips learn from each other, patterns propagate across the portfolio

| Task | Effort | Impact |
|------|--------|--------|
| Build transfer pattern extractor | 4 hrs | Learn from production chips |
| Implement pattern applicator for struggling chips | 4 hrs | Auto-apply proven patterns |
| Add cross-chip scoring comparison dashboard | 4 hrs | Watchtower portfolio view |
| Build contradiction sharing (chip A found X contradicts chip B) | 4 hrs | Cross-domain learning |
| Design graduation ceremony (promote patterns that work 3+ times) | 2 hrs | Institutional memory |

**Deliverable**: Production chip patterns automatically applied to new scaffolds

---

## Success Metrics

### Efficiency Metrics

| Metric | Current | Phase 1 Target | Phase 4 Target |
|--------|---------|----------------|----------------|
| Time to create chip (human effort) | 10-20 hours | 2-4 hours | 15-30 minutes |
| Time to reach score 60 (beta) | Days-weeks | Hours | Hours (unattended) |
| Time to reach score 80 (production) | Weeks | 1-2 weeks | 3-5 days |
| Boilerplate ratio | 50-55% | 10-15% | 5% |
| Chips with test coverage | 2/12 (17%) | 100% of new chips | 100% |

### Intelligence Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Portfolio average score | 93.7/100 (top chips only) | 85+ across all chips |
| Chips at production maturity | 1/12 (8%) | 50%+ |
| Cross-chip transfer patterns | 0 | 10+ validated patterns |
| Autonomous improvement cycles per week | ~5 (manual) | 50+ (automated) |
| Research-to-evidence conversion rate | Unknown | Tracked, 30%+ |

### Loop Health Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Loop velocity | Score points gained per iteration | > 2 pts/iteration |
| Fix success rate | Applied fixes that increase score | > 80% |
| Stall detection | Iterations with 0 score change | < 3 consecutive |
| Evidence freshness | Days since last research ingestion | < 7 days |
| Contradiction density | Contradictions found per 100 packets | 5-15% (healthy range) |

---

## Experimental Validation Plan

This PRD is NOT based on assumptions. Each phase will be validated through experimental runs.

### Experiment 1: Scaffold Speed Test
- **Method**: Scaffold 5 chips across 5 categories using the factory
- **Measure**: Time to scaffold, initial quality score, tests passing
- **Success**: All 5 score >= 45, < 15 min each, all tests pass

### Experiment 2: Auto-Improvement Depth Test
- **Method**: Run improve_chip() on each scaffold with max 20 iterations
- **Measure**: Score trajectory, fixes applied, where it plateaus
- **Success**: All 5 reach score >= 60 without human intervention

### Experiment 3: Full Loop Velocity Test
- **Method**: Run autoloop on 3 chips for 24 hours unattended
- **Measure**: Score trajectory, research gathered, evidence quality
- **Success**: At least 1 chip reaches score >= 75

### Experiment 4: Category Template Effectiveness
- **Method**: Compare scaffold+improve with vs without category templates
- **Measure**: Score delta after 10 iterations
- **Success**: Category-templated chips score 10+ points higher

### Experiment 5: Cross-Chip Transfer Test
- **Method**: Extract patterns from startup-yc, apply to 3 weak chips
- **Measure**: Score improvement from transferred patterns
- **Success**: Each recipient gains >= 5 points from transfer

### Experiment 6: End-to-End Factory Test
- **Method**: Human writes brief → factory runs fully autonomous → measure final state
- **Measure**: Total human time, total autonomous time, final score, evidence quality
- **Success**: < 30 min human time, score >= 60 within 4 hours

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Auto-generated code is low quality | Scaffold skeleton follows proven patterns from mature chips; all output scored by rubric |
| Recursive loops diverge or stall | Max iteration limits, stall detection, score regression detection (revert on decrease) |
| Cross-chip transfer introduces domain contamination | Transfer patterns are structural only (scoring model, loop design), not domain content |
| Category templates are too generic | Templates provide defaults that are overridden by domain brief; they accelerate, not replace |
| Auto-fixes pass rubric but produce meaningless content | Content-dependent checks (evidence, evaluation depth) require real research, not stubs |
| Human oversight bottleneck returns | Progressive autonomy levels: start gated, reduce gates as chip proves reliability |

---

## Appendix A: Current Portfolio Gap Analysis

Based on quality rubric analysis of all discovered chips:

### Highest-Impact Quick Fixes (applicable to ALL chips scoring < 80)

| Fix | Points Recovered | Effort | Automatable |
|-----|-----------------|--------|-------------|
| Add frontier block to manifest | 2-3 pts | 5 min | Yes |
| Create obsidian-vault/ directory | 3 pts | 1 min | Yes |
| Add memory backend to project.json | 3 pts | 1 min | Yes |
| Add self_edit config to project.json | 3 pts | 2 min | Yes |
| Create docs/architecture.md | 3 pts | 5 min | Yes |
| Add field_patterns to manifest | 2 pts | 10 min | Yes |
| Add baseline candidate trial | 4 pts | 15 min | Partial |
| **Total quick-fix potential** | **18-21 pts** | **< 40 min** | **Mostly** |

### Chip-Specific Improvement Paths

| Chip | Current Estimate | Quick Fix Target | Domain Work for Production |
|------|-----------------|------------------|---------------------------|
| content | ~74 | 85+ | Improve evidence depth, add benchmarks |
| predictive-worlds-lab | ~40 (no manifest) | 60+ (add chip contract) | Wrap existing code in 4-hook pattern |
| pokemon-red | Unknown | 60+ | Game-specific scoring and evidence |
| roblox-development | Unknown | 60+ | Platform-specific benchmarks |
| xcontent | Unknown | 60+ | Content quality metrics |

---

## Appendix B: Evidence From Existing Chips

### What Makes startup-yc (v0.3.0) the Most Mature

1. **DSPy integration** — Model-assisted packet extraction and probe ranking
2. **Agent cooldown** — 6-hour default prevents overuse of same research paths
3. **Anchor retirement** — Prevents fixation on stale evidence
4. **Selection memory** — Recent 12 limit forces exploration diversity
5. **Doctrine review cadence** — Every 15 runs, review underweight areas
6. **Contradiction detection** — Tags, category-level contradictions, penalty system
7. **External benchmark** — startup-bench as independent truth surface
8. **Coverage maturity tracking** — Knows what areas are well-researched vs sparse

### What Makes trading-crypto Effective Despite Lower Maturity

1. **Real data** — JSONL candle data, timeline packs, contract windows
2. **Walk-forward validation** — Holdout splits prevent overfitting
3. **Tri-loop architecture** — Learning → Backtest → Paper-trade progression
4. **46+ automated cycles** — Evidence of sustained recursive improvement
5. **Regime classification** — Compression, event-driven, trend, range, volatile

### What Makes web-designer Unique

1. **Massive reference vault** — 90+ design studies from award sites
2. **Site scaffolding** — Generates actual code (React, Next, Astro)
3. **Research review site** — HTML reports for human review
4. **Owner decision capture** — Structured feedback from human reviewers
5. **Test coverage** — Only conforming chip with tests (2,008 lines)

---

## Appendix C: Ideal Recursive Loop Architecture

```
┌──────────────────────────────────────────────────────┐
│                  RECURSIVE LOOP                       │
│                                                       │
│  ┌─────────┐    ┌──────────┐    ┌─────────────┐     │
│  │ EVALUATE │───►│ GAP      │───►│ AUTO-FIX    │     │
│  │ (score)  │    │ ANALYZER │    │ (structural)│     │
│  └────▲─────┘    └──────────┘    └──────┬──────┘     │
│       │                                  │            │
│       │          ┌──────────┐           │            │
│       │          │ SUGGEST  │◄──────────┘            │
│       │          │ (gaps +  │                         │
│       │          │ research)│                         │
│       │          └────┬─────┘                         │
│       │               │                               │
│       │          ┌────▼─────┐                         │
│       │          │ RESEARCH │                         │
│       │          │ (gather  │                         │
│       │          │ evidence)│                         │
│       │          └────┬─────┘                         │
│       │               │                               │
│       │          ┌────▼─────┐                         │
│       │          │ PACKETS  │                         │
│       │          │ (store   │                         │
│       │          │ evidence)│                         │
│       │          └────┬─────┘                         │
│       │               │                               │
│       │          ┌────▼──────┐                        │
│       └──────────│ WATCHTOWER│                        │
│                  │ (observe) │                        │
│                  └───────────┘                        │
│                                                       │
│  Telemetry: score_trajectory, loop_velocity,         │
│             stall_detection, evidence_freshness       │
└──────────────────────────────────────────────────────┘
```

**Key difference from current architecture**: The `GAP ANALYZER` sits between evaluate and suggest, converting score failures into specific research/fix directives. Currently evaluate and suggest are independent — the gap analyzer creates the missing data bridge.
