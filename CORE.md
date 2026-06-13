# The Core Contract (start here)

`chip-labs` exposes 70+ CLI subcommands. **You need eight.** The rest are lab research surfaces (mirofish discovery, portfolio analytics, startup-yc specifics) that you can ignore until you have a reason not to.

A "creator run" turns one capability into a measured, self-improving loop. The core contract is the folder shape, the gates, and these commands. Everything else is optional.

## The eight commands

```bash
# 0. Health-check the templates before you build (expect verdict: pass)
python -m chip_labs.cli creator-run-template-check --fail-on-blocked

# 1. Scaffold a run (writes 6 files + 6 dirs; output-dir IS the run dir)
python -m chip_labs.cli creator-run-init --output-dir <run-dir> \
    --domain "<domain>" --goal "<plain goal>" --source-channel local

# 2. Check readiness after each artifact group
python -m chip_labs.cli creator-run-smoke <run-dir>

# 3. Get a repair plan when smoke says blocked
python -m chip_labs.cli creator-run-doctor <run-dir>

# 4. Strict gate before sharing anything
python -m chip_labs.cli creator-run-smoke <run-dir> --fail-on-blocked --fail-on-warn
```

That is the whole loop: init -> fill artifacts -> smoke -> doctor -> repeat -> strict gate. The four readiness commands plus their flags are the eight surfaces that matter.

## The folder shape

```
<run-dir>/
  creator-intent.json          what you're improving + privacy boundary  [gate-checked]
  adapter-map.json             6 adapters (domain/benchmark/tool/loop/absorption/swarm)  [gate-checked]
  created-artifact-manifest.json   live progress tracker  [gate-checked]
  domain-chip/      doctrine.md (the expertise) + manifest + scoring_hooks
  benchmark/        cases.jsonl + traps.jsonl + scoring_rubric.md + manifest.json
  autoloop/         policy.json (the safety contract) + mutation_surface + stop_conditions
  specialization-path/   path.manifest.json + absorption_bundle.md
  reports/          baseline.json + candidate.json + evidence_ladder.md
  swarm/            contribution_packet.json
```

## The verdict ladder

`blocked` (fix it) -> `prototype` (fill core artifacts) -> `ready_for_baseline` (run the loop) -> `ready_for_swarm_packet` (review). `ready_for_swarm_packet` means artifacts are complete, **not** that anything is network-publishable. Network publication stays off by default.

## The five rules that keep claims honest

1. The CLI is the source of truth; if a doc disagrees, trust the CLI.
2. Claim only the weakest passing gate on the evidence ladder.
3. A self-authored benchmark caps at `benchmark_signal` (see `docs/creator_system/BENCHMARK_AUTHORSHIP_AND_EVIDENCE_EXPIRY.md`).
4. Evidence expires; record `validated_at` / `revalidate_by`.
5. `chip-labs autoloop` (the standalone subcommand) is a structural scaffolder, not a capability loop. It does not produce evidence of quality. The real loop is the human/agent procedure above. (See `docs/creator_system/BENCHMARK_AND_AUTOLOOP_PROTOCOL.md`.)

## Where to go deeper

| You want to | Read |
| --- | --- |
| The full step-by-step | `docs/creator_system/CREATOR_RUN_GOLDEN_PATH_V1.md` |
| Drive it as an agent | `docs/creator_system/AGENT_CREATOR_PLAYBOOK.md` |
| Understand the loop governance | `docs/creator_system/BENCHMARK_AND_AUTOLOOP_PROTOCOL.md` |
| Pick the right claim tier | `docs/creator_system/PROMOTION_GATES_AND_EVIDENCE_TIERS.md` |
| A one-sentence-to-loop skill | the `spark-autoloop` Claude skill in `.claude/skills/` |

The lab research commands (`mirofish-*`, `portfolio-*`, `startup-yc-*`, `creator-swarm-*`) are not part of the core contract and are not needed to build a creator run.
