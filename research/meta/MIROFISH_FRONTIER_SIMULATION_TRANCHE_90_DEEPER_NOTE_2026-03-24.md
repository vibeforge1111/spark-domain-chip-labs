## MiroFish Frontier Simulation Tranche 90 Deeper

Date: 2026-03-24

### Why This Tranche Exists

The first `90`-domain frontier tranche proved that the full `1000`-domain frontier could not be evaluated directly in one bounded hybrid run, but the initial harness was too thin to separate "no frontier demand" from "frontier interest that never gets enough rounds to convert."

This deeper tranche re-used the same diversity-preserving `90`-domain packet and increased harness depth to:

- `12` rounds
- `6` flagship domains per persona type
- `6` ensemble runs
- `3` ensemble domains per persona type

### Artifact Set

- `research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_SIMULATION_TRANCHE_90_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_SPEC_FRONTIER_TRANCHE_90_DEEPER_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_FRONTIER_TRANCHE_90_DEEPER_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_DIAGNOSTIC_FRONTIER_TRANCHE_90_DEEPER_2026-03-24.json`

### Top Line

- top choice-signal domain: `defi_yield_rotation_loop`
- top choice signal: `0.1666`
- top final adoption domain: `defi_yield_rotation_loop`
- top final adoption: `0.0333`
- top ensemble domain: `chip_ai_agent_07`
- top ensemble mean adoption: `0.0518`
- benchmark median adoption: `0.0252`

### Comparison To The Thinner Tranche

The earlier tranche stayed pinned at:

- top choice signal: `0.10`
- top final adoption: `0.00`
- top ensemble mean adoption: `0.00`

The deeper harness escapes that failure mode. This means the frontier read was not purely "zero demand." The thinner run was understating frontier conversion and retained adoption.

### Diagnostic Read

The frontier still shows real friction:

- interest-to-choice friction is still common
- several domains still collapse from trial to retained adoption
- many domains remain below the benchmark median

But the deeper run now surfaces a usable frontier instead of a zeroed one. The strongest ensemble signal is no longer the same as the strongest raw attention signal, which is useful separation instead of total collapse.

Notable readouts from the diagnostic:

- strongest attention domain: `fandom-drop-interpretation-loop`
- strongest ensemble domain: `chip_ai_agent_07`
- worst attention-to-ensemble gap domain: `defi_yield_rotation_loop`
- largest trial-to-adoption gap domain: `chip_ai_agent_03`

### Decision

Do not mutate MiroFish conversion logic again based on the earlier zeroed frontier tranche.

The next tractable step should be:

1. treat this deeper `90`-domain run as the current trustworthy frontier checkpoint
2. export or rank the top frontier domains from this run
3. if more breadth is needed, scale to a larger tractable tranche before attempting another full-frontier hybrid run

### Verification

Commands used:

```powershell
$env:PYTHONPATH='src'
python -m pytest tests/test_trend_prediction.py tests/test_mirofish_portfolio.py tests/test_mirofish_discovery.py -q
python -m chip_labs.cli mirofish-hybrid-spec --input research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_SIMULATION_TRANCHE_90_2026-03-24.json --rounds 12 --flagship-count-per-type 6 --ensemble-runs 6 --ensemble-count-per-type 3 --scenario-label mirofish-frontier-tranche-90-deeper --output research/meta/MIROFISH_HYBRID_SPEC_FRONTIER_TRANCHE_90_DEEPER_2026-03-24.json
python -m chip_labs.cli mirofish-hybrid-run --input research/meta/MIROFISH_HYBRID_SPEC_FRONTIER_TRANCHE_90_DEEPER_2026-03-24.json --output research/meta/MIROFISH_HYBRID_RUN_FRONTIER_TRANCHE_90_DEEPER_2026-03-24.json
python -m chip_labs.cli mirofish-run-diagnostic --input research/meta/MIROFISH_HYBRID_RUN_FRONTIER_TRANCHE_90_DEEPER_2026-03-24.json --output research/meta/MIROFISH_HYBRID_DIAGNOSTIC_FRONTIER_TRANCHE_90_DEEPER_2026-03-24.json
```
