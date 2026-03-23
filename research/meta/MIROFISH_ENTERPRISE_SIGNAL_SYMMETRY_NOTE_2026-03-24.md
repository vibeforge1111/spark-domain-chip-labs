# MiroFish Enterprise Signal Symmetry Note: 2026-03-24

## Scope

Align churn and retention checks with the same macro-aware, fit-aware signal family used during adoption advancement, then rerun the symmetric enterprise cluster playoff.

Code change:

- `src/chip_labs/mirofish/simulation.py`

Input artifacts:

- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_PLAYOFF_TUNED_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_TUNED_2026-03-24.json`

Output artifacts:

- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_SIGNAL_SYMMETRY_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_SIGNAL_SYMMETRY_2026-03-24.json`

Focused domains:

- `ai-security-questionnaire-copilot`
- `ai-renewal-risk-briefing-copilot`
- `ai-compliance-evidence-copilot`
- `ai-rfp-response-copilot`

## What Changed

Before this tranche, the simulation used one signal family for advancement and a weaker one for churn and retention:

- advancement used macro-adjusted awareness and persona fit
- churn and retention used raw awareness without the same semantic modifiers

This patch closes that asymmetry:

- phase-1 evaluation now uses a shared `_effective_awareness(...)` helper
- churn and retention now use `_fit_adjusted_awareness(...)`
- retention-side checks now see macro context and persona-domain fit rather than only raw signal exposure

## Before / After Read

Graph-tuned enterprise replay:

1. `startup-yc` at `4.65%` ensemble adoption
2. `cursor-copilot` at `3.88%`
3. `ai-security-questionnaire-copilot` at `1.54%`
4. `ai-rfp-response-copilot` at `0.80%`
5. `ai-renewal-risk-briefing-copilot` at `0.47%`
6. `ai-compliance-evidence-copilot` at `0.18%`

Signal-symmetry replay:

1. `startup-yc` at `4.62%` ensemble adoption
2. `cursor-copilot` at `2.25%`
3. `ai-security-questionnaire-copilot` at `1.30%`
4. `ai-rfp-response-copilot` at `1.04%`
5. `ai-compliance-evidence-copilot` at `0.47%`
6. `ai-renewal-risk-briefing-copilot` at `0.41%`

Meaningful directional changes:

- `ai-rfp-response-copilot` improves from `0.80%` to `1.04%`
- `ai-compliance-evidence-copilot` improves from `0.18%` to `0.47%`
- `ai-security-questionnaire-copilot` softens from `1.54%` to `1.30%` but remains the strongest enterprise ensemble domain
- `ai-renewal-risk-briefing-copilot` still leads the enterprise cluster on direct attention signal at `16.67%`
- `startup-yc` remains the overall ensemble leader

## Signal-Symmetry Diagnostic Read

Benchmark median ensemble adoption in the signal-symmetry replay is `0.75%`.

### `ai-security-questionnaire-copilot`

- ensemble adoption: `1.30%`
- choice signal: `10.0%`
- peak interest: `83.33%`
- benchmark status: above median

Main bottleneck:

- interest-to-choice friction

Questionnaire still looks like the best enterprise candidate for ensemble stability, but the next constraint remains conversion into actual choice.

### `ai-rfp-response-copilot`

- ensemble adoption: `1.04%`
- choice signal: `13.33%`
- peak interest: `70.0%`
- benchmark status: above median

Main bottlenecks:

- interest-to-choice friction
- attention-to-retention drop

RFP benefits the most from signal symmetry. It is no longer just a weak discovery lane. It is now a real mixed conversion-plus-retention candidate.

### `ai-compliance-evidence-copilot`

- ensemble adoption: `0.47%`
- choice signal: `13.33%`
- peak interest: `80.0%`
- benchmark status: below median

Main bottlenecks:

- interest-to-choice friction
- attention-to-retention drop

Compliance evidence improves materially, but not enough to clear the new benchmark median.

### `ai-renewal-risk-briefing-copilot`

- ensemble adoption: `0.41%`
- choice signal: `16.67%`
- peak interest: `73.33%`
- benchmark status: below median

Main bottlenecks:

- attention-to-retention drop
- interest-to-choice friction

Renewal keeps the strongest enterprise attention profile, but symmetry alone does not solve its persistence problem.

## Interpretation

This tranche is a real methodology improvement even though it does not produce a benchmark-admission winner.

- The old asymmetric retention logic was masking some enterprise viability, especially for RFP and compliance evidence.
- Once retention-side checks use fit-aware signals, RFP and compliance evidence both strengthen.
- Questionnaire stays first on enterprise ensemble adoption, which means its strength is not an artifact of the old asymmetry.
- Renewal remains strategically interesting, but it still cannot turn attention into durable ensemble strength.

The new enterprise read is:

1. `ai-security-questionnaire-copilot` remains the best ensemble-stable enterprise domain
2. `ai-rfp-response-copilot` becomes the clearest improved challenger
3. `ai-renewal-risk-briefing-copilot` remains a persistence hypothesis rather than a promotion candidate
4. `ai-compliance-evidence-copilot` improves, but still trails the median

## Decision

Do not change maintained benchmark membership.

Treat this tranche as the first actual post-diagnostic tuning result:

- it validates that retention-side signal symmetry matters
- it improves enterprise-response conversion outcomes for RFP and compliance evidence
- it does not yet close the gap to `startup-yc`

## Next Batch

The next tuning tranche should narrow further around two hypotheses:

1. reduce interest-to-choice friction for questionnaire, RFP, and compliance evidence
2. reduce attention-to-retention loss for renewal and RFP once a domain has already won choice
