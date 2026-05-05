# Creator System Spark Swarm Phased Build Plan

This is the working build plan for turning creator-system runs into reusable
Spark Swarm workspace and proposal artifacts while preserving private
workspaces, user consent, and blocked network absorption.

It follows the alignment in
`CREATOR_SYSTEM_SPARK_SWARM_ALIGNMENT_AND_LAUNCH_TASKS.md` and breaks the work
into executable phases with tests, artifacts, commits, and stop-ship gates.

## Build Standard

- Commit coherent slices often.
- Add or update unit/docs tests before claiming a phase is complete.
- Keep `network_absorbable=false` until a separate future publication authority
  explicitly approves network absorption.
- Treat `ready_for_swarm_packet` as artifact readiness only.
- Keep private workspace sync separate from public network contribution.
- Prefer thin summaries plus artifact references over moving full creator-run
  trees through Spark Swarm hot paths.
- Do not wire Builder, Telegram, Spawner, Canvas, or Kanban runtime creator
  controls in this repo.

## Phase Overview

| Phase | Intent | Primary Output | Exit Gate |
| --- | --- | --- | --- |
| P0 | Planning and guardrails | This phased task plan, linked from first-read docs | Docs test proves phases, claims, and stop-ship gates are visible. |
| P1 | Lane taxonomy | Creator-to-Swarm lane mapping contract | Unit/docs tests prove private, workspace, proposal, reviewed, blocked, and forbidden transitions. |
| P2 | Proposal bundle contract | Network proposal bundle schema and example | Schema validation blocks missing privacy, rollback, replay, PR proof, and publication placeholders. |
| P3 | Dry-run Collective mapper | Local CLI or module mapping creator runs to `SparkResearcherCollectiveSyncPayload`-shaped JSON | Unit test proves thin payload, artifact refs, no secrets, no network approval. |
| P4 | Privacy and redaction gates | `share_class`, redaction status, allowed lane, forbidden-lane blockers | Tests prove private/unredacted artifacts cannot enter proposal lane. |
| P5 | Specialization-path compatibility | Spark Swarm authoring checklist mapping for generated specialization paths | Tests prove generated path manifests can be translated without hosted runtime coupling. |
| P6 | Proposal UX and templates | Review copy, proposal status states, and PR template handoff notes for Spark Swarm | Docs tests prove user-facing states do not conflate private sync with publication. |
| P7 | Startup YC rehearsal | Cross-repo launch rehearsal plan and evidence packet | Rehearsal records blocked/approved states, replay commands, and no automatic publish. |
| P8 | Supply-chain and scalability hardening | CI/security checklist, payload-size rules, artifact-reference rules | Tests/docs prove least privilege, pinned checks, and thin hot-route payloads. |

## P0 Planning And Guardrails

Status: in progress.

Tasks:

- [x] Read Spark Swarm private workspace and network contribution design.
- [x] Read Spark Swarm shared insight publication security docs.
- [x] Align creator-system launch work with OWASP LLM, NIST AI RMF, GitHub
  token scoping, GitHub Actions hardening, and OpenSSF Scorecard references.
- [x] Add alignment task ledger with CSS-01 through CSS-12.
- [ ] Add this phase plan to first-read documentation.
- [ ] Add docs unit tests for phase coverage and blocked network boundaries.

Verification:

```powershell
python -m pytest tests/test_creator_system_docs.py -q
python -m ruff check tests/test_creator_system_docs.py
```

Commit target:

- `Document Spark Swarm phased build plan`

## P1 Lane Taxonomy Contract

Status: next.

Purpose:

Define one shared language for the creator system and Spark Swarm so private
workspace learning never silently upgrades into public network trust.

Build outputs:

- `docs/creator_system/schemas/creator-swarm-lane-taxonomy.schema.json`
- `docs/creator_system/examples/swarm-lane-taxonomy/startup-yc-private-workspace.json`
- `docs/creator_system/examples/swarm-lane-taxonomy/startup-yc-network-proposal-blocked.json`
- Tests that validate both examples and reject forbidden upgrades.

Required states:

- `private_draft`
- `workspace_validated`
- `pr_submitted`
- `reviewed_candidate`
- `blocked_network_absorption`

Required creator mappings:

- `local_only` -> `private_draft`
- `candidate_review` -> `workspace_validated`
- `transfer_supported` -> `workspace_validated` or `pr_submitted`
- `network_absorbable` -> blocked unless explicit future approval exists

Forbidden transitions:

- `private_draft` -> `reviewed_candidate` without proposal review
- `workspace_validated` -> `network_absorbable` from sync alone
- `ready_for_swarm_packet` -> `network_absorbable`
- generated matrix evidence -> network publication

Verification:

```powershell
python -m pytest tests/test_creator_system_docs.py -q
```

Commit target:

- `Add creator Swarm lane taxonomy contract`

## P2 Network Proposal Bundle Contract

Status: planned.

Purpose:

Create the contract that turns a local review bundle into a deliberate network
proposal package without approving publication.

Build outputs:

- `docs/creator_system/schemas/creator-network-proposal-bundle.schema.json`
- `docs/creator_system/examples/network-proposal-bundles/startup-yc-blocked-proposal.json`
- Schema README entry.
- Tests that validate the example and reject unsafe proposal packets.

Required fields:

- schema version
- proposal id
- source creator run id
- evidence tier
- lane state
- artifact refs with hashes
- replay commands
- privacy review
- redaction review
- rollback review
- verified-repo GitHub PR proof placeholder
- publication approval placeholder
- `network_absorbable=false`
- `network_publication_allowed=false`

Stop-ship blockers:

