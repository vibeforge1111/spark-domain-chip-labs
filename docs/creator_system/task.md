# Creator System Long-Running Tasks

Date: 2026-05-01

This file is the working task ledger for continuing Spark creator-system
standardization after the long handoff thread. It keeps the work durable across
sessions and prevents long-running implementation from lowering evidence
quality.

## Operating Rules

- Run `git status --short` before each editing slice.
- Do not revert unrelated dirty or untracked files.
- Stage only files relevant to the active slice.
- Keep product surfaces deferred unless a task explicitly says otherwise.
- Do not wire Spawner, Canvas, Kanban, Telegram, or Builder creator surfaces yet.
- Do not claim `network_absorbable` without multi-seed validation,
  human/operator calibration, privacy review, rollback review, and publication
  approval.
- Prefer executable proof over polished prose.
- Every claim needs saved evidence or a fresh recompute path.

## Current Proven Baseline

- Creator-run CLI, schemas, templates, evidence ladder, and Startup YC reference
  fixture exist.
- Startup YC passes strict smoke as `ready_for_swarm_packet` with evidence tier
  `transfer_supported`.
- Startup YC is not `network_absorbable`.
- Generator acceptance tests now prove Spark can create creator-run systems from
  scratch across multiple proof domains.
- Recompute mode exists for `creator-run-smoke` so saved evidence can be checked
  against freshly rerun evidence.
- MiroFish content simulation has a deterministic local harness and a direct
  candidate CLI path.
- `.github/workflows/creator-system.yml` now runs the focused creator-system
  lint, proof-domain tests, strict Startup YC smoke check, and template check on
  relevant pushes and pull requests.

## Build Phases

These phases are the order of work. A later phase can be designed early, but it
should not be promoted as complete until the phase gate passes.

### Phase 0: Durable Task Ledger And Local Baseline

Status: active, staged

Purpose:

Create a stable long-running work ledger and preserve the already proven
creator-system baseline.

Deliverables:

- [x] `docs/creator_system/task.md` exists.
- [x] Current proven baseline is recorded.
- [x] Operating rules are recorded.
- [x] Unrelated dirty/untracked files are left untouched.

Phase gate:

- Commit the task ledger together with the route-mode slice that created it.

### Phase 1: Spark-Callable MiroFish Content Tool

Status: active, staged

Purpose:

Make content selection an executable local tool flow. Spark should be able to
ask whether a normal content prompt should invoke the simulator, then run the
simulator with clear claim boundaries.

Deliverables:

- [x] `mirofish-content-simulate` deterministic local simulator.
- [x] Direct candidate input through `--task` and repeated `--candidate`.
- [x] Prompt trigger and candidate extraction helpers.
- [x] `mirofish-content-route` route packet command.
- [x] Route tests for invoke, skip, missing candidates, explicit candidates, and
  CLI output.
- [x] Saved example packets for route mode and simulation mode.

Phase gate:

- Focused MiroFish tests pass.
- Wider creator generator/run tests pass.
- Startup YC strict smoke remains green.
- Template check remains green.
- Claim boundary remains local simulator candidate review only.

### Phase 2: Artifact Quality For Design Docs And PRs

Status: active

Purpose:

Turn the artifact-quality proof domain into a practical local evaluator for
Spark design documents, PR descriptions, implementation handoffs, and
mission-control packets.

Deliverables:

- [x] Fixture set of good, weak, and polished-but-unproven design/PR documents.
- [x] Local scoring adapter for evidence, tests, risks, rollback, and acceptance
  gates.
- [x] Report format that can be attached to future missions.
- [x] Baseline/candidate reports that can be recomputed.

Phase gate:

- At least one trap fixture proves document polish is not treated as product
  correctness.
- Reports name missing evidence and exact repair steps.
- No generated PR text is treated as a replacement for human review.

### Phase 3: Tool Operation Safety

Status: active

Purpose:

Teach Spark to plan, execute, and verify local creator-run operations before any
mission-control state change.

Deliverables:

