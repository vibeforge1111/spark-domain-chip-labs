# MiroFish Benchmark Review Note: Enterprise Response 2026-03-24

## Scope

Validate the promotion recommendation for `ai-security-questionnaire-copilot` by moving it into a benchmark-review lane and rerunning the focused enterprise-response panel without discovery breakout support for that candidate.

Input artifacts:

- `research/meta/MIROFISH_DISCOVERY_BATCH_FOCUSED_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_PROMOTION_BRIEF_ENTERPRISE_RESPONSE_2026-03-24.json`

Output artifacts:

- `research/meta/MIROFISH_HYBRID_SPEC_BENCHMARK_REVIEW_ENTERPRISE_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_BENCHMARK_REVIEW_ENTERPRISE_2026-03-24.json`

## What Changed In This Validation

- `ai-security-questionnaire-copilot` moved from `discovered_candidate` to `promotion_review_candidate`
- the breakout shock no longer targeted it
- breakout support shifted to the remaining discovered candidates:
  - `ai-sales-call-prep-copilot`
  - `ai-rfp-response-copilot`
  - `ai-compliance-evidence-copilot`

## Key Comparison

Earlier focused run:

- `ai-security-questionnaire-copilot` builder ensemble mean adoption: `4.83%`
- flagship choice signal: `23.34%`

Benchmark-review rerun:

- `ai-security-questionnaire-copilot` builder ensemble mean adoption: `2.64%`
- flagship choice signal: `16.67%`

This is a real drop. The earlier promotion read was directionally correct, but part of the lead came from discovery-lane favoritism.

## Current Standing

`ai-security-questionnaire-copilot` still beats several relevant maintained benchmarks in the rerun:

- `startup-yc` at `1.21%`
- `legal-ops` at `0.56%`
- `compliance-shield` at `0.32%`

But it no longer leads the broader mixed panel:

- `cursor-copilot` leads at `6.67%`
- `ai-investor-update-copilot` reaches `3.56%`
- `ai-sales-call-prep-copilot` reaches `3.11%`
- `indie-hacker` reaches `2.73%`

## Decision

Do not graduate `ai-security-questionnaire-copilot` into the maintained benchmark universe yet.

Keep it in a `benchmark_review_candidate` lane.

The candidate is strong enough to justify continued benchmark review, but not strong enough to skip one more narrow validation pass after removing discovery-lane favoritism.

## Next Batch

Run one narrower enterprise-only review batch with:

- maintained benchmarks:
  - `compliance-shield`
  - `legal-ops`
  - `startup-yc`
  - `cursor-copilot`
- review candidate:
  - `ai-security-questionnaire-copilot`
- shadow challenger:
  - `ai-rfp-response-copilot`

That batch should answer a stricter question:

Is `ai-security-questionnaire-copilot` truly a maintained benchmark candidate, or only the current best enterprise-response frontier chip?
