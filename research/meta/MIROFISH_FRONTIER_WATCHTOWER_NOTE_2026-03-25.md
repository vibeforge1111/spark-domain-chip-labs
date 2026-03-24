## MiroFish Frontier Watchtower Surface

Date: 2026-03-25

### Scope

Expose the current frontier checkpoint inside the repo-local watchtower surface and make the local-host review path point at the real latest frontier export.

### What Changed

- added `MiroFish Frontier.md` to the watchtower page set
- added a comparative local-host page:
  - `research/meta/MIROFISH_FRONTIER_CHECKPOINTS_2026-03-25.html`
- refreshed:
  - `research/meta/watchtower_latest/MiroFish Frontier.md`
  - `research/meta/MIROFISH_WATCHTOWER_LATEST_RESULT_2026-03-25.json`

### Important Fix

The watchtower helper that picked the "latest" frontier export was sorting by filename. That was wrong for frontier tranche names because:

- `TRANCHE_90_*` sorted after `TRANCHE_180_*`

So the watchtower page was incorrectly pointing at the older deeper `90` export instead of the newer deeper `180` export.

The helper now selects by file modification time, which fixes the frontier page and is also a better rule for the portfolio and related surfaces.

### Result

The current repo-local frontier dashboard page now resolves to:

- canonical export: `research/meta/MIROFISH_FRONTIER_EXPORT_TRANCHE_180_DEEPER_2026-03-25.md`
- comparison page: `research/meta/MIROFISH_FRONTIER_CHECKPOINTS_2026-03-25.html`

That means the current agent-selected domain chips are visible both as:

1. a comparative local-host HTML surface
2. a watchtower markdown page under the repo-local dashboard surface

### Verification

Commands used:

```powershell
$env:PYTHONPATH='src'
python -m pytest tests/test_watchtower.py tests/test_mirofish_hybrid.py tests/test_mirofish_discovery.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q
python -m chip_labs.cli mirofish-watchtower-snapshot --vault-dir research/meta/watchtower_latest --output research/meta/MIROFISH_WATCHTOWER_LATEST_RESULT_2026-03-25.json
```

Result:

- `37 passed`
- `watchtower_latest` now contains `MiroFish Frontier.md`
- the frontier watchtower page points at the deeper `180` checkpoint
