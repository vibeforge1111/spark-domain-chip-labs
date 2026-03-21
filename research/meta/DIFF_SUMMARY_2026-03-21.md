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

## Follow-On Tranche: Factory Support Implementation Move

## `src/chip_labs/chip_factory/`

- Moved `methodology.py` and `graduation.py` implementations into the factory namespace
- Expanded the factory namespace exports to include methodology and graduation helpers

## `src/chip_labs/methodology.py`, `src/chip_labs/graduation.py`

- Replaced the previous implementation files with compatibility wrappers that re-export the moved implementations

## `research/packets/packet_factory_support_impl_move.json`

- Added a packet documenting why the final factory support modules should follow scaffold behind the namespace

## Expected Effect

- Make the factory namespace the real home of the remaining factory support behavior
- Preserve top-level imports while significantly reducing factory logic still implemented at the top level

## Follow-On Tranche: Intelligence Server Implementation Move

## `src/chip_labs/intelligence_serving/intelligence_server.py`

- Moved the real intelligence-serving implementation behind the serving namespace
- Updated the moved module's `quality_rubric` import for the deeper package path

## `src/chip_labs/intelligence_server.py`

- Replaced the previous implementation file with a compatibility wrapper that re-exports the moved serving implementation

## `src/chip_labs/intelligence_serving/api.py`

- Repointed `refresh_skill` and `serve_context` imports to the moved implementation instead of the top-level compatibility wrapper

## `research/packets/packet_intelligence_server_impl_move.json`

- Added a packet documenting why the first serving implementation move should be the central intelligence module instead of the more coupled runtime path

## Expected Effect

- Turn the serving namespace into a partial real implementation boundary
- Preserve existing imports while reducing the amount of serving logic still implemented at the top level

## Follow-On Tranche: Serving Advisory Implementation Move

## `src/chip_labs/intelligence_serving/chip_advisor.py`, `src/chip_labs/intelligence_serving/chip_context_injector.py`

- Moved the advisory and context-injection implementations behind the serving namespace
- Updated their runtime imports for the deeper package location

## `src/chip_labs/chip_advisor.py`, `src/chip_labs/chip_context_injector.py`

- Replaced the previous implementation files with compatibility wrappers that re-export the moved serving implementations

## `src/chip_labs/intelligence_serving/api.py`

- Repointed advisory and context-injection imports to the moved implementations instead of the top-level compatibility wrappers

## `research/packets/packet_serving_advisory_impl_move.json`

- Added a packet documenting why advisory and context injection are the next safe serving modules to move before runtime

## Expected Effect

- Extend the serving namespace into a larger real implementation boundary
- Preserve existing imports while reducing serving-surface logic still implemented at the top level

## Follow-On Tranche: Serving MCP Implementation Move

## `src/chip_labs/intelligence_serving/chip_mcp_server.py`

- Moved the MCP server implementation behind the serving namespace
- Updated its runtime imports for the deeper package path

## `src/chip_labs/chip_mcp_server.py`

- Replaced the previous implementation file with a compatibility wrapper that re-exports the moved serving implementation

## `src/chip_labs/intelligence_serving/api.py`

- Repointed the `ChipMCPServer` import to the moved implementation instead of the top-level compatibility wrapper

## `research/packets/packet_serving_mcp_impl_move.json`

- Added a packet documenting why the MCP server is the next safe serving module to move before runtime

## Expected Effect

- Make the serving namespace the real home of nearly all serving entrypoints except runtime
- Preserve existing imports while reducing one more large top-level serving module

## Follow-On Tranche: Serving Runtime Implementation Move

## `src/chip_labs/intelligence_serving/chip_runtime.py`

- Moved the runtime implementation behind the serving namespace
- Updated it to import the namespace-local intelligence server implementation

## `src/chip_labs/chip_runtime.py`

- Replaced the previous implementation file with a compatibility alias that points at the moved serving runtime

## `src/chip_labs/intelligence_serving/api.py`, `src/chip_labs/intelligence_serving/chip_advisor.py`, `src/chip_labs/intelligence_serving/chip_context_injector.py`, `src/chip_labs/intelligence_serving/chip_mcp_server.py`

- Repointed serving-surface runtime imports to the moved implementation instead of the top-level compatibility wrapper

## `src/chip_labs/intelligence_server.py`, `src/chip_labs/chip_advisor.py`, `src/chip_labs/chip_context_injector.py`, `src/chip_labs/chip_mcp_server.py`, `src/chip_labs/chip_runtime.py`

