# MiroFish Enterprise Symmetric Review Note: 2026-03-24

## Scope

Run the cleanest remaining enterprise-response comparison:

- maintained benchmarks:
  - `compliance-shield`
  - `legal-ops`
  - `startup-yc`
  - `cursor-copilot`
- review candidates:
  - `ai-security-questionnaire-copilot`
  - `ai-rfp-response-copilot`

Input artifact:

- `research/meta/MIROFISH_DISCOVERY_BATCH_ENTERPRISE_REVIEW_RESULT_2026-03-24.json`

Output artifacts:

- `research/meta/MIROFISH_HYBRID_SPEC_ENTERPRISE_SYMMETRIC_REVIEW_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_SYMMETRIC_REVIEW_2026-03-24.json`

## Symmetry Change

This batch removes the remaining discovery asymmetry:

- `discovered_domain_ids` is empty
- both enterprise-response candidates move into `promotion_review_domain_ids`
- the breakout shock disappears entirely

The only remaining positive scenario support is the open-source release shock for `cursor-copilot`.

## Result

Builder ensemble mean adoption:

1. `cursor-copilot` at `6.85%`
2. `ai-rfp-response-copilot` at `3.20%`
3. `ai-security-questionnaire-copilot` at `2.93%`
4. `startup-yc` at `2.40%`
5. `compliance-shield` at `0.89%`
6. `legal-ops` at `0.35%`

Flagship choice signal:

1. `cursor-copilot` at `23.34%`
2. `ai-security-questionnaire-copilot` at `20.0%`
3. `startup-yc` at `16.67%`
4. `legal-ops` at `10.0%`
5. `ai-rfp-response-copilot` at `6.67%`
6. `compliance-shield` at `6.66%`

## Interpretation

The symmetric run resolves the main ambiguity from the prior batch.

- `ai-rfp-response-copilot` still edges `ai-security-questionnaire-copilot` on builder ensemble adoption once the breakout asymmetry is removed
- `ai-security-questionnaire-copilot` still wins on flagship choice signal and peak interest strength
- both enterprise-response domains now outrun `startup-yc`, `compliance-shield`, and `legal-ops` on builder ensemble adoption

That means the enterprise-response wedge is real, and the ranking inside that wedge now depends on what the maintained benchmark universe is supposed to optimize.

If the maintained benchmark universe should optimize reproducible ensemble adoption, the cleaner first admission is:

- `ai-rfp-response-copilot`

If it should optimize strongest direct in-run selection signal, the cleaner first admission is:

- `ai-security-questionnaire-copilot`

## Decision

Recommend `ai-rfp-response-copilot` for first maintained benchmark admission.

Reason:

- the symmetric run removes the remaining discovery favoritism
- maintained benchmark membership should prefer stable ensemble performance over a single stronger flagship choice-signal read
- `ai-rfp-response-copilot` still holds the top enterprise-response ensemble result under symmetric conditions

Keep `ai-security-questionnaire-copilot` in the benchmark-review lane immediately behind it.

## Next Batch

The next useful batch is no longer another rivalry test.

The next step should be a maintained benchmark proposal artifact that:

- adds `ai-rfp-response-copilot` to the enterprise benchmark panel
- keeps `ai-security-questionnaire-copilot` as the first challenger
- reruns a broader enterprise benchmark set to confirm the admission does not collapse outside the narrow two-candidate slice
