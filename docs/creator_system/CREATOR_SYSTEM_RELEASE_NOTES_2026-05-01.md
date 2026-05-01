# Creator System Release Notes - 2026-05-01

## Shipped In This Continuation

- Generator proof domains now cover artifact quality, safe tool operation,
  MiroFish content simulation, doctor security, Startup YC operator validation,
  and retrieval-memory boundaries.
- Tool operation checks replay blocked smoke, stale recompute evidence, missing
  artifacts, and unsafe secret-handling requests with rollback reports.
- `creator-run-doctor --recompute` emits repair replay and quarantine metadata
  for stale evidence and unsafe packet claims.
- Startup YC has a validation pack with held-out founder-advice cases,
  multi-seed requirements, calibration gates, privacy review, rollback review,
  and publication approval gates.
- Retrieval memory has a local contract and fixtures for correct prior
  decisions, stale memory, contradicted memory, residue contamination, and
  unreviewed network-shareable context.
- `creator-mission-status` provides a read-only product adapter packet for
  Builder, Telegram, Spawner, Canvas, and Kanban without wiring runtime
  publication controls.
- The README now includes current claim levels and an executable command index.
- Creator-system CI now runs focused lint, proof-domain tests, strict Startup YC
  smoke, and template checks on relevant pushes and pull requests.

## Current Claim Boundary

- Startup YC remains `transfer_supported`, not `network_absorbable`.
- Generated proof domains remain local or `candidate_review` unless a stronger
  evidence tier is explicitly proven.
- Product runtime wiring remains deferred. Builder, Telegram, Spawner, Canvas,
  and Kanban should consume `creator-mission-status`, not invent independent
  truth.
- Network absorption remains blocked until multi-seed validation,
  human/operator calibration, privacy review, rollback review, and publication
  approval are complete.

## Verification

```bash
python -m pytest tests/test_retrieval_memory.py tests/test_creator_system_docs.py tests/test_startup_yc_operator_validation.py tests/test_tool_operation.py tests/test_artifact_quality.py tests/test_mirofish_content_simulation.py tests/test_creator_generator_acceptance.py tests/test_creator_run.py tests/test_creator_run_examples.py -q
python -m chip_labs.cli creator-run-smoke docs/creator_system/examples/startup-yc-creator-run --fail-on-blocked --fail-on-warn
python -m chip_labs.cli creator-run-template-check --fail-on-blocked
```

Latest focused creator-system suite result before CI push: `85 passed`.
