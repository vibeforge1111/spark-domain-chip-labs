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

Status: complete.

Tasks:

- [x] Read Spark Swarm private workspace and network contribution design.
- [x] Read Spark Swarm shared insight publication security docs.
- [x] Align creator-system launch work with OWASP LLM, NIST AI RMF, GitHub
  token scoping, GitHub Actions hardening, and OpenSSF Scorecard references.
- [x] Add alignment task ledger with CSS-01 through CSS-12.
- [x] Add this phase plan to first-read documentation.
- [x] Add docs unit tests for phase coverage and blocked network boundaries.

Verification:

```powershell
python -m pytest tests/test_creator_system_docs.py -q
python -m ruff check tests/test_creator_system_docs.py
```

Commit target:

- `Document Spark Swarm phased build plan`

## P1 Lane Taxonomy Contract

Status: initial contract complete.

Purpose:

Define one shared language for the creator system and Spark Swarm so private
workspace learning never silently upgrades into public network trust.

Build outputs:

- `docs/creator_system/schemas/creator-swarm-lane-taxonomy.schema.json`
- `docs/creator_system/examples/swarm-lane-taxonomy/startup-yc-private-workspace.json`
- `docs/creator_system/examples/swarm-lane-taxonomy/startup-yc-network-proposal-blocked.json`
- Tests that validate both examples and reject forbidden upgrades.

Implementation status:

- [x] Schema added.
- [x] Private workspace example added.
- [x] Blocked network proposal example added.
- [x] Unit tests reject network publication, private-to-reviewed jumps,
  missing proposal review, and missing forbidden-transition markers.

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

Status: initial contract complete.

Purpose:

Create the contract that turns a local review bundle into a deliberate network
proposal package without approving publication.

Build outputs:

- `docs/creator_system/schemas/creator-network-proposal-bundle.schema.json`
- `docs/creator_system/examples/network-proposal-bundles/startup-yc-blocked-proposal.json`
- Schema README entry.
- Tests that validate the example and reject unsafe proposal packets.

Implementation status:

- [x] Schema added.
- [x] Blocked Startup YC proposal example added.
- [x] Unit tests reject network absorption claims, missing replay commands,
  malformed hashes, raw Windows paths, and reviewed-candidate promotion without
  verified PR proof and passed reviews.

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

Status: initial dry-run mapper complete.

Purpose:

Produce Spark Swarm-compatible payload shape locally without syncing or
publishing anything.

Build outputs:

- A small mapper module under `src/chip_labs/` or a CLI command if local style
  favors command exposure.
- Example dry-run output for Startup YC.
- Unit tests that verify payload shape and privacy boundaries.

Implementation status:

- [x] `src/chip_labs/creator_swarm_collective.py` builds a
  `SparkResearcherCollectiveSyncPayload`-shaped dry-run payload from a creator
  run.
- [x] `creator-swarm-collective-dry-run` emits the local payload without sync or
  publication.
