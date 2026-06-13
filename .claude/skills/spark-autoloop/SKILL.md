---
name: spark-autoloop
description: Turn any domain, job, tool, or workflow into a self-improving AutoLoop using Spark Domain Chip Labs. Use when the user wants a domain chip, benchmark pack, specialization path, or autoloop policy, or says "make Spark good at X", "build an autoloop for X", "make X self-improving", "create a self-improving loop around X".
---

# Spark AutoLoop Builder

You are about to build a **creator run**: a folder of artifacts that turns one capability into a measured, self-improving loop.

- **Domain chip** = the expertise (doctrine, decision rules, failure modes)
- **Benchmark pack** = the proof (cases, held-out cases, traps, scoring rubric)
- **Autoloop policy** = the safety contract for self-improvement
- **Reports + evidence ladder** = honest claims about what actually improved

Division of labor: **you execute the improvement loop** (author content, run cases, score, keep or revert). The `chip-labs` CLI scaffolds and gates. The human approves at review boundaries.

Detailed artifact shapes live in `reference.md` and the loop procedure in `loop-protocol.md`, both in this skill's directory. Read them when you reach Steps 3-10.

## Ground rules (non-negotiable)

1. The CLI is the source of truth. If docs and CLI disagree, trust the CLI.
2. `network_publication_allowed` stays `false` everywhere. Everything is local-first.
3. Missing proof means **unproven**. Never report "probably improved".
4. The benchmark is frozen during the loop: never edit expected answers, weights, traps, or the rubric to make a candidate look better. Benchmark changes happen in a separate pass with their own review.
5. Never write secrets, tokens, chat logs, or personal identifiers into run artifacts.
6. Do not use the `chip-labs autoloop` subcommand as evidence of quality. It is a structural scaffolder that pads stub files to raise its own v1 rubric score. Semantic improvement is your job, via Steps 9-10.
7. Hard cap: **8 autonomous improvement rounds**, then stop for human review.

## Step 0 - Preflight

1. Locate the lab repo: `$env:SPARK_CHIP_LABS_DIR` if set, else `$env:USERPROFILE\Desktop\spark-domain-chip-labs`, else `git clone https://github.com/vibeforge1111/spark-domain-chip-labs.git`.
2. Invoke the CLI as `python -m chip_labs.cli` (the bare `chip-labs` exe is usually not on PATH). If the module is missing, run `python -m pip install -e <repo-root>` (the package has zero runtime dependencies).
3. Health check: `python -m chip_labs.cli creator-run-template-check --fail-on-blocked`. Expect verdict `pass`. If it fails, stop and report; do not build on broken templates.

## Step 1 - Interview the user (4 questions)

Ask, then confirm your restatement before scaffolding:

1. **Domain**: what job, tool, or workflow? Narrow it to ONE capability. Good first scopes: one task, one tool operation, one content decision, one recurring failure class. "Make me better at marketing" is too broad; "score my X post hooks before publishing" is right.
2. **Success**: what measurable behavior counts as success? This becomes the benchmark target and the keep condition.
3. **Mutation surface**: what may the loop change? (doctrine wording, prompts, checklists, scripts, configs.)
4. **Frozen + traps**: what must never change, and what known mistakes should become trap cases?

## Step 2 - Scaffold the run

Pick the output directory first. If the domain material is private (it usually is), put the run OUTSIDE the lab repo, for example `<user-project>\creator-runs\<slug>` or `$env:USERPROFILE\spark-creator-runs\<slug>`. The lab repo is public and its `runs/` folder is not gitignored.

```
python -m chip_labs.cli creator-run-init --output-dir <run-dir> --domain "<domain>" --goal "<plain-language goal>" --source-channel local
```

`--output-dir` IS the run directory (no subdirectory gets nested inside it). This writes 6 root files (creator-intent.json, adapter-map.json, created-artifact-manifest.json, creator-run-summary.md, swarm-contribution-packet.json, standard-change-proposal.md) and 6 empty dirs (domain-chip, specialization-path, benchmark, autoloop, reports, swarm). The run id `creator-run-YYYY-MM-DD-<slug>` is metadata inside the files.

