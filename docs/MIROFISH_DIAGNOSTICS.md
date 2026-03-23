# MiroFish Diagnostics

MiroFish ranking artifacts answer which domains are ahead. Diagnostic artifacts answer why a domain is underperforming.

## Purpose

Use a run diagnostic brief after a stable playoff or benchmark-review run when the next step is model tuning or methodology tuning rather than another ranking batch.

The diagnostic brief is meant to surface:

- which domains convert interest into choice poorly
- which domains convert choice into retained adoption poorly
- which domains stall between trial and retained adoption
- which domains are still below the current benchmark median

## CLI

Build a diagnostic brief from a saved hybrid run:

```bash
python -m chip_labs.cli mirofish-run-diagnostic \
  --input research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_PLAYOFF_2026-03-24.json \
  --domains ai-security-questionnaire-copilot,ai-renewal-risk-briefing-copilot,ai-compliance-evidence-copilot,ai-rfp-response-copilot \
  --output research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_2026-03-24.json
```

If `--domains` is omitted, the command defaults to:

- `promotion_review_domain_ids`, or
- `discovered_domain_ids` if no review candidates exist

## Output Shape

The diagnostic brief should include:

- benchmark median reference
- strongest benchmark ensemble domains
- per-domain bottleneck metrics:
  - `attention_to_ensemble_gap`
  - `interest_to_choice_gap`
  - `flagship_retention_gap`
  - `trial_to_adoption_gap`
  - `benchmark_gap`
- diagnostic tags
- short diagnostic summaries

## Reading The Metrics

- `attention_to_ensemble_gap`
  - large values mean agents notice and choose the domain, but it does not survive into ensemble adoption
- `interest_to_choice_gap`
  - large values mean the domain attracts attention but does not turn into actual selection
- `trial_to_adoption_gap`
  - large values mean trial behavior exists, but retained adoption collapses
- `benchmark_gap`
  - negative values mean the domain still trails the current benchmark median on ensemble adoption

## Governance

Diagnostics do not mutate the benchmark library. They are for tuning and investigation only.
