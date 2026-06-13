# AutoLoop Artifact Reference

Source of truth: `python -m chip_labs.cli` in spark-domain-chip-labs. Templates: `docs/creator_system/templates/creator-run/`. Schemas: `docs/creator_system/schemas/`. Worked example: `docs/creator_system/examples/startup-yc-creator-run/`.

**How to read this file.** The gates enforce two different things:
- **[gate-checked]**: smoke/doctor blocks if this is wrong. Get these exact.
- **[convention]**: smoke only checks the file EXISTS. The shape shown is this skill's recommended convention (mostly from the repo's real runs). Content quality is on you, not the gates.

## Run directory contract

```
<run-dir>/                              <- --output-dir IS the run dir (run_id is metadata, no subdir is nested)
  creator-intent.json                   [gate-checked]
  adapter-map.json                      [gate-checked]
  created-artifact-manifest.json        [gate-checked]
  creator-run-summary.md
  swarm-contribution-packet.json
  standard-change-proposal.md
  domain-chip/        chip.manifest.json, doctrine.md, scoring_hooks.json          [existence + convention]
  specialization-path/ path.manifest.json, absorption_bundle.md                    [existence + convention]
  benchmark/          manifest.json, cases.jsonl, traps.jsonl, scoring_rubric.md   [existence + convention]
  autoloop/           policy.json [gate-checked], mutation_surface.md, stop_conditions.md
  reports/            baseline.json, candidate.json, absorption_summary.json,
                      evidence_ladder.md, creator_run_summary.md
                      + transfer_summary.json (REQUIRED at transfer_supported and above)
                      + broad_transfer_probe.json (network tiers only)
  swarm/              contribution_packet.json
```

