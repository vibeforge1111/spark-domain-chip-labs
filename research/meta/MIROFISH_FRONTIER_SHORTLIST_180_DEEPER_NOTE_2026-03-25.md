## MiroFish Frontier Shortlist 180 Deeper

Date: 2026-03-25

### Why This Exists

The deeper `180`-domain frontier checkpoint is broad enough to show live frontier breadth, but the raw readout is still too large for fast operator review.

This shortlist extracts three practical buckets from the saved deeper `180` readout:

- `winners`: domains already above the benchmark floor and not obviously collapsing between trial and retention
- `breakouts`: domains with strong raw choice signal that still need better retained conversion
- `speculative`: watchlist domains worth monitoring because they still show frontier pull or distinctive mechanism shape

### Artifact Set

- `research/meta/MIROFISH_FRONTIER_SHORTLIST_180_DEEPER_2026-03-25.json`
- `research/meta/MIROFISH_FRONTIER_SHORTLIST_180_DEEPER_2026-03-25.md`
- `research/meta/MIROFISH_FRONTIER_SHORTLIST_180_DEEPER_NOTE_2026-03-25.md`

### Source Checkpoint

- source readout: `research/meta/MIROFISH_FRONTIER_READOUT_TRANCHE_180_DEEPER_2026-03-25.json`
- benchmark median adoption: `1.63%`

### Shortlist Shape

- winners: `10`
- breakouts: `8`
- speculative: `5`

### Winners

1. `chip_ai_agent_07`
2. `governance-vote-brief-loop`
3. `crypto_airdrop_hunting_loop`
4. `pricing-review-copilot`
5. `pricing-review-loop`
6. `chip_ai_agent_11`
7. `repo-proof-loop`
8. `perp-risk-reset-loop`
9. `resume-refresh-copilot`
10. `changelog-thread-tool`

### Breakouts

1. `defi_yield_rotation_loop`
2. `product-angle-test-loop`
3. `chip_ai_agent_03`
4. `devrel-reply-loop`
5. `paycheck-allocation-loop`
6. `pricing-review-system`
7. `chip_ai_agent_01`
8. `crypto_tax_tracking_loop`

### Speculative

1. `pricing-call-feedback-loop`
2. `fandom-drop-interpretation-loop`
3. `changelog-to-launch-loop`
4. `resume-refresh-workflow`
5. `live-raid-coordination-loop`

### Current Read

The shortlist confirms the deeper `180` checkpoint is not concentrated in a single wedge:

- agent-builder domains still anchor the top retained set
- crypto / governance loops remain strong on both choice and retained outcomes
- pricing, resume, changelog, and fandom loops keep showing up, which suggests the frontier is broader than just crypto or startup tooling

This is a better operator surface than the full ranked export when the goal is to decide what to inspect or promote next.

### Decision

Use the deeper `180` shortlist as the fast review layer for the current frontier checkpoint.

Checkpoint stack now becomes:

1. full breadth checkpoint: deeper `180`
2. fast operator shortlist: deeper `180` shortlist
3. stronger benchmark-floor reference: deeper `90`

### Verification

Commands used:

```powershell
$env:PYTHONPATH='src'
python -m pytest tests/test_mirofish_hybrid.py tests/test_watchtower.py tests/test_mirofish_discovery.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q
python -m chip_labs.cli mirofish-frontier-shortlist --input research/meta/MIROFISH_FRONTIER_READOUT_TRANCHE_180_DEEPER_2026-03-25.json --output research/meta/MIROFISH_FRONTIER_SHORTLIST_180_DEEPER_2026-03-25.json --winner-n 10 --breakout-n 8 --speculative-n 8
python -m chip_labs.cli mirofish-frontier-shortlist-export --input research/meta/MIROFISH_FRONTIER_SHORTLIST_180_DEEPER_2026-03-25.json --output research/meta/MIROFISH_FRONTIER_SHORTLIST_180_DEEPER_2026-03-25.md --title "MiroFish Frontier Shortlist 180 Deeper"
```
