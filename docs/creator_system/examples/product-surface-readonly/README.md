# Product Surface Read-Only Fixture

This fixture is the canonical saved example for product surfaces consuming
`adaptive_creator_loop.creator_mission_status.v1`.

Source reports:

- `startup-yc-smoke.json`
- `startup-yc-doctor.json`
- `../startup-yc-operator-validation/validation_plan.json`

Derived packet:

- `startup-yc-mission-status.json`

The derived packet requests `swarm_shared` display mode to prove that product
surfaces keep publication blockers visible. It remains read-only:

- `canonical.verdict` is `ready_for_swarm_packet`.
- `canonical.evidence_tier` is `transfer_supported`.
- `canonical.stage_status` is `review_required`.
- `publication.swarm_shared_allowed` is `false`.
- `publication.network_absorbable` is `false`.
- Builder, Telegram, Spawner, Canvas, and Kanban adapters all expose read-only
  capability flags.

Regenerate with:

```bash
python -m chip_labs.cli creator-run-smoke docs/creator_system/examples/startup-yc-creator-run --fail-on-blocked --fail-on-warn --output docs/creator_system/examples/product-surface-readonly/startup-yc-smoke.json
python -m chip_labs.cli creator-run-doctor docs/creator_system/examples/startup-yc-creator-run --output docs/creator_system/examples/product-surface-readonly/startup-yc-doctor.json
python -m chip_labs.cli creator-mission-status --smoke docs/creator_system/examples/product-surface-readonly/startup-yc-smoke.json --doctor docs/creator_system/examples/product-surface-readonly/startup-yc-doctor.json --startup-validation docs/creator_system/examples/startup-yc-operator-validation/validation_plan.json --publish-mode swarm_shared --mission-id startup-yc-product-readonly --output docs/creator_system/examples/product-surface-readonly/startup-yc-mission-status.json
```
