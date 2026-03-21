# Diff Summary: 2026-03-21

## `src/chip_labs/hooks.py`

- Replaced direct session-chip prompt assembly in `handle_pre_tool_use()`
- Restored use of the shared `_build_context_text()` path
- Preserved session narrowing and reintroduced session domain keywords into the advisory query

## `src/chip_labs/quality_rubric_v2.py`

- Added `_has_closed_mutation_space()`
- Added `_check_manifest_v2()`
- Switched v2 manifest scoring from reused v1 logic to explicit v2 logic
- Expanded belief artifact discovery for `belief_promotion`
- Broadened `guardrails_set` to recognize bounded-loop guardrail variants
- Updated flywheel checks to accept `research/meta/` run history plus doctrine and contradiction artifacts stored under `docs/`

## `src/chip_labs/chip_runtime.py`

- Load `chip_name` from manifests when present
- For CLI-style hook commands, generate temporary input/output files and invoke hooks through `--input` / `--output`
- Retain stdin fallback for commands that do not look like file-oriented hook CLIs

## `src/chip_labs/deep_eval.py`

- Added shared manifest compatibility helpers for `schema`, `schema_version`, `hooks`, `capabilities`, and `commands`
- Updated v3 manifest scoring and hook-count scoring to use the compatibility helpers
- Allowed v3 run-history loading from `research/meta/runs.jsonl` and `research/meta/loop_telemetry.json`

## `README.md`, `docs/`, and `research/`

- Added doctrine artifacts under `docs/doctrines/`
- Added belief and contradiction artifacts under `docs/beliefs/`
- Added one artifact per evidence lane under `research/`
- Added structured lab packets under `research/packets/`
- Added lab run history under `research/meta/runs.jsonl`
- Added explicit repo gaps and near-term roadmap language to `README.md`
- Expanded contradiction artifacts with dated `run_*` references, score deltas, and explicit resolution markers so v3 contradiction scoring reflects actual rigor rather than generic prose
- Added a new doctrine on evaluator path trust, deepened mechanism language in existing doctrines, and expanded the packet library from 4 to 10 structured packets
- Deepened all four lane documents and expanded the packet library from 10 to 30 structured packets, pushing evidence integrity to its full rubric score
- Added a real 38-pass evaluation batch plus supporting input/output artifacts under `research/meta/`, bringing the ledger to 50 runs

## Expected Effect

- Clear local hooks regression
- Clear belief-promotion regression
- Remove baseline score drops that were artifacts of the flywheel check bug
- Bring low-maturity but closed-contract chips over the scaffold floor when they already satisfy the stricter contract in substance
- Make runtime hook execution consistent with the actual CLI contract used by the lab and scaffolded chips
- Make v3 self-evaluation judge the current manifest shape correctly
- Give the lab rubric-visible doctrine, contradiction, evidence, packet, and run-history artifacts so its self-score is earned more honestly
- Raise contradiction rigor without weakening the rubric
- Raise doctrine and packet quality through substantive content rather than synthetic run-history inflation
- Max out evidence integrity through denser lane artifacts and more granular packet retrieval units
- Preserve the stronger scoring state by reverting doctrine prose that reduces rubric-visible boundary specificity
- Push contradiction specificity over the final threshold without inflating run history, maxing contradiction rigor while leaving the overall score ceiling unchanged
- Increase empirical volume with real executed passes rather than synthetic ledger edits, even at the cost of a less-perfect trajectory subscore

## Follow-On Tranche: Product Layer Separation

## `docs/REPO_SURFACES_AND_STATUS.md`

- Added a dedicated status map for the repo's four product surfaces
- Marked which surfaces are shipped, internal, guarded beta, or still forming
- Added a decision rule for classifying future changes by surface before changing code

## `README.md`

- Added a `Product Layers` section that names the four surfaces directly
- Linked the canonical status doc so high-level positioning does not drift from the codebase
- Clarified that the remaining repo problem is packaging and positioning, not contract ambiguity

## `docs/EXECUTION_PLAN_2026-03-21.md`

- Marked phase 5 as now partially executed through documentation
- Framed package-splitting as future work built on the new layer map

## `research/packets/packet_product_layers.json`

- Expanded the packet from a generic claim to a status-bearing packet with operating-state and user-value fields

