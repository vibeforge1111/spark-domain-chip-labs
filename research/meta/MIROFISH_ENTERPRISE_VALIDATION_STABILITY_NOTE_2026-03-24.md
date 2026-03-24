# MiroFish Enterprise Validation Stability Note: 2026-03-24

## Scope

Complete the planned post-choice-conversion enterprise validation replay, but first remove process-dependent simulation drift so that a saved spec and seed actually replay to the same result.

Code changed:

- `src/chip_labs/mirofish/simulation.py`

Output artifacts:

- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_VALIDATION_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_VALIDATION_2026-03-24.json`

## What Was Wrong

The simulation cooldown path used Python's built-in `hash((pid, domain_id)) % 3` to create per-pair variation between persona-domain pairs.

That is not stable across Python processes because `hash()` is randomized by `PYTHONHASHSEED`. As a result, the same saved spec and the same MiroFish seed could drift between runs launched in different shells.

This was the actual blocker before the full `515`-domain rerun. The methodology was not ready to be trusted end to end until replay stability was restored.

## Fix

Replace the cooldown variation with a deterministic md5-based bucket keyed by `persona_id` and `domain_id`.

This keeps the intended behavior:

- different persona-domain pairs still settle on slightly different cooldown lengths
- the intervention stays narrow to the pacing mechanic
- the replay becomes process-stable

This tranche does not add a new enterprise boost, does not lower retention thresholds, and does not change benchmark membership logic.

## Validation Read

Cross-process replay check:

- one enterprise replay was run with `PYTHONHASHSEED=11`
- the same replay was run again with `PYTHONHASHSEED=99`
- the focus-domain outputs matched exactly

Stable validation replay results:

1. `startup-yc` remains the top ensemble domain at `3.23%`
2. `cursor-copilot` remains second at `2.67%`
3. `ai-security-questionnaire-copilot` is the strongest enterprise ensemble domain at `1.51%`
4. `ai-renewal-risk-briefing-copilot` is next at `0.74%`
5. `ai-rfp-response-copilot` lands at `0.59%`
6. `ai-compliance-evidence-copilot` lands at `0.24%`

Benchmark median ensemble adoption in the stable validation replay is `0.66%`.

Enterprise focus read:

- `ai-security-questionnaire-copilot` stays above the median and remains the strongest enterprise ensemble candidate
- `ai-renewal-risk-briefing-copilot` also stays above the median, but only narrowly, and still looks like an attention-to-retention problem
- `ai-rfp-response-copilot` remains just below the median and still looks primarily blocked at interest-to-choice conversion
- `ai-compliance-evidence-copilot` remains clearly below the median and does not justify another pre-rerun methodology mutation

## Decision

Keep the determinism fix and treat this validation artifact as the trusted handoff before the full portfolio rerun.

Why:

- it removes a real replay-integrity bug
- it preserves the current methodology rather than adding another speculative tuning step
- it confirms that the enterprise cluster is now stable enough to widen back to the full `515`-domain run

## Next Batch

Run the repo-local `515`-domain portfolio wrapper and save the ranked readout under `research/meta/` before refreshing any dashboard or export surfaces.