- Converted top-level serving wrappers into module aliases so patches against the legacy module paths apply to the moved implementations too

## `research/packets/packet_serving_runtime_impl_move.json`

- Added a packet documenting why the runtime should move last within the serving surface

## Expected Effect

- Make the serving namespace the real home of the full serving implementation surface
- Preserve existing imports while reducing top-level serving modules to compatibility wrappers

## Follow-On Tranche: Transfer Implementation Move

## `src/chip_labs/transfer_surface/transfer.py`

- Moved the transfer implementation behind the transfer namespace
- Updated its rubric import for the deeper package path

## `src/chip_labs/transfer.py`

- Replaced the previous implementation file with a compatibility alias that points at the moved transfer implementation

## `src/chip_labs/transfer_surface/api.py`

- Repointed transfer-surface exports to the moved implementation instead of the top-level compatibility alias

## `research/packets/packet_transfer_impl_move.json`

- Added a packet documenting why the transfer surface should start with `transfer.py` before moving other adjacent modules

## Expected Effect

- Turn the transfer namespace into a partial real implementation boundary
- Preserve existing imports while reducing one more top-level surface module

## Follow-On Tranche: Scoring Engine Implementation Move

## `src/chip_labs/transfer_surface/scoring_engine.py`

- Moved the scoring-engine implementation behind the transfer namespace

## `src/chip_labs/scoring_engine.py`

- Replaced the previous implementation file with a compatibility alias that points at the moved scoring engine

## `research/packets/packet_scoring_engine_impl_move.json`

- Added a packet documenting why the standalone scoring engine should move before the loop controller

## Expected Effect

- Extend the transfer namespace into another real implementation boundary
- Preserve existing imports while reducing one more top-level transfer-surface module

## Follow-On Tranche: Loop Controller Implementation Move

## `src/chip_labs/transfer_surface/loop_controller.py`

- Moved the loop-controller implementation behind the transfer namespace
- Updated its imports for the deeper package path

## `src/chip_labs/loop_controller.py`

- Replaced the previous implementation file with a compatibility alias that points at the moved loop controller

## `src/chip_labs/transfer_surface/api.py`, `src/chip_labs/transfer_surface/__init__.py`, `src/chip_labs/cli.py`

- Exported loop-controller types and controller entrypoints through the transfer namespace
- Repointed the CLI autoloop import to the transfer namespace instead of the top-level compatibility alias

## `research/packets/packet_loop_controller_impl_move.json`

- Added a packet documenting why the loop controller should move after the lower-coupling transfer modules

## Expected Effect

- Make the transfer namespace the real home of the main transfer/orchestration implementation surface
- Preserve existing imports while reducing the remaining top-level transfer-surface orchestration module

## Follow-On Tranche: Hooks Serving Namespace Cleanup

## `src/chip_labs/hooks.py`

- Repointed internal serving imports to `intelligence_serving` modules instead of the legacy top-level serving aliases
- Left hook behavior unchanged while reducing dependency on the compatibility layer from inside the repo

## `research/packets/packet_hooks_serving_namespace_cleanup.json`

- Added a packet documenting why internal serving callers should prefer the serving namespace once the implementation lives there

## Expected Effect

- Make the top-level serving modules more purely compatibility-oriented
- Tighten the serving boundary by reducing internal reach-through to legacy aliases

## Follow-On Tranche: Factory Serving Import Cleanup

## `src/chip_labs/chip_factory/gap_analyzer.py`

- Repointed the `build_skill` import to the namespace-local serving implementation instead of the legacy top-level alias

## `research/packets/packet_factory_serving_import_cleanup.json`

- Added a packet documenting why factory code should call serving through the serving namespace now that the implementation lives there

## Expected Effect

- Remove one remaining internal factory-to-serving alias reach-through
- Keep the top-level serving modules more purely compatibility-oriented

## Follow-On Tranche: Wrapper Alias Hardening

## `src/chip_labs/evaluate.py`, `src/chip_labs/suggest.py`, `src/chip_labs/packets.py`, `src/chip_labs/watchtower.py`

- Converted the remaining top-level hook wrappers from `*` re-exports into module aliases

## `src/chip_labs/scaffold.py`, `src/chip_labs/gap_analyzer.py`, `src/chip_labs/category_templates.py`, `src/chip_labs/methodology.py`, `src/chip_labs/graduation.py`

- Converted the remaining top-level factory wrappers from `*` re-exports into module aliases

## `research/packets/packet_wrapper_alias_hardening.json`

- Added a packet documenting why compatibility aliases are stronger than plain re-export wrappers once implementations move behind namespaces

