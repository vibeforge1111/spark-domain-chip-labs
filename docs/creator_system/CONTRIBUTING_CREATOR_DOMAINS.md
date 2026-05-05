# Contributing Creator-System Domains

Use this guide when proposing a new creator-system domain, benchmark pack,
specialization path, autoloop policy, or local Swarm packet.

This is for outside users and fresh Spark agents. It keeps contributions
reviewable by Spark Swarm without approving network absorption.

## Contribution Boundary

Your contribution may prove local value, `candidate_review`, or focused
`transfer_supported` evidence.

It must not claim:

- `network_absorbable=true`
- automatic Spark Swarm publication
- product runtime creator controls
- production memory promotion
- broad mastery from a narrow benchmark

## Start With One Narrow Domain

Pick one capability that can be measured:

- review a specific artifact type
- operate one local tool safely
- rank one kind of content candidate
- catch one doctor/security failure class
- improve one founder-advice scenario family
- classify one retrieval-memory lane

Avoid broad domains until one narrow benchmark passes.

## Required Files

Create or update a creator run with:

- `creator-intent.json`
- `adapter-map.json`
- `created-artifact-manifest.json`
- `domain-chip/`
- `benchmark/`
- `specialization-path/`
- `autoloop/policy.json`
- `reports/evidence_ladder.md`
- `swarm/contribution_packet.json`

If the contribution is meant for Spark Swarm review, also create a review
bundle using `SWARM_REUSABLE_CREATOR_PATH.md`.

## Required Checks

Run these before asking for review:

```bash
python -m chip_labs.cli creator-run-smoke <run-dir> --fail-on-blocked
python -m chip_labs.cli creator-run-doctor <run-dir>
python -m chip_labs.cli creator-run-smoke <run-dir> --fail-on-blocked --fail-on-warn
```

Run recompute when supported:

```bash
python -m chip_labs.cli creator-run-smoke <run-dir> --recompute --fail-on-blocked
```

If recompute is not supported, explain the source adapter or external repo that
is missing.

## Pull Request Checklist

Include:

- the domain goal and non-goals
- benchmark cases and trap cases
- smoke, doctor, strict-smoke, and recompute results
- weakest supported evidence tier
- local Swarm packet path
- rollback or deprecation rule
- known limits
- explicit `network_absorbable=false`
- statement that product runtime controls remain read-only

## Review Rule

Reviewers should reject the contribution if it:

- rewrites benchmark expectations to make a candidate win
- hides failed seeds or blocked checks
- uses conversational residue as doctrine
- lacks provenance for source evidence
- has no rollback path
- sets `network_publication_allowed=true`
- treats `ready_for_swarm_packet` as network approval

## Next Step After Review

A passing review can make the bundle easier for other agents to reuse locally.
It still cannot publish to Spark Swarm or claim `network_absorbable` until the
full promotion bundle passes.
