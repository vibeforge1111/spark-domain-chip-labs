# Spark Domain Chip Labs

The recursive improvement engine for the Spark domain chip ecosystem.

## What This Is

A research lab that runs as a **meta-chip** -- it follows the same `spark-chip.v1` contract as every domain chip, but its domain is *chip research itself*. The lab evaluates other chips, improves chip-building methodology, discovers new domain opportunities, and studies how domain specialization contributes to collective intelligence.

## Quick Start

```bash
cd spark-domain-chip-labs
pip install -e .

# Run the meta-evaluator against a chip
python -m chip_labs.cli evaluate --input eval_input.json --output eval_output.json

# Get research direction suggestions
python -m chip_labs.cli suggest --input suggest_input.json --output suggest_output.json

# Generate methodology and quality packets
python -m chip_labs.cli packets --input packets_input.json --output packets_output.json

# Build lab observatory pages
python -m chip_labs.cli watchtower --input wt_input.json --output wt_output.json
```

## With spark-researcher

```bash
# Run a single evaluation pass
spark-researcher run --command research --config spark-researcher.project.json

# Run all candidate trials
spark-researcher loop --command research --config spark-researcher.project.json

# Run bounded autonomous improvement
spark-researcher autoloop --command research --rounds 2 --config spark-researcher.project.json
```

## Agent Research Team

Seven specialized workstreams within one governing flywheel:

| Agent | Focus | Trigger |
|-------|-------|---------|
| Frontier Scout | New domain discovery | portfolio_coverage_gap |
| Methodology Researcher | Improve chip-building methodology | methodology_gap |
| Chip Architect | Design new chip manifests | domain_brief reaches research_grounded |
| Benchmark Engineer | Quality benchmarks | periodic + regression |
| Integration Specialist | spark-researcher/swarm compat | integration_gap |
| Growth Analyst | Ecosystem adoption tracking | growth_signal_gap |
| AGI Theorist | Recursive self-improvement research | every 15 passes + transfer events |

## Quality Rubric (100 points)

The lab evaluates chips on six dimensions:

| Dimension | Points | What It Measures |
|-----------|--------|-----------------|
| Manifest Validity | 15 | Schema, hooks, frontier definition |
| Evidence Separation | 20 | Four evidence lanes kept distinct |
| Evaluation Depth | 20 | Scoring dimensions, benchmark bridge |
| Memory & Knowledge | 15 | Source registry, packet quality, watchtower |
| Integration Health | 15 | spark-researcher/swarm compatibility |
| Documentation | 15 | Mission, architecture, graduation criteria |

## Chip Portfolio

Currently tracking 10+ domain chips:

- **startup-yc** (Production v0.3.0) -- YC startup factor research
- **trading-crypto** (Beta v0.1.0) -- Crypto trading doctrine + strategy
- **agentic-marketing** (Beta v0.2.0) -- Growth loop systems
- **web-designer** (Beta v0.1.0) -- Award-level web design
- **roblox-development** (Beta v0.1.0) -- Viral game systems
- **pokemon-red** (Beta v0.1.0) -- Speedrun automation
- **xcontent** (Alpha v0.1.0) -- X/Twitter content
- **content** (Alpha v0.1.0) -- Content mechanisms
- **vibe-incubator** (Beta v0.1.0) -- Venture incubation
- **predictive-worlds-lab** (Exploratory) -- Prediction markets

## MiroFish Prediction Engine

A zero-dependency multi-agent simulation engine for predicting adoption dynamics. Runs 1000 stakeholder personas through a 20-round adoption simulation with Monte Carlo ensemble for confidence intervals.

```bash
# Run the full prediction pipeline (1000 agents, 32 domains, ensemble + sensitivity)
python scripts/predict_1000_agents.py

# View the interactive knowledge graph visualization
cd viz && python -m http.server 8888
# Open http://localhost:8888/mirofish-graph.html
```

**What it predicts**: Which domains/products/technologies will gain adoption, with confidence intervals, sensitivity analysis, and calibration scoring.

**How to adapt it**: Define your own domains, inject signals, run the ensemble. Works for product roadmaps, market entry analysis, technology bets, content strategy, investment thesis -- anything where you're predicting adoption.

Full documentation: **[docs/MIROFISH_PREDICTION_ENGINE.md](docs/MIROFISH_PREDICTION_ENGINE.md)**

### Latest Predictions (March 2026)

| Rank | Domain | Ensemble Mean | Confidence | Status |
|------|--------|--------------|------------|--------|
| 1 | prompt-engineer | 67.8% | HIGH (68%-69%) | New candidate |
| 2 | indie-hacker | 67.8% | HIGH (68%-69%) | New candidate |
| 3 | security-audit | 67.8% | HIGH (68%-69%) | New candidate |
| 4 | solana-dev | 66.8% | HIGH (66%-68%) | New candidate |
| 5 | ai-agent-builder | 65.9% | HIGH (65%-68%) | New candidate |
| 6 | agentic-marketing | 61.3% | HIGH (60%-62%) | Existing (beta) |
| 7 | defi-architect | 58.4% | HIGH (57%-60%) | New candidate |
| 8 | game-balance | 54.0% | HIGH (54%-55%) | New candidate |

## Connected Systems

- **spark-researcher** -- Autoloop runtime (the lab runs as a chip)
- **spark-swarm** -- Collective intelligence platform (the lab emits insights)
- **Domain chips** -- The subjects of the lab's research

## Key Principles

1. **Meta-chip, not framework** -- follows spark-chip.v1, not a custom system
2. **Agent roles = workstreams** -- routing within one flywheel, not separate processes
3. **Quality rubric = fixed evaluator** -- consistent with Spark's architecture
4. **Selective memory** -- shares methodology, absorbs chip masteries, keeps raw research private
5. **Graduation = real-world eval** -- success metric is: do graduated chips actually work?
6. **Prove before abstracting** -- no methodology chip until 2+ successful graduations

## License

Private -- Spark ecosystem internal.
