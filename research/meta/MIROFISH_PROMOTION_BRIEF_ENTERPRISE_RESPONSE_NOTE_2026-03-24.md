# MiroFish Promotion Brief Note: Enterprise Response 2026-03-24

## Scope

Review which enterprise-response candidate deserves first promotion into maintained benchmark review from the focused hybrid run.

Input artifact:

- `research/meta/MIROFISH_HYBRID_RUN_FOCUSED_2026-03-24.json`

Output artifact:

- `research/meta/MIROFISH_PROMOTION_BRIEF_ENTERPRISE_RESPONSE_2026-03-24.json`

Reviewed candidates:

- `ai-security-questionnaire-copilot`
- `ai-rfp-response-copilot`
- `ai-compliance-evidence-copilot`
- `ai-renewal-risk-briefing-copilot`

## Benchmark Read

Focused benchmark panel:

- `compliance-shield`
- `legal-ops`
- `startup-yc`
- `indie-hacker`
- `cursor-copilot`

Builder-ensemble benchmark median adoption: `1.75%`

Builder-ensemble benchmark leader: `cursor-copilot` at `6.07%`

## Promotion Table Read

### 1. `ai-security-questionnaire-copilot`

- builder ensemble mean adoption: `4.83%`
- flagship choice signal: `23.34%`
- benchmark wins: `4/5`
- verdict: `review_now`

This is the only candidate that clearly clears the review bar. It beats the benchmark median by `3.08` points, outruns every focused benchmark except `cursor-copilot`, and has the strongest in-run agent-selection signal in the enterprise-response set.

### 2. `ai-rfp-response-copilot`

- builder ensemble mean adoption: `2.52%`
- flagship choice signal: `10.0%`
- benchmark wins: `3/5`
- verdict: `watchlist`

This is the closest secondary candidate by benchmark comparison. It clears the benchmark median and beats `startup-yc`, `compliance-shield`, and `legal-ops`, but its in-run choice signal is weaker than the lead candidate.

### 3. `ai-compliance-evidence-copilot`

- builder ensemble mean adoption: `1.30%`
- flagship choice signal: `16.67%`
- benchmark wins: `2/5`
- verdict: `watchlist`

This remains strategically important, but the current harness shows stronger attention than retained adoption. It is better read as supporting infrastructure for the enterprise-response wedge than as first-promotion material.

### 4. `ai-renewal-risk-briefing-copilot`

- builder ensemble mean adoption: `1.60%`
- flagship choice signal: `10.0%`
- benchmark wins: `2/5`
- verdict: `watchlist`

This candidate is close to the benchmark floor, but it does not yet show enough selection strength to outrank the questionnaire or RFP lanes.

## Recommendation

Recommend `ai-security-questionnaire-copilot` for first maintained benchmark review.

Do not auto-promote it. The correct next step is a human-reviewed benchmark proposal that inserts it into a maintained comparison panel and reruns the relevant hybrid comparison.

## Next Batch

The follow-up batch should test:

- `ai-security-questionnaire-copilot`
- `ai-rfp-response-copilot`
- `ai-compliance-evidence-copilot`

against a maintained enterprise benchmark panel built around:

- `compliance-shield`
- `legal-ops`
- `startup-yc`
- `cursor-copilot`

That batch should answer whether the questionnaire wedge is robust enough to become a standing benchmark rather than only the current frontier leader.
