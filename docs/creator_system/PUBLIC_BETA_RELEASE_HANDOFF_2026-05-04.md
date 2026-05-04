# Spark Creator System Public Beta Handoff - 2026-05-04

This is the public-facing handoff for the Spark creator-system technical beta.
It is meant for technical users and Spark agents who want to create local domain
chips, benchmark packs, specialization paths, autoloop policies, and Swarm
contribution packets from a repo checkout.

## Release Identity

- Repo: `https://github.com/vibeforge1111/spark-domain-chip-labs`
- Branch: `main`
- Recommended tag: `creator-system-beta-2026-05-04`
- Latest verified hardening baseline: `6ead089`
- Latest hardening tag: `creator-system-beta-2026-05-04-hardening-2`
- Latest hardening prerelease:
  `https://github.com/vibeforge1111/spark-domain-chip-labs/releases/tag/creator-system-beta-2026-05-04-hardening-2`
- Release type: local creator-system technical beta
- Network claim: not `network_absorbable`

## First Commands

```bash
git clone https://github.com/vibeforge1111/spark-domain-chip-labs.git
cd spark-domain-chip-labs
python -m pip install -e .
chip-labs creator-system-beta-check --fail-on-blocked
```

Expected result:

- `verdict`: `pass`
- `network_absorbable`: `false`
- templates: `57` pass, `0` warn, `0` fail
- Startup YC strict smoke: `101` pass, `0` warn, `0` fail
- Startup YC evidence tier: `transfer_supported`
- stronger-release gate: still blocked

## What This Beta Can Do

- Scaffold a creator-run workspace from a user goal.
- Smoke-check and doctor a creator-run workspace.
- Generate creator systems from briefs in a temporary clean workspace.
- Run the 36-row generated multi-domain, multi-seed matrix.
- Emit read-only `creator-mission-status` packets for product surfaces.
- Validate Startup YC as a `transfer_supported` reference fixture.
- Keep saved evidence separate from recomputed evidence.
- Block premature network, product runtime, and Swarm-publication claims.

## What This Beta Does Not Do

- It does not approve `network_absorbable`.
- It does not publish creator-run output to Spark Swarm automatically.
- It does not wire Builder, Telegram, Spawner, Canvas, or Kanban creator
  controls.
- It does not prove real-world content virality.
- It does not prove production memory safety.
- It does not extract or publish a separate public `spark-creator` repo.

## Verified Evidence

- Local creator-system beta check: passed.
- Fresh clone plus isolated virtualenv beta check: passed from
  `C:\Users\USER\AppData\Local\Temp\spark-domain-chip-labs-beta-check-20260504190038`.
- GitHub push CI for `06153f2`: passed.
- GitHub manual generated multi-seed workflow dispatch for `06153f2`: passed.
- Manual generated matrix output: `passed=36/36`,
  `mission_run_count=36`, `release_gate=blocked`,
  `network_absorbable=false`.
- Extended local generated matrix output: `passed=54/54`, `check=pass`,
  `row_count=54`, `network_absorbable=false`, from
  `C:\Users\USER\AppData\Local\Temp\generated-creator-matrix-54-0c2bd9886a154f27977a6108fa71ccc9`.
- Creator System CI for hardening baseline `01bc6de`: passed as run
  `25336050060`.
- Fresh clone plus isolated virtualenv beta check for hardening baseline
  `01bc6de`: passed from
  `C:\Users\USER\AppData\Local\Temp\spark-domain-chip-labs-beta-fresh-20260504223056`.
  The aggregate beta check included the Startup YC production-gate workbench
  subcheck and kept `network_absorbable=false`.
- Creator System CI for hardening baseline `6ead089`: passed as run
  `25337256803`, including the uploaded
  `creator-system-release-evidence` workflow artifact.
- Pushed hardening tag `creator-system-beta-2026-05-04-hardening-2` points to
  commit `6ead089b7b3d31a8f9b4304f59e63d156c40ae63`.
- GitHub prerelease `Spark Creator System Beta Hardening 2` is published for
  the hardening tag and includes `creator-system-release-evidence.json` as a
  release asset with digest
  `sha256:b7fb79142196c70b06b21689ae5ffffd7dca9d1a317b3581428d2341baac210c`.

## Release Shape Decision

Keep this beta inside `spark-domain-chip-labs` for now.

Do not extract a separate `spark-creator` repo. Reconsider extraction only after the schema surface,
generator matrix, product runtime reviews, privacy review, rollback review, and
publication approval are stable enough to version independently.

## Production Upgrade Gates

Before any stronger release claim, require:

- Multi-seed validation over the intended production domains.
- Human/operator calibration.
- Privacy review.
- Rollback review.
- Publication approval.
- Product runtime review evidence for Builder, Telegram, Spawner, Canvas, and
  Kanban.
- `creator-release-gate` run with generated summary, Startup YC review, and
  product runtime review evidence.

Even when these packets pass, `network_absorbable` must remain false until the
publication authority explicitly approves that claim.

Production rehearsal command:

```bash
chip-labs startup-yc-production-gate-workbench \
  --validation-plan docs/creator_system/examples/startup-yc-operator-validation/validation_plan.json \
  --workspace-dir /tmp/startup-yc-production-gate-workbench \
  --output /tmp/startup-yc-production-gate-workbench/summary.json
```

Run it in an empty workspace. The expected beta-state result is still
`verdict=blocked` and `network_absorbable=false`.
