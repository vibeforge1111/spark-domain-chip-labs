# Swarm Reusable Creator Path

This path explains how to make a creator-system domain reusable by Spark Swarm
reviewers without publishing it to the network.

Use it after a creator run already has intent, adapter map, domain chip,
benchmark pack, specialization path, autoloop policy, reports, evidence ladder,
mission status, and `swarm/contribution_packet.json`.

## Boundary

The output is a local review bundle. It can be attached to a GitHub pull
request, downloaded from CI, or handed to another Spark agent for replay.

It is not network absorption. Keep:

- `governance.network_publication_allowed=false`
- `publication.network_absorbable=false`
- evidence tier at the weakest passing gate
- product runtime controls read-only

## Reusable Bundle Contents

Every Swarm-reusable creator domain should provide these paths or explain why a
path is intentionally absent:

| Bundle Part | Required Path | Review Purpose |
| --- | --- | --- |
| Creator intent | `creator-intent.json` | Confirms domain, goal, constraints, and target evidence tier. |
| Adapter map | `adapter-map.json` | Shows local repos, product surfaces, and Swarm path boundaries. |
| Artifact manifest | `created-artifact-manifest.json` | Lists chip, benchmark, path, autoloop, reports, and packet status. |
| Domain chip | `domain-chip/` | Shows the domain behavior is implemented, not prompt-only. |
| Benchmark pack | `benchmark/` | Proves the improvement target and trap coverage. |
| Specialization path | `specialization-path/` | Tells another agent how to load, practice, and emit evidence. |
| Autoloop policy | `autoloop/policy.json` | Defines mutation, keep, revert, stop, and rollback rules. |
| Reports | `reports/` | Preserves baseline, candidate, absorption, transfer, and known-gap evidence. |
| Evidence ladder | `reports/evidence_ladder.md` | States safe and unsafe claims in plain language. |
| Swarm packet | `swarm/contribution_packet.json` | Packages the local contribution for review. |
| Mission status | `reports/creator-mission-status.json` | Gives product surfaces a read-only status packet. |

## Required Review Checks

Run the local checks before sending a bundle for Swarm review:

```bash
python -m chip_labs.cli creator-run-smoke <run-dir> --fail-on-blocked
python -m chip_labs.cli creator-run-doctor <run-dir>
python -m chip_labs.cli creator-run-smoke <run-dir> --recompute --fail-on-blocked
python -m chip_labs.cli creator-run-smoke <run-dir> --fail-on-blocked --fail-on-warn
```

If recompute is not supported for the run, the bundle must say why and point to
the source-specific adapter or missing source repo.

For generated-domain matrix evidence, attach the CI artifact
`generated-creator-matrix-evidence` when available. It should contain:

- `generated-multi-seed-summary.json`
- `generated-multi-seed-summary-check.json`
- `generated-mission-status.json`
- `generated-release-gate.json`

## Swarm Packet Rules

`swarm/contribution_packet.json` must stay schema-valid against
`docs/creator_system/schemas/swarm-contribution-packet.schema.json`.

Before review, confirm:

- `evidence.tier` matches the smoke evidence tier
- `evidence.report_paths` exist
- `evidence.mean_delta` matches the saved reports
- `governance.network_publication_allowed=false`
- `governance.rollback_or_deprecation_rule` is not empty
- `anti_drift.known_limits` names the network/publication/calibration boundary

## Review Outcomes

| Outcome | Meaning | Next Step |
| --- | --- | --- |
| `local_only` | Bundle is useful only inside the current workspace. | Keep improving artifacts and reports. |
| `candidate_review` | Bundle is reviewable by other agents, but not transfer-proven. | Attach packets to a pull request or local review. |
| `transfer_supported` | Focused transfer evidence exists. | Add broader probes and promotion-gate evidence before stronger claims. |
| `network_absorbable` | Blocked in this beta. | Requires the full promotion bundle and publication authority. |

## Pull Request Shape

A review pull request should include:

- changed creator-run files
- exact commands run
- smoke, doctor, recompute, and strict-smoke verdicts
- generated matrix artifact link if relevant
- local Swarm packet path
- evidence tier and forbidden claims
- rollback or deprecation rule
- note that product runtime controls remain read-only

## Spark Swarm Handoff Text

Use this handoff in review packets or pull requests:

```text
This creator-system bundle is prepared for Spark Swarm review as local evidence.
It is not network absorption. The local Swarm packet is schema-valid, the
weakest supported evidence tier is <tier>, and network_absorbable remains false.
Do not publish or absorb this bundle until multi-seed validation,
human/operator calibration, privacy review, rollback review, publication
approval, product runtime review, and publication authority all pass.
```
