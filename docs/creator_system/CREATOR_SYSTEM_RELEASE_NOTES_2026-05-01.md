# Creator System Release Notes - 2026-05-01

## Shipped In This Continuation

- Generator proof domains now cover artifact quality, safe tool operation,
  MiroFish content simulation, doctor security, Startup YC operator validation,
  and retrieval-memory boundaries.
- Tool operation checks replay blocked smoke, stale recompute evidence, missing
  artifacts, and unsafe secret-handling requests with rollback reports.
- `creator-run-doctor --recompute` emits repair replay and quarantine metadata
  for stale evidence and unsafe packet claims.
- Startup YC has a validation pack with held-out founder-advice cases,
  multi-seed requirements, calibration gates, privacy review, rollback review,
  and publication approval gates.
- Retrieval memory has a local contract and fixtures for correct prior
  decisions, stale memory, contradicted memory, residue contamination, and
  unreviewed network-shareable context.
- `creator-mission-status` provides a read-only product adapter packet for
  Builder, Telegram, Spawner, Canvas, and Kanban without wiring runtime
  publication controls.
- The README now includes current claim levels and an executable command index.
- Creator-system CI now runs focused lint, proof-domain tests, strict Startup YC
  smoke, and template checks on relevant pushes and pull requests.
- The handoff, master plan, production readiness, promotion gates, and Phase 2
  backlog now point to the same CI-backed read-only product adapter boundary.
- Product consumer PR ledger now records refreshed Builder and Telegram branch
  heads with passing remote CI.
- MiroFish content simulation now has saved route, JSON result, and Markdown
  readout examples under `examples/mirofish-content/`.
- The product-surface mission-status fixture now references the saved MiroFish
  content route as read-only evidence and emits Canvas edges only for present
  packets.
- Artifact quality now has saved JSON and Markdown reports for the review-ready
  design/PR fixture, and product mission status references that report as
  read-only `artifact_quality` evidence.
- Retrieval memory now has a saved pass check for the correct-prior-decision
  fixture, and product mission status references it as read-only
  `retrieval_memory` evidence with network absorption still blocked.
- Tool operation now has a saved pass check for a safe local
  `creator-run-smoke` operation, and product mission status references it as
  read-only `tool_operation` evidence without granting execution authority.
- Recompute/provenance documentation now distinguishes supported
  provenance-tagged generated runs from the curated Startup YC fixture, which
  still requires external Startup Bench/source-report rerun adapters for full
  recompute.
- Product consumer branch ledger now records the refreshed Builder PR head
  `6525942` with green remote CI.
- Startup YC external recompute work is now split into explicit adapter gates
  for Startup Bench transfer, specialization-path absorption, broad transfer,
  and Swarm packet regeneration.
- `creator-run-smoke --recompute` now performs the Startup YC external transfer
  check when the source selector report is locally available.
- `creator-run-smoke --recompute` also compares Startup YC baseline, candidate,
  and absorption summaries to the external absorption proof report when that
  source report is locally available.
- `creator-run-smoke --recompute` now compares Startup YC broad-transfer
  aggregates and scenario rows to the external selector report when that source
  report is locally available.
- `creator-run-smoke --recompute` now compares Startup YC Swarm packet evidence
  and publication-boundary fields to the recomputed report bundle.
- `creator-run-smoke --recompute --fail-on-blocked` now passes for the Startup
  YC fixture when the sibling external source repo is present and the
  `startup_yc_external_v1` provenance hashes match.
- `creator-run-doctor --recompute` now quarantines stale Startup YC external
  recompute failures through a dedicated adversarial fixture.
- `creator-mission-status` now has an executable regression proving blocked
  canonical smoke plus a `swarm_shared` request stays blocked and read-only in
  Builder, Telegram, Spawner, Canvas, and Kanban views.
- `startup-yc-promotion-gate-check` now emits a machine-readable blocked packet
  for `network_absorbable` and fails with `--fail-on-blocked` until every
  Startup YC promotion gate has explicit pass evidence.
- `startup-yc-multi-seed-check` now makes the multi-seed validation gate
  executable: required tracks, seed counts, held-out pass flags, constraint pass
  flags, and minimum delta are checked while `network_absorbable` remains false.
- `startup-yc-heldout-check` now makes the held-out founder-advice gate
  executable: every held-out case needs evaluated response evidence for
  operator moves, rejected claims, success gate, and privacy lane.
- `startup-yc-review-gates-check` now makes the remaining human review gates
  executable: operator calibration, privacy review, rollback review, and
  publication approval require structured evidence before final promotion.
- `startup-yc-promotion-evidence-check` now makes saved promotion evidence
  coherent: bundled gate outputs must have expected schemas, match the same
  validation plan, and report passed gates before final review can use them.
- `startup-yc-validation-suite` now runs all Startup YC gate checks together and
  still blocks final promotion unless the validation plan explicitly records
  approved gates, claim removal, and publication permission.