- missing replay commands
- missing artifact hashes
- raw private paths in network copy
- secrets or unredacted sensitive values
- missing rollback review
- missing verified-repo PR proof placeholder
- any `network_absorbable=true`

Verification:

```powershell
python -m pytest tests/test_creator_system_docs.py -q
```

Commit target:

- `Add blocked network proposal bundle contract`

## P3 Dry-Run Collective Payload Mapper

Status: planned.

Purpose:

Produce Spark Swarm-compatible payload shape locally without syncing or
publishing anything.

Build outputs:

- A small mapper module under `src/chip_labs/` or a CLI command if local style
  favors command exposure.
- Example dry-run output for Startup YC.
- Unit tests that verify payload shape and privacy boundaries.

Payload requirements:

- `workspaceId`
- `agentId`
- `runtimeSource`
- `specialization`
- `runtimePulse`
- `intelligencePulse`
- `insights`
- `masteries`
- `outcomes`
- `artifactRefs`
- `emittedAt`

Guardrails:

- no secret-looking values
- no raw full creator-run tree
- no product runtime controls
- no network publication authority
- `artifactRefs` point to local/repo evidence rather than embedding heavy
  artifacts

Verification:

```powershell
python -m pytest tests/test_creator_swarm_collective_mapper.py -q
python -m ruff check src/chip_labs tests
```

Commit target:

- `Add creator Swarm dry-run payload mapper`

## P4 Privacy Classification And Redaction Gates

Status: planned.

Purpose:

Make every artifact declare how far it is allowed to travel before a review
bundle can become a proposal bundle.

Build outputs:

- `share_class` field for bundle path records or proposal artifact refs.
- allowed lane field.
- redaction status field.
- validator checks for forbidden network proposal inputs.

Allowed share classes:

- `private`
- `workspace`
- `proposal_redacted`
- `network_candidate`
- `forbidden`

Verification:

```powershell
python -m pytest tests/test_creator_system_docs.py tests/test_creator_run.py -q
```

Commit target:

- `Add creator artifact privacy classification gates`

## P5 Specialization Path Compatibility

Status: planned.

Purpose:

Make generated specialization paths usable by Spark Swarm's specialization path
authoring and runtime-context model without moving runtime authority into this
repo.

Build outputs:

- Authoring checklist mapping doc.
- Compatibility fields in generated path manifests if needed.
- Tests that prove Startup YC path output names replay, benchmark, rollback,
  and scope requirements.

Guardrails:

- no hosted runtime coupling
- no provider secrets
- no identity or channel-auth ownership
- no global tool authority

Verification:

```powershell
python -m pytest tests/test_creator_generator_acceptance.py -q
```

Commit target:

- `Align creator specialization paths with Spark Swarm authoring`

## P6 Proposal UX And Spark Swarm Templates

Status: planned.

Purpose:

Prepare the handoff that Spark Swarm UI and PR flows can use to explain status
without making users read raw JSON.

Build outputs:

- Proposal-status copy states.
- Spark Swarm PR template handoff notes.
- Review checklist for verified-repo proof.

Required user-visible states:

- private
- workspace validated
- proposal blocked
- proposal submitted
- reviewed candidate
- network absorbable

Copy rule:

The UI may say a creator run is ready for review, but it must not say the run is
network absorbable until the separate publication authority approves it.

Verification:

```powershell
python -m pytest tests/test_creator_system_docs.py -q
```

Commit target:

- `Document Spark Swarm proposal UX handoff`

## P7 Startup YC Launch Rehearsal

Status: planned.

Purpose:

Use the strongest proof domain to rehearse the full path before any launch
claim changes.

Rehearsal path:

```text
Startup YC creator run
  -> smoke and doctor
  -> review bundle
  -> lane taxonomy packet
  -> dry-run Collective payload
  -> blocked network proposal bundle
  -> verified-repo PR proof placeholder
  -> launch-readiness report
```

Verification:

```powershell
python -m pytest tests/test_creator_generator_acceptance.py tests/test_creator_system_docs.py -q
python -m chip_labs.cli creator-system-production-readiness --fail-on-blocked
```

Commit target:

- `Record Startup YC Spark Swarm launch rehearsal`

## P8 Supply-Chain And Scalability Hardening

Status: planned.

Purpose:

Make the launch path practical for many creator runs, many workspaces, and
future public review without creating hidden cost or security debt.

Build outputs:

- least-privilege GitHub token checklist
- GitHub Actions hardening checklist
- OpenSSF Scorecard posture notes
- payload size and artifact reference rules
- pagination/snapshot guidance for Spark Swarm hot routes

Scalability rules:

- hot routes consume summaries, not full run trees
- large reports remain repo artifacts or CI artifacts
- payloads include hashes and stable refs
- proposal review can fetch full evidence only when needed

Verification:

```powershell
python -m pytest tests/test_creator_system_docs.py -q
```

Commit target:

- `Add Spark Swarm launch hardening checklist`

## Cross-Phase Done Definition

The plan is launch-ready only when:

- all P0 through P8 exit gates pass
- every new schema has at least one valid example and one rejection test
- docs, schemas, examples, and CLI outputs all keep `network_absorbable=false`
  until the future publication approval lane exists
- Spark Swarm can consume a dry-run payload without private-data leakage
- network proposal remains deliberate, replayable, reviewable, and revocable
- product runtime creator controls remain read-only/deferred from this repo

## Current Next Build Slice

Start with P1:

1. Add the lane taxonomy schema.
2. Add one private workspace example and one blocked network proposal example.
3. Add unit/docs tests for valid examples and forbidden transitions.
4. Commit the slice.

