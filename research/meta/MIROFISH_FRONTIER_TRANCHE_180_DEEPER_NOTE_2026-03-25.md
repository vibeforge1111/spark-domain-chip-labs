## MiroFish Frontier Tranche 180 Deeper

Date: 2026-03-25

### Why This Tranche Exists

The anchored `180`-domain frontier slice from March 24, 2026 was broader and tractable, but the medium harness was too weak:

- top ensemble adoption only `2.67%`
- top retained adoption `0.00%`
- benchmark median `0.00%`

This deeper rerun keeps the same anchored `180`-domain tranche and upgrades only the harness depth.

### Artifact Set

- `research/meta/MIROFISH_HYBRID_SPEC_FRONTIER_TRANCHE_180_DEEPER_2026-03-25.json`
- `research/meta/MIROFISH_HYBRID_RUN_FRONTIER_TRANCHE_180_DEEPER_2026-03-25.json`
- `research/meta/MIROFISH_HYBRID_DIAGNOSTIC_FRONTIER_TRANCHE_180_DEEPER_2026-03-25.json`
- `research/meta/MIROFISH_FRONTIER_READOUT_TRANCHE_180_DEEPER_2026-03-25.json`
- `research/meta/MIROFISH_FRONTIER_EXPORT_TRANCHE_180_DEEPER_2026-03-25.md`

### Harness

- `12` rounds
- `6` flagship domains per persona type
- `6` ensemble runs
- `3` ensemble domains per persona type

### Top Line

- top choice-signal domain: `governance-vote-brief-loop`
- top choice signal: `0.20`
- top final adoption domain: `governance-vote-brief-loop`
- top final adoption: `0.0667`
- top ensemble domain: `chip_ai_agent_07`
- top ensemble mean adoption: `0.0533`
- benchmark median adoption: `0.0163`

### Comparison

Versus the weaker medium `180` run:

- top ensemble improves from `2.67%` to `5.33%`
- top retained adoption improves from `0.00%` to `6.67%`
- benchmark median improves from `0.00%` to `1.63%`

Versus the deeper `90` run from March 24, 2026:

- top ensemble improves slightly from `5.18%` to `5.33%`
- top retained adoption improves from `3.33%` to `6.67%`
- benchmark median is lower (`1.63%` vs `2.52%`)

So the broader slice now has a real non-zero floor and a top line that is competitive with the deeper `90`, but the narrower `90` still has the stronger benchmark floor.

### Current Read

Top overall domains in the deeper `180` slice:

1. `chip_ai_agent_07`
2. `governance-vote-brief-loop`
3. `crypto_airdrop_hunting_loop`
4. `pricing-review-copilot`
5. `pricing-review-loop`

Interpretation:

- startup / launch loops still hold up
- crypto and governance loops remain strong frontier categories
- pricing / review loops enter the retained winner set at broader scale
- the broader frontier still shows interest-to-choice friction, but it no longer collapses the way the medium `180` did

### Decision

The deeper `180` run is now the best breadth checkpoint.

Current checkpoint hierarchy:

1. best breadth checkpoint: deeper `180`
2. best benchmark-floor checkpoint: deeper `90`

The next move should be a comparative operator surface that shows both checkpoints side by side, rather than immediately jumping to another larger run.

### Verification

Commands used:

```powershell
$env:PYTHONPATH='src'
python -m pytest tests/test_mirofish_hybrid.py tests/test_mirofish_discovery.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q
python -m chip_labs.cli mirofish-hybrid-spec --input research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_SIMULATION_TRANCHE_180_2026-03-24.json --rounds 12 --flagship-count-per-type 6 --ensemble-runs 6 --ensemble-count-per-type 3 --scenario-label mirofish-frontier-tranche-180-deeper --output research/meta/MIROFISH_HYBRID_SPEC_FRONTIER_TRANCHE_180_DEEPER_2026-03-25.json
python -m chip_labs.cli mirofish-hybrid-run --input research/meta/MIROFISH_HYBRID_SPEC_FRONTIER_TRANCHE_180_DEEPER_2026-03-25.json --output research/meta/MIROFISH_HYBRID_RUN_FRONTIER_TRANCHE_180_DEEPER_2026-03-25.json
python -m chip_labs.cli mirofish-run-diagnostic --input research/meta/MIROFISH_HYBRID_RUN_FRONTIER_TRANCHE_180_DEEPER_2026-03-25.json --output research/meta/MIROFISH_HYBRID_DIAGNOSTIC_FRONTIER_TRANCHE_180_DEEPER_2026-03-25.json
python -m chip_labs.cli mirofish-frontier-readout --input research/meta/MIROFISH_HYBRID_RUN_FRONTIER_TRANCHE_180_DEEPER_2026-03-25.json --output research/meta/MIROFISH_FRONTIER_READOUT_TRANCHE_180_DEEPER_2026-03-25.json --top-n 25 --watchlist-n 15 --benchmark-n 10
python -m chip_labs.cli mirofish-frontier-export --input research/meta/MIROFISH_FRONTIER_READOUT_TRANCHE_180_DEEPER_2026-03-25.json --output research/meta/MIROFISH_FRONTIER_EXPORT_TRANCHE_180_DEEPER_2026-03-25.md --title "MiroFish Frontier Tranche 180 Deeper Export"
```
