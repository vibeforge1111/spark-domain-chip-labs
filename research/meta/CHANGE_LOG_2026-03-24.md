# Change Log: 2026-03-24

## Tranche: MiroFish v4 Engine Rebalance

### Files Changed

- `src/chip_labs/mirofish/personas.py`
- `src/chip_labs/mirofish/simulation.py`
- `src/chip_labs/mirofish/report.py`
- `research/meta/MIROFISH_V4_ENGINE_REBALANCE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_v4_engine_rebalance.json`

### Why

The latest committed MiroFish v4 run had effectively collapsed into near-zero final adoption across the 515-domain universe. The output made it look like agents never chose anything, even though curve inspection showed meaningful mid-run attention and trial behavior.

### What Changed

- Reduced threshold inflation by limiting learning-based threshold adjustments to retained stages only
- Stopped counting `trial` as full adoption inside the fatigue penalty
- Relaxed retention and fallback gates so exploratory behavior has time to convert into retained adoption
- Added peak trajectory metrics and `agent_choice_signal` so reports preserve what agents actually tried during the run

### Verification

- `python -m pytest tests/test_trend_prediction.py -q`
- 30-domain validation slice comparing:
  - threshold drift
  - final adoption
  - peak adoption
  - peak active signal

### Notes

- `tests/test_simulation.py` still carries pre-existing expectations from the older simulation contract:
  - 6 adoption stages
  - exact requested ensemble run count even though v4 enforces a minimum
- Those mismatches predate this rebalance tranche.
