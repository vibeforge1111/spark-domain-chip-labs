# MiroFish Enterprise Cluster Diagnostic Note: 2026-03-24

## Scope

Explain the enterprise-cluster playoff result in bottleneck terms rather than only ranking terms.

Input artifact:

- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_PLAYOFF_2026-03-24.json`

Output artifact:

- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_2026-03-24.json`

Focused domains:

- `ai-security-questionnaire-copilot`
- `ai-renewal-risk-briefing-copilot`
- `ai-compliance-evidence-copilot`
- `ai-rfp-response-copilot`

## Core Read

Benchmark median ensemble adoption in the playoff is `2.10%`.

### `ai-security-questionnaire-copilot`

- ensemble adoption: `2.58%`
- choice signal: `26.67%`
- attention-to-ensemble gap: `24.09` points
- benchmark status: above median

Main bottleneck:

- not lack of demand
- not churn
- conversion from choice into retained ensemble adoption

This domain is winning attention more than it is winning retention.

### `ai-renewal-risk-briefing-copilot`

- ensemble adoption: `2.67%`
- choice signal: `20.0%`
- attention-to-ensemble gap: `17.33` points
- benchmark status: above median

Main bottleneck:

- same choice-to-retention leak as questionnaire
- slightly less severe than questionnaire

This is why renewal leads the cluster on ensemble adoption even though questionnaire leads on direct choice signal.

### `ai-compliance-evidence-copilot`

- ensemble adoption: `1.63%`
- choice signal: `16.67%`
- attention-to-ensemble gap: `15.04` points
- benchmark status: below median

Main bottlenecks:

- interest-to-choice friction
- choice-to-retention leak
- still below the benchmark median

This domain has real demand, but the current harness still treats it as too abstract or too late-converting.

### `ai-rfp-response-copilot`

- ensemble adoption: `1.45%`
- choice signal: `3.33%`
- interest-to-choice gap: `70.0` points
- benchmark status: below median

Main bottleneck:

- the problem happens before retention
- agents notice the domain but rarely choose it

RFP is not currently losing because of churn. It is losing because the model is not letting high interest convert into actual selection.

## Methodology Read

The enterprise cluster currently has two different failure modes:

1. questionnaire and renewal:
   strong demand, weak downstream retention
2. compliance evidence and RFP:
   demand exists, but the model under-converts that demand into actual choice

That means the next tuning batch should not use one generic “enterprise boost.”

It should target two separate mechanisms:

- improve choice-to-retention persistence for questionnaire and renewal
- improve interest-to-choice conversion for RFP and compliance evidence

## Recommendation

The next methodology tranche should tune the enterprise cluster with explicit hypotheses:

1. security and renewal loops need stronger retained-value persistence
2. RFP and compliance evidence need lower evaluation friction or stronger choice conversion
3. startup-yc’s advantage is still retention stability, not just raw attention