- [x] Local command manifest for safe creator-run operations.
- [x] Dry-run and postcondition checks for smoke, doctor, template check, and
  recompute flows.
- [x] Failure replay fixtures for blocked smoke, stale evidence, missing
  artifacts, and unsafe secret handling.
- [x] Rollback-note output for failed operations.

Phase gate:

- Tests prove stdout alone is not accepted as success.
- Secret-paste workflows are rejected.
- No publish, push, or network mutation is allowed without review.

### Phase 4: Doctor Adversarial And Provenance Hardening

Status: active

Purpose:

Improve Spark's doctor system so it catches fake evidence, unsafe promotion,
missing provenance, stale reports, and weak repair plans.

Deliverables:

- [x] Malicious or stale report fixtures.
- [x] Doctor checks that map blockers to exact repair steps.
- [x] Repair replay proof that reruns smoke after a proposed repair.
- [x] Quarantine examples for malicious contribution packets.

Phase gate:

- Candidate-review evidence cannot pass as network absorption.
- Repair advice requires rerun evidence.
- Privacy, rollback, and provenance boundaries remain visible in every report.

### Phase 5: Startup YC Operator Validation

Status: active

Purpose:

Keep Startup YC as the golden reference while turning it into a future startup
operator capability for Spark.

Deliverables:

- [x] Multi-seed startup advice validation plan.
- [x] Held-out founder-advice examples.
- [x] Human/operator calibration checklist.
- [x] Privacy and rollback review packet.
- [x] Publication approval gate for any stronger claim.

Phase gate:

- `transfer_supported` remains separate from `network_absorbable`.
- Vanity-metric traction claims are rejected.
- No stronger claim ships without multi-seed validation and review.

### Phase 6: Retrieval And Memory Proof Layer

Status: local contract active, production wiring deferred

Purpose:

Prove Spark can retrieve useful prior context without treating workflow residue
or stale conversation as memory truth.

Deliverables:

- [x] Memory lane contract for local, private, and network-shareable context.
- [x] Retrieval fixtures for correct prior decision, stale memory,
  contradiction, and residue contamination.
- [x] Recompute/provenance checks for retrieved context.

Phase gate:

- Conversational residue is never promoted as evidence by default.
- Contradicted or stale memory blocks promotion.
- Privacy lanes are explicit in every packet.

### Phase 7: Product Surface Integration

Status: read-only adapter contract active, runtime wiring deferred

Purpose:

Wire creator-system capabilities into Builder, Telegram, Spawner UI, Canvas, and
Kanban only after local proof domains are stable.

Deliverables:

- [x] Builder read-only mission status consumer.
- [ ] Telegram guided creator commands.
- [x] Telegram read-only mission status formatter.
- [ ] Spawner mission execution and trace storage.
- [x] Spawner read-only mission status projection.
- [x] Canvas/Kanban read-only mission visualization contract.
- [x] Shared read-only creator mission status packet.

Phase gate:

- Local proof domains have executable tests and saved evidence.
- Product surfaces read canonical creator-run outputs instead of inventing
  independent truth.
- No surface hides claim boundaries or publication gates.

Current handoff:

- Local proof domains now have executable tests and saved evidence.
- Product runtime wiring is still intentionally deferred to product repos.
- `creator-mission-status` now provides read-only adapters over existing smoke,
  doctor, tool-operation, content-route, artifact-quality, retrieval-memory, and
  Startup YC validation packets.
- Builder, Telegram, Spawner, Canvas, and Kanban should consume the shared
  status packet and preserve blocked states, missing gates, and claim
  boundaries.
- Product-side consumer branches are recorded in
  `PRODUCT_SURFACE_CONSUMER_BRANCHES_2026-05-01.md`.
- Creator-system CI is active on `main` so future proof-domain edits must keep
  generator acceptance, recompute/provenance checks, and Startup YC strict smoke
  green before they can land.
- Runtime creator controls remain deferred; these branches are validators,
  formatters, and read-only projections only.

### Phase 8: Network Absorption And Public Standard

Status: future

Purpose:

