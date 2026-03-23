# MiroFish Hybrid Evaluation Spec

## Purpose

This bridge converts accepted discovery candidates into a simulation-ready hybrid evaluation spec.

It exists so MiroFish can:

- discover candidates without seeding the 515-chip universe first
- compare those candidates against a stable benchmark panel
- produce a graph, signal set, and shock scenario without relying on the UI/export layer

## Inputs

The CLI expects a canonical discovery packet, not raw discovery observations.

Current input path:

- `research/meta/MIROFISH_DISCOVERY_BATCH_TEMPLATE_RESULT_2026-03-24.json`

## What The Bridge Produces

The hybrid spec contains:

- discovered candidate opportunities
- benchmark panel opportunities
- combined static rankings
- graph payload
- generated signals
- recommended shock scenario
- harness config for:
  - flagship run
  - ensemble runs

## Conservative Priors

Discovered candidates do not arrive with the full static score surface that MiroFish expects.

So the bridge infers conservative priors from:

- specialization surface
- mastery surface
- repeated value loop
- evidence sources
- evidence summary
- adjacent domains
- qualitative confidence

These inferred scores are only for exploratory comparison. They are not truth claims.

## Default Benchmark Panel

If no custom benchmark list is passed, the bridge uses:

- `trading-crypto`
- `startup-yc`
- `cursor-copilot`
- `mcp-server-builder`
- `ai-agent-builder`

The point is not to prove those are the only good domains. The point is to keep a stable comparison panel while discovery starts feeding new candidates in.

## Default Harness

- rounds: `20`
- flagship personas per type: `30`
- flagship total agents: `450`
- ensemble runs: `15`
- ensemble personas per type: `15`
- ensemble total agents per run: `225`
- persona types assumed by the current engine: `15`

Read output in this order:

1. `agent_choice_signal`
2. `peak_interest_probability`
3. `final_adoption_rate`

## Current CLI Path

```powershell
$env:PYTHONPATH='src'
python -m chip_labs.cli mirofish-hybrid-spec --input research/meta/MIROFISH_DISCOVERY_BATCH_TEMPLATE_RESULT_2026-03-24.json --output research/meta/MIROFISH_HYBRID_SPEC_TEMPLATE_2026-03-24.json
```

To run the saved hybrid spec:

```powershell
$env:PYTHONPATH='src'
python -m chip_labs.cli mirofish-hybrid-run --input research/meta/MIROFISH_HYBRID_SPEC_TEMPLATE_2026-03-24.json --output research/meta/MIROFISH_HYBRID_RUN_TEMPLATE_2026-03-24.json
```

To override the benchmark panel:

```powershell
$env:PYTHONPATH='src'
python -m chip_labs.cli mirofish-hybrid-spec --input research/meta/MIROFISH_DISCOVERY_BATCH_TEMPLATE_RESULT_2026-03-24.json --benchmarks trading-crypto,startup-yc,compliance-shield --output research/meta/MIROFISH_HYBRID_SPEC_TEMPLATE_2026-03-24.json
```

## Starter Sample

The current starter batch produces:

- `1` discovered clear candidate
- `5` benchmark domains
- `6` combined domains
- `56` generated signals
- `3` recommended shocks

Top-ranked benchmark in the starter panel:

- `trading-crypto`

Starter discovered candidate:

- `ai-meeting-prep-copilot`

## Starter Run Snapshot

The first end-to-end starter run currently shows:

- top choice signal: `cursor-copilot` at `20.0%`
- top final retained adoption in the flagship run: `cursor-copilot` at `6.67%`
- top ensemble mean adoption: `cursor-copilot` at `6.10%`
- discovered candidate `ai-meeting-prep-copilot` places second in ensemble mean adoption at `5.03%`

So the discovered candidate is not winning the benchmark panel yet, but it is already competitive enough to justify another discovery batch and a broader hybrid comparison.

## Governance

- hybrid specs remain `exploratory_frontier`
- inferred priors must stay visible in the output
- benchmark membership still requires human review
- discovery output should never auto-promote directly into the maintained universe
