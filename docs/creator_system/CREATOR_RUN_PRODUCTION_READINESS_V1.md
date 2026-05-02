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

Validate the template set:

```bash
python -m chip_labs.cli creator-run-template-check --fail-on-blocked
```

Diagnose a run and get concrete repair steps:

```bash
python -m chip_labs.cli creator-run-doctor runs/<run-name>
```

Bot or CI validation:

```bash
python -m chip_labs.cli creator-run-smoke runs/<run-name> --fail-on-blocked
```

Focused repo CI:

```bash
python -m ruff check src/chip_labs/creator_mission_adapter.py src/chip_labs/cli.py tests/test_creator_mission_adapter.py tests/test_creator_system_docs.py
python -m pytest tests/test_creator_mission_adapter.py tests/test_creator_system_docs.py tests/test_startup_yc_operator_validation.py tests/test_tool_operation.py tests/test_artifact_quality.py tests/test_mirofish_content_simulation.py tests/test_creator_generator_acceptance.py tests/test_creator_run.py tests/test_creator_run_examples.py tests/test_retrieval_memory.py -q
```

Strict publication validation:

```bash
python -m chip_labs.cli creator-run-smoke runs/<run-name> --fail-on-blocked --fail-on-warn
```

Recompute saved benchmark evidence when reports include supported provenance:

```bash
python -m chip_labs.cli creator-run-smoke runs/<run-name> --recompute --fail-on-blocked
```

For curated fixtures that reference external source repos, full recompute also
requires source-specific rerun adapters. The Startup YC adapter contract is
tracked in `STARTUP_YC_EXTERNAL_RECOMPUTE_ADAPTERS.md`.
The first partial Startup YC external check compares transfer summaries against
the `specialization-path-startup-yc` selector report when that source repo is
available.

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

## Doctor Result Contract

`creator-run-doctor` wraps the smoke result with a repair plan:

```json
{
  "schema_version": "adaptive_creator_loop.doctor_result.v1",
  "run_dir": "runs/example",
  "verdict": "prototype",
  "evidence_tier": "prototype",
  "summary": "Creator run has intent/adapters and needs core artifacts.",
  "publication_ready": false,
  "workspace_ready": true,
  "repair_steps": [],
  "smoke": {}
}
```

Use doctor output when the caller needs human-readable next steps instead of raw check names.

## Template Check Contract

`creator-run-template-check` validates that the template set still contains the fields required to scaffold a usable creator run:

```json
{
  "schema_version": "adaptive_creator_loop.template_check_result.v1",
  "template_dir": "docs/creator_system/templates/creator-run",
  "verdict": "pass",
  "status_counts": {
    "pass": 31,
    "warn": 0,
    "fail": 0
  },
  "blocking_checks": [],
  "checks": []
}
```

Run this before changing templates or asking Builder to generate new creator-run workspaces.

## Evidence Promotion Rules

The creator-run smoke gate enforces conservative evidence claims:

- Every creator run requires `created-artifact-manifest.json` with aligned `creator_run_id`, publication boundary, required artifact kinds, and valid artifact statuses.
- `candidate_review` requires positive candidate delta, baseline beat, positive absorption delta, trap coverage, provenance, and rollback.
- `transfer_supported` requires a positive transfer report and matching Swarm packet transfer evidence.
- `broad_transfer_probe.json`, when present, defines the claim boundary.
- Negative broad transfer warns at `transfer_supported`, because focused transfer can still be useful.
- Negative broad transfer blocks `network_absorbable` and `standard_update`.
- Positive broad transfer with hidden negative rows or non-positive `min_delta` warns at `transfer_supported` and blocks `network_absorbable` or `standard_update`.
- Broad-transfer probes should include `scenario_results` rows so reviewers can audit the aggregate score.
- `--recompute` requires supported report provenance and compares saved baseline, candidate, and absorption values against current benchmark source artifacts.

## Generator Acceptance Proof

The executable generator proof lives in `src/chip_labs/creator_generator.py`
and is covered by `tests/test_creator_generator_acceptance.py`.

It creates creator-run workspaces from fresh briefs in temporary clean
workspaces, then verifies:

- domain chip artifacts plus hook smoke
- benchmark pack plus baseline report
- specialization path artifacts
- autoloop policy plus one kept and one reverted simulation round
- Swarm contribution packet derived from reports
- normal smoke and recompute smoke both reach `ready_for_swarm_packet`

The current multi-family proof covers:

- artifact quality: design docs and PR writeups for mission-control handoff
- tool operation: safe local creator-run CLI operation with dry-run and verification boundaries
- simulator-heavy: MiroFish-style content simulation with persona batches, multi-RLM judges, and weak-row diagnosis
- adversarial/security: Spark doctor checks for fake evidence and unsafe promotion
- startup/founder advice: Startup YC operator guidance with bounded evidence

Generated proofs claim only `candidate_review`. They do not claim
`transfer_supported` or `network_absorbable`. Retrieval/memory proof remains
deferred until Spark's memory system is ready to plug into the benchmark flow.

## Integration Rules

These rules are the future integration contract, not a completed product-flow release.

V1 is CLI and repo based. Spark Intelligence Builder, Telegram, Spawner UI, Canvas, and Kanban should wire into this contract only when their own builder, memory, conversation, and mission-control surfaces are ready.

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
- warnings: none
- artifact manifest: present and aligned

The fixture is now backed by the Startup YC fresh validation suite:

- `12/12` fresh scenarios won
- mean scenario delta: `+0.0560`
- min scenario delta: `+0.0144`
- broad fresh-transfer probe: positive, with no negative rows

The fixture remains `transfer_supported`, not `network_absorbable`, because multi-seed validation, human/operator calibration, and publication review are still open gates.

The fixture is strict saved-evidence proof today. Full external recompute needs
the Startup Bench transfer, specialization-path absorption, broad-transfer, and
Swarm packet regeneration adapters defined in
`STARTUP_YC_EXTERNAL_RECOMPUTE_ADAPTERS.md`.
The Startup Bench transfer comparison is implemented as a partial recompute
check, but `creator-run-smoke --recompute` still blocks the fixture until the
remaining source-report adapters provide provenance for baseline, candidate, and
absorption reports.

## Ship Gate For V1

Before shipping changes to this contract:

1. Run the focused creator-system ruff command from this document.
2. Run the focused creator-system pytest command from this document.
3. Run `python -m chip_labs.cli creator-run-template-check --fail-on-blocked`.
4. Run strict smoke on the Startup YC fixture with `--fail-on-blocked --fail-on-warn`.
5. Run `creator-run-doctor` on the fixture and confirm it returns publication review next steps.
6. Confirm synthetic negative or mixed broad-transfer probes warn at `transfer_supported` and fail at `network_absorbable`.
7. Confirm `creator-mission-status` keeps product views read-only and preserves publication blockers.
8. Update this document if CLI flags, result fields, verdicts, or promotion semantics change.
