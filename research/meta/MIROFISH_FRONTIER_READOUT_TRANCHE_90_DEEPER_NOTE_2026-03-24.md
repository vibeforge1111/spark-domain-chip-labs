## MiroFish Frontier Readout Tranche 90 Deeper

Date: 2026-03-24

### Why This Exists

The deeper `90`-domain frontier run finally produced a usable non-zero checkpoint, but the raw hybrid run packet was still too awkward to inspect directly. This tranche adds a ranked JSON readout and operator-facing markdown export so the frontier can be reviewed without re-parsing the raw run structure.

### Artifact Set

- `research/meta/MIROFISH_FRONTIER_READOUT_TRANCHE_90_DEEPER_2026-03-24.json`
- `research/meta/MIROFISH_FRONTIER_EXPORT_TRANCHE_90_DEEPER_2026-03-24.md`

### Current Read

Top overall frontier domains from the deeper tranche:

1. `chip_ai_agent_07`
2. `chip_ai_agent_11`
3. `fandom-drop-interpretation-loop`
4. `changelog-to-launch-loop`
5. `chip_ai_agent_01`

Top choice-led frontier domains:

1. `defi_yield_rotation_loop`
2. `fandom-drop-interpretation-loop`
3. `repo-proof-loop`
4. `chip_ai_agent_03`
5. `devrel-reply-loop`

Above-benchmark frontier slice:

- `chip_ai_agent_07`
- `chip_ai_agent_11`
- `fandom-drop-interpretation-loop`
- `changelog-to-launch-loop`
- `chip_ai_agent_01`
- `live-raid-coordination-loop`
- `chip_ai_agent_12`
- `subscription-prune-loop`
- `crypto_airdrop_hunting_loop`
- `creator-idea-sprint-loop`

### Interpretation

The frontier is now reviewable in a useful way:

- builder / agent loops are showing up near the top of the retained frontier
- fandom, changelog, creator, and crypto loops are still visibly alive
- some of the strongest raw attention domains still lag on retained adoption

The most important split is now clear:

- retained frontier leaders are not identical to pure choice leaders
- that makes the frontier more trustworthy than the earlier zeroed read

### Decision

Use this exported deeper frontier readout as the current operator surface for frontier review.

The next tractable step should be either:

1. build a larger frontier tranche from the `1000`-domain pool using this readout as the selection anchor, or
2. wire this readout into the watchtower surface the same way the portfolio checkpoint is surfaced

### Verification

Commands used:

```powershell
$env:PYTHONPATH='src'
python -m pytest tests/test_mirofish_hybrid.py tests/test_mirofish_discovery.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q
python -m chip_labs.cli mirofish-frontier-readout --input research/meta/MIROFISH_HYBRID_RUN_FRONTIER_TRANCHE_90_DEEPER_2026-03-24.json --output research/meta/MIROFISH_FRONTIER_READOUT_TRANCHE_90_DEEPER_2026-03-24.json --top-n 25 --watchlist-n 15 --benchmark-n 10
python -m chip_labs.cli mirofish-frontier-export --input research/meta/MIROFISH_FRONTIER_READOUT_TRANCHE_90_DEEPER_2026-03-24.json --output research/meta/MIROFISH_FRONTIER_EXPORT_TRANCHE_90_DEEPER_2026-03-24.md --title "MiroFish Frontier Tranche 90 Deeper Export"
```
