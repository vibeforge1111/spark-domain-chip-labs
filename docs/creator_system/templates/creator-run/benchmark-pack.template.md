# Benchmark Pack

Benchmark ID:
Domain:
Capability measured:
Benchmark family: fixed_case_rubric | simulator | tool_operation | artifact_quality | retrieval_memory | adversarial | longitudinal | collective

## Oracle Authorship (sets the evidence-tier ceiling)

Who or what produced the expected answers / oracle labels?

- [ ] self_authored -- the same author wrote the doctrine and the expected answers. **Caps the run at `benchmark_signal`.** A self-authored oracle measures conformance to your own rules, not real-world outcome, and a loop can saturate it in 1-2 rounds.
- [ ] measured_outcome -- expected labels come from observed real-world signal (engagement, pass/fail, revenue, conversion). Required to claim `candidate_review` or above.
- [ ] second_party -- labels supplied by a human/system other than the doctrine author. Required for `transfer_supported`.

Oracle source (file, dataset, or measurement protocol):

See `BENCHMARK_AUTHORSHIP_AND_EVIDENCE_EXPIRY.md`.

## What This Benchmark Measures

Capability:

Real-world behavior this should correspond to:

What better scores should mean:

## What This Benchmark Does Not Measure

- 

## Case Mix

| Case lane | Minimum count | Actual count | Path |
| --- | ---: | ---: | --- |
| Development cases | 5 |  |  |
| Held-out cases | 5 |  |  |
| Adversarial/trap cases | 3 |  |  |
| No-op regression cases | 1 |  |  |
| Seeded-variance cases | optional |  |  |
| Simulator/arena transfer cases | optional |  |  |

## Scoring Dimensions

| Dimension | Weight | Why it matters | Gaming risk |
| --- | ---: | --- | --- |
|  |  |  |  |

## Calibration

Known-good answer or behavior:

Known-bad answer or behavior:

Judge calibration examples, if using an LLM judge:

Validated on (date):
Revalidate by (date):  <!-- LLM-judge and provider-dependent oracles drift; re-run validation by this date or downgrade the claim. See BENCHMARK_AUTHORSHIP_AND_EVIDENCE_EXPIRY.md -->

## Run Variance (multi-seed default)

Seeds per arm (minimum 3): 
Per-seed scores:
Mean and spread (report both; a single seed can sign-flip a small-n delta):
Majority-vote ensemble used for the headline verdict? (yes/no):

## Anti-Gaming Checks

- format inflation:
- keyword stuffing:
- public-case overfit:
- confidence without decision improvement:
- no-op regression:
- unsafe mutation-surface widening:

## Baseline Protocol

Command or process:

Expected artifacts:

## Candidate Protocol

Command or process:

Expected artifacts:

## Promotion Rule

Minimum promotion condition:

Rollback condition:

Claim boundary:

