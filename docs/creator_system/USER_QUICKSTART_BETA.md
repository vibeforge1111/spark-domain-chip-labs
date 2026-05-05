# Spark Creator System Beta Quickstart

This quickstart is for technical users and Spark agents who want to create
local domain chips, benchmark packs, specialization paths, autoloop policies,
and Swarm contribution packets from a repo checkout.

## What This Beta Supports

- Scaffold a creator-run workspace from a domain brief.
- Generate creator-system proof artifacts in a clean temporary workspace.
- Run smoke, doctor, template, benchmark, autoloop, MiroFish, retrieval-memory,
  tool-operation, operator-review, and Startup YC validation commands.
- Produce local `candidate_review` or `transfer_supported` evidence when the
  relevant gates pass.

## What This Beta Does Not Claim

- It does not approve `network_absorbable`.
- It does not publish to Spark Swarm automatically.
- It does not wire Builder, Telegram, Spawner, Canvas, or Kanban runtime
  creator controls.
- It does not prove live provider-judge calibration or real content virality.

## Where To Start

If you are new to this system, read
`CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md` before creating a run. It explains
how users get value from each part of the system and how Spark agents should
move through intent, adapter map, domain chip, benchmark pack, specialization
path, autoloop policy, evidence ladder, local Swarm packet, mission status, and
release evidence.

Use this quickstart for commands. Use the onboarding guide for the step-by-step
operating model.

## Install From A Fresh Clone

```bash
git clone https://github.com/vibeforge1111/spark-domain-chip-labs.git
cd spark-domain-chip-labs
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .
```

Verify the command entrypoint:

```bash
chip-labs creator-run-template-check --fail-on-blocked
```

Expected result: `verdict` is `pass`, with `57` passing checks.

Run the aggregate beta readiness check:

```bash
chip-labs creator-system-beta-check --fail-on-blocked
```

Expected result: `verdict` is `pass`, while `network_absorbable` remains
`false`, the Startup YC production-gate workbench subcheck passes by preserving
the expected blocked rehearsal state, and stronger network/product release
claims stay blocked.

For a machine-readable release evidence packet from a clean checkout:

```bash
chip-labs creator-system-release-evidence --fail-on-blocked --output /tmp/creator-system-release-evidence.json
```

Expected result: `verdict` is `pass`, `release_ready` is `true`, and
`network_absorbable` remains `false`. The packet also includes
`production_readiness_summary`, which should show repo/user beta readiness and
the production-grade creator-system standard at `100`, while
`network_absorption_publication` remains `blocked`. If the checkout has local
edits, this packet blocks with `repo:worktree_dirty` so release evidence cannot
silently include uncommitted work.

On pushed commits, Creator System CI also uploads this JSON as the
`creator-system-release-evidence` workflow artifact.

To check the two 100% readiness targets without approving network absorption:

```bash
chip-labs creator-system-production-readiness --fail-on-blocked --output /tmp/creator-system-production-readiness.json
```

Expected result: top-level `verdict` is `pass`,
`repo_user_beta_readiness.score` is `100`,
`production_grade_creator_system_standard.score` is `100`, and
`network_absorption_publication` remains `blocked` with
`network_absorbable=false`. This command creates generated proof in a clean
temporary workspace and attaches the read-only product runtime review fixture;
it does not wire product controls.

## Create A Creator Run

```bash
chip-labs creator-run-init \
  --output-dir runs/artifact-quality-demo \
  --domain "Artifact Quality" \
  --goal "Create a creator system that reviews design docs and PR writeups" \
  --source-channel local
```

The generated folder starts as a scaffold. It is expected to be incomplete until
the chip, benchmark, reports, autoloop policy, and Swarm packet artifacts are
filled.

Check readiness:

```bash
chip-labs creator-run-smoke runs/artifact-quality-demo
```

If blocked or incomplete, ask for repair steps:

```bash
chip-labs creator-run-doctor runs/artifact-quality-demo
```

## Prove The Generator Path

Run the multi-domain generator acceptance matrix in a clean workspace:

```bash
chip-labs generated-multi-seed-run \
  --briefs docs/creator_system/examples/generated-multi-domain-briefs.json \
  --workspace-dir /tmp/generated-creator-matrix \
  --fail-on-blocked
```

Then recompute-check the summary if you saved it:

```bash
chip-labs generated-multi-seed-summary-check \
  --summary /tmp/generated-creator-matrix/multi_seed_validation_summary.json \
  --fail-on-blocked
```

On scheduled or manually dispatched Creator System CI runs with
`run_generated_multi_seed=true`, the workflow uploads
`generated-creator-matrix-evidence` with the generated summary, summary-check,
mission-status, and release-gate JSON packets. These artifacts are downloadable
evidence for review; they do not change the `network_absorbable=false`
boundary.

## Validate The Startup YC Reference

Strict saved-evidence smoke:

```bash
chip-labs creator-run-smoke \
  docs/creator_system/examples/startup-yc-creator-run \
  --fail-on-blocked \
  --fail-on-warn
```

Expected result: `ready_for_swarm_packet` with evidence tier
`transfer_supported`.

External recompute, when sibling external source repos are available:

```bash
chip-labs creator-run-smoke \
  docs/creator_system/examples/startup-yc-creator-run \
  --recompute \
  --fail-on-blocked
```

## Interpret Evidence Tiers

| Tier | Meaning In This Repo |
| --- | --- |
| `prototype` | Scaffold exists, but proof artifacts are missing. |
| `benchmark_signal` | Early benchmark signal only. |
| `candidate_review` | Local review evidence; useful for iteration, not broad transfer. |
| `transfer_supported` | Focused transfer evidence exists. Startup YC is here. |
| `network_absorbable` | Blocked in this beta until multi-seed validation, human/operator calibration, privacy review, rollback review, and publication approval pass. |

## Before Sharing A Result

Run:

```bash
chip-labs creator-run-smoke <run-dir> --fail-on-blocked --fail-on-warn
chip-labs creator-run-doctor <run-dir>
```

Do not claim stronger evidence than the weakest passing gate supports.