- `startup-yc-operator-validation/validation_suite_blocked.json` now preserves
  the current blocked validation-suite packet, with tests that recompute the
  critical blockers from the validation plan.
- Creator-system CI now lints `startup_yc_promotion.py` and explicitly runs the
  Startup YC validation suite without `--fail-on-blocked`, preserving the
  expected blocked command path.
- `startup-yc-validation-suite.schema.json` now anchors saved validation-suite
  packets and rejects any packet claiming `network_absorbable=true`.
- `startup-yc-gate-check-result.schema.json` now anchors individual Startup YC
  gate-check outputs and rejects any gate packet claiming
  `network_absorbable=true`.
- Startup YC gate-check outputs now include raw-evidence input hashes, and
  promotion evidence bundles block when saved gate outputs are stale against
  their source evidence files.
- Startup YC CLI coverage now generates gate outputs, bundles them, verifies
  the coherent bundle, and then proves the same bundle blocks after raw evidence
  changes.
- `startup-yc-validation-suite.schema.json` now validates each saved subcheck
  through the individual gate-check schema, and the blocked suite fixture was
  regenerated with provenance-bearing subcheck packets.
- `startup-yc-validation-evidence.schema.json` now anchors raw Startup YC
  multi-seed, held-out, review-gate, and promotion-bundle inputs before they
  become gate-check outputs.
- `startup-yc-validation-evidence-check` now gives operators an executable
  raw-evidence shape gate before running Startup YC gate commands.
- Creator-system CI now runs that raw-evidence shape gate against
  `shape_only_multi_seed_evidence.json`, a bounded command-path fixture that
  does not count as Startup YC multi-seed validation or network absorption
  evidence.
- Startup YC operator-validation tests now prove that the shape-only fixture
  remains blocked by the real multi-seed gate.
- Raw validation-evidence shape-check outputs now include source input hashes
  so saved shape evidence can be compared with freshly checked evidence.
- Generator acceptance tests now assert generated report input hashes match the
  current benchmark/source artifacts and pass recompute provenance checks.
- `startup-yc-validation-evidence-check-result.schema.json` now anchors raw
  evidence shape-check outputs and rejects accidental `network_absorbable=true`
  claims.
- Startup YC CLI tests now validate saved `startup-yc-validation-evidence-check`
  output against that result schema.
- The raw evidence check-result schema now distinguishes present evidence with
  input hashes from absent evidence with explicit missing-input records.
- The same schema now rejects impossible raw-evidence verdicts, such as
  `passed` with blockers or `blocked` without blockers.
- Creator-system CI now writes the raw validation-evidence check output and
  validates it against the check-result schema.
- Creator-system CI now also writes `startup-yc-validation-suite` output and
  validates it against the validation-suite schema plus gate-check schema refs.
- Startup YC gate-check and validation-suite schemas now reject incoherent
  verdict packets such as `passed` with blockers or `blocked` with no blockers.
- The saved blocked Startup YC validation-suite fixture now has a
  path-normalized full-payload equality regression against a fresh suite run,
  covering provenance drift.
- Creator-system CI now validates both freshly generated and saved blocked
  Startup YC validation-suite packets against the referenced schema pair.
- Creator-system CI focused lint now includes
  `tests/test_startup_yc_operator_validation.py`, where the Startup YC
  schema/provenance regression checks live.
- Creator-system CI now opts JavaScript actions into Node.js 24 to avoid the
  GitHub-hosted runner Node.js 20 deprecation path.
- Creator-system CI now validates the shape-only raw Startup YC evidence
  fixture against the raw validation-evidence schema before producing a
  shape-check result.
- The raw Startup YC validation-evidence schema now rejects
  `network_absorbable=true` while preserving the shape-only fixture's explicit
  false boundary.

## Current Claim Boundary

- Startup YC remains `transfer_supported`, not `network_absorbable`.
- Generated proof domains remain local or `candidate_review` unless a stronger
  evidence tier is explicitly proven.
- Product runtime wiring remains deferred. Builder, Telegram, Spawner, Canvas,
  and Kanban should consume `creator-mission-status`, not invent independent
  truth.
- Network absorption remains blocked until multi-seed validation,
  human/operator calibration, privacy review, rollback review, and publication
  approval are complete.

## Verification

```bash
python -m pytest tests/test_retrieval_memory.py tests/test_creator_system_docs.py tests/test_startup_yc_operator_validation.py tests/test_tool_operation.py tests/test_artifact_quality.py tests/test_mirofish_content_simulation.py tests/test_creator_generator_acceptance.py tests/test_creator_run.py tests/test_creator_run_examples.py -q
python -m chip_labs.cli creator-run-smoke docs/creator_system/examples/startup-yc-creator-run --fail-on-blocked --fail-on-warn
python -m chip_labs.cli creator-run-template-check --fail-on-blocked
```

Latest focused creator-system suite result before CI push: `135 passed`.
