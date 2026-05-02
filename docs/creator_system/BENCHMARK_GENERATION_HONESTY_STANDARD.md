# Benchmark Generation Honesty Standard

Date: 2026-05-02

This standard defines the minimum evidence shape for generated creator-system
benchmark packs. The goal is to make generated benchmarks useful for Spark
Swarm standardization without letting plausible benchmark prose become an
unsupported mastery claim.

## Current Scope

Generated benchmark packs prove factory readiness:

- a fresh brief can become runnable benchmark artifacts
- cases and traps are deterministic and CI-safe
- saved reports can be checked against recomputed evidence
- Swarm packets keep `network_publication_allowed` false
- mission-status packets preserve `evidence_mode`

They do not prove domain mastery, real content outcomes, production memory
safety, autonomous publication safety, or `network_absorbable`.

## Required Case Contract

Every generated benchmark case must carry:

- `case_id`
- `case_kind`
- `case_lane`
- `prompt`
- `oracle.expected_behavior`
- `oracle.failure_mode`
- `oracle.minimum_candidate_delta`
- `baseline_mutations`
- `candidate_mutations`
- `trap`
- `hallucination_risk`
- `calibration_status`

The oracle does not need to be a perfect judge. It must state what the case is
trying to prove and what failure would mean. This keeps later reviewers and
Swarm consumers from treating a vague prompt as calibrated evidence.

## Required Manifest Contract

Every generated benchmark manifest must expose:

- target capability
- case count and trap count
- case lane counts
- scoring dimensions and report schema
- anti-gaming checks
- promotion rules
- claim boundaries
- aggregation policy

The aggregation policy must make this explicit:

- aggregate mean is allowed for local comparison
- lane breakdown is required
- failed lanes block stronger claims
- failed seeds cannot be hidden behind a passing aggregate

## Required Report Contract

Generated candidate and absorption reports must expose `lane_results`.

At minimum, each lane result must include:

- case count
- baseline mean
- candidate mean
- mean delta
- trap regressions

Recompute mode must compare saved lane results to freshly recomputed lane
results. A report that changes only the aggregate score is stale. A report that
changes lane results is also stale.

## Provenance Requirements

Generated report provenance must include hashes for:

- `benchmark/manifest.json`
- `benchmark/cases.jsonl`
- `domain-chip/scoring_hooks.json`

Changing benchmark cases, benchmark rules, or scoring hooks must block
recomputed evidence until reports are regenerated.

## Swarm Standardization Boundary

Spark Swarm can consume generated benchmark packets as standardized local
evidence when:

- the packet reports `candidate_review`
- recompute mode passes
- trap regressions are zero
- lane results match recompute
- governance keeps network publication disabled
- claim boundaries are visible

Spark Swarm must not upgrade generated benchmark packets to
`network_absorbable` without the separate promotion gates: multi-seed validation,
human/operator calibration, privacy review, rollback review, and publication approval.