## Expected Effect

- Make compatibility behavior consistent across all four repo surfaces
- Preserve public imports while strengthening alias identity and patch behavior

## Follow-On Tranche: Phase 7D Package Decision

## `docs/PACKAGE_BOUNDARY_MIGRATION_PLAN.md`

- Replaced the placeholder packaging question with an explicit decision to stay in one repo/package for now
- Added concrete split triggers and a rule for when to revisit the decision

## `docs/REPO_SURFACES_AND_STATUS.md`, `README.md`, `docs/EXECUTION_PLAN_2026-03-21.md`

- Propagated the same packaging decision across the high-level repo narrative and execution plan

## `research/packets/packet_package_decision_single_repo.json`

- Added a packet documenting why the current decision is one package with internal seams instead of an early split

## Expected Effect

- Remove ambiguity about the current packaging posture
- Keep future splitting as an explicit option, but only when repo-state triggers justify it

## Follow-On Tranche: Phase 7D Operational Validation Batch

## `research/meta/VALIDATION_BATCH_2026-03-21_phase7d.json`, `research/meta/VALIDATION_BATCH_2026-03-21_phase7d.md`

- Added a fresh post-decision validation snapshot covering both scorers and a broad targeted regression pack

## `research/meta/runs.jsonl`

- Appended three real validation entries for v2 scoring, v3 scoring, and the targeted regression suite

## `research/packets/packet_operational_validation_batch.json`

- Added a packet documenting why structural work should be converted into observable operating history through real validation passes

## Expected Effect

- Turn the latest structural and packaging work into ledger-visible operating evidence
- Keep the repo's claimed stability grounded in executed scorer and regression results rather than only in code movement

## Follow-On Tranche: Phase 8 Workspace Serving Fallback

## `src/chip_labs/intelligence_serving/chip_runtime.py`

- Added a default-search helper that appends the active workspace chip to the portfolio when the process is already running inside a chip repo
- Kept explicit `search_dir` calls unchanged so external callers still control the search scope directly

## `src/chip_labs/intelligence_serving/chip_context_injector.py`

- Added an active-workspace fallback so `inject_context_for_task()` uses the current chip when lexical chip selection returns nothing

## `tests/test_chip_runtime.py`, `tests/test_chip_context_injector.py`

- Added coverage for current-workspace portfolio inclusion and current-workspace context fallback

## `research/packets/packet_current_workspace_serving_fallback.json`

- Added a packet documenting why repo-local serving should include the active workspace chip even when it is outside the Desktop prefix registry

## Expected Effect

- Prevent empty `serve-intelligence` outputs for repo-local work inside this chip
- Keep the external relevance floor intact while making the active workspace chip first-class in local serving flows

## Follow-On Tranche: Phase 8 Serving Validation

## `research/meta/serve_output_phase7d_2026-03-21.json`, `research/meta/serve_intelligence_output_phase7d_2026-03-21.json`, `research/meta/advise_output_phase7d_2026-03-21.json`

- Captured fresh raw outputs from the repaired serving flows

## `research/meta/WORKSPACE_SERVING_VALIDATION_2026-03-21_phase8.json`, `research/meta/WORKSPACE_SERVING_VALIDATION_2026-03-21_phase8.md`

- Added a structured summary of the repo-local serving validation batch, including the repaired `serve-intelligence` behavior and the still-noisy advisory ranking

## `research/meta/runs.jsonl`

- Appended three real serving-validation entries covering `serve`, `serve-intelligence`, and `advise`

## `research/packets/packet_workspace_serving_validation.json`

- Added a packet documenting why repo-local serving validation is a product check rather than a cosmetic one

## `docs/EXECUTION_PLAN_2026-03-21.md`

- Extended the execution plan with the phase 8 workspace-aware serving checkpoint and the remaining advisory-ranking gap

## Expected Effect

- Convert the workspace-serving repair into ledger-visible operating history
- Narrow the next serving tranche to advisory ranking quality instead of active-workspace discovery

## Follow-On Tranche: Phase 8 Domain-Hint Advisory Filter

## `src/chip_labs/intelligence_serving/chip_advisor.py`

- Made explicit domain hints filter the candidate portfolio before advisory relevance scoring
- Tightened token matching so `chip-labs` no longer matches unrelated `domain-chip-*` repos just because they share the generic token `chip`

## `tests/test_chip_advisor.py`

- Strengthened the domain-hint selection test and added a regression test for filtering unrelated chips

## `research/meta/advise_output_phase7d_2026-03-21.json`

