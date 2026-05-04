# Spark Creator System Beta Release Readiness Checklist

Use this checklist before announcing the creator-system beta to technical users
or handing it to Spark agents as a repo-local creator workflow.

## Release Boundary

- [x] Release type is technical beta, not network publication.
- [x] `network_absorbable` remains blocked.
- [x] Product runtime wiring remains deferred.
- [x] Public `spark-creator` extraction remains deferred.
- [x] Startup YC remains `transfer_supported`, not `network_absorbable`.

## Fresh Clone Install

- [x] Fresh clone succeeds.
- [x] `python -m pip install -e .` succeeds.
- [x] `chip-labs --help` shows the console entrypoint.
- [x] `chip-labs creator-run-template-check --fail-on-blocked` passes.
- [x] `chip-labs creator-system-beta-check --fail-on-blocked` passes.
- [x] `chip-labs creator-system-release-evidence --fail-on-blocked` exists for
  clean-checkout release evidence packets.
- [x] `chip-labs creator-system-production-readiness --fail-on-blocked` exists
  for the honest 100% repo/user beta and creator-system standard readiness
  packet, while the network publication track remains blocked.
- [x] Creator System CI uploads `creator-system-release-evidence` as a workflow
  artifact for clean pushed commits.
- [x] Creator System CI uploads `creator-system-production-readiness` as a workflow
  artifact for clean pushed commits.
- [x] Strict Startup YC saved-evidence smoke passes.

Verified on 2026-05-04 from clean temp checkouts at
`C:\Users\USER\AppData\Local\Temp\spark-domain-chip-labs-release-smoke-20260504162044`
and
`C:\Users\USER\AppData\Local\Temp\spark-domain-chip-labs-beta-check-20260504190038`.
The second checkout used an isolated virtual environment and passed
`chip-labs creator-system-beta-check --fail-on-blocked`.
Latest fresh clone plus isolated virtualenv verification also passed on
2026-05-04 from
`C:\Users\USER\AppData\Local\Temp\spark-domain-chip-labs-beta-fresh-20260504223056`;
that run included the Startup YC production-gate workbench beta subcheck.

## Creator-Run Proof

- [x] `creator-run-init` exists and writes a scaffold.
- [x] `creator-run-smoke` distinguishes blocked, prototype, baseline-ready, and
  Swarm-packet-ready states.
- [x] `creator-run-doctor` returns repair guidance.
- [x] Generator acceptance creates domain chip, benchmark pack, specialization
  path, autoloop policy, and Swarm packet artifacts from briefs.
- [x] Generated multi-domain matrix has CI coverage.
- [x] Manual generated multi-seed matrix workflow dispatch passed on
  2026-05-04 with `36/36` runs and `network_absorbable=false`.
- [x] Extended local generated matrix passed on 2026-05-04 with `54/54`
  runs, `check=pass`, and `network_absorbable=false`.
- [x] Creator-system CI enforces full `src/chip_labs` and `tests` ruff lint on
  relevant pushes and pull requests.

## Evidence And Safety

- [x] Saved evidence is separated from recomputed evidence.
- [x] Startup YC external provenance packets pin source hashes.
- [x] Startup YC network-absorption review has a saved blocked fixture and CI
  recomputes it before any stronger release claim.
- [x] Local beta readiness aggregate proves usable local creator workflows while
  keeping stronger release gates blocked.
- [x] Local beta readiness aggregate now includes the fresh Startup YC
  production-gate workbench rehearsal.
- [x] Broad-transfer aggregate counts are checked against row deltas.
- [x] Tool-operation checks block protected commands, missing postconditions,
  unsafe secrets, and rollback-less failures.
- [x] MiroFish provider adapters forbid live credentials and live provider calls
  in this repo-local contract.
- [x] MiroFish outcome calibration blocks insufficient or vanity-only real
  outcome rows as `inconclusive`.

## Documentation

- [x] Root README points users to the creator-system beta quickstart.
- [x] Creator-system README lists executable commands.
- [x] Release artifact states tag, evidence, workspace handling, non-goals, and
  next production gates.
- [x] User quickstart explains install, first run, smoke, doctor, generator
  matrix, Startup YC validation, and evidence tiers.
- [x] Public repo split decision is documented.
- [x] Known non-goals are visible.

## Release Handling

- [x] Release tag selected: `creator-system-beta-2026-05-04`.
- [x] Tag target is the clean pushed `main` commit after CI, not the dirty local
  working tree.
- [x] Unrelated modified and untracked research files remain untouched and
  unstaged.

## Pre-Release Commands

```bash
python -m ruff check src/chip_labs tests
python -m pytest tests/test_creator_mission_adapter.py tests/test_creator_system_docs.py tests/test_startup_yc_operator_validation.py tests/test_tool_operation.py tests/test_artifact_quality.py tests/test_mirofish_content_simulation.py tests/test_operator_review.py tests/test_creator_generator_acceptance.py tests/test_creator_run.py tests/test_creator_run_examples.py tests/test_retrieval_memory.py -q
chip-labs creator-run-template-check --fail-on-blocked
chip-labs creator-system-beta-check --fail-on-blocked
chip-labs creator-system-release-evidence --fail-on-blocked --output /tmp/creator-system-release-evidence.json
chip-labs creator-system-production-readiness --fail-on-blocked --output /tmp/creator-system-production-readiness.json
chip-labs creator-run-smoke docs/creator_system/examples/startup-yc-creator-run --fail-on-blocked --fail-on-warn
```

## Remaining Before A Stronger Release

- Do not upgrade claims to `network_absorbable` without the full promotion gate
  bundle.
- Decide whether to extract a separate public `spark-creator` repo after schema,
  provenance, transfer evidence, and product read-only contracts stabilize.
- Review live product runtime wiring separately before exposing creator controls
  in Builder, Telegram, Spawner, Canvas, or Kanban.
- Run `creator-release-gate` with generated multi-seed, Startup YC review, and
  product runtime review evidence before considering any stronger release claim.
