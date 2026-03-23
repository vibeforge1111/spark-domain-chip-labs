# MiroFish v4 Engine Rebalance: 2026-03-24

## Symptom

The latest committed MiroFish v4 run produced almost no usable end-state signal for the 515-domain portfolio:

- `viz/mirofish_500_data.json` showed `mean_adoption = 0.0001`
- `median_adoption = 0.0`
- `max_adoption = 0.0044`
- `0` domains above `1%` final adoption
- `0` domains with meaningful trial left by the final round

This made the output look like agents never chose anything, even though curve inspection showed broad mid-run attention and some trial behavior.

## Root Cause

The regression was primarily engine-side, not a pure dashboard/export issue.

### 1. Threshold inflation in the learning loop

The v4 learning loop allowed `trial` stages to raise global persona thresholds whenever `round_adoption_rate < 0.1`.

On a 30-domain validation slice before the fix:

- mean persona threshold started at `0.3227`
- mean persona threshold ended at `0.4526`
- max persona threshold rose from `0.6832` to `0.8785`

That made late-stage progression materially harder as the run continued.

### 2. Trial counted too strongly in attention fatigue

The fatigue penalty counted `trial` the same way as retained adoption, so exploratory behavior could self-choke the funnel before retention was observable.

### 3. Retention gate was too aggressive for a 20-round simulation

Trial users churned too quickly, and adopted users could regress on relatively light evidence loss.

### 4. Reporting path over-weighted final retained adoption

The report path mostly surfaced final retained adoption, which hid the stronger mid-run choice signal.

## Changes

### Engine

- Excluded `trial` from the attention-fatigue adoption count.
- Limited learning-based threshold changes to retained stages:
  - `adopted`
  - `committed`
  - `advocating`
- Reduced the magnitude of disappointing-outcome threshold inflation:
  - trigger lowered from `< 0.10` to `< 0.03`
  - multiplier reduced from `1.02x` to `1.005x`
- Slightly softened the retention gate:
  - longer trial churn window
  - lower churn threshold
  - stricter conditions before adopted users fall back to trial

### Reporting / observability

- Added `final_active_rate`
- Added peak trajectory metrics:
  - `peak_adoption_rate`
  - `peak_active_rate`
  - `peak_interest_rate`
  - `peak_trial_rate`
- Updated report ranking to prefer `agent_choice_signal = peak_active_rate`
- Added driver/risk language for:
  - strong mid-run attention
  - real try-out behavior
  - poor conversion from attention to durable retention

## Validation

### 30-domain slice, same scenario, after fix

- mean threshold drift: `0.3227 -> 0.3262`
- mean final adoption: `0.0100`
- max final adoption: `0.0417`
- max peak adoption: `0.0750`
- max peak active: `0.1750`

### Same slice, before fix

- mean threshold drift: `0.3227 -> 0.4526`
- mean final adoption: `0.0044`
- max final adoption: `0.0167`

### Report output after fix

The top report entries now surface agent-choice signal explicitly, for example:

- `trading-crypto`
  - `adoption_probability = 0.025`
  - `peak_active_probability = 0.15`
  - `peak_interest_probability = 0.85`
- `roblox-development`
  - `adoption_probability = 0.025`
  - `peak_active_probability = 0.15`
  - `peak_interest_probability = 0.8083`

This preserves the distinction between:

- what attracted agents during the run
- what survived into retained end-state adoption

## Verification Commands

- `python -m pytest tests/test_trend_prediction.py -q`
- command-based 30-domain simulation slice comparing threshold drift and final/peak adoption metrics

## Test Notes

`tests/test_trend_prediction.py` passes.

`tests/test_simulation.py` still contains pre-existing expectations for the older simulation contract:

- `ADOPTION_STAGES == 6`
- `run_ensemble(..., n_runs=3)` returns exactly `3`

Those assertions no longer match the already-committed v4 model, which now uses:

- 9 stages
- minimum 15 ensemble runs

That mismatch predates this rebalance patch.
