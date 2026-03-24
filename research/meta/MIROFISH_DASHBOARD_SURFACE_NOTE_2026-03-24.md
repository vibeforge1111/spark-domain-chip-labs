# MiroFish Dashboard Surface Note: 2026-03-24

## Decision

Use the watchtower surface as the first in-repo dashboard path for the current canonical MiroFish checkpoint.

Why this path was chosen:

- `viz/` is outside the mutable-target contract for this session
- the watchtower page generator already exists inside `src/chip_labs/`
- the medium checkpoint already has a canonical markdown export artifact that can be embedded directly

## What Changed

- added a `MiroFish Portfolio.md` watchtower page
- linked that page from:
  - `Lab Home.md`
  - `Portfolio Dashboard.md`
  - `Trend Predictions.md`
- made the page prefer the saved markdown export artifact
- added a JSON-readout fallback if the markdown export does not exist yet
- added a clear stub if neither artifact exists

## Result

The repo now has an in-repo dashboard surface that points at the canonical medium checkpoint without touching the legacy `viz/` path.

This is still not a claim that the medium checkpoint is final portfolio truth. It is simply the cleanest current surface for the saved checkpoint inside the allowed edit scope.

## Verification

- `$env:PYTHONPATH='src'; python -m pytest tests/test_watchtower.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q`
- result: `22 passed`

- `$env:PYTHONPATH='src'; python -c "from chip_labs.watchtower import generate_watchtower_pages; pages=generate_watchtower_pages({}, chip_search_dir='.'); page=next(p for p in pages if p['path']=='MiroFish Portfolio.md'); print(page['content'][:1200])"`
- result: the generated page resolves to the canonical medium export artifact under `research/meta/`
