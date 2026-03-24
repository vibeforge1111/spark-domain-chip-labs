# MiroFish Portfolio Rerun Decision: 2026-03-24

## Decision

Do not launch another deeper full-universe rerun from the current March 24 state.

Keep the medium checkpoint as canonical for now:

- `research/meta/MIROFISH_PORTFOLIO_RUN_515_MEDIUM_2026-03-24.json`
- `research/meta/MIROFISH_PORTFOLIO_READOUT_515_MEDIUM_2026-03-24.json`
- commit `6eb669b` `MiroFish: save medium portfolio checkpoint`

## Why

Three facts now point to deferring another rerun:

1. the medium checkpoint already restored non-zero full-universe signal
2. the last speculative runtime experiment regressed the tiny full-universe benchmark to `78.8s`
3. deeper and step-up rerun attempts after the medium checkpoint did not finish quickly enough to justify replacing it inside this session

That means the open question is no longer whether the repo can rerun. It can.

The open question is whether the next rerun has a strong enough hypothesis and runtime budget to beat the medium checkpoint on actual usefulness.

## Reopen Criteria

Only reopen the deeper-rerun path if all of these are true:

1. there is a profiler-backed reason to expect better runtime behavior or better retained-adoption resolution
2. the harness is declared before launch
3. the runtime budget is declared before launch
4. the success criterion is declared before launch

## Minimum Rerun Contract

If a deeper rerun is approved later, define at least:

- candidate harness
  - `rounds=7`
  - `flagship_count_per_type=5`
  - `ensemble_runs=5`
  - `min_runs=5`
  - `ensemble_count_per_type=2`
  - `bootstrap_resamples=10`
- runtime budget
  - must stay interactive enough to finish inside one operator session
- success criterion
  - must materially improve retained-adoption resolution or enterprise separation relative to the medium checkpoint
- rejection rule
  - if the run does not clearly beat the medium checkpoint on usefulness, keep the medium checkpoint canonical

## Dashboard Rule

Do not refresh dashboard or export until either:

- a deeper rerun clears the above contract and clearly improves usefulness, or
- the team explicitly chooses to treat the medium checkpoint as the final operator-facing portfolio artifact for now
