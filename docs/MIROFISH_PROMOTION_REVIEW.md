# MiroFish Promotion Review

MiroFish discovery and hybrid evaluation artifacts are exploratory. They should not auto-promote a discovered domain into the maintained benchmark universe. Promotion requires a separate review step that compares the strongest discovered candidates against the active benchmark panel and emits a human-review recommendation.

## Purpose

Use the promotion brief when a focused hybrid run has already identified a narrow cluster and the next question is which candidate deserves benchmark-review priority first.

The promotion brief is not a doctrine packet. It is an operator-facing comparison layer that:

- merges flagship prediction metrics with builder-ensemble metrics
- compares discovered candidates against the current benchmark panel
- emits a recommendation of `review_now`, `watchlist`, or `hold`
- recommends at most one candidate for benchmark-review escalation

## Current Read

Promotion review is strongest when the run already used a relevant benchmark panel. For example, the enterprise-response focused batch should be read against:

- `compliance-shield`
- `legal-ops`
- `startup-yc`
- `indie-hacker`
- `cursor-copilot`

That panel is not perfect, but it is strong enough to answer a narrower question: which newly discovered enterprise-response domain has earned first benchmark-review priority.

## CLI

Build a promotion brief from a saved hybrid run:

```bash
python -m chip_labs.cli mirofish-promotion-brief \
  --input research/meta/MIROFISH_HYBRID_RUN_FOCUSED_2026-03-24.json \
  --domains ai-security-questionnaire-copilot,ai-rfp-response-copilot,ai-compliance-evidence-copilot,ai-renewal-risk-briefing-copilot \
  --output research/meta/MIROFISH_PROMOTION_BRIEF_ENTERPRISE_RESPONSE_2026-03-24.json
```

If `--domains` is omitted, the command reviews all discovered candidates from the run.

## Decision Rules

The brief currently uses a conservative operator heuristic:

- `review_now`
  - clears the benchmark median on builder-ensemble adoption
  - shows at least `15%` flagship choice signal
  - outruns at least two benchmark domains on builder-ensemble adoption
- `watchlist`
  - does not yet clear the full review bar, but still shows meaningful adoption or choice signal
- `hold`
  - remains exploratory and should stay in the frontier lane

These are promotion-review thresholds, not benchmark-membership thresholds.

## Output Shape

The promotion brief should expose:

- benchmark summary
- promotion table for the selected candidates
- benchmark win counts
- recommendation and rationale
- governance note that benchmark membership still requires human review

## Governance

Promotion review does not edit benchmark membership. It only nominates a candidate for human review.

If the brief recommends `promote_for_human_review`, the next step is to create a new focused benchmark batch or maintained-benchmark update proposal that is reviewed explicitly before adoption.
