## MiroFish Frontier Shortlist Watchtower Surface

Date: 2026-03-25

### Scope

Promote the saved deeper `180` shortlist to the primary watchtower view for the current frontier checkpoint, while still keeping the full export and local comparison page available.

### What Changed

- update the `MiroFish Frontier` watchtower page to show the saved frontier shortlist first
- keep the full ranked frontier export below the shortlist on the same page
- refresh `research/meta/watchtower_latest/` so the repo-local dashboard reflects the new operator-first layout

### Important Fix

The first shortlist watchtower pass matched the wrong markdown artifact because both of these names fit the broad shortlist glob:

- `MIROFISH_FRONTIER_SHORTLIST_180_DEEPER_2026-03-25.md`
- `MIROFISH_FRONTIER_SHORTLIST_180_DEEPER_NOTE_2026-03-25.md`

That caused the watchtower page to render the tranche note instead of the shortlist export.

The frontier page now detects that failure mode and falls back to the newest non-note shortlist markdown artifact.

### Result

The current repo-local frontier dashboard page now resolves to:

- canonical shortlist: `research/meta/MIROFISH_FRONTIER_SHORTLIST_180_DEEPER_2026-03-25.md`
- canonical export: `research/meta/MIROFISH_FRONTIER_EXPORT_TRANCHE_180_DEEPER_2026-03-25.md`
- comparison page: `research/meta/MIROFISH_FRONTIER_CHECKPOINTS_2026-03-25.html`

That means the first thing the user sees in the frontier dashboard is now the smaller winner / breakout / speculative surface instead of the full ranked export.

### Verification

Commands used:

```powershell
$env:PYTHONPATH='src'
python -m pytest tests/test_watchtower.py tests/test_mirofish_hybrid.py tests/test_mirofish_discovery.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q
python -m chip_labs.cli mirofish-watchtower-snapshot --vault-dir research/meta/watchtower_latest --output research/meta/MIROFISH_WATCHTOWER_LATEST_RESULT_2026-03-25.json
```

Result:

- `40 passed`
- `watchtower_latest/MiroFish Frontier.md` now points at the shortlist export, not the shortlist note
