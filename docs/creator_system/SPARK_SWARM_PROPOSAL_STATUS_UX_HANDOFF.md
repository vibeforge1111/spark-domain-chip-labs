# Spark Swarm Proposal Status UX Handoff

This handoff gives Spark Swarm product surfaces stable copy and state names for
creator-system artifacts. It is intentionally status-only: it does not wire
runtime creator controls, publish anything, or approve network absorption.

## UX Rule

A creator run may be ready for review without being ready for network absorption.

User-facing copy must preserve three separate questions:

- Is this private workspace evidence usable by the owner?
- Is this artifact ready for a deliberate proposal review?
- Has a publication authority approved network-visible sharing?

## Status States

| State | Use When | User-Facing Meaning | Forbidden Copy |
| --- | --- | --- | --- |
| `private` | The artifact is local, workspace-only, or classified as `private`. | Only this workspace can use it. | Do not say public, shared, published, or absorbed. |
| `workspace_validated` | Smoke/doctor/schema gates pass for private or workspace use. | The workspace can inspect and reuse the evidence locally. | Do not say network approved. |
| `proposal_blocked` | A proposal bundle exists but privacy, rollback, replay, PR proof, or publication approval is missing. | More review work is required before Spark Swarm can consider sharing. | Do not say ready to publish. |
| `proposal_submitted` | A verified-repo PR proof has been submitted but checks or review are pending. | A public-review proposal is open. | Do not say published or network absorbable. |
| `reviewed_candidate` | Required checks and reviews passed, but publication authority has not approved absorption. | The proposal is a reviewed candidate. | Do not say absorbed. |
| `network_absorbable` | Future publication authority explicitly approves the claim. | Spark Swarm may expose the approved shared insight. | Do not reach this state from this repo today. |

## Copy Patterns

Private workspace:

```text
Private workspace evidence. Ready for local review; not published to Spark Swarm.
```

Workspace validated:

```text
Workspace validated. Evidence is replayable locally and remains private.
```

Proposal blocked:

```text
Proposal blocked. Complete privacy, rollback, replay, verified PR proof, and publication approval before sharing.
```

Proposal submitted:

```text
Proposal submitted. Waiting for required checks and review; network absorption is not approved.
```

Reviewed candidate:

```text
Reviewed candidate. Publication authority is still required before network absorption.
```

Network absorbable:

```text
Network absorbable. Approved publication proof exists and names this claim.
```

## Required Product Signals

Spark Swarm UI should show these fields when rendering creator-system artifacts:

- `share_class`
- `redaction_status`
- `allowed_lane`
- `network_absorbable`
- `network_publication_allowed`
- `verified_repo_pr_proof.status`
- `publication_approval.status`
- replay command count
- artifact reference count
- blocked reason count

## Stop-Ship Copy Checks

Block launch copy if any of these strings appear for non-approved artifacts:

- network absorbable
- published to Spark Swarm
- shared with the network
- absorbed by Collective
- approved for network

Allowed safe wording:

- private workspace evidence
- workspace validated
- ready for review
- proposal blocked
- proposal submitted
- reviewed candidate
- network absorption not approved

## Handoff To Spark Swarm

Spark Swarm should map creator-system packets as follows:

| Creator-System Source | Spark Swarm Display State |
| --- | --- |
| `creator-swarm-lane-taxonomy` with `private_draft` | `private` |
| `creator-swarm-lane-taxonomy` with `workspace_validated` | `workspace_validated` |
| `creator-network-proposal-bundle` with blocked reasons | `proposal_blocked` |
| `creator-network-proposal-bundle` with PR proof submitted | `proposal_submitted` |
| `creator-network-proposal-bundle` with passed reviews and verified PR proof | `reviewed_candidate` |
| Future approved publication manifest | `network_absorbable` |

Until a future approved publication manifest exists, Spark Swarm should render
creator-system artifacts as private, workspace validated, proposal blocked,
proposal submitted, or reviewed candidate only.
