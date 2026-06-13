# AutoLoop Execution Protocol

You are the loop runner. The policy in `autoloop/policy.json` is your contract. Source standard: `docs/creator_system/BENCHMARK_AND_AUTOLOOP_PROTOCOL.md` and `docs/doctrines/loop_governance.md` in spark-domain-chip-labs.

## Stage 0 - Readiness

Confirm before any round: smoke verdict is `ready_for_baseline` or better, `reports/baseline.json` exists, the policy file is filled, and you can state the mutation surface and frozen surfaces from memory. If any fail, go back to the skill steps.

## Round 0 - Validation, not a loop round

Comparing the chip against no-chip (doctrine vs nothing) is **validation**, not round 1. It tells you the chip helps at all and seeds your baseline; it does not count against the 8-round mutation budget and is not subject to the keep rule (there is no mutation to keep or revert yet). Log it as `round 0 / chip_validation` in the lineage. Round 1 is the first time you mutate the doctrine.

## Stage 1 - Baseline (once per pass)

Run every case in `benchmark/cases.jsonl` against the un-mutated state. Score with `benchmark/scoring_rubric.md`, dimension by dimension, anchors only (never interpolate to flatter a result). Save: mean score, per-case and per-dimension scores, which prompt/doctrine version was used, and provenance hashes (path -> sha256, at minimum `benchmark/cases.jsonl` and `domain-chip/scoring_hooks.json`). The weakest dimension becomes the first mutation target.

## Stage 2 - Candidate generation (each round)

Produce exactly ONE narrow candidate mutation. It must include, written down in the lineage log before applying:

1. **Hypothesis**: why this change should improve the target capability (causal, not "might help")
2. **Mutated file or setting**: must be inside `mutation_surface`, never inside `frozen_surfaces`
3. **Expected score movement**: which dimension, roughly how much
4. **Risk**: what could regress
5. **Rollback**: how to revert (usually: restore the saved pre-mutation copy)

Save a copy of the file you are about to mutate. Then apply the mutation.

## Stage 3 - Candidate evaluation (each round)

Re-run ALL lanes: development cases, held-out cases, trap cases, no-op regression case. Score with the same frozen rubric.

**Keep rule, ALL four required:**
1. Primary score improves
2. Held-out score does not regress
3. Anti-gaming checks pass (see below) and zero trap regressions
4. Complexity does not rise without measured gain

If any fail: revert to the saved copy, log the round as `reverted` with the reason. If all pass: keep, log as `kept`.

**Anti-gaming checks** (run them on every kept candidate): format inflation (longer or prettier output scored as better), keyword stuffing, overfitting to development cases (development up, held-out flat or down), confidence increase without decision improvement, regression on the no-op case, silent widening of the mutation surface.

## Stage 4 - Diagnosis

After each round, state in one line: hypothesis tested, artifact changed, score movement, kept or reverted.

**Zero keeps after 3+ rounds** triggers the policy's 5-point diagnosis, written into `reports/creator_run_summary.md`:
1. Weakest component of the system
2. Did candidate generation produce causal mechanisms, or surface tweaks?
3. Is scoring saturated (baseline already near ceiling)?
4. Is the mutation surface too narrow to express the fix?
5. Can the benchmark even see the intended improvement?

A zero-keep loop with a good diagnosis is a successful run. Report it honestly.

## Stop conditions (end the pass when ANY hits)

1. Benchmark target met (from `success_criteria.benchmark_target`)
2. No improvement after the policy's round budget
3. Repeated candidates converge on the same pattern
4. Held-out cases regress
5. An anti-gaming check fails
6. The mutation surface needs expansion (that is a human decision, not yours)
7. The benchmark can no longer distinguish candidate quality (saturation in 1-2 rounds is a signal, not a win: it usually means the benchmark is self-authored and just restates the doctrine; stop mutating and open a benchmark-governance pass with harder cases or an outcome-grounded oracle per SKILL.md Step 9b)
8. **Hard cap: `max_rounds_before_review` (8) rounds**

## Wrap-up (every pass, kept or not)

1. Write `reports/candidate.json`: `mode: "validated_pack"`, mean score, `mean_delta` vs baseline, positive/negative/flat case counts, provenance hashes (same files as baseline).
2. Update the lineage log (`autoloop/` or as named in the policy) with every round, kept and reverted.
3. Update `reports/creator_run_summary.md` and `created-artifact-manifest.json` statuses.
4. Optional but valuable: a fresh-agent absorption test. Give ONLY `specialization-path/absorption_bundle.md` to a fresh subagent, run the held-out cases through it, write `reports/absorption_summary.json`. This is what separates "I improved" from "anyone can absorb this improvement".
5. Answer the six minimum-result questions in the summary: what changed; why it should improve the capability; which benchmark proved it; held-out and trap status; boundaries; whether another agent can use the lesson.

## Honesty boundary

- Claim only the weakest passing gate on the evidence ladder.
- `ready_for_swarm_packet` means artifact completeness, not network readiness.
- Mutation scope claimed must match the actual diff; mismatch means reject the round.
- Never present structural file-count gains (including anything from `chip-labs autoloop`) as capability evidence.
- Never run smoke or doctor with `--recompute` on a hand-scored run; that mode is for machine-recomputable provenance sources only and will block on `recompute_provenance_source`.