- Captured a fresh explicit-domain advisory output showing `chips_consulted = ["domain-chip-labs"]`

## `research/meta/WORKSPACE_SERVING_VALIDATION_2026-03-21_phase8.json`, `research/meta/WORKSPACE_SERVING_VALIDATION_2026-03-21_phase8.md`

- Updated the repo-local serving validation summary to reflect that the explicit hinted advisory path is now clean

## `research/packets/packet_domain_hint_advisory_filter.json`

- Added a packet documenting why domain hints should constrain candidate chips instead of acting as loose free-text bias

## Expected Effect

- Remove off-domain consultation from explicit `chip-labs` advisory calls
- Reduce the remaining serving-product uncertainty to unhinted advisory ranking only

## Follow-On Tranche: Phase 8 Unhinted Workspace Advisory

## `src/chip_labs/intelligence_serving/chip_advisor.py`

- Added an active-workspace fallback for no-match advisory selection so repo-local unhinted requests do not fail closed

## `tests/test_chip_advisor.py`

- Added a regression test proving the unhinted repo-local advisory path falls back to `domain-chip-labs`

## `research/meta/advise_output_phase8_unhinted_2026-03-21.json`

- Captured a fresh unhinted advisory output showing `chips_consulted = ["domain-chip-labs"]`

## `research/meta/WORKSPACE_SERVING_VALIDATION_2026-03-21_phase8.json`, `research/meta/WORKSPACE_SERVING_VALIDATION_2026-03-21_phase8.md`

- Extended the repo-local serving validation summary to include the repaired unhinted advisory path

## `research/packets/packet_unhinted_workspace_advisory_fallback.json`

- Added a packet documenting why repo-local unhinted advisory should use the active workspace chip instead of returning nothing

## Expected Effect

- Remove the empty-result failure mode from unhinted repo-local advisory
- Narrow the remaining serving uncertainty to broader multi-chip ranking outside workspace-local fallback cases

## Follow-On Tranche: Live Portfolio Audit

## `research/meta/portfolio_v3_audit_2026-03-21.json`

- Added a fresh full-portfolio v3 report generated from the current Desktop inventory

## `research/meta/PORTFOLIO_AUDIT_2026-03-21.json`, `research/meta/PORTFOLIO_AUDIT_2026-03-21.md`

- Added a dated portfolio audit that separates the leadership tier, middle tier, scaffold cluster, and invalid inventory

## `research/meta/REQUEST_PACKET_2026-03-21_portfolio_audit.json`

- Added the request packet capturing the scope, commands, and constraints for the live portfolio audit

## Expected Effect

- Replace stale or assumed portfolio narratives with a live dated snapshot
- Make it easier to decide which chips deserve active investment versus archival or quarantine

## Follow-On Tranche: Top-Tier Deep Dive

## `research/meta/TOP_TIER_DEEP_DIVE_2026-03-21.json`, `research/meta/TOP_TIER_DEEP_DIVE_2026-03-21.md`

- Added a deep-dive analysis of the current top 6 chips, including v2/v3 contrast, operating read, and per-chip risks

## `research/meta/REQUEST_PACKET_2026-03-21_top_tier_deep_dive.json`

- Added the request packet capturing the scope and verification basis for the leadership-tier deep dive

## Expected Effect

- Turn the top tier from a ranking list into an actual strategic read
- Clarify which chips are strong because of scale, which are strong because of doctrine quality, and which are strong but still risky

## Follow-On Tranche: Tomorrow Focus Documentation

## `docs/TOMORROW_FOCUS_2026-03-22.md`

- Added a one-session plan grounded in what was actually completed today
- Summarized completed chip-labs work:
  - contract stabilization
  - package seams
  - serving repairs
  - self-score checkpoint
  - portfolio audit artifacts
- Summarized completed startup-yc work:
  - routing improvements
  - fallback hardening
  - memory prioritization
  - synthesis focus
  - explicit note that the idea-ranking experiment was reverted
- Reduced tomorrow's scope to four concrete tasks that are realistically finishable

## `docs/EXECUTION_PLAN_2026-03-21.md`

- Added a short next-session reference pointing to the new tomorrow-focus document

## `research/meta/REQUEST_PACKET_2026-03-21_tomorrow_focus_documentation.json`

- Added a request packet documenting the purpose, file scope, and intended follow-up for this documentation-only tranche

## Expected Effect

- Prevent tomorrow from starting with a vague backlog
- Keep the next session focused on product behavior and audit clarity rather than another broad refactor
- Preserve a transparent record of why the immediate next tasks are these four and not a larger wish list
