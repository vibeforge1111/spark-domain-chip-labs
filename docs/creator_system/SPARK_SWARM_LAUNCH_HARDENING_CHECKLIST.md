# Spark Swarm Launch Hardening Checklist

This checklist is the P8 gate for taking creator-system artifacts into Spark
Swarm launch work. It is a launch-readiness checklist, not a live deployment
change.

## Non-Negotiable Boundary

- `network_absorbable=false`
- `network_publication_allowed=false`
- no automatic publish
- no product runtime creator controls from this repo
- no private workspace artifact becomes network-visible without proposal review

## Supply-Chain Gates

| Gate | Requirement | Launch State |
| --- | --- | --- |
| Least-privilege GitHub tokens | GitHub App installation tokens must be scoped to the specific repo and minimum permissions needed for proposal PR proof. | Required before launch |
| Actions hardening | Workflows that produce proposal evidence must set explicit read-only default `GITHUB_TOKEN` permissions, avoid untrusted script injection, and pin third-party actions to full-length commit SHAs or an approved internal allowlist. | Required before launch |
| Secret scanning | Proposal bundles must be scanned for tokens, private keys, emails, phone numbers, internal URLs, and raw local absolute paths. | Required before launch |
| Dependency posture | Launch checklist must include dependency audit and OpenSSF Scorecard review or documented equivalent. | Required before launch |
| Verified-repo PR proof | Network-visible proposal review must reference protected/default branch, head SHA, required checks, and PR URL. | Required before reviewed candidate |
| Signed publication manifest | Future network absorption must require a signed publication manifest or explicit publication authority record. | Required before network absorption |

## Privacy Gates

- every review-bundle path has `share_class`
- every review-bundle path has `redaction_status`
- every review-bundle path has `allowed_lane`
- private artifacts cannot enter `blocked_network_absorption`
- proposal artifacts cannot omit replay commands
- proposal artifacts cannot use raw Windows absolute paths
- reviewed-candidate proposals require verified PR proof and passed reviews

## Scalability Gates

Hot Spark Swarm routes must consume:

- `SparkResearcherCollectiveSyncPayload` summaries
- bounded `artifactRefs`
- hashes and stable repo paths
- pagination for long insight/mastery/outcome lists
- snapshot or receipt ids for replay and debugging

Hot Spark Swarm routes must not consume:

- full creator-run trees
- raw benchmark case corpora by default
- full report blobs on every Collective read
- local temp paths
- private workspace absolute paths

## Payload Budget

Initial launch budget:

| Payload Surface | Budget | Rule |
| --- | --- | --- |
| Collective dry-run payload | <= 128 KB target | Keep normal workspace sync lightweight. |
| Artifact refs | <= 50 refs target | Link heavy evidence instead of embedding it. |
| Insight/mastery/outcome records | <= 25 records per dry-run payload target | Use pagination or snapshots for larger batches. |
| Proposal bundle | <= 256 KB target | Store large reports as referenced artifacts with hashes. |

## UX Gates

Spark Swarm surfaces must visibly distinguish:

- private
- workspace validated
- proposal blocked
- proposal submitted
- reviewed candidate
- future network absorbable

Unsafe copy is a stop-ship condition when it claims any of the following before
publication authority exists:

- published to Spark Swarm
- absorbed by Collective
- approved for network
- network absorbable

## Launch Rehearsal Gates

Before launch:

- repeat `CREATOR_SYSTEM_SPARK_SWARM_LAUNCH_REHEARSAL_2026-05-05.md` from a
  clean clone
- produce a dry-run Collective payload for Startup YC
- validate lane taxonomy examples
- validate blocked proposal bundle examples
- validate review-bundle privacy classification
- confirm no automatic publish path exists
- confirm `network_absorbable=false` in every creator-system launch artifact

## Residual Blockers

Spark Swarm launch integration is still blocked on:

- mirroring the proposal-bundle template into `spark-swarm`
- adding Spark Swarm UI rendering for proposal states
- running a clean-clone rehearsal after this hardening checklist lands
- recording verified-repo PR proof placeholder through the real launch flow
- deciding future signed publication manifest authority

Until these are complete, the correct claim is:

```text
creator-system artifacts are reusable for private workspace sync and proposal
review rehearsal; they are not network absorbable.
```
