# Creator System Multi-Domain Validation Plan

Date: 2026-05-02

This plan turns the creator-system standard into a repeatable validation
program. The goal is to prove Spark can generate many kinds of domain-chip lab
systems from scratch, not only validate a curated Startup YC fixture.

## Current Proof

The executable generator acceptance harness already creates fresh creator-run
workspaces in temporary directories. Each generated run builds:

- domain chip artifacts
- benchmark pack and cases
- baseline, candidate, and absorption reports
- specialization path
- autoloop policy and keep/revert simulation
- Swarm contribution packet
- saved smoke and recompute smoke

Generated runs currently claim `candidate_review`. They do not claim
`transfer_supported` or `network_absorbable`.

## Domain Matrix

| Domain family | Example domain | Current executable proof | Claim boundary |
| --- | --- | --- | --- |
| Artifact quality | Design Doc PR Quality | Generated brief, reports, recompute smoke, mission-status packet | Local review quality only |
| Tool operation | Spark Tool Operation | Safe command planning, dry-run/postcondition checks, recompute smoke, mission-status packet | No push, publish, or secret-paste workflow |
| Content simulation | MiroFish Content Simulation | Persona-batch simulator metadata, multi-RLM judge shape, recompute smoke, mission-status packet | Candidate-review simulator protocol only |
| Doctor/security | Spark Doctor Adversarial | Stale/fake evidence and unsafe promotion traps, recompute smoke, mission-status packet | Doctor pass is not publication approval |
| Startup operator | Startup YC Operator | Founder-advice benchmark cases, recompute smoke, mission-status packet | Not Startup YC network mastery |
| Retrieval/memory | Retrieval Memory Boundary | Source-aware memory, stale/contradicted/residue traps, recompute smoke, mission-status packet | No production memory runtime or network-shareable recall claim |

## Benchmark Maturity

There are two benchmark layers today:

1. **Generated acceptance benchmark packs** prove that Spark can create the
   correct benchmark structure from a fresh brief. These are deterministic,
   small, and CI-safe.
2. **Domain-specific benchmark systems** prove deeper quality for a domain.
   These are stronger but heavier and should grow domain by domain.

Current maturity by domain:

| Domain family | Generated benchmark pack | Domain-specific benchmark depth | Next benchmark upgrade |
| --- | --- | --- | --- |
| Artifact quality | Yes: cases, traps, recompute reports | Good local fixture set for strong, weak, polished-but-unproven, design-decision, and mission-handoff docs with reviewer calibration rows plus schema-anchored reports and benchmark bundles | Add real human-edited PR/design-doc examples and disagreement rows |
| Tool operation | Yes: safe command, rollback, token trap | Good local operation packets for dry-run, postconditions, stale recompute, missing artifacts, secret handling, MiroFish content multi-seed, doctor adversarial sweep commands, and schema-anchored packet/check contracts | Add more real command families and postcondition adapters |
| Content simulation | Yes: title/angle cases and simulator metadata | Local MiroFish simulation, route examples, multi-seed stability, and schema-anchored packets exist, but real outcome calibration is not done | Add multi-seed simulator batches and compare against actual content outcomes |
| Doctor/security | Yes: fake evidence, repair specificity, unsafe promotion trap | Good stale/malicious fixture coverage, repair calibration, schema-family adversarial sweep coverage, and schema anchors for malformed sweep packets | Add broader generated mutation manifests |
| Startup operator | Yes: generated founder-advice benchmark cases | Strongest curated reference fixture plus Startup YC gate checks and external recompute comparisons | Add real multi-seed evaluated founder-advice evidence before stronger claims |
| Retrieval/memory | Yes: correct prior, stale memory, residue trap | Local memory-lane contract, fixture-suite validation, and schema anchors exist, but production memory runtime is deferred | Add real memory-system adapter checks when Spark memory is ready |

The generated benchmark packs are the right first benchmark systems for
factory-proof. They prove artifact creation, scoring hooks, trap coverage,
recompute provenance, and Swarm packet consistency. They are not yet enough to
claim domain mastery, real content virality, production memory safety, or
network absorption.

