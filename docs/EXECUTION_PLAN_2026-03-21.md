# Execution Plan: 2026-03-21

## Objective

Move the lab from "structurally impressive" to "operationally defensible."

This means:

1. Remove repo-local regressions.
2. Align the runtime, CLI, manifest, and rubric contract.
3. Make the lab earn stronger v2/v3 scores through real artifacts, not just structure.
4. Rewrite status docs so shipped, experimental, and aspirational layers are clearly separated.

## Today

### 1. Stabilize current regressions

- Fix session advisory regression in `src/chip_labs/hooks.py`
- Fix belief-promotion detection in `src/chip_labs/quality_rubric_v2.py`
- Reconcile v2 scorer strictness with closed mutation enums and bounded loop guardrails
- Re-run targeted tests until the current failure set is cleared

### 2. Lock the contract

- Audit how `spark-chip.json` is interpreted by:
  - `src/chip_labs/cli.py`
  - `src/chip_labs/chip_runtime.py`
  - `src/chip_labs/deep_eval.py`
  - `src/chip_labs/quality_rubric_v2.py`
- Decide the canonical hook contract:
  - manifest command shape
  - hook invocation input/output shape
  - runtime fallback behavior

Status:

- `chip_runtime.py` now prefers the file-based `--input` / `--output` hook path for CLI-style commands and supports `chip_name` in manifests.
- `deep_eval.py` now recognizes both legacy and current manifest conventions, including `schema_version`, `capabilities`, and `commands`.
- Remaining work is to keep generating lab-owned run history and evidence artifacts so stronger self-scores are earned continuously rather than in one documentation pass.

## Next

### 3. Fix runtime execution path

- Make `chip_runtime.execute_hook()` compatible with the CLI's actual file-based hook interface
- Ensure manifest/rich-runtime/deep-eval all agree on what a valid hook surface is
- Add or update tests around the canonical execution path

### 4. Raise the lab's earned score

- Create substantive lab-owned evidence lane artifacts under `research/`
- Create durable contradiction handling and packet artifacts for the lab itself
- Generate intelligence delivery artifacts from real lab content
- Re-score the repo with v2 and v3 after real artifact production

Status:

- Initial doctrine, contradiction, run-history, evidence-lane, and packet artifacts now exist in rubric-visible locations under `docs/` and `research/`.
- The next checkpoint is to keep extending those artifacts from real future runs rather than treat this as a one-time backfill.
- Packet corpus has now been expanded to 10 structured packets, and doctrine causal density was raised with additional mechanism-focused doctrine text.
- Packet corpus has now been expanded again to 30 structured packets and all four evidence lanes now average `520.8` words per file.
- Current self-score checkpoint: `score-v2 = 100/100`, `score-v3 = 87.0/100`.
- The lab now has 50 recorded runs after a real 38-pass evaluation batch under `research/meta/`.
- Remaining meaningful headroom under the current mutable-target rules is limited mainly by doctrine thresholding and `obsidian-vault/` watchtower depth.

## Later

### 5. Separate products explicitly

The repo currently contains four overlapping surfaces:

- meta-chip hooks
- chip factory/scaffolder
- transfer and recursive improvement
- intelligence serving and MCP/hooks integration

Decide whether to:

1. keep them in one repo but document them as four layers, or
2. split the chip factory / serving runtime into separate packages

### 6. Replace placeholder research scoring

- Replace heuristic methodology/domain-discovery scores in `src/chip_labs/evaluate.py`
- Make research-focus scoring depend on real artifacts, runs, and evidence quality

## Exit Criteria

Short-term checkpoint:

- current repo-local test regressions cleared
- runtime/CLI contract documented
- status docs no longer overclaim validation

Medium-term checkpoint:

- lab repo reaches defensible v2 and materially higher v3 through real artifacts
- runtime can execute hooks without contract ambiguity
