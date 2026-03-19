# MiroFish-Inspired Trend Prediction Architecture

## What is MiroFish?

MiroFish is an open-source swarm intelligence prediction engine that uses:
1. **GraphRAG** -- Knowledge graph construction from diverse data sources
2. **Multi-agent social simulation** -- Stakeholder personas that simulate adoption dynamics
3. **Report generation** -- Structured prediction outputs with calibration data

## What We Borrow

### Graph Building (`mirofish/graph.py`)
- Entity-relationship graphs from domain opportunity data
- Entity types: technologies, communities, companies, trends, platforms, regulations
- Relationship types: ENABLES, COMPETES_WITH, DEPENDS_ON, SERVES, DISRUPTS, EXTENDS
- Zero deps -- plain Python dicts, not Neo4j/Zep

### Persona Generation (`mirofish/personas.py`)
- 8 differentiated stakeholder archetypes (early_adopter, builder, investor, skeptic, enterprise_buyer, content_creator, researcher, regulator)
- Each persona has: influence_score, adoption_threshold, risk_tolerance, network_reach, expertise_domains
- Bounded generation: 12-30 personas per simulation (not thousands)
- Deterministic variation from seed for reproducibility

### Social Simulation (`mirofish/simulation.py`)
- Bounded multi-round simulation (max 20 rounds)
- Adoption funnel: unaware -> aware -> interested -> evaluating -> adopted -> advocating
- Influence propagation between personas
- Dual-context simulation (builder community vs enterprise market)
- Output: adoption curves, consensus scores, tipping point detection

### Report Generation (`mirofish/report.py`)
- Per-domain predictions with adoption probability, timeline, confidence
- Cross-domain analysis with portfolio gaps and synergy opportunities
- Comparison with static scoring for calibration delta
- Markdown output for Obsidian integration

## What We DON'T Borrow

- **External APIs** -- No LLM calls, no web scraping, no Zep/Neo4j. Everything is deterministic.
- **Thousands of agents** -- We use 12-30 meaningful stakeholder archetypes, not social media bots.
- **Ungrounded narrative reports** -- All predictions carry evidence lane metadata and calibration scores.
- **Self-promoting predictions** -- Simulation output NEVER auto-promotes to doctrine.

## Evidence Lane Governance

This is the critical architectural boundary:

```
Simulation Output -> exploratory_frontier
                     |
                     v
              Replay-benchmarked?
              /              \
            No                Yes
            |                  |
            v                  v
    Stay exploratory    Promote to benchmark_grounded
```

**Rule**: Simulation predictions are `exploratory_frontier` until they have been replay-benchmarked against historical outcome data.

### Calibration Discipline (from predictive-worlds-lab)

Every prediction gets an **outcome contract**:
- Question (e.g., "Will defi-architect chip be built by Q3 2026?")
- Predicted probability
- Resolution deadline
- Resolution rule

Historical replay cases track which predictions were right. We use **Brier scoring** to measure calibration:
- Brier score = (predicted - actual)^2
- Lower is better (0.0 = perfect, 0.25 = random for binary)
- We compare against two baselines: constant 50% predictor and frequency-based predictor

## Signal & Shock Grammar (`mirofish/signals.py`)

### Signal Types
- `github_trending` -- Developer interest signal (decay: 0.08/round)
- `producthunt_launch` -- Market interest (decay: 0.10/round)
- `viral_tweet` -- Social amplification (decay: 0.15/round, fast)
- `vc_funding` -- Investment signal (decay: 0.03/round, slow)
- `regulation` -- Policy changes (decay: 0.02/round, very persistent)
- `competitor_chip` -- Competitive pressure (decay: 0.05/round)
- `community_request` -- Grassroots demand (decay: 0.06/round)

### Shock Templates
- `market_crash` -- Reduces investor/enterprise adoption
- `breakout_tool` -- Amplifies early adopter/builder awareness
- `regulatory_ban` -- Blocks regulated personas
- `viral_adoption` -- Mass awareness spike
- `ecosystem_integration` -- Reduces friction for builders/enterprise

Shocks are injected at specific simulation rounds to test domain robustness under different scenarios.

## Integration Points

### evaluate hook
`research_focus="trend_simulation"` runs the full simulation pipeline and returns:
- `trend_prediction_score` -- Inverse of Brier score (higher = better calibrated)
- `simulation_calibration` -- Raw Brier score
- `domain_predictions_count` -- Number of domains evaluated

### suggest hook
MiroFish trend simulation appears as a high-priority suggestion candidate, informing which domains to explore next.

### packets hook
`research_focus="trend_simulation"` emits a `trend_prediction` packet with:
- Domain predictions with adoption probabilities
- Cross-domain analysis
- Calibration summary
- Evidence lane: `exploratory_frontier`

### watchtower hook
Generates a "Trend Predictions" Obsidian page with:
- Simulation-backed domain rankings table
- Cross-domain analysis
- Calibration metrics
- Governance notes

## Design Principles

1. **Zero external deps** -- Pure Python, deterministic simulation, configurable seed
2. **Bounded agents** -- 12-30 meaningful personas, not thousands
3. **Simulation = exploratory only** -- Never auto-promote to doctrine
4. **Calibration-first** -- Every prediction gets an outcome contract with Brier scoring
5. **Dual-context** -- Builder community + enterprise market for comparative signals
6. **Shock grammar** -- Test domain robustness under market/regulatory/viral scenarios

## Key Insight from predictive-worlds-lab

> "Never let a vivid simulation promote itself into doctrine."

MiroFish is Layer 4 (optional simulation backend), not a governance system. The lab's governance comes from evidence lane discipline and Brier-scored calibration, not from simulation consensus scores.
