# MiroFish Enterprise-Only Review Note: 2026-03-24

## Scope

Run the narrowest enterprise-only review batch requested by the previous benchmark-review note:

- maintained benchmarks:
  - `compliance-shield`
  - `legal-ops`
  - `startup-yc`
  - `cursor-copilot`
- review candidate:
  - `ai-security-questionnaire-copilot`
- shadow challenger:
  - `ai-rfp-response-copilot`

Input artifacts:

- `research/meta/MIROFISH_DISCOVERY_BATCH_FOCUSED_RESULT_2026-03-24.json`

Output artifacts:

- `research/meta/MIROFISH_DISCOVERY_BATCH_ENTERPRISE_REVIEW_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_SPEC_ENTERPRISE_ONLY_REVIEW_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_ONLY_REVIEW_2026-03-24.json`

## Narrowing Change

This batch narrows the candidate universe to only two enterprise-response domains:

- `ai-security-questionnaire-copilot`
- `ai-rfp-response-copilot`

`ai-security-questionnaire-copilot` stays in the `promotion_review_candidate` lane.

`ai-rfp-response-copilot` remains the only discovered challenger, so the breakout shock still favors it in this run.

## Result

Builder ensemble mean adoption:

1. `cursor-copilot` at `6.16%`
2. `ai-rfp-response-copilot` at `4.35%`
3. `ai-security-questionnaire-copilot` at `3.97%`
4. `startup-yc` at `3.20%`
5. `legal-ops` at `0.59%`
6. `compliance-shield` at `0.53%`

Flagship choice signal:

1. `startup-yc` at `26.67%`
2. `cursor-copilot` at `23.34%`
3. `ai-security-questionnaire-copilot` at `20.0%`
4. `legal-ops` at `10.0%`
5. `ai-rfp-response-copilot` at `6.67%`

## Interpretation

The narrow enterprise-only batch does not justify maintained benchmark admission yet.

It does show two useful things:

- `ai-security-questionnaire-copilot` still beats `startup-yc`, `legal-ops`, and `compliance-shield` on builder ensemble adoption
- `ai-rfp-response-copilot` is a real shadow challenger and now slightly outruns the questionnaire lane on builder ensemble adoption

But the comparison is still not symmetric:

- the review candidate does not get discovery breakout support
- the shadow challenger does

That means the `4.35%` versus `3.97%` gap is real enough to matter, but not clean enough to treat as final.

## Decision

Do not admit `ai-security-questionnaire-copilot` into the maintained benchmark universe yet.

Do not downgrade it either.

Promote `ai-rfp-response-copilot` from shadow challenger to co-review candidate for the next batch.

## Next Batch

Run one symmetric enterprise-response review batch where both:

- `ai-security-questionnaire-copilot`
- `ai-rfp-response-copilot`

are treated as benchmark-review candidates, with no discovery-breakout favoritism for either one.

That batch should answer the cleanest remaining question:

Which enterprise-response wedge deserves first maintained benchmark admission under symmetric conditions?