- [x] Unit tests verify thin artifact refs, private `shareScope`, isolated
  memory policy, deferred mastery review, no raw Windows paths, and no network
  approval tokens.

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
python -m pytest tests/test_creator_swarm_collective.py -q
python -m ruff check src/chip_labs tests
```

Commit target:

- `Add creator Swarm dry-run payload mapper`

## P4 Privacy Classification And Redaction Gates

Status: initial privacy gates complete.

Purpose:

Make every artifact declare how far it is allowed to travel before a review
bundle can become a proposal bundle.

Build outputs:

- `share_class` field for bundle path records or proposal artifact refs.
- allowed lane field.
- redaction status field.
- validator checks for forbidden network proposal inputs.

Implementation status:

- [x] Local Swarm review-bundle path records now require `share_class`,
  `redaction_status`, and `allowed_lane`.
- [x] Startup YC review-bundle fixture classifies private workspace artifacts
  separately from proposal-redacted artifacts.
- [x] Unit tests reject missing privacy classification, private paths entering
  network-absorption lanes, and forbidden paths without blocked redaction.

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

Status: initial compatibility fields complete.

Purpose:

Make generated specialization paths usable by Spark Swarm's specialization path
authoring and runtime-context model without moving runtime authority into this
repo.

Build outputs:

- Authoring checklist mapping doc.
- Compatibility fields in generated path manifests if needed.
- Tests that prove Startup YC path output names replay, benchmark, rollback,
  and scope requirements.

Implementation status:

- [x] `specialization-path-manifest.schema.json` now requires
  `spark_swarm_compatibility`.
- [x] Generated and Startup YC path manifests name Spark Researcher as the
  runtime core, `SparkResearcherCollectiveSyncPayload` as the payload shape,
  the runtime-context contract, external path ownership, and forbidden ownership
  of identity, channel auth, provider secrets, and global tool authority.
- [x] Unit tests reject runtime-core drift and missing forbidden-ownership
  boundaries.

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

Status: initial UX handoff complete.

Purpose:

Prepare the handoff that Spark Swarm UI and PR flows can use to explain status
without making users read raw JSON.

Build outputs:

- Proposal-status copy states.
- Spark Swarm PR template handoff notes.
- Review checklist for verified-repo proof.

Implementation status:

- [x] `SPARK_SWARM_PROPOSAL_STATUS_UX_HANDOFF.md` defines private,
  workspace-validated, proposal-blocked, proposal-submitted,
  reviewed-candidate, and future network-absorbable display states.
- [x] Handoff copy separates ready-for-review wording from publication approval.
- [x] Docs tests guard required status fields and stop-ship copy checks.

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

Status: initial rehearsal complete.

Purpose:

Use the strongest proof domain to rehearse the full path before any launch
claim changes.

Implementation status:

- [x] `CREATOR_SYSTEM_SPARK_SWARM_LAUNCH_REHEARSAL_2026-05-05.md` records the
  Startup YC smoke, doctor, Collective dry-run payload, and blocked contract
  test evidence.
- [x] Rehearsal keeps `shareScope=private`, review decision `defer`,
  `network_absorbable=false`, and no automatic publish.
- [x] Remaining P7 work is explicitly scoped to clean-clone rehearsal,
  Spark Swarm template mirroring, verified-repo PR proof placeholder, and UI
  state rendering.

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

Status: initial hardening checklist complete.

Purpose:

Make the launch path practical for many creator runs, many workspaces, and
future public review without creating hidden cost or security debt.

Build outputs:

- least-privilege GitHub token checklist
- GitHub Actions hardening checklist
- OpenSSF Scorecard posture notes
- payload size and artifact reference rules
- pagination/snapshot guidance for Spark Swarm hot routes

Implementation status:

- [x] `SPARK_SWARM_LAUNCH_HARDENING_CHECKLIST.md` records supply-chain,
  privacy, scalability, UX, payload-budget, and launch-rehearsal gates.
- [x] Checklist requires least-privilege GitHub App installation tokens,
  GitHub Actions hardening, secret scanning, dependency/Scorecard posture,
  verified-repo PR proof, and future signed publication authority.
- [x] Checklist blocks hot routes from consuming full creator-run trees or raw
  private workspace paths.

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

P1 through P8 are complete from this repo's side and have post-P8 clean-clone
evidence. The next slice is the Spark Swarm launch bridge:

1. Attach creator-system proposal bundles in `spark-swarm`. Done in
   Spark Swarm commit `c225fcf`, which adds `--creator-proposal-bundle` and
   keeps creator-system proposals blocked on `creatorVerifiedRepoPrProof` and
   `creatorPublicationApproval`. Spark Swarm commit `2185f3f` adds bundle
   policy validation for schema version, replay commands, artifact refs, raw
   Windows paths, `no_automatic_publish`, and unexpected public absorption
   claims.
2. Mirror the proposal bundle template into `spark-swarm`. Done in
   Spark Swarm commit `d487e18` via
   `templates/creator-system-network-proposal/creator-network-proposal-bundle.template.json`.
3. Open a verified-repo PR proof placeholder in the real launch repo flow.
   Done in Spark Swarm commit `cd68cf7` with
   `templates/creator-system-network-proposal/verified-repo-pr-proof.placeholder.json`;
   Spark Swarm keeps placeholder and incomplete approved proofs blocked until
   repo, PR URL, head SHA, base branch, and required checks are present.
3a. Define explicit publication approval as a standalone blocked authority.
    Done in Spark Swarm commit `0783c7d` at
    `templates/creator-system-network-proposal/publication-approval.placeholder.json`;
    it remains `not_approved`, keeps `network_absorbable=false`, and rejects
    private workspace sync, `ready_for_swarm_packet`, generated matrix JSON, and
    runtime creator controls as approval inputs.
4. Record hosted Spark Swarm UI consumption of private, workspace-validated,
   proposal-blocked, proposal-submitted, and reviewed-candidate states. UI
   state contract fixture done in Spark Swarm commit `83cb10f` at
   `templates/creator-system-network-proposal/creator-system-proposal-status.ui-fixture.json`;
   it is a display-only contract that keeps every current state
   `network_absorbable=false` and `automatic_publish=false`. Hosted runtime UI
   proof remains pending because this slice did not touch the dirty web runtime
   files.
5. Define signed publication manifest authority before any stronger network
   claim. Placeholder authority contract done in Spark Swarm commit `6a61b9e`
   at
   `templates/creator-system-network-proposal/signed-publication-manifest-authority.placeholder.json`;
   it remains `not_configured` and keeps `network_absorbable=false` until a
   signed manifest, signature, signing key id, protected-branch keyring
   reference, and reviewed artifact paths exist.
6. Maintain a machine-readable launch readiness report for agents and
   reviewers. Done in Spark Swarm commit `4b160d8` at
   `templates/creator-system-network-proposal/creator-system-launch-readiness.template.json`;
   it reports `overall_stage=workspace_and_proposal_contract_ready`,
   `network_launch_stage=blocked_by_design`, and remaining gates for hosted
   runtime UI proof, verified-repo PR proof, publication approval, signed
   publication manifest authority, and scoped absorption policy.
7. Define scoped absorption policy before any network-memory movement. Placeholder
   policy done in Spark Swarm commit `8a8efe7` at
   `templates/creator-system-network-proposal/scoped-absorption-policy.placeholder.json`;
   it remains `placeholder_blocked`, keeps `network_absorbable=false`, forbids
   private/workspace artifacts, runtime creator controls, raw private paths,
   secrets, and full creator-run trees, and requires verified PR proof,
   publication approval, signed manifest authority, privacy review, rollback
   review, and revocation coverage before activation.
8. Define hosted runtime UI proof before touching dirty web runtime files. Proof
   template done in Spark Swarm commit `4951c64` at
   `templates/creator-system-network-proposal/hosted-runtime-ui-proof.template.json`;
   it is `template_only`, requires desktop/mobile screenshots and interactive
   assertions, and does not prove hosted runtime behavior until a future UI run
   verifies no active network absorption badges or publish controls.
9. Define hosted UI state-by-state assertions before any visual proof claim.
   Assertion matrix template done in Spark Swarm commit `5e90b4e` at
   `templates/creator-system-network-proposal/hosted-runtime-ui-assertion-matrix.template.json`;
   it covers desktop/mobile viewports, forbidden public-approval copy,
   forbidden publish/promote/absorb controls, and disabled future
   network-absorbable state.
10. Define user sharing preference as data before runtime creator controls.
   Sharing preference template done in Spark Swarm commit `00fa489` at
   `templates/creator-system-network-proposal/sharing-preference.template.json`;
   it supports `private_only`, `review_everything`, `trusted_auto_propose`, and
   `public_by_policy`, but broad sharing creates proposal candidates only and
   cannot bypass redaction, verified PR proof, publication approval, signed
   manifest authority, rollback, or revocation.

Still blocked:

- `network_absorbable=true`
- automatic Spark Swarm publish
- product runtime creator controls
