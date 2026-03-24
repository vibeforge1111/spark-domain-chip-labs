## MiroFish Frontier Tranche 180 Medium

Date: 2026-03-24

### Why This Tranche Exists

After the deeper `90`-domain frontier checkpoint produced non-zero retained adoption, the next practical question was whether a broader slice could stay tractable without immediately collapsing back into a meaningless zeroed read.

This tranche used the full canonical `1000`-domain frontier, anchored selection on the deeper `90` readout, and built a broader `180`-domain packet before running a medium harness.

### Selection Strategy

The tranche was built with:

- `35` retained readout anchors
- round-robin fill across primary tags
- total size: `180`

This keeps current winners while widening the frontier beyond the narrower `90`-domain slice.

### Artifact Set

- `research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_SIMULATION_TRANCHE_180_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_SPEC_FRONTIER_TRANCHE_180_MEDIUM_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_FRONTIER_TRANCHE_180_MEDIUM_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_DIAGNOSTIC_FRONTIER_TRANCHE_180_MEDIUM_2026-03-24.json`
- `research/meta/MIROFISH_FRONTIER_READOUT_TRANCHE_180_MEDIUM_2026-03-24.json`
- `research/meta/MIROFISH_FRONTIER_EXPORT_TRANCHE_180_MEDIUM_2026-03-24.md`

### Harness

- `8` rounds
- `5` flagship domains per persona type
- `4` ensemble runs
- `2` ensemble domains per persona type

### Top Line

- top choice-signal domain: `governance-vote-brief-loop`
- top choice signal: `0.20`
- top final adoption domain: `governance-vote-brief-loop`
- top final adoption: `0.00`
- top ensemble domain: `changelog-to-launch-loop`
- top ensemble mean adoption: `0.0267`
- benchmark median adoption: `0.00`

### Current Read

Top overall frontier domains in this broader slice:

1. `changelog-to-launch-loop`
2. `crypto_airdrop_hunting_loop`
3. `pricing-review-copilot`
4. `resume-cycle-copilot`
5. `repo-proof-loop`

The anchored `180` slice still surfaces interesting domains across startup, crypto, pricing, career, and creator-adjacent loops, but it is weaker than the deeper `90` checkpoint:

- broader retained adoption survives, but barely
- top ensemble drops from `5.18%` in the deeper `90` to `2.67%` here
- benchmark median falls back to `0.00`
- raw attention again outruns retention by a wide margin

### Interpretation

This means:

1. the anchored tranche approach is viable
2. the `180`-domain slice is still tractable enough to run
3. medium harness depth is too thin to preserve the stronger benchmark floor seen in the deeper `90`

So the problem is not tranche selection. The problem is that the broader slice plus thinner harness washes out retained adoption quality.

### Decision

Keep the anchored `180` tranche as the current scale-up checkpoint, but do not treat this medium read as better than the deeper `90`.

Current best frontier checkpoints are:

- best quality checkpoint: deeper `90`
- best breadth checkpoint: anchored `180` medium

The next step should be either:

1. run the anchored `180` tranche under a deeper harness, or
2. wire both checkpoints into a comparative operator surface

### Verification

Commands used:

```powershell
$env:PYTHONPATH='src'
python -m pytest tests/test_mirofish_hybrid.py tests/test_mirofish_discovery.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q
python -m chip_labs.cli mirofish-frontier-tranche --input research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_RESULT_2026-03-24.json --anchor-readout research/meta/MIROFISH_FRONTIER_READOUT_TRANCHE_90_DEEPER_2026-03-24.json --target-count 180 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_SIMULATION_TRANCHE_180_2026-03-24.json
python -m chip_labs.cli mirofish-hybrid-spec --input research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_SIMULATION_TRANCHE_180_2026-03-24.json --rounds 8 --flagship-count-per-type 5 --ensemble-runs 4 --ensemble-count-per-type 2 --scenario-label mirofish-frontier-tranche-180-medium --output research/meta/MIROFISH_HYBRID_SPEC_FRONTIER_TRANCHE_180_MEDIUM_2026-03-24.json
python -m chip_labs.cli mirofish-hybrid-run --input research/meta/MIROFISH_HYBRID_SPEC_FRONTIER_TRANCHE_180_MEDIUM_2026-03-24.json --output research/meta/MIROFISH_HYBRID_RUN_FRONTIER_TRANCHE_180_MEDIUM_2026-03-24.json
python -m chip_labs.cli mirofish-run-diagnostic --input research/meta/MIROFISH_HYBRID_RUN_FRONTIER_TRANCHE_180_MEDIUM_2026-03-24.json --output research/meta/MIROFISH_HYBRID_DIAGNOSTIC_FRONTIER_TRANCHE_180_MEDIUM_2026-03-24.json
python -m chip_labs.cli mirofish-frontier-readout --input research/meta/MIROFISH_HYBRID_RUN_FRONTIER_TRANCHE_180_MEDIUM_2026-03-24.json --output research/meta/MIROFISH_FRONTIER_READOUT_TRANCHE_180_MEDIUM_2026-03-24.json --top-n 25 --watchlist-n 15 --benchmark-n 10
python -m chip_labs.cli mirofish-frontier-export --input research/meta/MIROFISH_FRONTIER_READOUT_TRANCHE_180_MEDIUM_2026-03-24.json --output research/meta/MIROFISH_FRONTIER_EXPORT_TRANCHE_180_MEDIUM_2026-03-24.md --title "MiroFish Frontier Tranche 180 Medium Export"
```
