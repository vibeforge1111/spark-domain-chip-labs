# MiroFish Portfolio Medium Checkpoint Note: 2026-03-24

## Scope

Run a deeper full-universe portfolio pass after the runtime fixes to recover non-zero signal while keeping the repo-local path interactive.

Output artifacts:

- `research/meta/MIROFISH_PORTFOLIO_RUN_515_MEDIUM_2026-03-24.json`
- `research/meta/MIROFISH_PORTFOLIO_READOUT_515_MEDIUM_2026-03-24.json`

Harness used:

- `rounds=6`
- `flagship_count_per_type=4`
- `ensemble_runs=4`
- `min_runs=4`
- `ensemble_count_per_type=2`
- `bootstrap_resamples=10`

## Main Result

This medium checkpoint is the first full-universe repo-local run in this session that restores non-zero portfolio signal.

Top line:

- top ensemble domain: `defi-architect` at `0.83%`
- top direct-choice domain: `ai-npc-dialog` at `3.33%`
- top retained adoption in the flagship run: `ai-npc-dialog` at `3.33%`

That is materially better than the earlier interactive checkpoint, where both ensemble adoption and direct choice collapsed to zero.

## Top Slices

Top overall:

1. `defi-architect`
2. `mcp-server-builder`
3. `tiktok-creator`
4. `discord-community`
5. `last-mile-delivery-ai`

Top enterprise slice:

1. `chronic-disease-mgr`
2. `legal-ops`
3. `workplace-ai-trainer`
4. `addiction-recovery-ai`
5. `quality-inspection-ai`

Top newly discovered `v4` slice:

1. `last-mile-delivery-ai`
2. `voice-assistant-senior`
3. `chronic-disease-mgr`
4. `hvac-optimizer-ai`
5. `remote-job-matcher`

## What This Checkpoint Still Does Not Solve

The read is still thin.

Important cautions from the readout:

- top ensemble adoption remains modest, so rank order is more trustworthy than absolute magnitude
- enterprise-response domains still show visible interest-to-choice friction
- several enterprise domains still lose too much between in-run choice and retained adoption

Many top rows still have `final_adoption_rate=0.0` even when they recover some ensemble or trial signal, so this should still be treated as a medium checkpoint rather than the final trusted `515`-domain verdict.

## Decision

Keep this checkpoint.

Why:

- it proves the runtime fixes support a fuller full-universe pass
- it recovers non-zero portfolio signal
- it gives a better next handoff than the zeroed interactive checkpoint

## Next Batch

Raise harness depth one more step, but only enough to preserve the recovered non-zero signal while improving retained adoption resolution. The next good target is a near-final portfolio read, not a dashboard refresh yet.
