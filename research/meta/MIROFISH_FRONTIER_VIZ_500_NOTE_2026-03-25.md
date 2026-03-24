# MiroFish Frontier Viz 500 Note

- Date: `2026-03-25`
- Surface: `research/meta/MIROFISH_FRONTIER_VIZ_500_2026-03-25.html`
- Data packet: `research/meta/MIROFISH_FRONTIER_VIZ_500_2026-03-25.json`
- Purpose: restore the old `mirofish-250-graph` style UI for the current frontier-selected `500`-domain set

## What This Surface Is

This is a `500`-domain frontier graph packet selected from the canonical `1000`-agent diverse frontier result and rendered with the legacy `viz/mirofish-500-graph.html` UI pattern.

The selection is anchored by the current deeper `180` checkpoint:

- `MIROFISH_FRONTIER_READOUT_TRANCHE_180_DEEPER_2026-03-25.json`
- `MIROFISH_HYBRID_RUN_FRONTIER_TRANCHE_180_DEEPER_2026-03-25.json`

## What It Is Not

This is not a claim that all `500` domains were rerun under the full deeper hybrid harness.

It is a frontier-selection visualization surface:

- anchored domains use real deeper-`180` run metrics
- the remainder are diversified from the canonical `1000`-domain frontier result
- non-anchored curves are synthetic exploratory curves derived from discovery scores and tag/category heuristics

## Sanity Check

- domain count: `500`
- graph nodes: `508`
- graph edges: `500`

Current first five domains in the rendered packet:

1. `governance-vote-brief-loop`
2. `chip_ai_agent_07`
3. `crypto_airdrop_hunting_loop`
4. `resume-refresh-copilot`
5. `pricing-call-feedback-loop`

## Review Path

- localhost: `http://localhost:8890/MIROFISH_FRONTIER_VIZ_500_2026-03-25.html`