## Step 3 - Fill intent, adapters, manifest

Fill from the interview (exact required fields in `reference.md`):

- `creator-intent.json`: domain, goal, privacy boundary, success criteria. `constraints.network_publication_allowed` must be exactly `false`.
- `adapter-map.json`: the 6 adapter sections (domain, benchmark, tool, autoloop, absorption, swarm).
- `created-artifact-manifest.json`: your live progress tracker. Update statuses `planned -> created -> validated` as you go.

## Step 4 - Build the domain chip (the expertise)

Write `domain-chip/chip.manifest.json`, `domain-chip/doctrine.md`, `domain-chip/scoring_hooks.json`. Copy the manifest and hooks shapes from the worked example at `docs/creator_system/examples/startup-yc-creator-run/domain-chip/` (their internals are not gate-checked, so match the example rather than inventing).

The doctrine is the heart: operating principles, decision rules, known failure modes, and explicit refusals, written from the user's real knowledge. Interview them where it is thin. Build the smallest chip that can improve the target capability; do not write an encyclopedia.

## Step 5 - Build the benchmark pack (the proof)

Write `benchmark/manifest.json`, `benchmark/cases.jsonl`, `benchmark/traps.jsonl`, `benchmark/scoring_rubric.md`.

- Case mix minimum: **5 development + 5 held-out + 3 adversarial/trap + 1 no-op regression**. Smaller packs are fine but the run must then claim only `prototype`.
- Pick the benchmark family that fits the domain. Recommended starters: `fixed_case_rubric` (advice, content, decisions), `tool_operation` (verifiable commands with a verification step), `artifact_quality` (docs, PRs, designs), `retrieval_memory`, `simulator`. The schema also allows adversarial, longitudinal, and collective.
- Honesty rules: the benchmark must be harder to game than the mutation surface. Held-out cases are never shown to the mutation step. Traps encode the user's "never do this" answers.

## Step 6 - Build the specialization path

Write `specialization-path/path.manifest.json` and `specialization-path/absorption_bundle.md`: how a fresh agent loads the chip, practices, receives feedback, and what it may safely share. This is what makes the loop transferable instead of personal.

## Step 7 - Write the autoloop policy (the safety contract)

Write `autoloop/policy.json` (schema `spark-autoloop-policy.v1`), `autoloop/mutation_surface.md`, `autoloop/stop_conditions.md`.

