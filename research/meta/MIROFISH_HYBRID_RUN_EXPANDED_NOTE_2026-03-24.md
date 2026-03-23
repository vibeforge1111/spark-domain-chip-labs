# MiroFish Hybrid Expanded Run Note: 2026-03-24

## Scope

Run the expanded discovery batch through the full hybrid harness after removing the blanket discovered-candidate breakout shock.

Input artifacts:

- `research/meta/MIROFISH_DISCOVERY_BATCH_EXPANDED_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_SPEC_EXPANDED_2026-03-24.json`

Output artifact:

- `research/meta/MIROFISH_HYBRID_RUN_EXPANDED_2026-03-24.json`

## Intake Summary

- raw candidates: `17`
- accepted candidates: `12`
- merged candidates: `2`
- rejected candidates: `3`
- clear chips: `11`
- proto chips: `1`

## Harness

- discovered candidates: `12`
- benchmark panel domains: `5`
- combined domains: `17`
- signals: `245`
- shocks: `4`
- rounds: `20`
- flagship run: `450` agents
- builder ensemble: `15` runs x `225` agents

## Scenario Guardrail

The breakout shock no longer boosts all discovered candidates.

Current breakout targets:

- `ai-sales-call-prep-copilot`
- `ai-rfp-response-copilot`
- `ai-compliance-evidence-copilot`

This makes the comparison less flattering to the intake set than the earlier blanket version.

## Topline

- top flagship choice signal: `cursor-copilot` at `33.34%`
- top flagship retained adoption: `cursor-copilot` at `13.33%`
- top builder ensemble mean adoption: `cursor-copilot` at `5.48%`

## Best Discovered Candidates

By builder ensemble mean adoption:

1. `ai-compliance-evidence-copilot` at `3.17%`
2. `ai-investor-update-copilot` at `2.82%`
3. `ai-partner-prospecting-copilot` at `2.67%`
4. `ai-sales-call-prep-copilot` at `2.58%`
5. `ai-rfp-response-copilot` at `2.16%`

By flagship choice signal:

1. `ai-hiring-debrief-copilot` peaked at `23.34%`
2. `ai-compliance-evidence-copilot` peaked at `20.0%`
3. `ai-incident-comms-coordinator` peaked at `16.66%`
4. `ai-sales-call-prep-copilot` peaked at `13.33%`

## Interpretation

The strongest discovery cluster is now clearer:

- compliance / enterprise evidence workflows
- founder / investor communication workflows
- sales / partner preparation workflows

The less compelling discovered candidates in this batch tended to show attention without durable retained adoption.

## Recommendation

The next discovery batch should bias harder toward:

- compliance operations
- enterprise response loops
- founder communication loops
- sales preparation and partner development loops

It should bias away from:

- generic research synthesis without a stronger operating edge
- broad operator categories without a repeated artifact loop
