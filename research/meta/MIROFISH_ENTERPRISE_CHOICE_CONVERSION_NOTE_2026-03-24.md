# MiroFish Enterprise Choice Conversion Note: 2026-03-24

## Scope

Test an explicit choice-conversion hypothesis for proof-heavy enterprise domains by adding a graph-level `choice_score` and a narrow awareness boost for personas already in the `interested` or `evaluating` stages.

Code changes:

- `src/chip_labs/mirofish/graph.py`
- `src/chip_labs/mirofish/simulation.py`

Input artifacts:

- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_CONVERSION_TUNING_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_CONVERSION_TUNING_2026-03-24.json`

Output artifacts:

- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_CHOICE_CONVERSION_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_CHOICE_CONVERSION_2026-03-24.json`

Focused domains:

- `ai-security-questionnaire-copilot`
- `ai-renewal-risk-briefing-copilot`
- `ai-rfp-response-copilot`
- `ai-compliance-evidence-copilot`

## What Changed

The sticky-workflow tranche improved questionnaire and renewal, but it still left RFP and compliance evidence without a domain-specific explanation for why interested personas would move into actual selection.

This tranche adds one narrower prior:

- infer graph-level `choice_score` from proof-heavy workflow cues such as `rfp`, `questionnaire`, `evidence`, `controls`, `audit`, `procurement`, `submit`, and reusable evidence packaging
- use that score only for personas already at `interested` or `evaluating`
- apply the boost in the awareness layer, not in retained-adoption gates

This keeps the intervention bounded:

- it does not lower late-stage retention standards
- it does not act as a generic enterprise threshold cut
- it mainly tests whether proof-heavy workflows deserve extra in-run decisiveness once a persona is already engaged

## Before / After Read

Sticky-workflow conversion replay:

1. `startup-yc` at `4.00%` ensemble adoption
2. `cursor-copilot` at `3.41%`
3. `ai-security-questionnaire-copilot` at `1.60%`
4. `ai-renewal-risk-briefing-copilot` at `1.15%`
5. `ai-rfp-response-copilot` at `0.98%`
6. `ai-compliance-evidence-copilot` at `0.29%`

Choice-conversion replay:

1. `startup-yc` at `3.91%` ensemble adoption
2. `cursor-copilot` at `2.58%`
3. `ai-security-questionnaire-copilot` at `2.16%`
4. `ai-renewal-risk-briefing-copilot` at `1.42%`
5. `ai-rfp-response-copilot` at `1.30%`
6. `ai-compliance-evidence-copilot` at `0.12%`

Directional effects:

- `ai-security-questionnaire-copilot` improves from `1.60%` to `2.16%`
- `ai-renewal-risk-briefing-copilot` improves from `1.15%` to `1.42%`
- `ai-rfp-response-copilot` improves from `0.98%` to `1.30%`, but still misses the benchmark median narrowly
- `ai-compliance-evidence-copilot` gains flagship choice signal from `10.0%` to `16.67%`, but its ensemble adoption falls from `0.29%` to `0.12%`

Flagship movement:

- `ai-renewal-risk-briefing-copilot` remains the top direct-choice domain at `30.0%`
- `ai-security-questionnaire-copilot` remains the strongest enterprise ensemble domain at `2.16%`
- `ai-compliance-evidence-copilot` shows that stronger choice alone does not guarantee durable ensemble survival

## Choice-Conversion Diagnostic Read

Benchmark median ensemble adoption in the choice-conversion replay is `1.36%`.

### `ai-security-questionnaire-copilot`

- ensemble adoption: `2.16%`
- choice signal: `13.34%`
- peak interest: `83.33%`
- benchmark status: above median

Main bottleneck:

- interest-to-choice friction

Questionnaire stays first on enterprise ensemble adoption and widens its lead over the benchmark median, but it still leaves too much demand stuck before decisive choice.

### `ai-renewal-risk-briefing-copilot`

- ensemble adoption: `1.42%`
- choice signal: `30.0%`
- peak interest: `73.33%`
- benchmark status: above median

Main bottleneck:

- attention-to-retention drop

Renewal keeps the strongest enterprise choice profile. The explicit choice tranche does not change its basic diagnosis: this is now mainly a persistence problem, not an early conversion problem.

### `ai-rfp-response-copilot`

- ensemble adoption: `1.30%`
- choice signal: `3.33%`
- peak interest: `70.0%`
- benchmark status: slightly below median

Main bottleneck:

- interest-to-choice friction

RFP moves closer to the benchmark line on ensemble adoption, but it still does not generate convincing direct-choice signal. The explicit choice hypothesis helps only partially here.

### `ai-compliance-evidence-copilot`

- ensemble adoption: `0.12%`
- choice signal: `16.67%`
- peak interest: `80.0%`
- benchmark status: below median

Main bottlenecks:

- attention-to-retention drop
- interest-to-choice friction

Compliance evidence is the most revealing result in the batch. It can now win more direct in-run choice, but the ensemble still does not hold it. That means its remaining weakness is not just a choice gate.

## Interpretation

This tranche is useful, but it is not a full fix.

- A proof-heavy choice prior improves ensemble positioning for questionnaire, renewal, and RFP.
- It does not produce a clean breakthrough for RFP.
- It exposes a sharper mechanism split for compliance evidence:
  stronger choice can appear without stronger retained ensemble adoption.

The cleanest read after this replay is:

1. `ai-security-questionnaire-copilot` remains the strongest enterprise ensemble candidate
2. `ai-renewal-risk-briefing-copilot` remains the strongest direct-choice enterprise lane
3. `ai-rfp-response-copilot` is close enough to the benchmark median to justify one stable post-tranche validation read
4. `ai-compliance-evidence-copilot` now looks like a mixed choice-plus-retention problem, not a pure choice problem

## Decision

Keep the explicit choice-conversion change.

Why:

- it improves enterprise ensemble behavior without becoming a broad enterprise uplift
- it narrows the remaining open questions instead of hiding them
- it clarifies that compliance evidence needs more than a pre-choice fix

Do not change maintained benchmark membership.

`startup-yc` still leads the cluster overall at `3.91%` ensemble adoption.

## Next Batch

The next useful step should be the stable post-tranche enterprise validation read that was already planned:

1. rerun the symmetric enterprise cluster playoff once more as the clean validation artifact
2. record whether RFP can hold its near-median position
3. record whether compliance evidence still loses after choice
4. only then widen back to the full `515`-domain rerun
