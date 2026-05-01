# Product Surface Consumer Branches - 2026-05-01

## Purpose

This ledger records product-side branches that consume
`adaptive_creator_loop.creator_mission_status.v1` as a read-only packet.

These branches prove that Builder, Telegram, Spawner, Canvas, and Kanban can
share one canonical creator-system status shape without inventing verdicts,
evidence tiers, publication state, or network absorption.

## Branches

| Repo | Branch | Commit | Proof |
| --- | --- | --- | --- |
| `spark-intelligence-builder` | `codex/spark-live-wiki-answer-builder` | `3295f15` | Adds `validate_creator_mission_status` and `summarize_creator_mission_status`; rejects `publication.network_absorbable`; validates all read-only surface adapters. |
| `spawner-ui` | `codex/creator-mission-status-spawner` | `cbc9d52` | Adds `creatorMissionStatusProjection`; rejects executable Spawner adapters, Canvas artifact edits, Kanban verdict mutation, and network absorption. |
| `spark-canvas` | `codex/creator-mission-status-canvas` | `5a41b63` | Adds `creatorMissionStatusToCanvasGraph`; rejects Canvas artifact editing and network absorption. |
| `spark-telegram-bot` | `codex/spark-live-wiki-answer-telegram` | `79b43b9` | Adds `formatCreatorMissionStatusForTelegram`; keeps publication blockers visible and rejects secret-paste or network-absorption claims. |

## Verification

Builder:

```bash
python -m pytest tests/test_creator_intent.py -q
python -m ruff check src/spark_intelligence/creator/contracts.py tests/test_creator_intent.py
```

Spawner UI:

```bash
npm run test:run -- src/lib/server/creator-mission.test.ts
npm run check
```

Spark Canvas:

```bash
npm run typecheck
```

Spark Telegram Bot:

```bash
node node_modules/ts-node/dist/bin.js tests/creatorMissionStatus.test.ts
npm run build
node scripts/run-tests.cjs
```

## Still Deferred

- Product branches are not merged here.
- Telegram natural-language creator routing is still deferred.
- Spawner runtime mission execution for creator runs is still deferred.
- Canvas/Kanban rendering is still a read-only contract/projection, not a full
  visible product workflow.
- `ready_for_swarm_packet` remains a review state, not `network_absorbable`.
- Startup YC remains `transfer_supported` until multi-seed validation,
  human/operator calibration, privacy review, rollback review, and publication
  approval are complete.
