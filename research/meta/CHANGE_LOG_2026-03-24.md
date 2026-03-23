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

## Tranche: MiroFish Discovery Factory Plan

### Files Changed

- `docs/MIROFISH_DISCOVERY_FACTORY_PLAN.md`
- `docs/EXECUTION_PLAN_2026-03-21.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_factory_plan.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The current MiroFish system can compare seeded domain-chip universes, but it cannot yet discover candidate domain chips from real specialization, mastery, and demand signals without being handed a menu first.

### What Changed

- Added a discovery-first hybrid architecture plan
- Defined the hard boundary between:
  - discovery
  - canonicalization
  - evaluation
  - promotion
- Defined the first implementation tranche:
  - discovery schema
  - output classes
  - canonicalization rules
  - one manual discovery batch
  - one smaller hybrid evaluation pass
- Linked the main repo execution plan to the new MiroFish discovery-factory plan

### Verification

- Manual consistency review against:
  - current MiroFish docs
  - current CLI/runtime structure
  - current execution plan

### Notes

- This tranche is planning-only.
- The next tranche should implement the discovery contract and repo-local packet scaffolding.

## Tranche: MiroFish Discovery Contract

### Files Changed

- `src/chip_labs/mirofish/discovery.py`
- `src/chip_labs/cli.py`
- `docs/MIROFISH_DISCOVERY_CONTRACT.md`
- `research/meta/MIROFISH_DISCOVERY_BATCH_TEMPLATE_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_BATCH_TEMPLATE_RESULT_2026-03-24.json`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_contract.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The discovery-first architecture had been planned, but there was still no concrete contract for what a valid discovered domain chip looks like, how noisy candidates get classified, or how operators should run the first packet-first intake flow.

### What Changed

- Added a discovery contract document that defines:
  - what counts as a domain chip
  - required candidate fields
  - classification outcomes
  - canonicalization rules
  - packet shape
  - operator workflow
- Added deterministic batch canonicalization code in `mirofish/discovery.py`
- Added a repo-local CLI command to canonicalize raw discovery batches
- Added a starter discovery batch packet that exercises:
  - accepted candidates
  - alias duplicates
  - workflow-only candidates
  - persona-only candidates
  - existing benchmark duplicates
  - too-vague candidates
- Saved the emitted canonicalized result packet for direct inspection and downstream handoff

### Verification

- Run `python -m chip_labs.cli mirofish-discovery-batch` on the starter packet
- Inspect the emitted accepted, merged, and rejected candidate groups

### Notes

- This tranche still stops before simulation.
- The next tranche should translate accepted discovery packets into a hybrid evaluation run spec with a stable benchmark panel.
