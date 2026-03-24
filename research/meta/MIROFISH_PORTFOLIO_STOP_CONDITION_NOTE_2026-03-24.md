# MiroFish Portfolio Stop Condition Note: 2026-03-24

## Scope

Record the final decision after the post-checkpoint runtime experiments.

This note closes the loop on the extra optimization attempts made after the medium full-universe checkpoint and states which portfolio artifact remains the best trusted handoff.

## What Was Tested

After the committed medium checkpoint, one more simulation-side optimization idea was tested:

- precompute per-round signal decay and warmup inside the domain signal index so awareness loops would reuse prepared signal tuples instead of recomputing shared work for every persona-domain pair

The tiny full-universe benchmark used for that decision was:

- `max_rounds=2`
- `flagship_count_per_type=1`
- `ensemble_runs=1`
- `ensemble_count_per_type=1`
- `min_runs=1`
- `bootstrap_resamples=5`

## Result

The experiment regressed runtime badly.

- prior tiny benchmark after the committed runtime fix: about `25.62s`
- later benchmark after a different failed precompute idea had already shown regression: about `41.31s`
- benchmark for this final signal-decay precompute idea: `78.8s`

That is directionally wrong and not close to good enough to justify another full-universe step-up run.

## Decision

Reject the uncommitted optimization and keep the committed medium checkpoint as the current best portfolio state.

Best committed checkpoint:

- `6eb669b` `MiroFish: save medium portfolio checkpoint`
- `research/meta/MIROFISH_PORTFOLIO_RUN_515_MEDIUM_2026-03-24.json`
- `research/meta/MIROFISH_PORTFOLIO_READOUT_515_MEDIUM_2026-03-24.json`
- `research/meta/MIROFISH_PORTFOLIO_MEDIUM_CHECKPOINT_NOTE_2026-03-24.md`

Why this is the correct stop condition:

- the medium harness is the first full-universe repo-local pass in this session that restores non-zero signal
- the rejected optimization made the tiny benchmark materially worse, not better
- the process ceiling is already hot, so another speculative deep rerun is lower value than preserving the validated checkpoint

## Verification

After reverting the failed optimization:

- `$env:PYTHONPATH='src'; python -m pytest tests/test_trend_prediction.py tests/test_mirofish_portfolio.py -q`
- result: `13 passed in 1.07s`

## Handoff

Resume from the medium checkpoint, not from the abandoned runtime experiment.

If work continues from here, the next high-value step is not another blind optimization pass. The next step should either:

- raise harness depth only with a very explicit runtime budget and success criterion, or
- turn the medium checkpoint into a clearer operator-facing readout and prioritization artifact