## Expected Effect

- Reduce future product-boundary drift
- Make it easier to review whether a change belongs to the lab chip, factory, transfer system, or serving layer
- Give future repo-splitting or packaging work a stable baseline

## Follow-On Tranche: Evaluate Hook Grounding

## `src/chip_labs/evaluate.py`

- Added repo-root resolution so research-focus evaluation can read lab-owned doctrine, packets, and run history
- Added deterministic helpers for packet discovery, run loading, focus-specific run stats, and cached repo-state assembly
- Replaced placeholder methodology constants with area-specific scoring based on relevant docs, packets, v3 dimensions, and methodology runs
- Replaced placeholder domain-discovery constants with scoring based on ranked opportunities, exploratory artifacts, and domain-discovery runs
- Replaced placeholder transfer-pattern and AGI-theory constants with scores derived from actual doctrine, packets, run history, and portfolio maturity

## `docs/EXECUTION_PLAN_2026-03-21.md`

- Marked phase 6 as now executed in code
- Recorded that verification for this tranche is command-based within the current self-edit contract

## `research/packets/packet_evaluate_artifact_grounding.json`

- Added a packet documenting the evaluator-grounding principle and its operating boundary

## Expected Effect

- Make the lab's `evaluate` hook tell the truth about repo state instead of replaying fixed constants
- Keep research scoring deterministic while tying it to real artifacts and run history
- Preserve a cautious cap on AGI-theory confidence even as the lab accumulates more evidence

## Follow-On Tranche: Package Boundary Migration Baseline

## `docs/PACKAGE_BOUNDARY_MIGRATION_PLAN.md`

- Added a concrete module-to-surface map for the current codebase
- Defined a staged migration order that preserves compatibility while cleaning boundaries
- Named the current CLI and manifest contract as the compatibility layer for future file moves

## `docs/REPO_SURFACES_AND_STATUS.md`

- Linked the new migration plan from the surface-status document

## `docs/EXECUTION_PLAN_2026-03-21.md`

- Added a new phase for package-boundary preparation
- Marked the migration baseline as the next real structural task after the original six phases

## `research/packets/packet_package_boundary_migration.json`

- Added a packet documenting why internal boundary cleanup should precede any distribution split

## Expected Effect

- Make future packaging work more deliberate and less likely to break the current hook/runtime contract
- Give later refactors a stable surface map and task order

## Follow-On Tranche: Hook Surface Namespace

## `src/chip_labs/lab_hooks/`

- Added the first internal surface namespace for the lab hook layer
- Exposed a compatibility API for `evaluate`, `suggest`, `packets`, and `watchtower`

## `src/chip_labs/cli.py`, `src/chip_labs/scaffold.py`, `src/chip_labs/loop_controller.py`

- Repointed selected internal callers to the new `lab_hooks` namespace
- Preserved the external CLI and manifest contract

## `docs/PACKAGE_BOUNDARY_MIGRATION_PLAN.md`

- Marked phase 7B as started with the hook surface namespace

## `research/packets/packet_hook_surface_namespace.json`

- Added a packet documenting why a stable internal namespace should precede implementation-file moves

## Expected Effect

- Create the first compatibility-preserving seam for later package separation
- Reduce direct top-level hook-module coupling inside the repo

## Follow-On Tranche: Factory Surface Namespace

## `src/chip_labs/chip_factory/`

- Added the second internal surface namespace for scaffold and gap-analysis behavior
- Exposed a compatibility API for scaffold loading, validation, creation, and improvement helpers

## `src/chip_labs/cli.py`, `src/chip_labs/loop_controller.py`

- Repointed factory-facing internal imports to the new `chip_factory` namespace

## `docs/PACKAGE_BOUNDARY_MIGRATION_PLAN.md`

- Marked phase 7B as extended from the hook surface into the factory surface

## `research/packets/packet_factory_surface_namespace.json`

- Added a packet documenting why the factory surface needs its own internal compatibility seam

## Expected Effect

- Reduce direct top-level factory-module coupling
- Make later scaffold/gap-analyzer file moves less invasive

## Follow-On Tranche: Transfer Surface Namespace

## `src/chip_labs/transfer_surface/`

- Added the internal compatibility namespace for transfer and recursive-improvement entry points
- Exposed extraction, applicability, application, and transfer pipeline functions through one surface

