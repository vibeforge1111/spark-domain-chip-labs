# Product Surface Read-Only Adapters

## Purpose

Phase 7 starts with a read-only adapter contract. Builder, Telegram, Spawner,
Canvas, and Kanban can display creator-system state, but they must not invent
verdicts, evidence tiers, evidence modes, publication readiness, or network
absorption.

The canonical source of truth remains:

- `creator-run-smoke`
- `creator-run-doctor`
- `tool-operation-check`
- `artifact-quality-score` / `artifact-quality-benchmark`
- `mirofish-content-route`
- `retrieval-memory-check`
- Startup YC validation packets

## Command

```bash
python -m chip_labs.cli creator-mission-status \
  --smoke reports/smoke.json \
  --doctor reports/doctor.json \
  --startup-validation docs/creator_system/examples/startup-yc-operator-validation/validation_plan.json \
  --mission-id creator-mission-001 \
  --output reports/creator-mission-status.json
```

The command only reads packet files and writes one status packet. It does not run
benchmarks, execute product actions, publish to Swarm, push to GitHub, or mutate
mission state.

## Surface Packets

The adapter emits:

- `builder`: handoff fields for Builder, including canonical verdict,
  evidence tier, evidence mode, missing paths, blockers, and recommended next
  command.
- `telegram`: a short user-facing summary that keeps publication warnings
  visible, names saved vs recomputed evidence mode, and never asks for
  token-paste workflows.
- `spawner`: read-only mission trace fields for status display, including
  evidence mode.
- `canvas`: artifact and validation graph nodes derived from source packets,
  including evidence mode on the creator-mission node.
- `kanban`: read-only columns derived from canonical status, including evidence
  mode on the mission card.

## Hard Boundaries

- Product surfaces must render `blocked`, warnings, missing gates, and claim
  boundaries.
- Product surfaces must preserve `evidence_mode` (`saved` vs `recomputed`)
  instead of parsing raw smoke packets independently.
- Product surfaces must not convert `ready_for_swarm_packet` into
  `network_absorbable`.
- Product surfaces must not allow `swarm_shared` until multi-seed validation,
  human/operator calibration, privacy review, rollback review, and publication
  approval pass.
- Product surfaces must not hide that Startup YC is currently
  `transfer_supported`.
- Product surfaces must not use stdout, summaries, chat residue, or route state
  as replacement evidence.

## Phase 7 Completion Gate

Phase 7 is not complete until downstream repos consume this packet directly and
tests prove they preserve the read-only boundary. This repo now provides the
contract and local adapter; product runtime wiring belongs in the product repos.
