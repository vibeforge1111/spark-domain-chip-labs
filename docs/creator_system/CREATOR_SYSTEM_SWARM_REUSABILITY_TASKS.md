# Creator System Swarm Reusability Tasks

This task ledger turns the remaining hardening work into a reusable Spark
Swarm path.

The goal is to make creator-system domains easy for humans and Spark agents to
review, replay, and eventually absorb through Spark Swarm. It does not approve
network absorption. Every task below preserves `network_absorbable=false` until
the full promotion bundle passes.

## Working Definition

Swarm-reusable means:

- a creator run has a schema-valid local Swarm contribution packet
- evidence packets have stable paths, provenance, and rollback notes
- another agent can replay the smoke, doctor, benchmark, and summary checks
- the bundle states its weakest evidence tier and forbidden claims
- product surfaces consume read-only mission status only

Swarm-reusable does not mean:

- automatic Spark Swarm publication
- `network_absorbable=true`
- product runtime creator controls
- hidden memory promotion
- treating `ready_for_swarm_packet` as approval

## Task Ledger

| ID | Task | Why It Matters | Reusable Output | Status |
| --- | --- | --- | --- | --- |
| SR-01 | Upload generated matrix JSON from manual and scheduled CI. | Reviewers need packets, not log scraping. | `generated-creator-matrix-evidence` workflow artifact. | Done in `f70c166`. |
| SR-02 | Add a Swarm reusable creator path. | Outside contributors need one path from domain idea to review bundle. | `SWARM_REUSABLE_CREATOR_PATH.md`. | Done in `100f015`. |
| SR-03 | Add contributor guidance for new creator-system domains. | New domains should follow the same evidence ladder and packet boundary. | `CONTRIBUTING_CREATOR_DOMAINS.md` linked from first-read docs. | Done. |
| SR-04 | Define a review bundle checklist for local Swarm packets. | Swarm reviewers need required packet, evidence, provenance, and rollback fields. | Checklist in the reusable path doc. | Done in `100f015`. |
| SR-05 | Add an example review bundle for a generated proof domain. | Contributors learn faster from one concrete bundle. | `examples/swarm-review-bundles/startup-yc-transfer-supported/`. | Done. |
| SR-06 | Add a lightweight bundle shape check if examples start drifting. | Reuse should be executable, not only prose. | `swarm-review-bundle.schema.json` plus focused docs tests. | Done. |
| SR-07 | Run fresh-clone verification after the next packaging change. | Public users need install proof independent from local dirty state. | Fresh-clone evidence note and clean output packet paths. | Done in `97397ea` via the post-P8 clean-clone rehearsal. |
| SR-08 | Decide whether generated matrix JSON should become release assets. | Release consumers may need stable downloadable evidence outside CI retention. | Release asset policy, only after a new public hardening tag. | Done: CI artifacts remain default; release assets require a future hardening tag with fresh evidence. |
| SR-09 | Review unrelated docs/research/viz files as a separate slice. | Research residue should not silently become creator-system doctrine. | Curated commit, archive decision, or explicit defer note. | Pending. |
| SR-10 | Continue proof-domain improvements through executable gates only. | Swarm reuse must be earned by tests, smoke, doctor, and provenance checks. | More passing proof-domain gates and blocked unsafe claims. | Ongoing. |
| SR-11 | Keep product runtime creator controls deferred. | Builder, Telegram, Spawner, Canvas, and Kanban must not mutate creator runs yet. | Read-only mission-status consumers only. | Ongoing boundary. |
| SR-12 | Prepare a future promotion bundle for real network absorption. | `network_absorbable` requires complete approval evidence. | Multi-seed, calibration, privacy, rollback, publication, product-runtime, and authority packets. | Blocked by design. |

## Build Order

1. Make the local review bundle path explicit. Done.
2. Add contributor guidance for new creator domains. Done.
3. Add one example bundle from an existing generated proof domain. Done.
4. Add the smallest executable check that prevents bundle drift. Done.
5. Run fresh-clone verification before a new hardening package. Done for the
   post-P8 clean-clone rehearsal.
6. Decide whether the bundle artifacts belong on a public release. Done:
   keep generated matrix JSON as `generated-creator-matrix-evidence` CI
   artifacts by default; attach them to GitHub Releases only for a future
   explicitly tagged hardening prerelease with fresh evidence and release notes.

## Remaining Launch Bridge

The reusable creator path is now ready for Spark Swarm private workspace and
proposal-template integration, but not for network absorption. Remaining work
belongs in the launch bridge:

- attach creator-system proposal bundles in `spark-swarm`; first bridge gate
  landed in Spark Swarm commit `c225fcf` with `--creator-proposal-bundle`,
  `creatorVerifiedRepoPrProof`, and `creatorPublicationApproval`;
  bundle policy hardening landed in Spark Swarm commit `2185f3f`
