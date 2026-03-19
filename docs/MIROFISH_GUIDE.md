# MiroFish: Multi-Agent Trend Prediction Engine

## Complete Guide to Building, Running, and Adapting Predictions

---

## Table of Contents

1. [What Is MiroFish?](#what-is-mirofish)
2. [Architecture Overview](#architecture-overview)
3. [How It Works (Step by Step)](#how-it-works)
4. [The 6 Modules](#the-6-modules)
5. [Running a Prediction](#running-a-prediction)
6. [Understanding the Output](#understanding-the-output)
7. [Tuning & Calibration](#tuning--calibration)
8. [Adapting for Any Domain](#adapting-for-any-domain)
9. [Real-World Examples](#real-world-examples)
10. [Visualization](#visualization)
11. [Troubleshooting](#troubleshooting)
12. [Design Decisions & Lessons Learned](#design-decisions--lessons-learned)

---

## What Is MiroFish?

MiroFish is a **multi-agent social simulation** that predicts adoption trends. Instead of using static scoring (which just ranks items by their attributes), MiroFish creates 1,000 AI personas that evaluate, adopt, and influence each other across multiple rounds -- producing dynamic adoption curves, tipping points, and consensus signals.

**The key insight**: Static scoring says "this domain has a high market score." MiroFish says "given 1,000 stakeholders with different risk tolerances, how does adoption actually spread through the network over time?"

### What It Predicts

- **Adoption probability**: What percentage of stakeholders will adopt each domain?
- **Tipping points**: At which round does adoption cross 50%?
- **Builder vs Enterprise gap**: How differently do builder communities and enterprise markets adopt?
- **Consensus vs disagreement**: Do stakeholders agree, or is there polarization?
- **Shock resilience**: How does adoption change when market crashes, regulations, or viral events hit?

### Core Principles

1. **Zero external dependencies** -- Pure Python, no LLM calls, no APIs, no databases
2. **Bounded simulation** -- Max 20 rounds, max ~1000 agents. Not unbounded chaos
3. **Deterministic** -- Same seed = same results. Reproducible predictions
4. **Calibration-first** -- Every prediction gets a Brier score. Trust is earned, not assumed
5. **Exploratory only** -- Simulation output is `exploratory_frontier`. Never auto-promotes to doctrine

---

## Architecture Overview

```
                    ┌─────────────────────────────────────┐
                    │           INPUT DATA                 │
                    │  (domain definitions + scores)       │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │         graph.py                     │
                    │  Build knowledge graph               │
                    │  59 nodes, 596 edges                 │
                    └──────────────┬──────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                     │
   ┌──────────▼─────────┐ ┌───────▼──────────┐ ┌───────▼──────────┐
   │   personas.py       │ │  signals.py       │ │  (shocks)        │
   │   Generate 1000     │ │  758 signals from │ │  5 shock events  │
   │   stakeholder agents│ │  opportunities +  │ │  at specific     │
   │   (8 types x 125)   │ │  graph edges      │ │  rounds          │
   └──────────┬──────────┘ └───────┬──────────┘ └───────┬──────────┘
              │                    │                     │
              └────────────────────┼─────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │        simulation.py                 │
                    │  20 rounds of:                       │
                    │  1. Signal propagation (awareness)   │
                    │  2. Attention-budgeted evaluation    │
                    │  3. Influence propagation            │
                    │  4. Adoption state recording         │
                    │  5. Signal decay                     │
                    └──────────────┬──────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                     │
   ┌──────────▼─────────┐ ┌───────▼──────────┐ ┌───────▼──────────┐
   │  calibration.py     │ │   report.py       │ │  Visualization   │
   │  Brier scoring      │ │   Prediction      │ │  Knowledge graph │
   │  Outcome contracts  │ │   reports         │ │  HTML/Canvas     │
   └─────────────────────┘ └──────────────────┘ └──────────────────┘
```

---

## How It Works

### The Simulation Loop (20 Rounds)

Each round represents a time period (roughly 1-2 weeks in real time). Here's exactly what happens:

#### Round N:

**Step 1: Shock Injection**
```
If any shock is scheduled for this round, add it to active signals.
Example: "Market Crash" hits at round 8, adding a negative signal to
trading-crypto, defi-architect, solana-dev, personal-finance.
```

**Step 2: Signal Propagation + Attention Budget**
```
For each of the 1000 personas:
  1. Compute awareness score for ALL 32 domains (probability union)
  2. Sort domains by awareness strength
  3. Only deeply evaluate the top 10 domains (attention budget)
  4. Domains the persona already has traction with are always evaluated
  5. Domains below the attention budget only get dampened discovery signal
```

The **attention budget** is the key differentiator. In reality, people can't pay attention to 32 things at once. This forces domains to compete for mindshare.

**Step 3: Persona Evaluation (Adoption Funnel)**
```
For each domain the persona evaluates:
  effective_signal = awareness * activity_score
  advance_threshold = adoption_threshold * stage_difficulty * (1 - risk * 0.2)

  If persona has adopted 5+ domains already:
    advance_threshold *= 1.0 + (adopted_count - 5) * 0.15  (fatigue)

  If effective_signal > advance_threshold:
    Advance one stage: unaware -> aware -> interested -> evaluating -> adopted -> advocating
```

Stage difficulty multipliers (the key gates):
| Transition | Difficulty | What It Means |
|-----------|-----------|---------------|
| unaware -> aware | 0.2x | Any signal gets noticed |
| aware -> interested | 0.45x | Moderate signal needed |
| interested -> evaluating | 0.8x | Real signal strength needed |
| evaluating -> adopted | 1.3x | **Hard gate** -- many domains stall here |
| adopted -> advocating | 1.7x | Strong conviction required |

**Step 4: Influence Propagation**
```
For each domain:
  Count advocates, adopters, evaluators
  adoption_fraction = weighted_count / total_personas
  avg_influence = weighted_influence_sum / influencer_count
  aggregate_influence = adoption_fraction * avg_influence

  For each persona still in early stages:
    If aggregate_influence > threshold * 0.8:
      Re-evaluate the domain (social proof effect)
```

**Step 5: Record State**
```
Take adoption snapshot: stage distribution, adoption rate, advocacy rate
Compute consensus score (how much do personas agree?)
Check for tipping point (first round where adoption > 50%)
```

**Step 6: Signal Decay**
```
Each signal loses strength over time:
  decayed_strength = base_strength - (decay_rate * rounds_elapsed)
  Remove signals that decay below 0.01
```

### Awareness Computation (Probability Union)

Instead of adding signal strengths (which leads to saturation), MiroFish uses probability union:

```
P(aware) = 1 - product(1 - signal_i)
```

This means:
- 1 signal at 0.5 = 0.50 awareness
- 2 signals at 0.5 = 0.75 awareness
- 5 signals at 0.5 = 0.97 awareness
- 10 signals at 0.5 = 0.999 awareness (diminishing returns)

This prevents signal flooding from making every domain look equally strong.

---

## The 6 Modules

### `graph.py` -- Knowledge Graph Builder

**What it does**: Builds an entity-relationship graph from your input data.

**Node types**: domain, technology, platform, community, regulation, trend, company

**Relationship types**: ENABLES, COMPETES_WITH, DEPENDS_ON, SERVES, DISRUPTS, EXTENDS

**Key function**: `build_graph_from_opportunities(opportunities)`
- Takes a list of opportunity dicts
- Creates domain nodes from each opportunity
- Seeds 12 core ecosystem nodes (GitHub, Product Hunt, X/Twitter, arXiv, etc.)
- Generates cross-domain edges based on score similarity:
  - Similarity > 0.85 -> COMPETES_WITH
  - Similarity > 0.70 -> ENABLES

```python
from chip_labs.mirofish.graph import build_graph_from_opportunities

graph = build_graph_from_opportunities(my_opportunities)
print(f"Nodes: {graph.node_count}, Edges: {graph.edge_count}")
```

### `personas.py` -- Stakeholder Generator

**What it does**: Creates differentiated agent archetypes that simulate real stakeholders.

**8 persona types**:

| Type | Influence | Threshold | Risk | Reach | Description |
|------|-----------|-----------|------|-------|-------------|
| early_adopter | 0.7 | 0.2 | 0.9 | 0.6 | Jumps on new tech fast |
| builder | 0.8 | 0.35 | 0.7 | 0.7 | Ships code, high influence |
| investor | 0.9 | 0.4 | 0.6 | 0.9 | Funds ecosystem, huge reach |
| skeptic | 0.5 | 0.8 | 0.2 | 0.4 | Slow to adopt, raises concerns |
| enterprise_buyer | 0.6 | 0.7 | 0.3 | 0.5 | Needs proven ROI |
| content_creator | 0.75 | 0.3 | 0.65 | 0.85 | Amplifies signal, tutorials |
| researcher | 0.55 | 0.5 | 0.5 | 0.4 | Provides rigor, domain expert |
| regulator | 0.85 | 0.9 | 0.1 | 0.3 | Can block/enable adoption |

**Key function**: `generate_personas(graph, domain_ids, count_per_type=125, seed=42)`
- `count_per_type=125` gives 1000 agents (125 x 8 types)
- `count_per_type=2` gives 16 agents (for testing)
- Deterministic variation from seed -- same seed = same persona traits

```python
from chip_labs.mirofish.personas import generate_personas

personas = generate_personas(graph, domain_ids, count_per_type=125, seed=42)
print(f"Generated {len(personas)} personas")
```

### `signals.py` -- Signal & Shock Grammar

**What it does**: Converts your input data into simulation signals, and defines shock events.

**7 signal types** (with default strength and decay rate):

| Signal Type | Strength | Decay/Round | Description |
|------------|----------|-------------|-------------|
| github_trending | 0.6 | 0.08 | Developer interest |
| producthunt_launch | 0.7 | 0.10 | Market interest |
| viral_tweet | 0.5 | 0.15 | High impact, fast decay |
| vc_funding | 0.8 | 0.03 | Strong, slow decay |
| regulation | 0.9 | 0.02 | Very persistent |
| competitor_chip | 0.65 | 0.05 | Competitive pressure |
| community_request | 0.4 | 0.06 | Grassroots demand |

**5 shock templates**:

| Shock | Effect | Strength | Affected Personas |
|-------|--------|----------|-------------------|
| market_crash | negative | 0.95 | investor, enterprise_buyer |
| breakout_tool | positive | 0.90 | early_adopter, builder, content_creator |
| regulatory_ban | negative | 0.95 | regulator, enterprise_buyer, investor |
| viral_adoption | positive | 0.85 | content_creator, early_adopter, builder |
| ecosystem_integration | positive | 0.80 | builder, enterprise_buyer |

**Signal bridge functions** (the critical link between static scores and simulation):

```python
from chip_labs.mirofish.signals import signals_from_opportunities, signals_from_graph

# Convert opportunity scores into simulation signals
opp_signals = signals_from_opportunities(opportunities)

# Generate cross-domain influence from graph edges
graph_signals = signals_from_graph(graph)

all_signals = opp_signals + graph_signals
```

`signals_from_opportunities` generates three kinds of signals per domain:
1. **Community demand** -- from `community_demand` score (if > 0.5)
2. **Market signals** -- from each evidence source (strength = composite * source_boost)
3. **Ecosystem pull** -- from related chips (if ecosystem_fit > 0.6)

`signals_from_graph` generates cross-domain influence:
- **EXTENDS** edges -> "existing chip validates domain" signals
- **ENABLES** edges -> "technology enables domain" signals
- **COMPETES_WITH** edges (weight > 0.80) -> competitive pressure signals

### `simulation.py` -- The Simulation Engine

**Key functions**:

```python
from chip_labs.mirofish.simulation import run_simulation, run_dual_context

# Single context
result = run_simulation(graph, domain_ids, personas=personas,
                        signals=signals, shocks=shocks,
                        max_rounds=20, seed=42, context="builder_community")

# Dual context (builder vs enterprise comparison)
result = run_dual_context(graph, domain_ids, signals=signals,
                          shocks=shocks, max_rounds=20, seed=42)
```

**Parameters you can tune**:
- `max_rounds` -- Simulation length (1-20, default 20)
- `seed` -- Random seed for reproducibility
- `context` -- `"builder_community"` (default) or `"enterprise_market"` (higher thresholds, lower risk)
- `personas` -- Pass pre-generated personas or let it auto-generate
- `signals` -- Initial signals to inject
- `shocks` -- Shock events with `inject_at_round` timing

### `calibration.py` -- Brier Scoring & Outcome Contracts

**What it does**: Measures prediction accuracy against historical outcomes.

```python
from chip_labs.mirofish.calibration import replay_calibration, calibration_report

# Check calibration against 8 historical cases
replay = replay_calibration()
print(f"Brier score: {replay['aggregate_brier']}")
print(f"Beats constant 0.5: {replay['better_than_constant']}")
print(f"Beats frequency: {replay['better_than_frequency']}")

# Create outcome contracts for new predictions
predictions = {"defi-architect": 0.585, "supply-chain": 0.029}
report = calibration_report(predictions, replay)
```

**Brier score** measures prediction accuracy:
- 0.0 = perfect prediction
- 0.25 = coin flip (random)
- Lower is better

**Outcome contracts** create accountability: "Will defi-architect chip be built within 6 months?" with a resolution rule, deadline, and predicted probability. When the deadline passes, you resolve the contract and compute the Brier score.

### `report.py` -- Prediction Report Generator

```python
from chip_labs.mirofish.report import generate_prediction_report, format_report_markdown

report = generate_prediction_report(simulation_results, static_rankings, calibration_data)
markdown = format_report_markdown(report)
```

Produces structured reports with:
- Per-domain: adoption probability, timeline estimate, confidence level, drivers, risks
- Cross-domain: portfolio gaps, synergy opportunities, simulation vs static delta
- Calibration: Brier scores, outcome contracts

---

## Running a Prediction

### Quick Start (16 agents, fast)

```python
import sys
sys.path.insert(0, "src")

from chip_labs.mirofish.graph import build_graph_from_opportunities
from chip_labs.mirofish.personas import generate_personas
from chip_labs.mirofish.simulation import run_simulation
from chip_labs.mirofish.signals import signals_from_opportunities, signals_from_graph

# 1. Define your domains
domains = [
    {
        "domain_id": "my-domain",
        "label": "My Domain",
        "description": "What this domain does.",
        "scores": {
            "market_size": 0.8,
            "data_availability": 0.7,
            "benchmark_feasibility": 0.6,
            "community_demand": 0.9,
            "spark_ecosystem_fit": 0.5,
            "monetization_potential": 0.75,
        },
        "composite_score": 0.72,  # weighted average of scores
        "related_chips": [],
        "evidence_sources": ["github", "community"],
    },
    # ... add more domains
]

# 2. Build graph
graph = build_graph_from_opportunities(domains)

# 3. Generate signals
domain_ids = [d["domain_id"] for d in domains]
signals = signals_from_opportunities(domains) + signals_from_graph(graph)

# 4. Generate personas (16 agents for quick test)
personas = generate_personas(graph, domain_ids, count_per_type=2, seed=42)

# 5. Run simulation
result = run_simulation(graph, domain_ids, personas=personas,
                        signals=signals, max_rounds=20, seed=42)

# 6. Read results
for d_id, data in result["domains"].items():
    print(f"{d_id}: {data['final_adoption_rate']:.1%}")
```

### Full 1000-Agent Prediction

```bash
cd spark-domain-chip-labs
python scripts/predict_1000_agents.py
```

This runs the complete pipeline with:
- 32 domains (10 existing + 22 candidates)
- 1000 agents (125 per type x 8 types)
- 758 signals (119 opportunity + 639 graph)
- 5 shock events
- Builder + enterprise contexts
- ~50 seconds total runtime

### With Visualization

```bash
# 1. Export data
python scripts/export_viz_data.py

# 2. Serve visualization
cd viz && python -m http.server 8000

# 3. Open http://localhost:8000/mirofish-graph.html
```

---

## Understanding the Output

### Key Metrics

| Metric | Range | What It Means |
|--------|-------|---------------|
| `builder_adoption` | 0-100% | % of personas in "adopted" or "advocating" stage |
| `enterprise_adoption` | 0-100% | Same, but with enterprise context (higher barriers) |
| `advocacy_rate` | 0-100% | % of personas actively advocating (highest stage) |
| `tipping_point` | R0-R20 or None | First round where adoption > 50% |
| `consensus` | 0-100% | How much personas agree on stage (high = strong signal, low = polarized) |
| `disagreement` | 0-100% | Inverse of consensus |
| `builder-enterprise gap` | -100% to +100% | How much faster builders adopt vs enterprise |

### Reading the Rankings

```
#    Domain                     Builder  Enterprise    Gap  Advocacy  Tipping
1    prompt-engineer             68.1%      62.5% +5.6%     0.8%       R3
2    indie-hacker                68.0%      62.3% +5.7%     0.8%       R3
...
31   pokemon-red                  2.5%       1.2%  +1.3%    0.0%     None
32   predictive-worlds-lab        0.0%       0.0%  +0.0%    0.0%     None
```

- **Builder > Enterprise**: Normal. Builders adopt faster than enterprises
- **Tipping R3**: Reached 50% adoption by round 3 (very fast)
- **Tipping None**: Never reached 50% -- adoption is weak
- **Gap +5.6%**: Builders adopt 5.6 percentage points more than enterprise
- **Advocacy 0.8%**: Only 8 out of 1000 agents are actively advocating

### Sim vs Static Delta

```
Domain                    Sim     Static    Delta    Signal
prompt-engineer          68.1%    0.8235   -0.14    SIM LOWER
newsletter-growth        68.0%    0.7190   -0.04    ALIGNED
supply-chain              2.9%    0.6180   -0.59    SIM LOWER
```

- **SIM HIGHER**: Simulation predicts more adoption than static scoring suggests (undervalued by static)
- **SIM LOWER**: Simulation predicts less adoption (overvalued by static -- competition/attention effects not captured by static scoring)
- **ALIGNED**: Delta < 5% -- both agree

---

## Tuning & Calibration

### Parameters to Tune

#### Stage Difficulty (in `personas.py`)

This is the **most impactful parameter**. Controls how hard it is to advance through adoption stages.

```python
stage_difficulty = {
    0: 0.2,    # unaware -> aware
    1: 0.45,   # aware -> interested
    2: 0.8,    # interested -> evaluating
    3: 1.3,    # evaluating -> adopted (KEY GATE)
    4: 1.7,    # adopted -> advocating
}
```

- **Raise stage 3-4**: Fewer domains reach adoption (more selective)
- **Lower stage 3-4**: More domains reach adoption (more permissive)
- Stage 4 (advocating) should always be higher than stage 3

#### Attention Budget (in `simulation.py`)

Controls how many domains each persona evaluates per round.

```python
attention_budget = min(10, max(4, len(domains) // 3))
```

- **Lower budget (3-5)**: More competition between domains, sharper differentiation
- **Higher budget (10-15)**: More domains get evaluated, less differentiation
- For 32 domains, budget of 10 means each persona focuses on ~1/3 of domains

#### Adoption Fatigue (in `personas.py`)

Prevents personas from adopting everything.

```python
if adopted_count > 5 and current_idx >= 3:
    advance_threshold *= 1.0 + (adopted_count - 5) * 0.15
```

- **Lower threshold (3)**: Personas become selective earlier
- **Higher threshold (8)**: Personas can adopt many domains before fatigue
- **0.15 multiplier**: How much harder each additional domain makes it

#### Enterprise Context (in `simulation.py`)

```python
if context == "enterprise_market":
    p["adoption_threshold"] *= 1.2  # 20% higher barrier
    p["risk_tolerance"] *= 0.8      # 20% less risk-tolerant
```

#### Signal Decay Rates (in `signals.py`)

```python
"viral_tweet": {"decay_per_round": 0.15}  # Fast decay (viral is fleeting)
"vc_funding": {"decay_per_round": 0.03}   # Slow decay (money talks for a while)
```

### Calibration Workflow

1. **Run replay calibration** against historical cases:
   ```python
   from chip_labs.mirofish.calibration import replay_calibration
   replay = replay_calibration()
   print(f"Brier: {replay['aggregate_brier']}")  # Lower is better
   ```

2. **Compare to baselines**:
   - Constant 0.5 predictor (always says 50/50)
   - Frequency predictor (uses base rate)
   - Your predictions should beat both

3. **Create outcome contracts** for new predictions:
   ```python
   contract = create_outcome_contract(
       question="Will defi-architect chip be built by Q4 2026?",
       domain_id="defi-architect",
       predicted_probability=0.585,
       resolution_deadline="2026-12-31",
       resolution_rule="Chip exists on Desktop with spark-chip.json",
   )
   ```

4. **Resolve when deadline passes** and compute Brier score

---

## Adapting for Any Domain

MiroFish can predict adoption for anything -- not just domain chips. Here's how to adapt it.

### Step 1: Define Your Domain Universe

Replace the domain definitions with whatever you're predicting:

```python
# Example: Predicting which programming languages will gain adoption
LANGUAGES = [
    {
        "domain_id": "rust",
        "label": "Rust",
        "description": "Systems programming language focused on safety.",
        "scores": {
            "market_size": 0.75,          # How big is the potential user base?
            "data_availability": 0.85,     # How much data/tooling exists?
            "benchmark_feasibility": 0.80, # Can we measure adoption?
            "community_demand": 0.90,      # How vocal is demand?
            "spark_ecosystem_fit": 0.60,   # Ecosystem integration potential
            "monetization_potential": 0.70, # Revenue opportunity
        },
        "composite_score": 0.77,
        "related_chips": [],
        "evidence_sources": ["github", "community"],
    },
    # ... more languages
]
```

**The 6 score dimensions can be renamed** but should always capture:
1. **Market size** -- How big is the addressable market?
2. **Data availability** -- How much signal data exists?
3. **Benchmark feasibility** -- Can success be measured?
4. **Community demand** -- How vocal is the demand?
5. **Ecosystem fit** -- How well does it fit the broader ecosystem?
6. **Monetization potential** -- Can it generate revenue?

### Step 2: Customize Persona Types

Edit `PERSONA_TYPES` in `personas.py` to match your domain:

```python
# Example: Predicting SaaS tool adoption
PERSONA_TYPES = {
    "power_user": {
        "influence_score": 0.8,
        "adoption_threshold": 0.25,
        "risk_tolerance": 0.85,
        "network_reach": 0.7,
    },
    "manager": {
        "influence_score": 0.7,
        "adoption_threshold": 0.5,
        "risk_tolerance": 0.4,
        "network_reach": 0.6,
    },
    "budget_holder": {
        "influence_score": 0.9,
        "adoption_threshold": 0.7,
        "risk_tolerance": 0.2,
        "network_reach": 0.5,
    },
    # ... etc
}
```

**Guidelines for persona traits**:
- `influence_score` (0-1): How much this persona type affects others' decisions
- `adoption_threshold` (0-1): How much signal is needed before they act (higher = more conservative)
- `risk_tolerance` (0-1): Willingness to try unproven things (higher = more adventurous)
- `network_reach` (0-1): How far their influence spreads (higher = more connected)

### Step 3: Customize Signal Types

Edit `SIGNAL_TYPES` in `signals.py`:

```python
# Example: Predicting restaurant success
SIGNAL_TYPES = {
    "yelp_review": {
        "default_strength": 0.5,
        "decay_per_round": 0.08,
    },
    "food_critic": {
        "default_strength": 0.8,
        "decay_per_round": 0.04,
    },
    "instagram_viral": {
        "default_strength": 0.6,
        "decay_per_round": 0.20,  # Very fast decay
    },
    "health_inspection": {
        "default_strength": 0.9,
        "decay_per_round": 0.01,  # Very persistent
    },
}
```

### Step 4: Customize Shock Templates

```python
# Example: Predicting crypto token adoption
SHOCK_TEMPLATES = {
    "rug_pull": {
        "signal_type": "regulation",
        "strength_override": 0.95,
        "affected_persona_types": ["investor", "trader"],
        "effect": "negative",
    },
    "exchange_listing": {
        "signal_type": "vc_funding",
        "strength_override": 0.85,
        "affected_persona_types": ["trader", "early_adopter"],
        "effect": "positive",
    },
}
```

### Step 5: Customize the Signal Bridge

Edit `signals_from_opportunities()` in `signals.py` to map your score dimensions to signal types:

```python
# Map your evidence sources to signal types
_SOURCE_TO_SIGNAL = {
    "github": "github_trending",
    "app_store": "producthunt_launch",
    "social_media": "viral_tweet",
    "investors": "vc_funding",
    # ... your mappings
}
```

### Step 6: Add Replay Cases for Calibration

Edit `REPLAY_CASES` in `calibration.py` with historical outcomes:

```python
REPLAY_CASES = [
    {
        "domain_id": "something-that-succeeded",
        "question": "Did X get adopted?",
        "predicted_probability": 0.75,
        "actual_outcome": True,
    },
    {
        "domain_id": "something-that-failed",
        "question": "Did Y get adopted?",
        "predicted_probability": 0.30,
        "actual_outcome": False,
    },
]
```

### Step 7: Write Your Prediction Script

```python
# predict_my_domain.py
import sys
sys.path.insert(0, "src")

from chip_labs.mirofish.graph import build_graph_from_opportunities
from chip_labs.mirofish.personas import generate_personas
from chip_labs.mirofish.simulation import run_simulation
from chip_labs.mirofish.signals import signals_from_opportunities, signals_from_graph, create_shock
from chip_labs.mirofish.calibration import calibration_report
from chip_labs.mirofish.report import generate_prediction_report

# Your domain data
MY_DOMAINS = [...]  # Step 1

# Build pipeline
graph = build_graph_from_opportunities(MY_DOMAINS)
domain_ids = [d["domain_id"] for d in MY_DOMAINS]
personas = generate_personas(graph, domain_ids, count_per_type=125, seed=42)
signals = signals_from_opportunities(MY_DOMAINS) + signals_from_graph(graph)

# Optional: custom shocks
shocks = [
    create_shock("my_shock_template", ["domain-a", "domain-b"], inject_at_round=5),
]

# Run simulation
result = run_simulation(graph, domain_ids, personas=personas,
                        signals=signals, shocks=shocks, max_rounds=20)

# Generate report
report = generate_prediction_report(result)
```

### Full Adaptation Checklist

- [ ] Define domain universe (list of dicts with 6 score dimensions)
- [ ] Customize persona types for your stakeholder ecosystem
- [ ] Customize signal types and decay rates
- [ ] Customize shock templates for your risk scenarios
- [ ] Update the signal bridge (`_SOURCE_TO_SIGNAL` mapping)
- [ ] Add historical replay cases for calibration
- [ ] Write prediction script
- [ ] Run and tune (adjust stage difficulty, attention budget)
- [ ] Create outcome contracts for accountability

---

## Real-World Examples

### Example 1: Predicting Domain Chip Adoption (what we built)

- **32 domains** (10 existing chips + 22 candidates)
- **1000 agents** (125 per type x 8 types)
- **758 signals** (119 opportunity + 639 graph)
- **5 shocks** (market crash, breakout tool, regulatory ban, viral adoption, ecosystem integration)
- **Result**: prompt-engineer (68.1%) and indie-hacker (68.0%) are top picks. supply-chain (2.9%) and predictive-worlds-lab (0%) are bottom.

### Example 2: Predicting SaaS Tool Adoption (hypothetical)

```python
TOOLS = [
    {"domain_id": "linear", "label": "Linear", "scores": {...}},
    {"domain_id": "notion", "label": "Notion", "scores": {...}},
    {"domain_id": "figma", "label": "Figma", "scores": {...}},
]

PERSONA_TYPES = {
    "designer": {"influence_score": 0.8, "adoption_threshold": 0.3, ...},
    "engineer": {"influence_score": 0.7, "adoption_threshold": 0.4, ...},
    "pm": {"influence_score": 0.6, "adoption_threshold": 0.5, ...},
    "cto": {"influence_score": 0.9, "adoption_threshold": 0.7, ...},
}
```

### Example 3: Predicting Crypto Token Trends (hypothetical)

```python
TOKENS = [
    {"domain_id": "sol", "label": "Solana", "scores": {...}},
    {"domain_id": "eth", "label": "Ethereum", "scores": {...}},
    {"domain_id": "new-l2", "label": "New L2 Chain", "scores": {...}},
]

SHOCK_TEMPLATES = {
    "sec_enforcement": {"effect": "negative", "strength_override": 0.95},
    "etf_approval": {"effect": "positive", "strength_override": 0.90},
    "hack_exploit": {"effect": "negative", "strength_override": 0.85},
}
```

---

## Visualization

The knowledge graph visualization is at `viz/mirofish-graph.html`.

### Running It

```bash
cd viz && python -m http.server 8000
# Open http://localhost:8000/mirofish-graph.html
```

### Features

- **Force-directed graph**: 59 nodes with pan/zoom/minimap
- **Color-coded nodes**: green (existing domains), orange (candidates), blue (tech), purple (platforms), yellow (communities), red (regulations)
- **Adoption rings**: Progress indicator around each domain node
- **Round-by-round playback**: Play/pause button, round slider, speed control
- **Left panel**: Domain rankings, persona distribution, builder vs enterprise comparison, legend
- **Right panel**: Adoption curve chart (click any domain), shock timeline, live activity feed
- **Navbar**: Sparkline charts for average adoption and signal distribution
- **Keyboard controls**: Space (play/pause), Arrow keys (step rounds)

### Regenerating Data

After changing the simulation, regenerate the viz data:

```bash
python scripts/export_viz_data.py
# Refresh the browser
```

---

## Troubleshooting

### All domains show same adoption rate

**Cause**: Attention budget too high or stage difficulty too low. Every domain gets enough signal to push through all stages equally.

**Fix**: Lower the attention budget and/or raise stage 3-4 difficulty:
```python
# In simulation.py
attention_budget = min(8, max(3, len(domains) // 4))  # More restrictive

# In personas.py
stage_difficulty[3] = 1.5  # Harder to adopt
stage_difficulty[4] = 2.0  # Much harder to advocate
```

### No domains reach adoption (all at 0%)

**Cause**: Stage difficulty too high or no signals injected.

**Fix**: Check that signals are being generated:
```python
signals = signals_from_opportunities(domains) + signals_from_graph(graph)
print(f"Generated {len(signals)} signals")  # Should be > 0
```

If signals exist but adoption is still 0%, lower stage difficulty:
```python
stage_difficulty[3] = 1.0  # Easier to adopt
```

### No advocacy (all at 0%)

**Cause**: Stage 4 difficulty (adopted -> advocating) is too high.

**Fix**: Lower the advocating gate:
```python
stage_difficulty[4] = 1.5  # Was 1.7
```

### Simulation is too slow

**Cause**: 1000 agents x 32 domains x 20 rounds = 640,000 evaluations.

**Fix**: Reduce agents:
```python
personas = generate_personas(graph, domain_ids, count_per_type=50, seed=42)
# 400 agents instead of 1000
```

### Enterprise adoption equals builder adoption

**Cause**: Enterprise context multipliers too weak.

**Fix**: Make enterprise harder:
```python
# In _apply_context()
p["adoption_threshold"] *= 1.4  # Was 1.2
p["risk_tolerance"] *= 0.6      # Was 0.8
```

---

## Design Decisions & Lessons Learned

### Why Attention Budgets Changed Everything

Our first simulation had all 32 domains at exactly 70.6% adoption. The problem: every persona evaluated every domain every round, so all domains got equal treatment. In reality, people have finite attention -- you can't seriously evaluate 32 things at once.

Adding attention budgets (top 10 per round) forced domains to compete for mindshare. Domains with stronger signals win attention, and domains that fall behind get less evaluation, creating a feedback loop that produces natural differentiation.

### Why Probability Union Over Additive Signals

Our first signal model added signal strengths: signal_a(0.5) + signal_b(0.5) = 1.0. With 44 signals per domain, everything saturated instantly.

Probability union: P = 1 - (1-0.5)(1-0.5) = 0.75. Each additional signal has diminishing marginal impact. This matches reality -- the 100th news article about a topic doesn't move you as much as the first one.

### Why Stage Difficulty Is Exponential

Early stages (unaware -> aware) are easy: any signal gets you noticed. Late stages (evaluating -> adopted) are hard: you need sustained, strong signal to actually commit. This models the real adoption funnel where awareness is cheap but conversion is expensive.

### Why Dual Context Matters

Builder communities and enterprise markets have fundamentally different adoption dynamics. Builders are risk-tolerant and fast-moving. Enterprise buyers need proven ROI and move slowly. Running both contexts reveals domains that appeal to builders but not enterprise (or vice versa), which is critical for strategy.

### Why Calibration Must Come First

It's tempting to trust simulation outputs because they look sophisticated. But predictions without calibration are just vibes. Every prediction gets an outcome contract, and every resolved contract updates the Brier score. If the simulation's Brier score is worse than a coin flip, the simulation is useless -- no matter how complex it is.

### The "Never Promote to Doctrine" Rule

Simulation output lives in the `exploratory_frontier` evidence lane. It never auto-promotes to `research_grounded` or `benchmark_grounded`. Only after replay-benchmarking (historical cases proving accuracy) can predictions earn trust. This prevents vivid simulations from becoming self-fulfilling prophecies.

---

## File Reference

| File | Purpose | Lines |
|------|---------|-------|
| `src/chip_labs/mirofish/__init__.py` | Package exports | 12 |
| `src/chip_labs/mirofish/graph.py` | Knowledge graph builder | 192 |
| `src/chip_labs/mirofish/personas.py` | Stakeholder persona generator | 254 |
| `src/chip_labs/mirofish/simulation.py` | Simulation engine | 340 |
| `src/chip_labs/mirofish/signals.py` | Signal/shock grammar + bridge | 311 |
| `src/chip_labs/mirofish/calibration.py` | Brier scoring + outcome contracts | 216 |
| `src/chip_labs/mirofish/report.py` | Report generation | 269 |
| `scripts/predict_1000_agents.py` | Full 1000-agent prediction | 513 |
| `scripts/export_viz_data.py` | Export data for visualization | 145 |
| `viz/mirofish-graph.html` | Interactive knowledge graph | 900+ |
| `viz/mirofish_data.json` | Exported simulation data | ~275KB |
| `docs/LAB_MIROFISH_ARCHITECTURE.md` | Architecture documentation | 300 |
| `tests/test_*.py` | 128 tests across 5 test files | ~400 |