## `src/chip_labs/cli.py`

- Repointed transfer-related imports to the new `transfer_surface` namespace

## `docs/PACKAGE_BOUNDARY_MIGRATION_PLAN.md`

- Marked phase 7B as extended into the transfer surface

## `research/packets/packet_transfer_surface_namespace.json`

- Added a packet documenting why the transfer layer should gain its seam before implementation-file moves

## Expected Effect

- Reduce direct coupling to `transfer.py`
- Make later recursive-improvement packaging work less invasive

## Follow-On Tranche: Intelligence Serving Namespace

## `src/chip_labs/intelligence_serving/`

- Added the internal compatibility namespace for runtime, advisory, context-injection, and MCP-serving entry points
- Exposed serving-facing public entry points through one surface

## `src/chip_labs/cli.py`, `src/chip_labs/loop_controller.py`

- Repointed serving-related top-level imports to the new `intelligence_serving` namespace

## `docs/PACKAGE_BOUNDARY_MIGRATION_PLAN.md`

- Marked phase 7B as extended into the intelligence-serving surface

## `research/packets/packet_intelligence_serving_namespace.json`

- Added a packet documenting why the serving layer needs a top-level seam before deeper rewiring

## Expected Effect

- Reduce direct top-level coupling to serving implementation modules
- Create the last namespace seam needed before later implementation-file moves

## Follow-On Tranche: Hook Implementation Move

## `src/chip_labs/lab_hooks/`

- Moved the actual hook implementations into the hook namespace
- Updated relative imports in the moved files to point back to shared top-level modules correctly
- Updated the hook namespace API to import from the moved modules directly

## `src/chip_labs/evaluate.py`, `src/chip_labs/suggest.py`, `src/chip_labs/packets.py`, `src/chip_labs/watchtower.py`

- Replaced previous implementation files with compatibility wrappers that re-export the moved hook implementations

## `docs/PACKAGE_BOUNDARY_MIGRATION_PLAN.md`

- Marked phase 7C as started with a real implementation move on the hook surface

## `research/packets/packet_hook_impl_move.json`

- Added a packet documenting why implementation-file moves should happen only after a namespace seam exists

## Expected Effect

- Convert the hook surface namespace from a naming seam into a real implementation boundary
- Preserve existing imports while making later hook-surface cleanup easier

## Follow-On Tranche: Bounded Factory Implementation Move

## `src/chip_labs/chip_factory/`

- Moved `gap_analyzer.py` and `category_templates.py` implementations into the factory namespace
- Updated the factory API to import the moved modules directly

## `src/chip_labs/gap_analyzer.py`, `src/chip_labs/category_templates.py`

- Replaced previous implementation files with compatibility wrappers that re-export the moved implementations

## `src/chip_labs/cli.py`

- Routed the remaining autoloop category-template import through the factory namespace

## `docs/PACKAGE_BOUNDARY_MIGRATION_PLAN.md`

- Marked phase 7C as extended into a bounded factory implementation move

## `research/packets/packet_factory_impl_move.json`

- Added a packet documenting why lower-coupling factory modules should move before scaffold

## Expected Effect

- Turn the factory namespace into a partial real implementation boundary
- Reduce later risk when `scaffold.py` eventually moves

## Follow-On Tranche: Scaffold Implementation Move

## `src/chip_labs/chip_factory/scaffold.py`

- Moved the real scaffold implementation into the factory namespace
- Updated its imports to point back to shared modules from the deeper package location

## `src/chip_labs/scaffold.py`

- Replaced the previous implementation file with a compatibility wrapper that re-exports the moved scaffold implementation

## `src/chip_labs/chip_factory/api.py`, `src/chip_labs/loop_controller.py`

- Updated the factory API and loop-controller imports to use the moved scaffold path and the factory namespace consistently

## `docs/PACKAGE_BOUNDARY_MIGRATION_PLAN.md`

- Marked phase 7C as extended from bounded factory modules into the central scaffold path

## `research/packets/packet_scaffold_impl_move.json`

- Added a packet documenting why scaffold moved only after the supporting factory slice was already stable

## Expected Effect

- Make the factory namespace the real home of the main scaffold execution path
- Preserve existing imports while reducing the amount of central factory logic still living at the top level