Decide what can safely become community-visible, Swarm-absorbed, or part of a
public creator standard.

Deliverables:

- [ ] Multi-seed validation.
- [ ] Human/operator calibration.
- [ ] Privacy review.
- [ ] Rollback review.
- [ ] Publication approval.
- [ ] Public `spark-creator` repo decision.

Phase gate:

- Only reviewed, calibrated, rollback-safe patterns can be considered
  `network_absorbable`.

## Active Workstream

### A. MiroFish Content Simulation As A Spark-Callable Tool

Goal:

Make Spark able to recognize normal content-selection tasks and invoke the
MiroFish-style simulator locally without requiring a hand-written JSON packet.

Deliverables:

- [x] Deterministic simulator for content ideas, titles, hooks, drafts, and
  angles.
- [x] Direct CLI input through `--task` and repeated `--candidate`.
- [x] Prompt trigger helper for choosing, ranking, comparing, or testing content
  candidates.
- [x] Route packet helper that returns `invoke` or `skip` with reasons,
  candidate count, claim boundary, and optional simulation result.
- [x] CLI command for the route packet helper.
- [x] Docs showing when agents should use route mode vs direct simulation mode.

Quality gates:

- Focused unit tests for trigger, extraction, routing, blocked route, and CLI.
- `python -m pytest tests/test_mirofish_content_simulation.py -q`
- Focused `ruff` on modified MiroFish/test files.
- No live provider calls in this slice.

Evidence boundary:

- Claim only `candidate_review local simulator protocol`.
- Do not claim real virality, real audience fit, or model-judge calibration.

### B. Artifact Quality Domain For Better Design Docs And PRs

Goal:

Turn the artifact-quality proof domain into a useful local system for improving
Spark design documents, PR descriptions, implementation handoffs, and
mission-control packets.

Deliverables:

- [x] Generator acceptance brief for `artifact_quality`.
- [x] Fixture documents with known quality failures.
- [x] Local scoring adapter for evidence, tests, risk, rollback, and acceptance
  gates.
- [x] PR/design-doc report format that can be attached to future missions.
- [x] Recomputeable baseline/candidate reports.

Quality gates:

- Acceptance tests must include at least one polished-but-unproven trap.
- Reports must distinguish document quality from product correctness.
- No claim that generated PR text replaces human review.

### C. Tool Operation Domain For Safe Local Creator-Run Use

Goal:

Teach Spark to plan, execute, and verify local tool operations safely before
mission-control state changes.

Deliverables:

- [x] Generator acceptance brief for `tool_operation`.
- [x] Local command manifest for safe creator-run operations.
- [x] Dry-run and postcondition checks for smoke, doctor, template check, and
  recompute flows.
- [x] Failure replay cases for blocked smoke, stale evidence, missing artifacts,
  and unsafe secret handling.
- [x] Rollback-note output for failed operations.

Quality gates:

- Tests must prove stdout alone is insufficient.
- Secret-paste workflows must be rejected.
- No publish, push, or network mutation without review.

### D. Doctor Adversarial And Security Domain

Goal:

Improve Spark's doctor system so it catches fake evidence, unsafe promotion,
missing provenance, and weak repair plans.

Deliverables:

- [x] Generator acceptance brief for `doctor_security_regression`.
- [x] Malicious or stale report fixtures.
- [x] Doctor checks that map blockers to exact repair steps.
- [x] Repair replay proof that reruns smoke after a proposed repair.
- [x] Quarantine examples for malicious contribution packets.

Quality gates:

- Candidate-review evidence must not pass as network absorption.
- Repair advice must require rerun evidence.
- Privacy and rollback boundaries must stay visible in every report.

### E. Startup YC Operator Domain

Goal:

Keep Startup YC as the golden reference while turning it into a future startup
operator capability for Spark.

Deliverables:

- [x] Startup YC creator-run fixture passes strict smoke.
- [x] Generator acceptance brief for startup founder advice.
- [x] Multi-seed startup advice validation plan.
- [x] Held-out founder-advice examples.
- [x] Human/operator calibration checklist.
- [x] Privacy and rollback review packet.
- [x] Publication-approval gate for any stronger claim.

