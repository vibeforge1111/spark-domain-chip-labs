# Validation Batch: 2026-03-21 Phase 7D

## Scope

Post-boundary-stabilization operational validation after the package-boundary decision.

## Commands Run

- `PYTHONPATH=src python -m chip_labs.cli score-v2 .`
- `PYTHONPATH=src python -m chip_labs.cli score-v3 . --verbose`
- `PYTHONPATH=src python -m pytest tests/test_chip_runtime.py tests/test_chip_mcp_server.py tests/test_transfer.py tests/test_scoring_engine.py tests/test_loop_controller.py tests/test_hooks.py tests/test_evaluate.py tests/test_suggest.py tests/test_packets.py tests/test_watchtower.py tests/test_graduation.py -q`

## Results

- `score-v2`: `100/100`, `production_ready`
- `score-v3`: `87.0/100`, `production_ready`
- regression pack: `304 passed in 59.58s`

## Interpretation

The repo is no longer failing because of boundary drift. The package-boundary work held under a broad regression pack, and the scorers stayed flat at the same defended checkpoint. The remaining limits are substantive ones:

- watchtower depth is still `4.0/8.0`
- empirical history is stronger than before, but the next lift still comes from more real runs rather than more structural edits
- the packaging question is now closed for the current state: one repo/package, internal subpackages, explicit future split triggers

## Ledger Effect

This batch appends three real validation runs to `research/meta/runs.jsonl`, bringing the lab ledger from `50` to `53` recorded runs.
