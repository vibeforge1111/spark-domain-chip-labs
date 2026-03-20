# MiroFish Prediction Engine

A zero-dependency multi-agent simulation engine for predicting adoption dynamics. Runs Monte Carlo ensembles with stakeholder personas to forecast which ideas, products, technologies, or domains will gain traction -- and which won't.

**No LLM calls. No external APIs. Pure Python. Deterministic with seed.**

## What It Does

You define a universe of **domains** (things you're evaluating) and the engine:

1. Builds a **knowledge graph** of relationships between domains (enables, competes, depends on)
2. Generates **stakeholder personas** (early adopters, skeptics, investors, builders, etc.)
3. Runs a **bounded simulation** where personas evaluate domains, share signals, and influence each other
4. Produces **adoption curves**, confidence intervals, tipping points, and sensitivity analysis
5. Outputs a **calibrated prediction** with Brier scoring against historical data

The result: a ranked forecast with confidence intervals that tells you what to build, what to avoid, and what factors drive each outcome.

## Quick Start

```bash
cd spark-domain-chip-labs
pip install -e .
```

### 1. Run the Full 1000-Agent Prediction

```bash
python scripts/predict_1000_agents.py
```

This runs:
- **Flagship simulation**: 1000 agents x 32 domains x 20 rounds (640K evaluations)
- **Monte Carlo ensemble**: 10 runs x 240 agents for confidence intervals (p10/p90)
- **Sensitivity analysis**: Tests 4 factors to identify what drives each domain's adoption
- **Actionable summary**: High-confidence picks, uncertain bets, and domains to avoid

### 2. View the Interactive Visualization

```bash
cd viz
python -m http.server 8888
# Open http://localhost:8888/mirofish-graph.html
```

Features:
- Force-directed knowledge graph with 59 nodes and 596 edges
- Play/pause simulation playback across 20 rounds
- Click any domain to see its adoption curve (builder vs enterprise vs advocacy)
- Live activity feed showing adoption surges, shock events, and stage transitions
- Minimap, zoom, pan, and keyboard controls (Space = play, arrows = scrub)

### 3. Use It Programmatically

```python
from chip_labs.mirofish.graph import build_graph_from_opportunities
from chip_labs.mirofish.simulation import run_simulation, run_ensemble, run_sensitivity
from chip_labs.mirofish.signals import signals_from_opportunities, signals_from_graph, create_shock

# Define your domains
domains = [
    {
        "domain_id": "my-product",
        "label": "My Product",
        "description": "What this thing does",
        "scores": {
            "market_size": 0.85,
            "data_availability": 0.70,
            "benchmark_feasibility": 0.75,
            "community_demand": 0.80,
            "spark_ecosystem_fit": 0.60,
            "monetization_potential": 0.90,
        },
        "related_chips": [],
        "evidence_sources": ["github", "producthunt"],
    },
    # ... more domains
]

# Build the knowledge graph
graph = build_graph_from_opportunities(domains)

# Generate signals from domain data
domain_ids = [d["domain_id"] for d in domains]
signals = signals_from_opportunities(domains) + signals_from_graph(graph)

# Inject shock events (optional)
shocks = [
    create_shock("viral_adoption", ["my-product"], inject_at_round=5),
    create_shock("market_crash", ["competitor-a"], inject_at_round=8),
]

# Single simulation
result = run_simulation(graph, domain_ids, signals=signals, shocks=shocks, max_rounds=20, seed=42)
for d_id in domain_ids:
    rate = result["domains"][d_id]["final_adoption_rate"]
    print(f"{d_id}: {rate:.1%} adoption")

# Monte Carlo ensemble (confidence intervals)
ensemble = run_ensemble(
    graph, domain_ids, signals=signals, shocks=shocks,
    max_rounds=20, n_runs=50, base_seed=42, count_per_type=30,
)
for d_id in domain_ids:
    stats = ensemble["domains"][d_id]
    print(f"{d_id}: {stats['mean_adoption']:.1%} (p10={stats['p10_adoption']:.0%}, p90={stats['p90_adoption']:.0%})")

# Sensitivity analysis (what drives adoption?)
sensitivity = run_sensitivity(
    graph, domain_ids, signals=signals, shocks=shocks,
    max_rounds=20, seed=42,
)
for d_id in domain_ids:
    factor = sensitivity["most_sensitive_factor"][d_id]
    print(f"{d_id}: most sensitive to {factor}")
```

## How It Works

### Architecture

```
Domains (your inputs)
    |
    v
Knowledge Graph Builder -----> Entity-relationship graph
    |                          (ENABLES, COMPETES_WITH, DEPENDS_ON, etc.)
    v
Persona Generator -----------> 8 stakeholder archetypes x N variants
    |                          (early adopter, skeptic, investor, builder, ...)
    v
Signal Injector -------------> Market signals + shock events
    |                          (VC funding, viral tweets, regulatory bans, ...)
    v
Simulation Engine -----------> 20-round adoption simulation
    |   |                      6 phases per round:
    |   |                        1. Signal propagation (awareness)
    |   |                        2. Churn check (regression)
    |   |                        3. Influence propagation (topology effects)
    |   |                        4. Record adoption state
    |   |                        5. Persona learning (threshold adaptation)
    |   |                        6. Signal decay
    |   |
    |   +---> Monte Carlo Ensemble (N runs, different persona seeds)
    |   +---> Sensitivity Analysis (vary signals, thresholds, counts, timing)
    |   +---> Dual-Context (builder community vs enterprise market)
    |
    v
Calibration Engine ----------> Brier scoring against historical replay cases
    |
    v
Report Generator ------------> Ranked predictions with confidence + key drivers
```

### Adoption Funnel

Each persona progresses through 6 stages per domain:

```
unaware --> aware --> interested --> evaluating --> adopted --> advocating
```

- **Stage difficulty scales exponentially**: unaware->aware is easy (0.2x threshold), evaluating->adopted is hard (1.3x threshold)
- **Attention budget**: Personas can only deeply evaluate ~10 domains per round (finite attention)
- **Churn**: Pre-commitment stages (aware/interested/evaluating) can regress if signal fades. Adopted/advocating personas are immune (sunk cost)
- **Learning**: Adopted personas adjust their thresholds based on observed adoption rates (confidence boost or caution)

### 8 Persona Types

| Type | Influence | Threshold | Risk | Reach | Role |
|------|-----------|-----------|------|-------|------|
| Early Adopter | 0.70 | 0.20 | 0.90 | 0.60 | Jumps on new tech fast |
| Builder | 0.80 | 0.35 | 0.70 | 0.70 | Ships code, high influence |
| Investor | 0.90 | 0.40 | 0.60 | 0.90 | Funds ecosystem, huge reach |
| Skeptic | 0.50 | 0.80 | 0.20 | 0.40 | Slow to adopt, valid concerns |
| Enterprise Buyer | 0.60 | 0.70 | 0.30 | 0.50 | Big budget, needs ROI proof |
| Content Creator | 0.75 | 0.30 | 0.65 | 0.85 | Amplifies signal, tutorials |
| Researcher | 0.55 | 0.50 | 0.50 | 0.40 | Provides rigor and validation |
| Regulator | 0.85 | 0.90 | 0.10 | 0.30 | Can block or enable adoption |

Each persona gets deterministic trait variation from the seed, so no two are identical.

### Signal Types

| Signal | Default Strength | Decay/Round | Effect |
|--------|-----------------|-------------|--------|
| GitHub Trending | 0.60 | 0.08 | Developer interest |
| Product Hunt Launch | 0.70 | 0.10 | Market interest |
| Viral Tweet | 0.50 | 0.15 | High impact, fast decay |
| VC Funding | 0.80 | 0.03 | Strong, persistent |
| Regulation | 0.90 | 0.02 | Very persistent |
| Competitor Launch | 0.65 | 0.05 | Competitive pressure |
| Community Request | 0.55 | 0.06 | Organic demand |

### Shock Templates

Inject sudden events at specific rounds:

| Shock | Strength | Effect | Decay | Use Case |
|-------|----------|--------|-------|----------|
| Market Crash | 0.90 | negative | 0.04 | Test resilience to downturns |
| Breakout Tool | 0.85 | positive | 0.05 | Simulate viral tool adoption |
| Regulatory Ban | 0.95 | negative | 0.02 | Test regulatory risk |
| Viral Adoption | 0.80 | positive | 0.08 | Simulate organic growth spikes |
| Ecosystem Integration | 0.70 | positive | 0.03 | Platform integration boost |

### Graph Topology Effects

The knowledge graph creates network effects:

- **ENABLES edges**: Adoption of domain A boosts domain B (weight x 0.3)
- **EXTENDS edges**: Proven ecosystem boost (weight x 0.4)
- **COMPETES_WITH edges**: Competitive displacement -- adopting A suppresses rival B (weight x 0.5)
- **Displacement**: When a persona commits to domain A and A strongly competes with B (weight > 0.7), B regresses one stage

### Dual-Context Simulation

Run the same domains in two market contexts:

- **Builder Community**: Default traits, lower thresholds, higher risk tolerance
- **Enterprise Market**: 1.2x adoption thresholds, 0.8x risk tolerance

This reveals domains that work in open-source/builder communities but struggle in enterprise sales (or vice versa).

## Adapting for Your Own Predictions

MiroFish works for any domain where you're predicting adoption/traction. Here's how to adapt it:

### Step 1: Define Your Domain Universe

Replace the domain list with whatever you're evaluating:

```python
# Predicting which features to build
features = [
    {
        "domain_id": "dark-mode",
        "label": "Dark Mode",
        "scores": {"market_size": 0.90, "data_availability": 0.95, "benchmark_feasibility": 0.90,
                   "community_demand": 0.95, "spark_ecosystem_fit": 0.80, "monetization_potential": 0.20},
        "related_chips": [],
        "evidence_sources": ["github"],
    },
    # ... more features
]
```

### Step 2: Define Relationships

The graph builder auto-generates relationships from `related_chips` and `evidence_sources`, but you can add custom edges:

```python
graph = build_graph_from_opportunities(features)
# Add custom competitive relationship
graph.add_edge("dark-mode", "high-contrast-mode", "COMPETES_WITH", weight=0.8)
# Add dependency
graph.add_edge("api-v2", "graphql-layer", "ENABLES", weight=0.9)
```

### Step 3: Inject Domain-Specific Signals

```python
from chip_labs.mirofish.signals import create_signal

signals = [
    create_signal("user-research", "community_request", ["dark-mode"], strength=0.9),
    create_signal("competitor-launch", "competitor_chip", ["api-v2"], strength=0.7),
]
```

### Step 4: Run and Interpret

```python
ensemble = run_ensemble(graph, domain_ids, signals=signals, n_runs=20, count_per_type=30)

# Sort by mean adoption
ranked = sorted(ensemble["domains"].items(), key=lambda x: x[1]["mean_adoption"], reverse=True)
for d_id, stats in ranked:
    width = stats["p90_adoption"] - stats["p10_adoption"]
    certainty = "HIGH" if width < 0.05 else "MEDIUM" if width < 0.15 else "LOW"
    print(f"{d_id}: {stats['mean_adoption']:.0%} ({certainty} confidence, CI: {stats['p10_adoption']:.0%}-{stats['p90_adoption']:.0%})")
```

### Use Cases

- **Product roadmap prioritization**: Which features will get adopted?
- **Market entry analysis**: Which markets are ready for your product?
- **Technology bets**: Which frameworks/tools will gain traction?
- **Content strategy**: Which topics will resonate with your audience?
- **Investment thesis**: Which sectors will grow vs stall?
- **Competitive analysis**: How does your domain compare against rivals?

## Calibration

Every prediction is scored against historical data using Brier scoring:

```python
from chip_labs.mirofish.calibration import calibration_report

# prediction_probs = {domain_id: predicted_probability}
cal = calibration_report(prediction_probs)
print(f"Brier score: {cal['brier_score']:.4f}")  # Lower is better (0 = perfect)
print(f"vs constant baseline: {cal['baseline_comparison']['constant_brier']:.4f}")
```

The engine includes 12 historical replay cases for backtesting. Add your own resolved predictions to improve calibration over time.

## File Structure

```
src/chip_labs/mirofish/
  __init__.py          # Public API exports
  graph.py             # Knowledge graph builder (DomainGraph)
  personas.py          # 8 persona types, generation, churn, learning
  simulation.py        # Core engine: run_simulation, run_ensemble, run_sensitivity
  signals.py           # Signal types, shock templates, decay
  calibration.py       # Outcome contracts, Brier scoring, replay cases
  report.py            # Structured prediction report generator

scripts/
  predict_1000_agents.py   # Full pipeline: flagship + ensemble + sensitivity
  export_viz_data.py       # Export simulation data as JSON for visualization

viz/
  mirofish-graph.html      # Interactive knowledge graph visualization
  mirofish_data.json       # Exported simulation data (auto-generated)

tests/
  test_graph.py            # 12 tests
  test_personas.py         # 28 tests (including churn + learning)
  test_simulation.py       # 35 tests (including ensemble + sensitivity + displacement)
  test_calibration.py      # 16 tests
  test_trend_prediction.py # 10 tests
```

## Key Design Decisions

1. **Zero external dependencies** -- No Neo4j, no LLM calls, no API keys. Pure Python dicts and deterministic math. The entire engine runs in seconds.

2. **Bounded agents (12-1000)** -- Each persona is a meaningful stakeholder archetype, not a social media bot. 1000 agents x 32 domains x 20 rounds = 640K evaluations in ~45 seconds.

3. **Simulation = exploratory only** -- Predictions are `exploratory_frontier` evidence, never auto-promoted to doctrine. "Never let a vivid simulation promote itself into doctrine."

4. **Calibration-first** -- Every prediction gets an outcome contract. Brier scoring before trust. If the engine isn't calibrated, the predictions are entertainment, not intelligence.

5. **Deterministic with seed** -- Same seed = same results. Change the seed = different persona variations. Monte Carlo ensemble = confidence intervals across seeds.

6. **Churn models real commitment** -- Adopted/advocating personas don't churn (sunk cost). Only pre-commitment stages regress. This prevents the "everything decays to zero" problem.

## Tests

```bash
python -m pytest tests/ -v
# 161 tests, all passing
```

## License

Private -- Spark ecosystem internal.