Quality gates:

- Keep `transfer_supported` separate from `network_absorbable`.
- Reject vanity-metric traction claims.
- Add held-out founder-advice examples before any stronger claim.

### F. Retrieval And Memory Domain

Goal:

Prepare a creator-system proof layer for retrieval and memory once Spark's
memory system is stable enough to plug into the benchmark flow.

Deliverables:

- [x] Deferred domain documented.
- [x] Memory lane contract for local, private, and network-shareable context.
- [x] Retrieval fixtures for correct prior decision, stale memory, contradiction,
  and residue contamination.
- [x] Recompute/provenance checks for retrieved context.

Quality gates:

- Conversational residue is never evidence by default.
- Contradicted or stale memory must block promotion.
- Privacy lanes must be explicit in every packet.

### G. Documentation And Example Standardization

Goal:

Make all proof domains understandable and reusable for future agents without
making premature product or network claims.

Deliverables:

- [x] `CREATOR_SYSTEM_PROOF_DOMAINS.md` describes six proof layers.
- [x] Add example command blocks for each executable proof domain.
- [x] Add a "current claim level" table to the README.
- [x] Add a focused creator-system CI workflow.
- [x] Add a release-note style summary for the CI guardrail slice.
- [x] Keep handoff, master plan, readiness, promotion gates, and backlog aligned.
- [x] Add release-note summary for MiroFish mission-status evidence slice.
- [x] Add release-note summary for artifact-quality mission-status evidence slice.
- [x] Add release-note summary for retrieval-memory mission-status evidence slice.
- [x] Add release-note summary for tool-operation mission-status evidence slice.
- [ ] Continue adding release-note summaries after future committed slices.

Quality gates:

- Docs must name unsafe claims.
- Docs must distinguish local artifacts from network absorption.
- Docs should point to executable commands whenever possible.

## Next Executable Slice

Current Phase 7 executable slice:

1. Verify `creator-mission-status` emits Builder, Telegram, Spawner, Canvas, and
   Kanban read-only views.
2. Verify blocked canonical packets remain blocked in product views.
3. Verify `swarm_shared` requests are blocked without network absorption gates.
4. Keep runtime wiring in product repos, not this methodology repo.
5. Keep network absorption blocked until multi-seed validation,
   human/operator calibration, privacy review, rollback review, and publication
   approval pass.

Next documentation/verification slice:

1. Continue monitoring product PR CI after further branch refreshes.
2. Keep the product mission-status fixture as read-only evidence aggregation;
   do not add product runtime controls here.
3. Treat network absorption gates as deferred until multi-seed validation,
   human/operator calibration, privacy review, rollback review, and publication
   approval are complete.

Completed documentation/verification:

- MiroFish examples are referenced by the product mission-status fixture as a
  read-only `content_route` source packet.
- Artifact-quality examples include saved JSON/Markdown reports and are
  referenced by the product mission-status fixture as a read-only
  `artifact_quality` source packet.
- Retrieval-memory examples include a saved pass check and are referenced by the
  product mission-status fixture as a read-only `retrieval_memory` source
  packet.
- Tool-operation examples include a saved pass check and are referenced by the
  product mission-status fixture as a read-only `tool_operation` source packet.
- Canvas mission-status edges now point only to source packets that are present
  in the canonical mission packet.

Completed product PR verification:

- Builder and Telegram read-only consumer PRs were refreshed after remote CI
  found non-creator blockers.
- Builder now passes remote `test-and-audit` and `secret-scan`.
- Telegram now passes remote `test-and-audit` and `secret-scan`.
- Spawner UI and Canvas still have no remote status checks reported by GitHub;
  their local verification commands remain recorded in the product branch
  ledger.

## Parking Lot

- Multi-RLM provider adapters for content simulation.
- Real content outcome calibration.
- Product wiring for Builder, Telegram, Spawner UI, Canvas, and Kanban.
- Public `spark-creator` repo decision.
- Network absorption review packet.
