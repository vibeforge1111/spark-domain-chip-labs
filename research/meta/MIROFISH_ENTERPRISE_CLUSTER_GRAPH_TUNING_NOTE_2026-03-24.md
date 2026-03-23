# MiroFish Enterprise Cluster Graph Tuning Note: 2026-03-24

## Scope

Tune the enterprise cluster methodology by enriching domain graph nodes with inferred behavioral fit tags and inferred retention scores before rerunning the symmetric enterprise cluster playoff.

Code change:

- `src/chip_labs/mirofish/graph.py`

Input artifacts:

- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_PLAYOFF_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_2026-03-24.json`

Output artifacts:

- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_PLAYOFF_TUNED_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_TUNED_2026-03-24.json`

Focused domains:

- `ai-security-questionnaire-copilot`
- `ai-renewal-risk-briefing-copilot`
- `ai-compliance-evidence-copilot`
- `ai-rfp-response-copilot`

## What Changed

The graph builder was previously emitting domain nodes without behavioral fit metadata and without explicit retention priors.

This tuning tranche adds two inferred graph properties per domain node:

- `domain_tags`: inferred from domain text, candidate context, and related chips so persona-fit logic can see audit, compliance, ROI, productivity, startup, DX, and similar behavioral surfaces
- `retention_score`: inferred from sticky workflow cues such as renewal, questionnaire, audit, compliance, evidence, recurring review, and weakened for lighter or more episodic cues such as prospecting, launch, viral, and idea

This matters because the enterprise cluster was being judged with much flatter semantics than intended. The prior playoff ranking should be treated as partially under-specified rather than fully trusted.

## Before / After Read

Previous symmetric enterprise playoff:

1. `cursor-copilot` at `4.89%` ensemble adoption
2. `startup-yc` at `4.18%`
3. `ai-renewal-risk-briefing-copilot` at `2.67%`
4. `ai-security-questionnaire-copilot` at `2.58%`
5. `ai-compliance-evidence-copilot` at `1.63%`
6. `ai-rfp-response-copilot` at `1.45%`

Tuned symmetric enterprise playoff:

1. `startup-yc` at `4.65%` ensemble adoption
2. `cursor-copilot` at `3.88%`
3. `ai-security-questionnaire-copilot` at `1.54%`
4. `ai-rfp-response-copilot` at `0.80%`
5. `ai-renewal-risk-briefing-copilot` at `0.47%`
6. `ai-compliance-evidence-copilot` at `0.18%`

Flagship signal changes:

- `cursor-copilot` becomes the top full-panel direct choice domain at `20.0%`
- `startup-yc` still leads the full panel on ensemble adoption at `4.65%`
- `ai-renewal-risk-briefing-copilot` becomes the strongest enterprise attention domain at `16.67%` choice signal
- `ai-security-questionnaire-copilot` becomes the strongest enterprise cluster domain on ensemble adoption at `1.54%`
- `ai-rfp-response-copilot` overtakes renewal on ensemble adoption, but not on direct choice conviction

## Tuned Diagnostic Read

Benchmark median ensemble adoption in the tuned playoff is `0.63%`.

### `ai-security-questionnaire-copilot`

- ensemble adoption: `1.54%`
- choice signal: `10.0%`
- peak interest: `83.33%`
- benchmark status: above median

Main bottleneck:

- interest-to-choice friction

This is a materially different read from the prior tranche. The graph tuning leaves questionnaire as the clearest enterprise ensemble survivor, and its main remaining weakness is still upstream conversion.

### `ai-rfp-response-copilot`

- ensemble adoption: `0.80%`
- choice signal: `6.67%`
- peak interest: `70.0%`
- benchmark status: slightly above median

Main bottleneck:

- interest-to-choice friction

RFP remains a conversion problem. The tuning helps it clear the benchmark median, but it still does not become a high-conviction enterprise winner.

### `ai-renewal-risk-briefing-copilot`

- ensemble adoption: `0.47%`
- choice signal: `16.67%`
- peak interest: `73.33%`
- benchmark status: slightly below median

Main bottleneck:

- attention-to-retention drop, plus some interest-to-choice friction

Renewal is now the highest-conviction enterprise attention lane, but it still fails to hold that strength across the builder ensemble.

### `ai-compliance-evidence-copilot`

- ensemble adoption: `0.18%`
- choice signal: `3.33%`
- peak interest: `80.0%`
- benchmark status: below median

Main bottleneck:

- interest-to-choice friction

Compliance evidence stays weak even after the graph enrichment and remains behind the other enterprise domains.

## Interpretation

The main outcome is methodological, not promotional.

- The prior cluster ordering was sensitive to missing graph semantics.
- After adding inferred tags and retention priors, the enterprise read changes from a single clean ranking to a split read:
  - `ai-security-questionnaire-copilot` wins enterprise ensemble adoption
  - `ai-renewal-risk-briefing-copilot` wins enterprise attention
  - `ai-rfp-response-copilot` becomes more ensemble-viable than renewal, but without stronger conviction
- `startup-yc` still beats the entire enterprise cluster on ensemble adoption, so no maintained benchmark admission should happen yet

The new question is narrower:

1. why questionnaire becomes materially stronger once fit semantics are present
2. why renewal can attract attention but still fail to survive the ensemble
3. why RFP and compliance evidence still convert interest into choice so weakly

## Decision

Do not change maintained benchmark membership.

Treat this tranche as a methodology correction:

- the graph builder now supplies the semantic fit signals the simulation expected
- the enterprise cluster ranking should now be evaluated from the tuned playoff, not the earlier under-specified playoff alone

Working enterprise priorities after tuning:

1. `ai-security-questionnaire-copilot` as the first ensemble-stable enterprise candidate
2. `ai-renewal-risk-briefing-copilot` as the first persistence-tuning hypothesis
3. `ai-rfp-response-copilot` as the second conversion-tuning hypothesis
4. `ai-compliance-evidence-copilot` as the trailing enterprise lane

## Next Batch

The next batch should be a targeted persistence-vs-conversion tuning tranche, not another admission attempt.

It should test:

1. stronger retained-value persistence for renewal-oriented workflows
2. stronger interest-to-choice conversion for questionnaire, RFP, and compliance evidence
3. whether `startup-yc` still leads once enterprise-specific fit semantics exist throughout the whole panel
