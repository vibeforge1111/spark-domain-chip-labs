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
| SR-02 | Add a Swarm reusable creator path. | Outside contributors need one path from domain idea to review bundle. | `SWARM_REUSABLE_CREATOR_PATH.md`. | In progress. |
| SR-03 | Add contributor guidance for new creator-system domains. | New domains should follow the same evidence ladder and packet boundary. | Contributor doc linked from first-read docs. | Pending. |
| SR-04 | Define a review bundle checklist for local Swarm packets. | Swarm reviewers need required packet, evidence, provenance, and rollback fields. | Checklist in the reusable path doc. | In progress. |
| SR-05 | Add an example review bundle for a generated proof domain. | Contributors learn faster from one concrete bundle. | Example under `docs/creator_system/examples/`. | Pending. |
| SR-06 | Add a lightweight bundle shape check if examples start drifting. | Reuse should be executable, not only prose. | Focused test or CLI check for bundle docs/examples. | Pending. |
| SR-07 | Run fresh-clone verification after the next packaging change. | Public users need install proof independent from local dirty state. | Fresh-clone evidence note and clean output packet paths. | Pending. |
| SR-08 | Decide whether generated matrix JSON should become release assets. | Release consumers may need stable downloadable evidence outside CI retention. | Release asset policy, only after a new public hardening tag. | Pending. |
| SR-09 | Review unrelated docs/research/viz files as a separate slice. | Research residue should not silently become creator-system doctrine. | Curated commit, archive decision, or explicit defer note. | Pending. |
| SR-10 | Continue proof-domain improvements through executable gates only. | Swarm reuse must be earned by tests, smoke, doctor, and provenance checks. | More passing proof-domain gates and blocked unsafe claims. | Ongoing. |
| SR-11 | Keep product runtime creator controls deferred. | Builder, Telegram, Spawner, Canvas, and Kanban must not mutate creator runs yet. | Read-only mission-status consumers only. | Ongoing boundary. |
| SR-12 | Prepare a future promotion bundle for real network absorption. | `network_absorbable` requires complete approval evidence. | Multi-seed, calibration, privacy, rollback, publication, product-runtime, and authority packets. | Blocked by design. |

## Build Order

1. Make the local review bundle path explicit.
2. Add contributor guidance for new creator domains.
3. Add one example bundle from an existing generated proof domain.
4. Add the smallest executable check that prevents bundle drift.
5. Run fresh-clone verification before a new hardening package.
6. Only then decide whether the bundle artifacts belong on a public release.

## Promotion Rule

No task in this ledger may change `network_absorbable` to `true`.

The first allowed stronger claim is still gated by multi-seed validation,
human/operator calibration, privacy review, rollback review, publication
approval, product runtime review, and explicit publication authority.
