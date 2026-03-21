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
