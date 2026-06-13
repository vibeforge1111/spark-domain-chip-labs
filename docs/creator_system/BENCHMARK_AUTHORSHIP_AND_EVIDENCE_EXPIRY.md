# Benchmark Authorship and Evidence Expiry

Two failure modes that passed every existing gate in real runs, now made explicit. Both are honesty rules, not new machinery; enforce them in review until smoke encodes them.

## 1. Oracle authorship caps the evidence tier

A benchmark proves something only if its expected answers (the oracle) come from a source independent of the thing being improved. When the same author writes the doctrine, the rubric, and the expected answers, the benchmark measures **conformance to the author's own rules**, not real-world outcome. Such a benchmark:

- saturates in 1-2 loop rounds (the doctrine just restates the rubric), and
- can show a large, real, and meaningless score gain.

Observed directly: a self-authored 14-case hook pack went 1.60 to 2.00 dev-lane in one round; the same doctrine against measured engagement on 120 real items scored ~0.26 Spearman, barely above the no-doctrine baseline.

**Rule, by oracle source:**

| Oracle authorship | Max claimable tier | Why |
| --- | --- | --- |
| `self_authored` (doctrine author wrote the expected answers) | `benchmark_signal` | conformance only; not outcome evidence |
| `second_party` (labels from a different human/system) | `transfer_supported` | independent of the doctrine, but still not a measured outcome |
| `measured_outcome` (labels are observed real signal: engagement, pass/fail, revenue, conversion) | `network_absorbable` (subject to the other gates) | the only oracle that tracks reality |

Declare the source in `benchmark/manifest.json` and `autoloop/policy.json` (`oracle_authorship`). A run claiming above its authorship ceiling is overstated regardless of its score delta.

## 2. Evidence expires

Validation describes a system **at a moment**. LLM judges, provider models, and retrieval corpora drift; a 0.53-Spearman judge silently became 0.17 over seven weeks and nothing noticed, because no artifact carried an expiry.

**Rule:**

- Every validation artifact (benchmark report, judge calibration, transfer probe) records `validated_at` and `revalidate_by`.
- Default shelf life: **provider-LLM-dependent evidence 30 days; deterministic/code-scored evidence 180 days; corpus-retrieval evidence 30 days** (corpus growth changes retrieval context).
- Past `revalidate_by`, the claim is downgraded one tier until re-earned. `ready_for_swarm_packet` on stale evidence is not shareable.
- Re-running validation is cheap relative to shipping a false claim downstream. Schedule it.

## How this shows up in the artifacts

- `benchmark-pack.template.md`: Oracle Authorship section + Validated-on / Revalidate-by lines + multi-seed Run Variance section.
- `autoloop-policy.template.json`: `oracle_authorship`, `evidence_validated_at`, `evidence_revalidate_by`.
- Evidence ladder: a row past its `revalidate_by` is marked `warn` (stale) and cannot support the Safe Claim.

## Related

- `PROMOTION_GATES_AND_EVIDENCE_TIERS.md` (tier definitions)
- `BENCHMARK_GENERATION_HONESTY_STANDARD.md` (anti-gaming)
- `BENCHMARK_AND_AUTOLOOP_PROTOCOL.md` (loop governance)
