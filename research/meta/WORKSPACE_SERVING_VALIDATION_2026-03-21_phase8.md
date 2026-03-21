# Validation Batch: 2026-03-21 Phase 8

## Scope

Repo-local intelligence serving validation after making the serving stack aware of the active chip workspace.

## Commands Run

- `PYTHONPATH=src python -m pytest tests/test_chip_runtime.py tests/test_chip_context_injector.py tests/test_chip_advisor.py tests/test_chip_mcp_server.py tests/test_hooks.py -q`
- `PYTHONPATH=src python -m chip_labs.cli serve . "package boundary migration" --output research/meta/serve_output_phase7d_2026-03-21.json`
- `PYTHONPATH=src python -m chip_labs.cli serve-intelligence "stabilize packaging and preserve hook compatibility" --max-chips 2 --style concise --output research/meta/serve_intelligence_output_phase7d_2026-03-21.json`
- `PYTHONPATH=src python -m chip_labs.cli advise "stabilize packaging and preserve hook compatibility" --domain chip-labs --output research/meta/advise_output_phase7d_2026-03-21.json`

## Results

- targeted serving/runtime test pack: `134 passed in 41.49s`
- `serve`: returned `domain-chip-labs`, score `100`, with doctrines across all four evidence lanes
- `serve-intelligence`: before the fix, the same task returned `<!-- No relevant chips found for this task -->`; after the fix it returned a non-empty `domain-chip-labs` context block
- `advise`: now consults `domain-chip-labs` first for the packaging-oriented action, but it still includes `content` and `domain-chip-agentic-marketing` in the consulted set

## Interpretation

The serving product is materially less brittle inside this repo now. Repo-local context injection no longer fails closed just because the active workspace is outside the Desktop prefix registry or because lexical overlap is sparse.

The remaining gap is narrower and more honest:

- `serve` is healthy for repo-local doctrine lookup
- `serve-intelligence` is now healthy for repo-local context injection
- `advise` is improved, but chip ranking is still too broad for packaging-focused tasks and needs a tighter relevance strategy if we want cleaner pre-action guidance

## Ledger Effect

This batch appends three real serving-validation runs to `research/meta/runs.jsonl`, bringing the lab ledger from `41` to `44` recorded runs.
