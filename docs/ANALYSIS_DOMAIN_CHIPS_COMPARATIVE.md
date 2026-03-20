# Comparative Analysis: Domain Chip Implementations

**Date**: 2026-03-20
**Source**: Cross-repo analysis of 4 domain chip repositories
**Method**: Direct code inspection, manifest comparison, pattern extraction

---

## Summary

| Chip | Version | Maturity | Lines of Code | Files | Tests | Evidence Type |
|------|---------|----------|---------------|-------|-------|---------------|
| startup-yc | 0.3.0 | Production | 9,434 | 244 | 0 | Research packets, DSPy |
| trading-crypto | 0.1.0 | Alpha | 3,592 | 451 | 0 | Backtest data, JSONL candles |
| web-designer | 0.1.0 | Alpha | 9,410 | 134 | 2,008 lines | Award references, vault |
| predictive-worlds-lab | N/A | Non-conforming | 5,699 | 73 | 1,536 lines | Replay cases, Brier scores |

## Boilerplate Patterns (Template Candidates)

These patterns are **identical** across all conforming chips:

1. **spark-chip.json schema**: `spark-chip.v1` + `spark-hook-io.v1` + 4 capabilities
2. **pyproject.toml**: `setuptools>=68`, `package-dir = {"" = "src"}`, `python >= 3.10`, `dependencies = []`
3. **CLI routing**: argparse with `--input`/`--output`, JSON in/out, `_load()`/`_write()` helpers
4. **project.json guardrails**: `blocked_command_fragments`, `consecutive_discard_limit: 3`, `max_loop_iterations: 8`, `require_clean_git`, `require_human_approval`
5. **Self-edit config**: `git_mode: manual`, `branch_prefix: self-edit/`, `auto_push: false`
6. **Memory backend**: `"local"` in all cases
7. **Evaluate return shape**: `{returncode, stdout, stderr, metrics, result: {claim, verdict, mechanism, boundary, recommended_next_step, evidence_lane}}`
8. **Verdict system**: approve / defer / reject

## Domain-Specific Patterns (Must Stay Custom)

| Aspect | trading-crypto | web-designer | startup-yc |
|--------|---------------|--------------|------------|
| Scoring | Doctrine/strategy/regime matrices | 7-axis design scoring | Factor catalog with priors |
| Mutations | 6 axes (regime-oriented) | 7 axes (aesthetics-oriented) | 7 axes (research-oriented) |
| Data | JSONL market candles | Design award references | YC/PG/SA research packets |
| External | None (self-contained) | Award site scraping | startup-bench, DSPy, YouTube |
| Knowledge | Doctrine cards | Reference studies | Research packets + sources |

## Maturity Gap: What v0.3.0 Has That v0.1.0 Doesn't

| Feature | startup-yc (v0.3.0) | Others |
|---------|---------------------|--------|
| DSPy integration | 2 slots | None |
| Agent cooldown | 6hr default | None |
| Anchor retirement | Prevents overuse | None |
| Selection memory | Recent 12 limit | None |
| Doctrine review cadence | Every 15 runs | None |
| Contradiction detection | Tag-based system | Basic only |
| Coverage maturity tracking | Yes | None |
| External benchmark | startup-bench | Inline only |

## The CLI Monolith Problem

| Chip | cli.py Lines | Mitigation |
|------|-------------|------------|
| startup-yc | 8,886 | None — single massive file |
| trading-crypto | 2,670 | backtest.py extracted (922 lines) |
| web-designer | 136 | Clean split: scoring.py (682), workflows.py (6,584) |

**Recommendation**: Web-designer's split pattern should be the template standard.

## Recursive Loop Architectures

### trading-crypto: Tri-Loop
```
Learning Loop → Backtest Loop → Paper-Trade Loop
     │                │                │
  Doctrine        Walk-forward     Promotion
  ingestion       validation       gating
```
- 46+ automated cycles visible in commits
- Contradiction probes prevent stagnation
- Variety backlog forces exploration

### web-designer: Research-First
```
Research Plan → Web Ingest → Packet Extraction → Evaluate → Promote
```
- Owner review decisions as feedback
- Site scaffolding validates design systems

### startup-yc: Governing State Machine
```
Refresh → DSPy Slot 1 → Quality Gate → Research Frontier →
Selection → Research Agent → DSPy Slot 2 → Benchmark →
Promotion → Trial Frontier → Real-World Validation → Memory Update
```
- Most sophisticated loop with 12 conditional stages
- Agent cooldown and stall detection
- YouTube transcript-backed discovery

## Key Finding: Test Coverage Inversely Correlates with Chip Maturity

The two most mature chips (startup-yc v0.3.0, trading-crypto v0.1.0 with 46 cycles) have **zero tests**. The two with tests (web-designer, predictive-worlds-lab) are less operationally mature. This suggests the recursive loop provides implicit testing through evaluation, but explicit tests are needed for structural regression prevention.

## Effort to Create a New Chip

| Phase | Time | Boilerplate % |
|-------|------|---------------|
| Minimum viable (v0.0.1) | 1-2 days | 55% |
| Real data integration (v0.1.0) | 1-2 weeks | 30% |
| Production maturity (v0.3.0) | 3-4 weeks | 15% |

**With scaffold engine**: Phase 1 drops to 15 minutes, Phase 2 to 2-3 days, Phase 3 to 1-2 weeks.
