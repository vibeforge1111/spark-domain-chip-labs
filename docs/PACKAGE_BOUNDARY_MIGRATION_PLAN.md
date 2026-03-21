# Package Boundary Migration Plan

This document turns the repo-surface map into an execution baseline for future packaging work. It does not split the repo yet. It defines the safest order to do it.

## Goal

Reduce cross-surface drift without breaking the current hook contract, CLI entry points, or runtime integrations.

## Current Surfaces To Preserve

1. Meta-chip hooks
2. Chip factory
3. Transfer and recursive improvement
4. Intelligence serving

## Proposed Module Boundaries

### A. Lab Hook Surface

Keep together:
- `src/chip_labs/cli.py`
- `src/chip_labs/evaluate.py`
- `src/chip_labs/suggest.py`
- `src/chip_labs/packets.py`
- `src/chip_labs/watchtower.py`
- `src/chip_labs/quality_rubric.py`
- `src/chip_labs/quality_rubric_v2.py`
- `src/chip_labs/deep_eval.py`
- `src/chip_labs/registry.py`
- `src/chip_labs/trend_scanner.py`
- `src/chip_labs/mirofish/`

Reason:
- These files define the lab's public chip behavior and scoring surfaces

### B. Chip Factory Surface

Keep together:
- `src/chip_labs/scaffold.py`
- `src/chip_labs/gap_analyzer.py`
- `src/chip_labs/category_templates.py`
- `src/chip_labs/methodology.py`
- `src/chip_labs/graduation.py`
- `src/chip_labs/dspy_slot.py`

Reason:
- These files generate and repair chips rather than serving the lab chip itself

### C. Transfer Surface

Keep together:
- `src/chip_labs/transfer.py`
- `src/chip_labs/loop_controller.py`
- `src/chip_labs/scoring_engine.py`

Reason:
- These files govern recursive improvement and cross-chip portability

### D. Intelligence Serving Surface

Keep together:
- `src/chip_labs/chip_runtime.py`
- `src/chip_labs/chip_mcp_server.py`
- `src/chip_labs/intelligence_server.py`
- `src/chip_labs/chip_advisor.py`
- `src/chip_labs/chip_context_injector.py`
- `src/chip_labs/hooks.py`

Reason:
- These files serve chip intelligence into agent and external-system workflows

## Migration Order

### Phase 7A: Internal Naming

- Add one canonical surface map to docs
- Tag each source module with the surface it belongs to
- Keep imports unchanged

Status:
- Completed for docs

### Phase 7B: Internal Subpackages

- Create internal subpackages under `src/chip_labs/` that mirror the four surfaces
- Move implementation files behind compatibility imports
- Keep `python -m chip_labs.cli` and existing import paths working

Status:
- Started with the hook surface
- Added `src/chip_labs/lab_hooks/` as the first internal namespace
- Routed CLI and selected internal consumers through that namespace without changing the external contract
- Extended the same pattern to the factory surface with `src/chip_labs/chip_factory/`
- Extended the same pattern to the transfer surface with `src/chip_labs/transfer_surface/`
- Extended the same pattern to the intelligence-serving surface with `src/chip_labs/intelligence_serving/`

Exit condition:
- No external caller needs to change import paths yet

### Phase 7C: Dependency Cleanup

- Remove cross-surface imports that violate the intended boundaries
- Push shared utilities into clearly named common modules instead of letting one surface reach through another

Status:
- Started with the hook surface
- Moved `evaluate.py`, `suggest.py`, `packets.py`, and `watchtower.py` implementations under `src/chip_labs/lab_hooks/`
- Left top-level compatibility wrappers in place so existing imports continue to work
- Extended the same pattern to the lower-coupling factory modules:
  - `gap_analyzer.py`
  - `category_templates.py`
- Moved `scaffold.py` under `src/chip_labs/chip_factory/` once the lower-coupling factory slice was stable

Exit condition:
- Each surface depends only on sanctioned shared utilities and public interfaces

### Phase 7D: Packaging Decision

Choose one:
1. keep one repo with clear internal subpackages
2. split factory and serving into separate distributions

Decision rule:
- Do not split packages until import boundaries are already stable inside the repo

## Risks

- Breaking the current hook CLI while moving files
- Letting serving concerns leak into hook logic again
- Splitting too early and converting one repo problem into four release problems

## Immediate Tasks

1. Add surface labels to the migration plan and status docs.
2. Preserve the current public CLI and manifest contract as the compatibility layer.
3. Use future refactors to move one surface at a time instead of doing a repo-wide shuffle.

## Non-Goals

- No package split in this tranche
- No runtime behavior change
- No import-path breakage for existing hook consumers
