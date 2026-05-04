# Spark Creator Public Repo Decision

Status: defer public repo split until the creator-system contract is stable.

## Decision

Keep `spark-domain-chip-labs` as the source of truth for creator-system
standardization while the proof domains, smoke gates, schemas, and promotion
boundaries are still moving. Do not create or publish a public `spark-creator`
repo from this work yet.

## Why

- The current repo still owns the executable proof chain: generator acceptance,
  Startup YC transfer support, MiroFish content simulation, artifact quality,
  tool operation, retrieval memory, doctor/security, and mission-status packets.
- Public extraction would make versioning and provenance harder before the
  schema set settles.
- Startup YC remains `transfer_supported`, not `network_absorbable`.
- Product wiring for Builder, Telegram, Spawner, Canvas, and Kanban remains
  deferred and should consume read-only packets rather than publish runtime
  controls from a new repo.

## Split Conditions

A future public `spark-creator` repo can be reconsidered when all of these are
true:

- Creator-run schemas have a tagged compatibility version and migration notes.
- Generator acceptance, recompute/provenance, and multi-domain checks pass in CI.
- At least one non-Startup-YC proof domain reaches `transfer_supported` with
  recomputed evidence.
- Startup YC network absorption review remains blocked unless multi-seed
  validation, human/operator calibration, privacy review, rollback review, and
  publication approval have explicit pass evidence.
- Product surfaces have read-only consumer contracts and no runtime publication
  control is moved into the public repo.

## Current Action

Document the boundary here, keep building in this repo, and revisit the split
after multi-seed validation and product-surface read-only contracts are stable.
