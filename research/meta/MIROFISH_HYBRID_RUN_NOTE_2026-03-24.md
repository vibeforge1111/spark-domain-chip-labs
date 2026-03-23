# MiroFish Hybrid Run Note: 2026-03-24

## Scope

Run the starter hybrid spec generated from the first canonical discovery packet.

Input artifacts:

- `research/meta/MIROFISH_DISCOVERY_BATCH_TEMPLATE_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_SPEC_TEMPLATE_2026-03-24.json`

Output artifact:

- `research/meta/MIROFISH_HYBRID_RUN_TEMPLATE_2026-03-24.json`

## Harness

- 1 discovered candidate
- 5 benchmark panel domains
- 6 combined domains
- 20 rounds
- flagship run: 450 agents
- builder ensemble: 15 runs x 225 agents

## Scenario

- breakout tool shock on `ai-meeting-prep-copilot`
- open source release shock on:
  - `cursor-copilot`
  - `mcp-server-builder`
  - `ai-agent-builder`
- market crash shock on `trading-crypto`

## Topline

- Top flagship choice signal: `cursor-copilot` at `20.0%`
- Top flagship retained adoption: `cursor-copilot` at `6.67%`
- Top builder ensemble mean adoption: `cursor-copilot` at `6.10%`

## Discovered Candidate Read

`ai-meeting-prep-copilot` did not win the panel, but it held up better than a throwaway idea:

- builder ensemble mean adoption: `5.03%`
- builder ensemble rank: `#2` of `6`
- mean trial rate: `2.25%`
- mean churn rate: `0.95%`

That makes it promotion-worthy for a larger discovery batch, not benchmark-worthy yet.

## Interpretation

The hybrid harness is now doing the intended job:

- discovery candidates enter through a separate intake path
- a stable benchmark panel keeps the comparison honest
- the output exposes both choice signal and retained adoption

This is enough to keep scaling discovery without routing everything through the UI/export path.