The benchmark honesty contract now lives in
`BENCHMARK_GENERATION_HONESTY_STANDARD.md`. Generated packs must include case oracles,
failure modes, lane counts, lane-level report results, anti-gaming checks,
aggregation policy, and report provenance hashes for the benchmark manifest,
cases, and scoring hooks. This makes aggregate scores easier to inspect and
harder to use as a cover for failed traps, stale benchmark rules, or unsupported
Swarm claims.

The artifact-quality benchmark has started the deeper domain-calibrated layer:
its manifest can now declare `case_expectations` for baseline, candidate, and
trap artifacts. The benchmark report emits expectation checks and a
`calibration_verdict`; failed expectations force a revert even when the raw
score delta looks positive.
It now also accepts `reviewer_calibration_cases`, which rescore reviewer-labeled
PR writeups, design docs, mission handoffs, and traps. Failed reviewer rows
block `calibration_verdict`, and their source artifacts are included in the
benchmark provenance hashes so stale calibration examples cannot silently drift.
The artifact-quality report, benchmark-manifest, and benchmark-result schemas
now anchor that local reviewer contract. A saved report must keep the local
review-only claim boundary and unsafe-claim caveat, while benchmark pass results
must align with calibration pass, zero trap regressions, and a `keep` decision.

The MiroFish content simulator now emits its own calibration checks. Ranked
results must prove multi-RLM judge coverage, persona-segment coverage, row-count
coherence, weak-segment inspection, and any optional expected-winner oracle
before their `calibration_verdict` can pass.
It also has a local `mirofish-content-multi-seed` batch command. The batch keeps
the claim at `candidate_review`, requires multiple deterministic seeds, and
blocks calibration unless a top candidate is stable across the seeded reruns.
The MiroFish content route, simulation-result, and multi-seed result schemas now
anchor the local simulator contract. They preserve the candidate-review claim
boundary, expose calibration blockers, and reject any accidental
`network_absorbable=true` multi-seed result before real outcome calibration.

The tool-operation checker now requires explicit expected postconditions for
successful parsed operations. A command result can no longer pass only because
the parsed packet looks successful; it must also declare the intended verdict,
blocking-check, missing-path, or automation state expectations that mission
control is allowed to trust.
It now also supports `mirofish-content-multi-seed` command packets with
postconditions for `calibration_verdict`, `network_absorbable=false`, minimum
seed count, and stable top-candidate evidence.
It also supports `creator-run-doctor-adversarial-sweep` packets with
postconditions for minimum case count, empty failed case ids, required
schema-family coverage, and `network_absorbable=false`.
The tool-operation manifest, input packet, and check-result schemas now anchor
the local mission-control safety boundary. Saved operation fixtures and fresh
check outputs validate against those schemas, while incoherent blocked/allowed
states and `network_absorbable=true` postconditions are rejected before a
mission trace can treat the packet as evidence.

The doctor/security layer now emits `repair_calibration` in doctor results. It
checks that blocking smoke checks are covered by specific repair steps or
quarantine findings, and that blocked runs require a recompute replay command
before repair advice can be treated as complete.
It also has a local `creator-run-doctor-adversarial-sweep` command. The sweep
copies a clean run into temporary workspaces, mutates adapter-map,
candidate-report, absorption-summary, Swarm-packet, and evidence-ladder
families, and requires the doctor to block with the expected repair or
quarantine evidence. The sweep keeps `network_absorbable=false`; it is a local
doctor-security benchmark, not a publication approval.
Its manifest and result packets are now anchored by JSON Schemas, so malformed
mutation manifests, empty expected blockers, hidden failed case ids, or
`network_absorbable=true` sweep results are rejected before they can be used as
operator evidence.

The retrieval/memory checker now emits `calibration_verdict` and requires each
entry's `provenance.source_path` to appear in its exact `source_refs`. A memory
packet can no longer pass by citing plausible nearby documentation while
recalling from a different saved source.
The retrieval-memory packet and check schemas now anchor the local adapter
boundary. Fixture-suite validation covers correct prior decisions, stale
memory, contradictions, residue contamination, network-shareable recall without
review, and malformed packet/check shapes while still keeping production memory
runtime integration deferred.

