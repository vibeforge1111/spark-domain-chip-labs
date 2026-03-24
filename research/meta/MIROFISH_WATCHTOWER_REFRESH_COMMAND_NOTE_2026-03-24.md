# MiroFish Watchtower Refresh Command Note: 2026-03-24

## Scope

Make the MiroFish watchtower surface refreshable through one dedicated repo-local CLI command instead of a manual watchtower packet plus environment setup.

## Command

```powershell
$env:PYTHONPATH='src'
python -m chip_labs.cli mirofish-watchtower-snapshot `
  --vault-dir research/meta/watchtower_latest `
  --output research/meta/MIROFISH_WATCHTOWER_LATEST_RESULT_2026-03-24.json
```

## Result

The command now:

- writes the page set into `research/meta/watchtower_latest`
- records the page list in `research/meta/MIROFISH_WATCHTOWER_LATEST_RESULT_2026-03-24.json`
- keeps the generated `MiroFish Portfolio.md` page pointed at the canonical medium export artifact

## Why This Matters

Before this tranche, regenerating the surface required:

- a manual request packet
- a generic watchtower invocation
- an explicit `SPARK_CHIP_SEARCH_DIR` override

Now the refresh path is one bounded command inside the repo's own CLI surface.

## Verification

- `$env:PYTHONPATH='src'; python -m pytest tests/test_watchtower.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q`
- result: `22 passed`

- `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-watchtower-snapshot --vault-dir research/meta/watchtower_latest --output research/meta/MIROFISH_WATCHTOWER_LATEST_RESULT_2026-03-24.json`
- result: six pages generated, including `MiroFish Portfolio.md`
