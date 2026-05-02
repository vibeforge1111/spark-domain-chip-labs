# Product Surface Read-Only Fixture

This fixture is the canonical saved example for product surfaces consuming
`adaptive_creator_loop.creator_mission_status.v1`.

Source reports:

- `startup-yc-smoke.json`
- `startup-yc-doctor.json`
- `../artifact-quality/good_design_pr.report.json`
- `../mirofish-content/route-invoke.json`
- `../retrieval-memory/correct_prior_decision.check.json`
- `../startup-yc-operator-validation/validation_plan.json`

Derived packet:

- `startup-yc-mission-status.json`

The derived packet requests `swarm_shared` display mode to prove that product
surfaces keep publication blockers visible. It remains read-only:

- `canonical.verdict` is `ready_for_swarm_packet`.
- `canonical.evidence_tier` is `transfer_supported`.
- `canonical.stage_status` is `review_required`.
- `source_packets.artifact_quality` references a local design/PR review report
  with `artifact_quality local review only` claim boundaries.
- `source_packets.content_route` references a local MiroFish route packet with
  `candidate_review` claim boundaries.
- `source_packets.retrieval_memory` references a local retrieval-memory check
  with `network_absorbable=false`.
- `publication.swarm_shared_allowed` is `false`.
- `publication.network_absorbable` is `false`.
- Builder, Telegram, Spawner, Canvas, and Kanban adapters all expose read-only
  capability flags.

Regenerate with:

```bash
python -m chip_labs.cli creator-run-smoke docs/creator_system/examples/startup-yc-creator-run --fail-on-blocked --fail-on-warn --output docs/creator_system/examples/product-surface-readonly/startup-yc-smoke.json
python -m chip_labs.cli creator-run-doctor docs/creator_system/examples/startup-yc-creator-run --output docs/creator_system/examples/product-surface-readonly/startup-yc-doctor.json
python -m chip_labs.cli artifact-quality-score --input docs/creator_system/examples/artifact-quality/good_design_pr.md --artifact-kind pr_writeup --output docs/creator_system/examples/artifact-quality/good_design_pr.report.json --markdown-output docs/creator_system/examples/artifact-quality/good_design_pr.report.md
python -m chip_labs.cli retrieval-memory-check --input docs/creator_system/examples/retrieval-memory/correct_prior_decision.json --output docs/creator_system/examples/retrieval-memory/correct_prior_decision.check.json
python -m chip_labs.cli creator-mission-status --smoke docs/creator_system/examples/product-surface-readonly/startup-yc-smoke.json --doctor docs/creator_system/examples/product-surface-readonly/startup-yc-doctor.json --startup-validation docs/creator_system/examples/startup-yc-operator-validation/validation_plan.json --artifact-quality docs/creator_system/examples/artifact-quality/good_design_pr.report.json --content-route docs/creator_system/examples/mirofish-content/route-invoke.json --retrieval-memory docs/creator_system/examples/retrieval-memory/correct_prior_decision.check.json --publish-mode swarm_shared --mission-id startup-yc-product-readonly --output docs/creator_system/examples/product-surface-readonly/startup-yc-mission-status.json
```
