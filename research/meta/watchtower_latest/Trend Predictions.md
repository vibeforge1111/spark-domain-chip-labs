# Trend Predictions

> Last updated: 2026-03-24 20:28 UTC
> Engine: MiroFish-inspired multi-agent simulation
> Evidence lane: exploratory_frontier

# Trend Prediction Report

> Generated: 2026-03-24T20:28:41.896584+00:00
> Evidence lane: exploratory_frontier
> Rounds simulated: 15
> Personas: 30

## Domain Predictions

| Domain | Choice Signal | Final Adoption | Peak Interest | Timeline |
|--------|---------------|----------------|---------------|----------|
| defi-architect | 33.34% | 3.33% | 93.33% | uncertain (no tipping point detected) |
| game-balance | 30.00% | 6.67% | 96.67% | uncertain (no tipping point detected) |
| indie-hacker | 13.34% | 3.33% | 53.33% | uncertain (no tipping point detected) |
| ai-agent-builder | 10.00% | 0.00% | 73.33% | uncertain (no tipping point detected) |
| compliance-shield | 6.67% | 0.00% | 63.33% | uncertain (no tipping point detected) |
| legal-ops | 3.33% | 0.00% | 53.33% | uncertain (no tipping point detected) |

## Cross-Domain Analysis

### Portfolio Gaps
- Fewer than 2 domains show strong adoption -- portfolio concentration risk.
- Weak adoption signals for: defi-architect, game-balance, indie-hacker, ai-agent-builder, compliance-shield, legal-ops

### Simulation vs Static Scoring

| Domain | Simulation | Static | Delta |
|--------|-----------|--------|-------|
| defi-architect | 3.33% | 0.8740 | -0.8407 |
| game-balance | 6.67% | 0.7305 | -0.6638 |
| indie-hacker | 3.33% | 0.7980 | -0.7647 |
| ai-agent-builder | 0.00% | 0.8270 | -0.8270 |
| compliance-shield | 0.00% | 0.6765 | -0.6765 |
| legal-ops | 0.00% | 0.6445 | -0.6445 |

## Calibration
- Aggregate Brier score: 0.142814
- Better than constant (0.5): True
- Better than frequency: True
- Open prediction contracts: 6

---

*All predictions are exploratory_frontier. Do not auto-promote to doctrine without replay-benchmarking.*

## How To Use This

1. **Do NOT auto-promote** these predictions to doctrine
2. Predictions are `exploratory_frontier` until replay-benchmarked
3. Use as input to the **suggest** hook for domain discovery candidates
4. Cross-reference with static scoring from trend_scanner for calibration

## Links

- [[Lab Home]]
- [[Portfolio Dashboard]]
- [[MiroFish Portfolio]]
- [[MiroFish Frontier]]
