# MiroFish Enterprise Benchmark Proposal Note: 2026-03-24

## Scope

Test the maintained benchmark proposal path after the symmetric enterprise review:

- provisional benchmark member:
  - `ai-rfp-response-copilot`
- first benchmark-review challenger:
  - `ai-security-questionnaire-copilot`
- secondary enterprise context domains:
  - `ai-compliance-evidence-copilot`
  - `ai-renewal-risk-briefing-copilot`
- maintained benchmark panel:
  - `compliance-shield`
  - `legal-ops`
  - `startup-yc`
  - `cursor-copilot`

Input artifact:

- `research/meta/MIROFISH_DISCOVERY_BATCH_ENTERPRISE_BENCHMARK_PROPOSAL_RESULT_2026-03-24.json`

Output artifacts:

- `research/meta/MIROFISH_HYBRID_SPEC_ENTERPRISE_BENCHMARK_PROPOSAL_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_BENCHMARK_PROPOSAL_2026-03-24.json`

## Proposal Setup

This tranche does not edit the maintained benchmark library.

Instead, it uses the new provisional benchmark lane:

- `ai-rfp-response-copilot` enters `proposed_benchmark_domain_ids`
- `ai-security-questionnaire-copilot` stays in `promotion_review_domain_ids`
- `ai-compliance-evidence-copilot` and `ai-renewal-risk-briefing-copilot` remain as discovered enterprise context domains

## Result

Builder ensemble mean adoption:

1. `cursor-copilot` at `5.63%`
2. `ai-renewal-risk-briefing-copilot` at `3.73%`
3. `ai-compliance-evidence-copilot` at `3.70%`
4. `ai-security-questionnaire-copilot` at `3.26%`
5. `ai-rfp-response-copilot` at `3.14%`
6. `startup-yc` at `1.42%`
7. `compliance-shield` at `0.98%`
8. `legal-ops` at `0.32%`

Key flagship choice signals:

- `ai-compliance-evidence-copilot` at `26.67%`
- `ai-renewal-risk-briefing-copilot` at `23.34%`
- `ai-security-questionnaire-copilot` at `23.33%`
- `ai-rfp-response-copilot` at `13.34%`

## Interpretation

The narrow symmetric review identified `ai-rfp-response-copilot` as the cleanest first-admission candidate when the comparison was only RFP versus questionnaire.

That recommendation does not survive the broader enterprise panel strongly enough to edit the maintained benchmark library yet.

Why:

- `ai-rfp-response-copilot` no longer leads the enterprise-response cluster
- it trails `ai-security-questionnaire-copilot` on builder ensemble adoption in this broader run
- it is also overtaken by `ai-renewal-risk-briefing-copilot` and `ai-compliance-evidence-copilot` once secondary enterprise domains return

The enterprise-response wedge is still clearly stronger than the incumbent enterprise benchmarks:

- all four enterprise-response domains beat `startup-yc`, `compliance-shield`, and `legal-ops`

But the wedge leader is not stable enough yet for a maintained benchmark library edit.

## Decision

Defer the maintained benchmark admission proposal for `ai-rfp-response-copilot`.

Do not edit the maintained benchmark library in this tranche.

Keep:

- `ai-rfp-response-copilot`
- `ai-security-questionnaire-copilot`
- `ai-compliance-evidence-copilot`
- `ai-renewal-risk-briefing-copilot`

inside the enterprise benchmark-review cluster.

## Next Batch

The next autonomous batch should stop treating this as a single-candidate admission question and instead run an enterprise cluster playoff:

- `ai-rfp-response-copilot`
- `ai-security-questionnaire-copilot`
- `ai-compliance-evidence-copilot`
- `ai-renewal-risk-briefing-copilot`

under symmetric non-discovered conditions, with a decision rule for:

1. first maintained benchmark admission
2. second benchmark-review priority
3. domains that stay as secondary enterprise challengers