Gate-required non-empty: `loop_key`, `target_capability`, `benchmark_manifest`, `keep_condition`, `rollback_condition`, `promotion_condition`, plus `mutation_surface` (list), `lineage_required: true`, `network_publication_allowed: false`. Also set `max_rounds_before_review` (template default 8; the CLI does not validate it, the 8-round cap is this skill's rule and you enforce it) and align `autoloop_adapter.max_rounds` in adapter-map.json to the same number (the scaffold defaults it to 3). Frozen surfaces always include: benchmark weights, success metrics, trap expected outcomes, privacy boundary, network publication gate.

## Step 8 - Gate with smoke + doctor

```
python -m chip_labs.cli creator-run-smoke <run-dir>
```

| Verdict | Meaning | Next action |
| --- | --- | --- |
| `blocked` | Schema or required field failed | `python -m chip_labs.cli creator-run-doctor <run-dir>` and fix |
| `prototype` | Core artifacts missing (smoke lists exact `missing_paths`) | Fill them, rerun smoke |
| `ready_for_baseline` | Artifacts complete, reports missing | Proceed to Step 9 |
| `ready_for_swarm_packet` | Reports and packet exist | Step 11 review |

Rerun smoke after each artifact group. Know what the gate actually checks: root files and policy.json are schema-validated, but doctrine, cases, traps, rubric, and hooks are existence-checked only. A green smoke proves structure, not content quality; content quality is your job. Doctor is the repair tool for `blocked` verdicts plus a good final sanity pass on clean runs. Do not run a baseline or claim benchmark evidence before the benchmark artifacts exist.

## Step 9 - Baseline

Run every benchmark case against the baseline: the agent or workflow WITHOUT the chip. Score each case with the rubric. Write `reports/baseline.json` (shape in `reference.md`) with `provenance.input_hashes` (path -> sha256, at minimum `benchmark/cases.jsonl` and `domain-chip/scoring_hooks.json`). Hand-scored runs gate with plain smoke + doctor; never use `--recompute`, which is reserved for machine-recomputable provenance sources.

## Step 10 - Run the AutoLoop

Follow `loop-protocol.md` exactly. One round = one narrow hypothesis-driven mutation inside the mutation surface, re-scored against development + held-out + trap cases, kept only if ALL keep conditions pass, reverted otherwise, and logged either way. Stop at a stop condition or at 8 rounds. Zero keeps triggers the 5-point diagnosis, not a shrug. Write `reports/candidate.json` and update `reports/creator_run_summary.md`.

## Step 9b - Calibrate against reality (the tier-raising step)

A self-authored benchmark caps the run at `benchmark_signal` no matter how good the delta looks (chip-labs `BENCHMARK_AUTHORSHIP_AND_EVIDENCE_EXPIRY.md`). To claim `candidate_review` or higher you need an oracle grounded in **measured outcomes**, not your own expected answers. Do this when the domain has any real outcome signal (engagement, pass/fail, revenue, conversion, downstream acceptance).

1. **Sample real cases with measured outcomes.** Use `assets/calibration_sampler.py` as a starting point: pull N items per outcome band from your real data, exclude anything already used, anonymize identifiers. Aim for 100+ items and balanced bands.
2. **Make the headline metric deterministic.** Map verdict to the measured band; compute band accuracy and Spearman vs the measured outcome with `assets/calibration_metrics.py`. **No LLM judge in the headline number.**
3. **Multi-seed, always.** Run 3+ seeds per arm (vary item order), majority-vote the verdicts, and bootstrap the metric difference between arms. A single seed can sign-flip a small-n delta; I have watched it happen.
4. **Compare arms that isolate the cause.** At minimum baseline (no doctrine) vs doctrine. Add a context arm if the domain has per-subject context.
5. **Report the honest ceiling.** If the doctrine beats baseline but the absolute metric is weak, say both. Calibration that fails to clear a useful absolute bar is still a real, publishable result; it tells you the bottleneck moved (often to an upstream judge or to missing context).

If a hybrid (doctrine strategy gate + an external outcome predictor) is in play, see `assets/hybrid_combiner.py`. Validate the external predictor on YOUR fresh sample before trusting it; documented accuracy drifts.

## Step 11 - Evidence ladder + honest claim

1. Fill `reports/evidence_ladder.md` (gate rows in `reference.md`).
2. Claim only the **weakest passing gate**: `prototype` -> `benchmark_signal` -> `focused_pattern` -> `candidate_review` -> `transfer_supported`. `network_absorbable` stays blocked by default.
3. Final gates: `python -m chip_labs.cli creator-run-smoke <run-dir> --fail-on-blocked`, then `python -m chip_labs.cli creator-run-doctor <run-dir> --fail-on-blocked`, then a strict `python -m chip_labs.cli creator-run-smoke <run-dir> --fail-on-blocked --fail-on-warn` before sharing anything (`--fail-on-warn` exists on smoke only).
4. Fill `creator-run-summary.md` with verdict `promote | defer | reject | local-only` and present the result to the user: what changed, what improved, by how much, what remains unproven, and how to roll it back.

## Running it again later

The loop is reusable: rerun smoke, then continue rounds from the latest kept candidate. Each pass is capped at 8 rounds before human review. To make it recurring, schedule "continue the autoloop in <run-dir>" as a periodic task; the artifacts carry all state.
