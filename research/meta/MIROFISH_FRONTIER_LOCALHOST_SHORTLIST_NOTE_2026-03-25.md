## MiroFish Frontier Localhost Shortlist Surface

Date: 2026-03-25

### Scope

Update the repo-local frontier comparison page so the current shortlist winners are visible immediately in the browser, not only inside the watchtower markdown page.

### What Changed

- added a shortlist section to `research/meta/MIROFISH_FRONTIER_CHECKPOINTS_2026-03-25.html`
- the page now loads:
  - `research/meta/MIROFISH_FRONTIER_SHORTLIST_180_DEEPER_2026-03-25.json`
  - the existing deeper `90`, medium `180`, and deeper `180` readouts
- the browser surface now shows:
  - winners
  - breakouts
  - speculative watchlist domains
  - then the checkpoint comparison below

### Result

The local host page at:

- `http://localhost:8890/MIROFISH_FRONTIER_CHECKPOINTS_2026-03-25.html`

now opens with the top chosen frontier chips first instead of forcing the user to scan checkpoint cards before seeing the shortlist.

### Verification

Manual consistency review:

- confirm the shortlist section reads from `MIROFISH_FRONTIER_SHORTLIST_180_DEEPER_2026-03-25.json`
- confirm the checkpoint comparison remains unchanged below the shortlist
- confirm the leading domains still include:
  - `chip_ai_agent_07`
  - `governance-vote-brief-loop`
  - `crypto_airdrop_hunting_loop`
  - `pricing-review-copilot`
  - `pricing-review-loop`