The Startup YC held-out founder-advice checker now requires concrete case
contracts: covered operator moves, avoided rejected claims, observed privacy
lane, promotion tier ceiling, and an advice artifact reference. Boolean pass
flags alone are not enough to pass the held-out gate.

Startup YC also has saved held-out founder-advice evidence wired into its
validation plan. This lets the held-out gate pass locally without changing the
overall claim boundary: multi-seed validation, review gates, publication
approval, and promotion evidence still block network absorption.

## Phase 1: Multi-Domain Generator Matrix

The first phase is the fast CI-safe matrix. It uses one representative generated
brief per domain family.

Success criteria:

- Each domain starts from a brief.
- Each produces a schema-valid creator intent with network publication disabled.
- Each creates schema-valid chip, benchmark, specialization path, autoloop
  policy, reports, and Swarm packet.
- Each keeps the created-artifact manifest local-only with no published
  artifact statuses.
- Generated benchmark manifests expose lane and seed failure-blocking policy.
- Each produces schema-valid scoring hooks and generated benchmark case rows.
- Each produces a schema-valid generated hook-smoke packet.
- Each produces schema-valid benchmark and absorption reports with provenance
  source and input-hash fields.
- Each produces schema-valid specialization-path and keep/revert autoloop
  simulation packets.
- Each produces a schema-valid autoloop policy with network publication
  disabled.
- Each produces a schema-valid Swarm contribution packet that keeps network
  publication disabled.
- Each passes normal smoke as saved evidence.
- Each passes recompute smoke when supported provenance is present.
- Each produces a schema-valid `creator-mission-status` packet from recomputed
  smoke.
- Each remains below `network_absorbable`.

Current executable anchor:

```bash
python -m pytest tests/test_creator_generator_acceptance.py -q
```

## Phase 2: Multi-Seed Validation

This phase proves the generator is not brittle to one handpicked brief.

Target matrix:

- 3 briefs per domain family.
- 2 seeds per brief.
- 6 domain families.
- 36 generated runs total.

Current executable status:

- `run_multi_seed_generator_validation` creates the 36-row generated matrix
  from six domain families, three generated brief variants per family, and two
  seeds per variant.
- `generated-multi-seed-run` exposes that matrix runner as a CLI command from a
  briefs JSON file, so manual or scheduled jobs do not need to import test
  helpers.
- `docs/creator_system/examples/generated-multi-domain-briefs.json` is the
  checked-in operator input for that generated matrix.
- The summary is written to `multi_seed_validation_summary.json`.
- The summary reports every seed row, keeps `network_absorbable` false, and
  sets `aggregate_hidden_failures` to false.
- A forced weak-seed regression proves a failed row blocks the aggregate and
  exposes its blocker names instead of disappearing behind the passing rows.
- `validate_multi_seed_generator_summary` recomputes every saved row from its
  run directory and blocks tampered summary fields or stale underlying run
  reports.
- `generated-multi-seed-summary-check` exposes that recompute check as a CLI
  command for manual or scheduled validation jobs.
- `generated-multi-seed-summary.schema.json` and
  `generated-multi-seed-summary-check.schema.json` anchor the saved summary and
  recomputed check packet shapes.
- `creator-mission-status --generated-multi-seed` can now project that
  generated matrix into Builder, Telegram, Spawner, Canvas, and Kanban
  read-only summaries without requiring product surfaces to parse raw generator
  internals.

Success criteria:

- Strong seeds converge on coherent evidence.
- Weak seeds fail honestly with blocker names.
- Doctor output gives exact repair steps.
- No failed seed is hidden behind a passing aggregate.
- All successful seeds stay at `candidate_review` unless stronger evidence is
  explicitly proven.

Suggested execution mode:

- Keep PR CI on the representative matrix plus the executable 36-row generated
  multi-seed acceptance test while it remains fast enough.
- Move heavier domain-calibrated multi-seed runs to manual or scheduled jobs
  when real outcome adapters are added.

Current executable anchor:

```bash
python -m pytest tests/test_creator_generator_acceptance.py -q
```

