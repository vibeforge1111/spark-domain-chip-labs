# Benchmark Pack

Benchmark ID: startup-yc-absorption-and-transfer-v1
Domain: Startup YC
Capability measured: Fresh-agent startup operating judgment and focused transfer
Benchmark family: fixed_case_rubric + adversarial + simulator

## What This Benchmark Measures

Capability: Whether a fresh agent becomes more concrete, doctrine-aligned, and trap-resistant after receiving the Startup YC validated pack.

Real-world behavior this should correspond to: Better early-stage startup decisions under false PMF, default-dead, hiring, fundraising, and focus pressure.

What better scores should mean: The agent gives more useful operating advice, not just more YC-sounding language.

## What This Benchmark Does Not Measure

- General startup mastery across every stage or business model.
- Investment advice quality.
- Live customer evidence quality.
- Broad transfer across all Startup Bench tracks.

## Case Mix

| Case lane | Minimum count | Actual count | Path |
| --- | ---: | ---: | --- |
| Development cases | 5 | 5 | `specialization-path-startup-yc/data/absorption/startup_yc_absorption_v1.json` |
| Held-out cases | 5 | 10 | `specialization-path-startup-yc/data/absorption/startup_yc_absorption_v1.json` |
| Adversarial/trap cases | 3 | 5 | `specialization-path-startup-yc/data/absorption/startup_yc_absorption_v1.json` |
| No-op regression cases | 1 | 1 | `specialization-path-startup-yc/data/absorption/startup_yc_absorption_v1.json` |
| Seeded-variance cases | optional | 6 tracks x 5 seeds | `startup-bench/examples/startup_yc_seeded_variance_suite.json` |
| Simulator/arena transfer cases | optional | 1 focused, 10 broad probe | `reports/transfer_summary.json`, `reports/broad_transfer_probe.json` |

## Scoring Dimensions

| Dimension | Weight | Why it matters | Gaming risk |
| --- | ---: | --- | --- |
| Doctrine alignment | 1 | Keeps advice grounded in Startup YC operating principles. | Keyword stuffing. |
| Operational specificity | 1 | Forces concrete next actions. | Verbose fake specificity. |
| Risk management | 1 | Penalizes default-dead, hiring, fundraising, and focus mistakes. | Overly cautious generic answers. |
| Revenue quality | 1 | Rewards real customer pull over vanity demand. | Naming revenue without proving quality. |
| Trap resistance | 1 | Prevents false-PMF and vanity-metric absorption. | Refusing too much. |
| Fresh-agent absorption delta | 1 | Measures whether the pack improves another agent. | Prompt residue or overfit examples. |

## Calibration

Known-good answer or behavior: Names the startup's binding constraint, rejects vanity demand, gives a narrow next operating move, and states what evidence would change the plan.

Known-bad answer or behavior: Optimizes growth, fundraising, or hiring before retention, customer pain, and runway evidence are clear.

Judge calibration examples, if using an LLM judge: Compare no-pack, pack, and validated-pack modes on the same cases and inspect trap-band failures manually.

## Anti-Gaming Checks

- format inflation: compare decisions and scored dimensions, not only polish.
- keyword stuffing: require causal mechanism and concrete next action.
- public-case overfit: run fresh/held-out cases and seeded variants.
- confidence without decision improvement: score outcome dimensions separately.
- no-op regression: include cases where the correct move is to avoid changing the system.
- unsafe mutation-surface widening: freeze benchmark weights, trap outcomes, and success metrics.

## Baseline Protocol

Command or process: Run no-pack fresh-agent mode on the 20-case absorption suite.

Expected artifacts: `reports/baseline.json`, source proof report, case-level score traces.

## Candidate Protocol

Command or process: Run validated-pack fresh-agent mode on the same suite, then run focused Startup Bench transfer.

Expected artifacts: `reports/candidate.json`, `reports/absorption_summary.json`, `reports/transfer_summary.json`.

## Promotion Rule

Minimum promotion condition: Positive validated-pack delta, no trap regression, positive transfer delta for `transfer_supported`.

Rollback condition: Deprecate if full-suite repeat loses positive validated-pack mean delta or introduces trap regression.

Claim boundary: This fixture is transfer-supported, not network-absorbable, until broad transfer turns positive.
