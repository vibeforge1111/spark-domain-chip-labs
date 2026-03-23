# MiroFish Enterprise Conversion Tuning Note: 2026-03-24

## Scope

Reduce the `interested -> evaluating -> trial` bottleneck for sticky workflow domains by using graph-level `retention_score` as a narrow conversion prior inside persona stage advancement.

Code changes:

- `src/chip_labs/mirofish/personas.py`
- `src/chip_labs/mirofish/simulation.py`

Input artifacts:

- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_SIGNAL_SYMMETRY_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_SIGNAL_SYMMETRY_2026-03-24.json`

Output artifacts:

- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_CONVERSION_TUNING_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_CONVERSION_TUNING_2026-03-24.json`

Focused domains:

- `ai-security-questionnaire-copilot`
- `ai-renewal-risk-briefing-copilot`
- `ai-rfp-response-copilot`
- `ai-compliance-evidence-copilot`

## What Changed

The signal-symmetry tranche showed that enterprise domains were still piling up in `interested` and `evaluating`, with only a few personas reaching `trial` and essentially none reaching retained adoption.

This tranche adds a narrow conversion prior:

- if a domain has high inferred `retention_score`
- and a persona is already at `interested` or `evaluating`
- the advancement threshold for that pair is eased modestly

This models a simple behavioral claim:

- recurring workflow domains are easier to justify trying once interest already exists
- but retained adoption still has to be earned later in the funnel

The change does not lower late-stage retained adoption gates.

## Before / After Read

Signal-symmetry replay:

1. `startup-yc` at `4.62%` ensemble adoption
2. `cursor-copilot` at `2.25%`
3. `ai-security-questionnaire-copilot` at `1.30%`
4. `ai-rfp-response-copilot` at `1.04%`
5. `ai-compliance-evidence-copilot` at `0.47%`
6. `ai-renewal-risk-briefing-copilot` at `0.41%`

Conversion-tuned replay:

1. `startup-yc` at `4.00%` ensemble adoption
2. `cursor-copilot` at `3.41%`
3. `ai-security-questionnaire-copilot` at `1.60%`
4. `ai-renewal-risk-briefing-copilot` at `1.15%`
5. `ai-rfp-response-copilot` at `0.98%`
6. `ai-compliance-evidence-copilot` at `0.29%`

Directional effects:

- `ai-security-questionnaire-copilot` improves from `1.30%` to `1.60%`
- `ai-renewal-risk-briefing-copilot` improves sharply from `0.41%` to `1.15%`
- `ai-rfp-response-copilot` softens slightly from `1.04%` to `0.98%`
- `ai-compliance-evidence-copilot` softens from `0.47%` to `0.29%`
- `startup-yc` weakens from `4.62%` to `4.00%`

Flagship movement:

- `ai-renewal-risk-briefing-copilot` becomes the top direct-choice domain at `30.0%`
- `ai-renewal-risk-briefing-copilot` also becomes the top flagship final-adoption domain at `6.67%`
- `ai-security-questionnaire-copilot` rises to `20.0%` direct choice signal

## Conversion-Tuning Diagnostic Read

Benchmark median ensemble adoption in the conversion-tuned replay is `1.06%`.

### `ai-security-questionnaire-copilot`

- ensemble adoption: `1.60%`
- choice signal: `20.0%`
- peak interest: `83.33%`
- benchmark status: above median

Main bottlenecks:

- attention-to-retention drop
- interest-to-choice friction

Questionnaire strengthens materially, but it still turns far more attention into trial than into retained adoption.

### `ai-renewal-risk-briefing-copilot`

- ensemble adoption: `1.15%`
- choice signal: `30.0%`
- flagship final adoption: `6.67%`
- benchmark status: above median

Main bottleneck:

- attention-to-retention drop

This is the clearest beneficiary of the recurring-workflow prior. Renewal now looks much more like a real enterprise candidate, but its persistence remains fragile.

### `ai-rfp-response-copilot`

- ensemble adoption: `0.98%`
- choice signal: `6.67%`
- peak interest: `70.0%`
- benchmark status: slightly below median

Main bottleneck:

- interest-to-choice friction

RFP does not benefit from this tuning. That is useful information: its problem is not mainly a missing sticky-workflow prior.

### `ai-compliance-evidence-copilot`

- ensemble adoption: `0.29%`
- choice signal: `10.0%`
- peak interest: `80.0%`
- benchmark status: below median

Main bottleneck:

- interest-to-choice friction

Compliance evidence also does not benefit from this tuning. It still needs a separate conversion-side hypothesis.

## Interpretation

This tranche does not solve the entire enterprise cluster, but it gives a cleaner decomposition.

- The recurring-workflow trial prior is real.
- It helps the domains that behave like recurring operational loops:
  - questionnaire
  - renewal
- It does not help the domains whose main problem is still earlier choice conversion:
  - RFP
  - compliance evidence

That means the enterprise cluster now splits more clearly into two groups:

1. sticky recurring workflows that need persistence tuning after choice
2. domains that still need a better reason for personas to choose them in the first place

## Decision

Do not change maintained benchmark membership.

Keep the conversion-tuning change because it improves the modeling of recurring workflow domains and narrows the gap to `startup-yc`, but do not treat it as a general enterprise boost.

Working enterprise priorities after this tranche:

1. `ai-security-questionnaire-copilot`
2. `ai-renewal-risk-briefing-copilot`
3. `ai-rfp-response-copilot`
4. `ai-compliance-evidence-copilot`

## Next Batch

The next useful tranche should stop targeting sticky workflow priors and instead target explicit choice conversion:

1. raise `interested -> evaluating` conversion for RFP and compliance evidence
2. keep retained-adoption standards unchanged
3. check whether questionnaire and renewal still hold their gains under that more specific choice-conversion tuning
