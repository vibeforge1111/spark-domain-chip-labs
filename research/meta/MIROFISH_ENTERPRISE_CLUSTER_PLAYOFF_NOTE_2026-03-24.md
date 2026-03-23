# MiroFish Enterprise Cluster Playoff Note: 2026-03-24

## Scope

Run the full enterprise cluster under symmetric benchmark-review conditions:

- `ai-compliance-evidence-copilot`
- `ai-security-questionnaire-copilot`
- `ai-rfp-response-copilot`
- `ai-renewal-risk-briefing-copilot`

All four domains are treated as benchmark-review candidates. None remain in the discovered lane, and no enterprise domain receives breakout support.

Maintained benchmark panel:

- `compliance-shield`
- `legal-ops`
- `startup-yc`
- `cursor-copilot`

Input artifact:

- `research/meta/MIROFISH_DISCOVERY_BATCH_ENTERPRISE_BENCHMARK_PROPOSAL_RESULT_2026-03-24.json`

Output artifacts:

- `research/meta/MIROFISH_HYBRID_SPEC_ENTERPRISE_CLUSTER_PLAYOFF_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_PLAYOFF_2026-03-24.json`

## Result

Builder ensemble mean adoption:

1. `cursor-copilot` at `4.89%`
2. `startup-yc` at `4.18%`
3. `ai-renewal-risk-briefing-copilot` at `2.67%`
4. `ai-security-questionnaire-copilot` at `2.58%`
5. `ai-compliance-evidence-copilot` at `1.63%`
6. `ai-rfp-response-copilot` at `1.45%`
7. `compliance-shield` at `0.80%`
8. `legal-ops` at `0.06%`

Flagship choice signal:

1. `ai-security-questionnaire-copilot` at `26.67%`
2. `cursor-copilot` at `23.34%`
3. `startup-yc` at `23.34%`
4. `ai-renewal-risk-briefing-copilot` at `20.0%`
5. `ai-compliance-evidence-copilot` at `16.67%`
6. `ai-rfp-response-copilot` at `3.33%`

## Interpretation

This playoff is the most stable enterprise-cluster read so far because:

- all four enterprise domains are symmetric
- none of them receive discovery breakout help
- the proposal lane is removed from the comparison

The result is more conservative than the earlier narrower slices.

What survives:

- the enterprise cluster clearly beats `compliance-shield` and `legal-ops`
- `ai-security-questionnaire-copilot` is the strongest direct choice-signal domain in the cluster
- `ai-renewal-risk-briefing-copilot` is the strongest cluster domain on builder ensemble adoption

What fails:

- no enterprise cluster domain beats `startup-yc` on builder ensemble adoption in this symmetric playoff
- `ai-rfp-response-copilot` falls to the bottom of the enterprise cluster under symmetric conditions

## Decision

Do not admit any enterprise-response domain into the maintained benchmark universe yet.

Within the cluster, the new ordering is:

1. `ai-security-questionnaire-copilot`
2. `ai-renewal-risk-briefing-copilot`
3. `ai-compliance-evidence-copilot`
4. `ai-rfp-response-copilot`

This ordering is based on the playoff as a whole, not just one metric:

- `ai-security-questionnaire-copilot` wins the cluster on flagship choice signal and is only slightly behind renewal on ensemble mean adoption
- `ai-renewal-risk-briefing-copilot` wins the cluster on ensemble mean adoption
- `ai-compliance-evidence-copilot` keeps a meaningful cluster position
- `ai-rfp-response-copilot` does not hold the narrow-run lead once the cluster is widened and symmetrized

## Next Batch

The next sensible batch is not another admission attempt.

It should be a cluster-strengthening batch focused on why:

- `startup-yc` still outruns the enterprise cluster on ensemble adoption
- `ai-security-questionnaire-copilot` converts attention better than RFP
- `ai-renewal-risk-briefing-copilot` retains better than the other enterprise domains

That batch should try to improve the enterprise cluster ranking model before any maintained benchmark admission is reconsidered.
