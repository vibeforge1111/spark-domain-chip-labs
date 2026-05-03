# Mission Status Evidence Mode Decision

## Summary

This design doc records the decision to preserve creator-run smoke
`evidence_mode` across mission-control views so downstream surfaces can tell
saved evidence from freshly recomputed evidence.

## Acceptance Gates

- Builder, Telegram, Spawner, Canvas, and Kanban packets include
  `evidence_mode`.
- Schema validation fails if Canvas or Kanban drop `evidence_mode`.
- The mission status report keeps `network_absorbable=false`.

## Evidence And Commands

- `python -m pytest tests/test_creator_mission_adapter.py -q` passed.
- `python -m chip_labs.cli creator-run-smoke docs/creator_system/examples/startup-yc-creator-run --recompute --fail-on-blocked` passed.
- `python -m chip_labs.cli creator-run-template-check --fail-on-blocked` passed.

## Risk Boundary

This is a read-only adapter decision. It does not grant execution authority,
publish creator packets, or prove that saved evidence is fresh.

## Rollback Plan

Revert the schema field, mission-status projections, docs, and tests if a
consumer cannot preserve the evidence-mode contract.

## Claim Boundary

Safe claim: mission-control packets can preserve evidence-mode provenance.

Do not claim: this decision proves product runtime integration or external
publication readiness.

## Mission Handoff

Owner: creator-system maintainer.

Next action: keep product runtime wiring deferred until review gates are
complete.
