# MiroFish Portfolio Runtime Fix Note: 2026-03-24

## Scope

Make the repo-local `515`-domain portfolio harness operationally usable for interactive reruns without changing the underlying MiroFish ranking semantics.

Code changed:

- `src/chip_labs/mirofish/graph.py`
- `src/chip_labs/mirofish/simulation.py`

## Profiling Read

Tiny full-universe timing harness used during profiling:

- `max_rounds=2`
- `flagship_count_per_type=1`
- `ensemble_runs=1`
- `ensemble_count_per_type=1`
- `min_runs=1`
- `bootstrap_resamples=5`

Measured hotspots from `py-spy`:

1. persona generation spent time in `_assign_expertise()` because `graph.get_edges_for()` did a full scan of `graph.edges` on every call
2. simulation spent time in `_compute_awareness()` because every persona-domain pair rescanned the full signal list
3. churn and retention checks recomputed the same awareness family again later in the same round

## Fixes

### Graph lookup fix

- Added `_edges_by_node` adjacency indexing to `DomainGraph`
- Updated `add_edge()` to populate the index
- Updated `get_edges_for()` to use the index instead of scanning all edges

### Simulation awareness fix

- Indexed active signals by domain once per round
- Reused that domain signal map inside `_compute_awareness()`
- Added a round-local `effective_awareness_cache` so churn and retention checks reuse the awareness already computed during the main evaluation phase

## Verification

- `python -m pytest tests/test_trend_prediction.py tests/test_mirofish_portfolio.py -q` passed
- The tiny full-universe timing harness completed in `25.62s` after the fixes

That is still not cheap, but it is operationally different from the earlier state where the same tiny full-universe run remained effectively stuck for much longer while profiling showed repeated structural scans.

## Decision

Keep these runtime fixes.

Why:

- they remove measured structural waste
- they do not change domain semantics or benchmark rules
- they make an interactive full-universe rerun materially more plausible

## Next Batch

Relaunch the `515`-domain portfolio run under an explicitly interactive harness and save the resulting portfolio packet and readout under `research/meta/`.
