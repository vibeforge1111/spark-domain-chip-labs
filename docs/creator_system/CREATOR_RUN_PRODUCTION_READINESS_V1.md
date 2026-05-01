# Creator Run Production Readiness V1

This document freezes the first shippable creator-run contract for Spark creator systems.

The goal is a stable local interface that Telegram, Spark Intelligence Builder, Spawner UI, Canvas/Kanban, local CLIs, and future creator repos can call without guessing how to interpret a partially built domain chip, benchmark, specialization path, autoloop, or Swarm packet.

## Shippable Interface

Initialize a creator run:

```bash
python -m chip_labs.cli creator-run-init \
  --output-dir runs/<run-name> \
  --domain "<domain or tool>" \
  --goal "<plain-language user goal>" \
  --source-channel local
```

Validate a creator run:

```bash
python -m chip_labs.cli creator-run-smoke runs/<run-name>
```

Bot or CI validation:

```bash
python -m chip_labs.cli creator-run-smoke runs/<run-name> --fail-on-blocked
```

Strict publication validation:

```bash
python -m chip_labs.cli creator-run-smoke runs/<run-name> --fail-on-blocked --fail-on-warn
```

## Smoke Result Contract

`creator-run-smoke` emits:

```json
{
  "schema_version": "adaptive_creator_loop.smoke_result.v1",
  "run_dir": "runs/example",
  "verdict": "prototype",
  "evidence_tier": "prototype",
  "status_counts": {
    "pass": 0,
    "warn": 0,
    "fail": 0
  },
  "blocking_checks": [],
  "warning_checks": [],
  "automation": {
    "blocked": false,
    "ci_exit_code": 0,
    "recommended_next_command": "Fill missing artifact paths, then rerun creator-run-smoke."
  },
  "checks": [],
  "missing_paths": [],
  "next_actions": []
}
```

Callers should treat `schema_version` as the compatibility anchor. If the schema changes, the version must change.

## Verdict Semantics

| Verdict | Meaning | Caller behavior |
| --- | --- | --- |
| `blocked` | Required schema, fields, evidence, or claim support failed. | Stop the flow and show `blocking_checks`. |
| `prototype` | Intent and adapters exist, but core artifacts are missing. | Route user/agent to artifact creation. |
| `ready_for_baseline` | Core artifacts exist; benchmark reports are missing. | Run baseline/candidate/absorption tasks. |
| `ready_for_swarm_packet` | Reports and Swarm packet exist. | Review provenance, privacy, rollback, traps, and claim boundaries before publication. |

Warnings do not block workspace iteration. Warnings should block strict publication if `--fail-on-warn` is used.

## Evidence Promotion Rules

The creator-run smoke gate enforces conservative evidence claims:

- `candidate_review` requires positive candidate delta, baseline beat, positive absorption delta, trap coverage, provenance, and rollback.
- `transfer_supported` requires a positive transfer report and matching Swarm packet transfer evidence.
- `broad_transfer_probe.json`, when present, defines the claim boundary.
- Negative broad transfer warns at `transfer_supported`, because focused transfer can still be useful.
- Negative broad transfer blocks `network_absorbable` and `standard_update`.

## Integration Rules

Telegram should:

- collect the user goal
- call `creator-run-init`
- show the run id and next action
- call `creator-run-smoke` after each build step

Spark Intelligence Builder should:

- own artifact generation and benchmark execution
- read `missing_paths`, `blocking_checks`, and `automation.recommended_next_command`
- refuse promotion when `automation.blocked` is true

Spawner UI / Canvas / Kanban should:

- map `verdict` to board state
- show warnings separately from blockers
- use `--fail-on-warn` only at publication or review gates

Spark Swarm should:

- only absorb packets after smoke passes
- require strict review for `network_absorbable`
- keep focused transfer claims separate from broad mastery claims

## Current Reference Fixture

The Startup YC fixture is the reference contract test:

```bash
python -m chip_labs.cli creator-run-smoke docs/creator_system/examples/startup-yc-creator-run
```

Current expected state:

- verdict: `ready_for_swarm_packet`
- evidence tier: `transfer_supported`
- blockers: none
- warnings: `broad_transfer_delta`

The warning is intentional. Startup YC has focused transfer support, but broad transfer is not yet proven.

## Ship Gate For V1

Before shipping changes to this contract:

1. Run `python -m pytest tests/test_creator_run.py tests/test_creator_run_examples.py -q`.
2. Run smoke on the Startup YC fixture.
3. Run `creator-run-smoke --fail-on-blocked` on the fixture.
4. Confirm the fixture still warns, rather than fails, on negative broad transfer.
5. Update this document if CLI flags, result fields, verdicts, or promotion semantics change.
