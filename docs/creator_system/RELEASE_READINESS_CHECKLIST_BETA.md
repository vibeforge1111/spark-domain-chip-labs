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

- [ ] Fresh clone succeeds.
- [ ] `python -m pip install -e .` succeeds.
- [ ] `chip-labs --help` shows the console entrypoint.
- [ ] `chip-labs creator-run-template-check --fail-on-blocked` passes.
- [ ] Strict Startup YC saved-evidence smoke passes.

## Creator-Run Proof

- [x] `creator-run-init` exists and writes a scaffold.
- [x] `creator-run-smoke` distinguishes blocked, prototype, baseline-ready, and
  Swarm-packet-ready states.
- [x] `creator-run-doctor` returns repair guidance.
- [x] Generator acceptance creates domain chip, benchmark pack, specialization
  path, autoloop policy, and Swarm packet artifacts from briefs.
- [x] Generated multi-domain matrix has CI coverage.

## Evidence And Safety

- [x] Saved evidence is separated from recomputed evidence.
- [x] Startup YC external provenance packets pin source hashes.
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
- [x] User quickstart explains install, first run, smoke, doctor, generator
  matrix, Startup YC validation, and evidence tiers.
- [x] Public repo split decision is documented.
- [x] Known non-goals are visible.

## Pre-Release Commands

```bash
python -m ruff check src/chip_labs tests
python -m pytest tests/test_creator_mission_adapter.py tests/test_creator_system_docs.py tests/test_startup_yc_operator_validation.py tests/test_tool_operation.py tests/test_artifact_quality.py tests/test_mirofish_content_simulation.py tests/test_operator_review.py tests/test_creator_generator_acceptance.py tests/test_creator_run.py tests/test_creator_run_examples.py tests/test_retrieval_memory.py -q
chip-labs creator-run-template-check --fail-on-blocked
chip-labs creator-run-smoke docs/creator_system/examples/startup-yc-creator-run --fail-on-blocked --fail-on-warn
```

## Remaining Before A Stronger Release

- Replace the remaining unchecked fresh-clone boxes above with a dated passing
  verification note.
- Decide how to handle unrelated local/untracked research files before tagging.
- Add a stable release tag after CI passes on the release commit.
- Do not upgrade claims to `network_absorbable` without the full promotion gate
  bundle.
