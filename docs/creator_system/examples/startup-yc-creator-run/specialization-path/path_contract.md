# Specialization Path Contract

Path ID: startup-yc
Domain: Startup YC
Target user or agent: Spark agents advising or operating on early-stage startup decisions
Primary capability: Concrete, risk-aware startup operating judgment

## Purpose

What the path should make an agent better at: diagnosing startup constraints, rejecting vanity evidence, choosing narrow next actions, and understanding when growth, hiring, fundraising, or product work is premature.

What it should not try to solve: guaranteed startup success, investment advice, late-stage company strategy, or replacing live customer evidence.

## Path Artifacts

| Artifact | Path | Required | Notes |
| --- | --- | --- | --- |
| `specialization-path.json` | `specialization-path-startup-yc/specialization-path.json` | yes | Path manifest. |
| default prompt or doctrine bundle | `specialization-path-startup-yc/prompts/startup-yc.md` | yes | Agent-facing doctrine. |
| benchmark manifest | `specialization-path-startup-yc/benchmarks/startup-yc-adapter-selection.v1.json` | yes | Adapter selector manifest. |
| mutation target | `specialization-path-startup-yc/templates/benchmarks/startup-yc.tool_calls.json` | yes | Default mutation target. |
| absorption bundle | `specialization-path-startup-yc/data/absorption/startup_yc_absorption_v1.json` | yes | Fresh-agent absorption suite. |
| Swarm sync config | `spark-swarm/config/specialization-paths.json` | optional | Network registry. |
| operator guide | `specialization-path-startup-yc/docs/STARTUP_BENCH_YC_GUIDE.md` | yes | Benchmark usage guide. |

## Mastery Ladder

| Stage | Agent capability | Evidence required | Exit gate |
| --- | --- | --- | --- |
| Orientation | Can explain Startup YC doctrine and limits. | Prompt/doctrine bundle exists. | Prototype smoke passes. |
| Baseline operator | Can answer fixed startup cases. | Baseline absorption score. | Benchmark signal. |
| Focused improvement | Improves fresh-agent answers without trap regression. | Candidate and absorption reports. | Candidate review. |
| Transfer-supported | Improves at least one adjacent Startup Bench scenario. | Positive transfer report. | Transfer supported. |
| Network-absorbable | Improves broad transfer or hidden/fresh family without privacy issues. | Positive broad transfer and review. | Network absorbable. |

## Runtime Use

How an agent loads the path: Read `specialization-path.json`, `spark-chip.json`, `prompts/startup-yc.md`, and the current evidence docs before running mutation or publication.

How an agent practices: Run absorption cases, Startup Bench adapter selector cases, and seeded-variance scenarios.

How an agent receives feedback: Use component scores, weakest-track diagnosis, trap failures, and transfer deltas.

How an agent emits packets: Only through Swarm contribution packets with evidence tier, provenance, rollback, and known limits.

## Benchmark Binding

Primary benchmark: Startup YC 20-case fresh-agent absorption suite.

Held-out/fresh benchmark: Startup Bench fresh activation transfer scenario.

Seeded-variance or simulator benchmark: Startup YC six-track seeded-variance suite in Startup Bench.

Trap/adversarial benchmark: Trap band inside `startup_yc_absorption_v1.json`.

## Mutation Boundary

Allowed mutation surfaces: Startup YC packets, adapter scripts, absorption bundle wording, focused weak-case mechanisms.

Frozen surfaces: benchmark weights, success metrics, trap expected outcomes, privacy boundaries.

Forbidden surfaces: score rubric weakening, hidden auth material, broad network publication without review.

Rollback: Revert promoted packet or adapter if repeat loses positive delta or introduces trap regression.

## Swarm Boundary

What can be shared: benchmark-backed insights, focused mastery candidates, weak-track diagnoses, and upgrade suggestions.

What must stay local: raw logs, private user data, access tokens, and unreviewed hypotheses.

Minimum evidence tier for network contribution: `network_absorbable`.

Review owner: human maintainer plus Spark Swarm publication gate.