- mirror the proposal bundle template into `spark-swarm`; done in
  Spark Swarm commit `d487e18` at
  `templates/creator-system-network-proposal/creator-network-proposal-bundle.template.json`
- open a verified-repo PR proof placeholder in the real launch repo flow; done
  in Spark Swarm commit `cd68cf7` at
  `templates/creator-system-network-proposal/verified-repo-pr-proof.placeholder.json`
- define explicit publication approval as a standalone blocked authority; done
  in Spark Swarm commit `0783c7d` at
  `templates/creator-system-network-proposal/publication-approval.placeholder.json`,
  still `not_approved` and rejecting private workspace sync,
  `ready_for_swarm_packet`, generated matrix JSON, and runtime creator controls as approval inputs
- record hosted Spark Swarm UI consumption of private, workspace-validated,
  proposal-blocked, proposal-submitted, and reviewed-candidate states; UI state
  contract fixture done in Spark Swarm commit `83cb10f` at
  `templates/creator-system-network-proposal/creator-system-proposal-status.ui-fixture.json`,
  with hosted runtime UI proof still pending
- define signed publication manifest authority before any stronger public
  claim; placeholder authority contract done in Spark Swarm commit `6a61b9e`
  at
  `templates/creator-system-network-proposal/signed-publication-manifest-authority.placeholder.json`
- maintain a machine-readable launch readiness template for agents and
  reviewers; done in Spark Swarm commit `4b160d8` at
  `templates/creator-system-network-proposal/creator-system-launch-readiness.template.json`,
  with `overall_stage=workspace_and_proposal_contract_ready` and
  `network_launch_stage=blocked_by_design`
- define scoped absorption policy before any network-memory movement; placeholder
  policy done in Spark Swarm commit `8a8efe7` at
  `templates/creator-system-network-proposal/scoped-absorption-policy.placeholder.json`,
  still `placeholder_blocked` and requiring verified PR proof, publication
  approval, signed manifest authority, privacy review, rollback review, and
  revocation coverage before activation
- define hosted runtime UI proof before touching dirty web runtime files; proof
  template done in Spark Swarm commit `4951c64` at
  `templates/creator-system-network-proposal/hosted-runtime-ui-proof.template.json`,
  still `template_only` and requiring desktop/mobile screenshots plus
  interaction assertions before hosted runtime proof can be claimed
- define a hosted UI state-by-state assertion matrix before any visual proof
  claim; assertion matrix template done in Spark Swarm commit `5e90b4e` at
  `templates/creator-system-network-proposal/hosted-runtime-ui-assertion-matrix.template.json`,
  covering desktop/mobile viewports, forbidden public-approval copy, forbidden
  publish/promote/absorb controls, and disabled future network-absorbable state
- define GitHub branch/ruleset review as data before trusting proposal proof;
  ruleset review template done in Spark Swarm commit `d4d5f84` at
  `templates/creator-system-network-proposal/github-ruleset-review.template.json`,
  requiring CODEOWNER review, required checks, direct-push blocking, and
  sensitive path evidence before proposal evidence is trusted
- define user sharing preference as data before runtime creator controls; sharing
  preference template done in Spark Swarm commit `00fa489` at
  `templates/creator-system-network-proposal/sharing-preference.template.json`,
  supporting `private_only`, `review_everything`, `trusted_auto_propose`, and
  `public_by_policy` while keeping `network_absorbable=false`, forbidding
  `share_everything` bypasses, and requiring redaction, verified PR proof,
  publication approval, signed manifest authority, rollback, and revocation
  before public network movement
- define artifact attestation readiness before public release/proposal bundles
  become launch assets; readiness template done in Spark Swarm commit `f47019c` at
  `templates/creator-system-network-proposal/artifact-attestation-readiness.template.json`,
  keeping the gate `template_only`, using `actions/attest` as the future
  pinned provenance action, isolating `id-token: write` to protected workflows,
  and stating that attestations are provenance/integrity evidence, not privacy
  review, content safety, publication approval, or network absorption approval
- record the live GitHub branch/ruleset review instead of assuming it passed;
  blocked evidence done in Spark Swarm commit `6834f81` at
  `templates/creator-system-network-proposal/github-ruleset-review.current.json`,
  with `status=blocked_unprotected` because `origin/main` was not
  branch-protected and no repository rulesets were returned by the GitHub API.
  Proposal evidence remains blocked until branch protection or rulesets enforce
  PR review, CODEOWNER review, direct-push blocking, and required checks.

## Promotion Rule

No task in this ledger may change `network_absorbable` to `true`.

The first allowed stronger claim is still gated by multi-seed validation,
human/operator calibration, privacy review, rollback review, publication
approval, product runtime review, and explicit publication authority.