A fresh scaffold smokes as `prototype` with exactly 17 `missing_paths`: domain-chip 3, specialization-path 2, benchmark 4, autoloop 3, reports 4 (baseline, candidate, absorption_summary, creator_run_summary), swarm/contribution_packet.json. Note `ready_for_baseline` arrives while reports/* and swarm/contribution_packet.json are still missing; the CLI groups the swarm packet with reports.

## creator-intent.json (schema `adaptive_creator_loop.creator_intent.v1`) [gate-checked]

Blocking non-empty: `run_id`, `source_channel`, `domain.name`, `domain.short_slug`, `goal.plain_language_goal`, `constraints.privacy_boundary` (init pre-fills run_id and the goal). Exact-false: `constraints.network_publication_allowed`. Required: `success_criteria.minimum_evidence_tier` at or below `transfer_supported`.

Fill well: `goal.capability_to_improve`, `goal.expected_user_value`, `goal.non_goals`, `constraints.human_review_required: true`, `success_criteria.benchmark_target`, `success_criteria.trap_regression_policy: "no_new_trap_regressions"`, `success_criteria.stop_ship_conditions`.

## adapter-map.json (schema `adaptive_creator_loop.adapter_map.v1`) [gate-checked structure]

Six sections, each must be an object (check names like `tool_adapter_section`). `swarm_adapter.evidence_tier` must be in the 7-tier enum. Section contents are convention (from ADAPTIVE_CREATOR_LOOP_STANDARD.md):

- **domain_adapter**: domain_name, target_user_or_agent, capabilities, doctrine_or_operating_principles, known_failure_modes, unsafe_or_out_of_scope_claims, baseline_examples
- **benchmark_adapter**: benchmark_family, case_manifest, scoring_dimensions, baseline_command_or_protocol, candidate_command_or_protocol, trap_cases, calibration_notes, minimum_evidence_tier
- **tool_adapter**: allowed_tools, protected_tools, auth_boundary, local_vs_network_mode, dry_run_mode, verification_command, human_review_required_for
- **autoloop_adapter**: mutation_surface, frozen_surfaces, candidate_generator, keep_rule, reject_rule, max_rounds, stop_conditions, rollback_condition, lineage_log
- **absorption_adapter**: bundle_inputs, fresh_agent_protocol, held_out_cases, expected_behavior_change, score_delta_threshold, trap_regression_policy, failure_summary_template
- **swarm_adapter**: contribution_type, source_repo, commit_or_artifact_hash, evidence_tier, review_state, proposed_packet, rollback_or_deprecation_rule, privacy_and_security_notes

Watch out: the scaffolded template defaults `autoloop_adapter.max_rounds` to 3. Nothing gates adapter-map vs policy consistency, so set it to the same round cap as your policy yourself.

## created-artifact-manifest.json (schema `adaptive_creator_loop.created_artifact_manifest.v1`) [gate-checked]

`status` in {planned, created, validated, blocked}. `kind` in {domain_chip, specialization_path, benchmark_pack, autoloop_policy, absorption_bundle, swarm_packet, report, standard_change}. Required kinds present: domain_chip, specialization_path, benchmark_pack, autoloop_policy, swarm_packet. `publication_boundary` must be `local_only`.

## Domain chip + specialization path files [existence + convention]

SKILL.md Steps 4 and 6 name the files; their internal shapes are not gate-checked. Copy the shapes and `schema_version` strings from the worked example (`docs/creator_system/examples/startup-yc-creator-run/domain-chip/` and `specialization-path/`) rather than inventing your own: chip.manifest.json, scoring_hooks.json (define your scoring dimensions here; they feed provenance hashing), path.manifest.json.

## Benchmark pack [existence + convention]

Smoke checks only that the four files exist. Recommended conventions:

- `cases.jsonl` rows: `{id, lane, input, expected, dimension}` with `lane` in {development, held_out, regression, adversarial} and `dimension` matching a rubric dimension name. This is hand-scoring convention; it is NOT compatible with `--recompute`. For machine-recomputable packs use the row shape in `schemas/benchmark-case.schema.json` (case_id, case_kind, case_lane, prompt, oracle{expected_behavior, failure_mode, minimum_candidate_delta}, baseline_mutations, candidate_mutations, trap, hallucination_risk, calibration_status).
- `traps.jsonl` rows: `{id, trap, expected_rejection}` (convention; no enforced schema). In the generated-case contract traps are simply cases with `trap: true`.
- `scoring_rubric.md`: this skill recommends a `| Dimension | 0 | 1 | 2 |` anchor table because it forces anchor-based scoring with no interpolation. The template's documented alternative is `| Dimension | Weight | Why it matters | Gaming risk |`. Pick one and stay consistent.
- `manifest.json`: benchmark family, case counts per lane, scoring dimensions. Family starters: fixed_case_rubric, tool_operation, artifact_quality, retrieval_memory, simulator (schema also allows adversarial, longitudinal, collective; the value is not gate-validated).
- Case mix minimum for non-prototype claims: 5 development, 5 held-out, 3 adversarial/trap, 1 no-op regression.

## autoloop/policy.json (schema `spark-autoloop-policy.v1`) [gate-checked]

Required non-empty strings: `loop_key`, `target_capability`, `benchmark_manifest`, `keep_condition`, `rollback_condition`, `promotion_condition`. Required: `mutation_surface` (list of strings), `lineage_required: true`, `network_publication_allowed: false`.

Validated only when present: `evidence_tier_goal` must be at or below `transfer_supported` (omitting it passes smoke).

Not gate-validated but set it anyway: `max_rounds_before_review` (template default 8, worked example uses 10, schema allows any integer >= 1). The 8-round hard cap is this skill's own rule from the loop governance doctrine; you enforce it, not the CLI.

Canonical `frozen_surfaces`: benchmark_weights, success_metrics, trap_case_expected_outcomes, privacy_boundary, network_publication_gate.

Canonical `forbidden_actions`: "mutate benchmark weights to create a score gain", "remove or relabel trap cases", "publish network-absorbable packets from focused transfer evidence", "write secrets or access tokens into artifacts".

Keep `diagnosis_when_zero_keeps` as shipped in the template (5 items): report weakest component; whether candidate generation produced causal mechanisms; whether scoring is saturated; whether mutation surface is too narrow; whether benchmark cannot see the intended improvement.

## Reports [gate-checked at elevated tiers]

- `reports/baseline.json`: schema_version, `mean_score`, `case_count`, `provenance` (+ `pass_rate`, `source_report`, `mode: "no_pack"` for the `.report.baseline.v1` variant). Keep your own per-case scoring log too, but the schema fields are what get checked.
- `reports/candidate.json`: as baseline plus `mean_delta` and positive/negative/flat case counts; `mode: "validated_pack"`. Elevated tiers require `mean_delta` strictly > 0 and packet `trap_regressions <= 0`.
- `reports/absorption_summary.json`: blocking at elevated tiers: `all_modes_present: true`, `all_modes_scored: true`, `mean_validated_pack_delta` strictly > 0, `trap_band_case_count` > 0, plus schema_version and provenance. The six guardrail keys from the worked example (schema_gate, lineage_gate, complexity_gate, memory_hygiene_gate, transfer_gate, autonomy_gate) are an optional nested `guardrails` convention, not gate-checked.
- `reports/transfer_summary.json`: REQUIRED at transfer_supported and above: source, scenario_count > 0, transfer_score, baseline_score, delta, constraints_passed, and a matching `evidence.simulator_or_arena_result` in the swarm packet.
- Provenance shape: `provenance{source, input_hashes}` where `source` must be one of `creator_generator_v1`, `artifact_quality_v1`, `startup_yc_external_v1` and `input_hashes` is a non-empty path -> sha256 map. **`--recompute` only works for machine-recomputable runs with one of those sources shared across all three reports. Hand-scored runs (this skill's primary flow) gate with plain smoke + doctor, never `--recompute`.**
- Prototype-tier honesty: narrative reports (status/evidence_tier/summary backed by real test counts) are tolerated at prototype tier because reports are existence-checked there. Do not give them a made-up schema_version and do not expect them to survive elevated-tier checks.

## Evidence ladder (`reports/evidence_ladder.md`) [gate-checked at elevated tiers]

Keep the template's literal headings `## Gate Checklist`, `## Safe Claim`, `## Unsafe Claim`: the validator locates gates and claim blocks by those exact section names. Gate rows (exact names): Prototype scaffold, Baseline benchmark, Candidate benchmark, Held-out or weak-case replay, Fresh-agent absorption, Trap/adversarial coverage, Swarm packet consistency, Privacy/provenance/rollback, plus Transfer probe (transfer_supported and above) and Broad transfer probe (network tiers). Each row pass/warn/fail; Held-out may be warn. Safe Claim and Unsafe Claim blocks must both be non-empty.

## Evidence tiers (claim = weakest passing gate)

| Tier | Requires | Network publication |
| --- | --- | --- |
| prototype | scaffold + intent | No |
| benchmark_signal | baseline + candidate on the pack | No (label as local evidence) |
| focused_pattern | repeated wins on a focused slice + rollback condition | Review only |
| candidate_review | candidate delta > 0, absorption all-modes present AND scored with positive delta, traps covered with zero regressions, packet consistent with reports, rollback rule | Human review required |
| transfer_supported | transfer_summary.json probe in a second context | Allowed with boundary, still human-gated |
| network_absorbable | multi-seed + operator calibration + privacy + rollback reviews | Blocked by default in this beta |

## Gotchas (learned the hard way)

- **Write JSON artifacts with the Write tool, not PowerShell `Set-Content -Encoding utf8`.** PS 5.1 writes a UTF-8 BOM that chip-labs' `json.load` rejects, producing confusing "blocked" smokes. (Editing a JSON file the harness already tracks is fine.)
- **External LLM judges need their full validated input contract.** An outcome predictor trained/validated on full posts will silently mis-score or fail to parse bare hooks. Feed it what it was validated on; verify on a fresh sample before trusting its number (predictors drift: one went 0.53 to 0.17 in seven weeks).
- **Benchmark saturation in 1-2 rounds means the benchmark is too easy / self-authored,** not that the chip is excellent. Switch to benchmark governance, don't keep mutating.
- **Multi-seed or it didn't happen.** A single seed sign-flipped a Spearman from -0.40 to +0.20 at small n. Run 3+, majority-vote, bootstrap the difference.
- **Workflow `args` delivery into a script can be unreliable;** embed benchmark DATA inline in the eval-harness script instead of passing via `args`.
- **Self-authored oracle caps the run at `benchmark_signal`** regardless of the delta. To go higher, ground the oracle in measured outcomes (Step 9b, `BENCHMARK_AUTHORSHIP_AND_EVIDENCE_EXPIRY.md`).

## Assets (in this skill's `assets/`)

- `eval_harness.workflow.js` -- blind runner+judge evaluation workflow (copy, edit DATA, run via Workflow).
- `calibration_sampler.py` -- sample real cases with measured outcomes into an oracle (Step 9b).
- `calibration_metrics.py` -- deterministic band accuracy, Spearman, ship precision/recall, paired bootstrap. No LLM in the numbers.
- `hybrid_combiner.py` -- doctrine strategy gate + external outcome channel, with the validation guard.

## CLI quick index

```
python -m chip_labs.cli creator-run-template-check --fail-on-blocked
python -m chip_labs.cli creator-run-init --output-dir <run-dir> --domain "<d>" --goal "<g>" --source-channel local
python -m chip_labs.cli creator-run-smoke <run-dir> [--fail-on-blocked] [--fail-on-warn] [--output <json>]
python -m chip_labs.cli creator-run-doctor <run-dir> [--fail-on-blocked] [--output <json>]
```

`--fail-on-warn` exists only on smoke, not doctor. `--recompute` exists on both but is for machine-recomputable provenance only (see Reports). Use `--output <json>` when capturing large results; truncating stdout mid-stream can produce misleading exit codes. Smoke JSON has `automation.recommended_next_command`, `missing_paths`, `blocking_checks`, `status_counts`. Doctor adds prioritized `repair_steps` and `quarantine`.
