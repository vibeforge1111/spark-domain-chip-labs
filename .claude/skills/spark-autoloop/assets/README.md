# spark-autoloop assets

Reusable templates the skill points to. Copy and edit; none run as-is.

| File | Use at | What it is |
| --- | --- | --- |
| `eval_harness.workflow.js` | Step 10 | Blind runner+judge evaluation across modes. Paste into a `Workflow()` call, edit `DATA`. The runner/judge separation is what stops the doctrine author from grading their own work. |
| `calibration_sampler.py` | Step 9b | Sample real cases with measured outcomes into an outcome-grounded oracle. Replace `load_records()`. |
| `calibration_metrics.py` | Step 9b | Deterministic band accuracy, Spearman vs measured outcome, ship precision/recall, multi-seed majority vote, paired bootstrap CI. No LLM in any number. |
| `hybrid_combiner.py` | optional | Doctrine strategy gate + external outcome predictor as two auditable channels, with the validation guard. |

All assets are local-only by default. Never commit a benchmark that embeds private real-world content (handles, customer data, raw outcomes) to a public repo.