## Phase 3: Evidence And Provenance Hardening

This phase makes stale saved evidence impossible to confuse with fresh
recompute evidence.

Checks:

- Changed benchmark manifests block recompute.
- Changed benchmark cases block recompute.
- Changed scoring hooks block recompute.
- Changed saved report values block recompute.
- Changed saved lane results block recompute.
- Changed generated multi-seed summary rows block summary validation.
- Changed underlying run reports block generated multi-seed summary validation.
- Swarm packet summaries must match current reports.
- Tool-operation packets must match command mode and `evidence_mode`.
- Mission-status packets must preserve `evidence_mode` across canonical,
  Builder, Telegram, Spawner, Canvas, and Kanban views.

Success criteria:

- Saved evidence can be coherent but marked `saved`.
- Fresh evidence is marked `recomputed`.
- Stale saved reports block recompute.
- Product projections cannot drop `evidence_mode`.

## Phase 4: Cross-Domain Mission Status

Every generated domain must produce a read-only mission packet that product
surfaces can consume without parsing raw smoke.

Required packet fields:

- canonical verdict
- evidence tier
- evidence mode
- blockers and warnings
- next actions
- publication boundary
- Builder, Telegram, Spawner, Canvas, and Kanban read-only projections

Success criteria:

- Product surfaces never invent verdicts.
- Product surfaces never upgrade evidence tiers.
- Product surfaces can show generated multi-seed row counts, failed seed IDs,
  and hidden-failure status from the canonical summary.
- `ready_for_swarm_packet` remains a review state, not publication approval.
- `network_absorbable` remains false without the separate promotion gates.

## Phase 5: Human And Operator Review Packets

Generated systems can become stronger only after review evidence exists.

Each domain needs:

- operator calibration checklist
- privacy boundary
- rollback plan
- publication approval placeholder
- known limits
- forbidden claims

Current executable status:

- Generated runs now emit `reports/operator_review_packet.json` with open
  human/operator calibration, privacy, rollback, and publication gates.
- `operator-review-check` blocks incomplete or unsafe review packets and keeps
  `network_absorbable` false even when review gates are otherwise complete.
- `operator-review-packet.schema.json` and
  `operator-review-check.schema.json` anchor the generic generated-domain
  review packet and check shapes.

Success criteria:

- Every stronger claim has a missing gate unless explicitly reviewed.
- Subcheck evidence alone cannot approve `network_absorbable`.
- Publication approval must name the claim being approved.

## Phase 6: CI Expansion

CI should grow in layers.

Fast PR CI:

- representative generated matrix
- generic operator-review packet/check regressions
- strict Startup YC saved smoke
- Startup YC shape-only raw evidence check
- validation-suite schema checks
- mission-status schema checks

Current executable status:

- Creator-system CI now runs `tests/test_operator_review.py` and focused lint
  for `src/chip_labs/operator_review.py`, so Phase 5 packet/check regressions
  are covered on relevant pushes and pull requests.

Manual or scheduled CI:

- 36-run multi-seed matrix
- `generated-multi-seed-run --briefs <briefs.json> --workspace-dir <dir>`
- `generated-multi-seed-summary-check --fail-on-blocked` against saved or
  freshly generated matrix summaries
- `workflow_dispatch` with `run_generated_multi_seed=true` runs the checked-in
  generated brief matrix and validates both generated summary schemas.
- A weekly scheduled Creator System workflow also runs the checked-in generated
  matrix so heavy drift checks do not depend on normal push CI.
- The same manual path also emits a generated matrix mission-status packet from
  `creator-mission-status --generated-multi-seed` and validates it against the
  product-safe mission-status schema.
- external recompute checks when sibling source repos are available
- stale-evidence mutation sweeps

Success criteria:

- PR CI remains fast enough for normal development.
- Heavy validation is available without turning every commit into a long run.
- CI proves claim boundaries, not only happy-path generation.

## Promotion Boundary

This plan does not approve `network_absorbable`.

Network absorption still requires:

- multi-seed validation
- human/operator calibration
- privacy review
- rollback review
- publication approval
