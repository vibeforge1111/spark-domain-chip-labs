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
- Creator-system CI now uses Node.js 24-native `actions/checkout@v6` and
  `actions/setup-python@v6` instead of relying on the forced-runtime workaround.
- Creator-system CI now validates the shape-only raw Startup YC evidence
  fixture against the raw validation-evidence schema before producing a
  shape-check result.
- The raw Startup YC validation-evidence schema now rejects
  `network_absorbable=true` while preserving the shape-only fixture's explicit
  false boundary.
- Startup YC raw validation-evidence tests now prove that
  `network_absorbable=true` is rejected across multi-seed, held-out,
  review-gate, and promotion-bundle raw inputs.
- Startup YC operator-validation tests now check the four Startup YC JSON
  Schemas are valid Draft 2020-12 schemas before payload validation.
- Startup YC validation-suite CLI output is now validated against the
  referenced validation-suite and gate-check schema pair in its CLI regression.
- Startup YC individual gate-check CLI regressions now validate their JSON
  outputs against `startup-yc-gate-check-result.schema.json`.
- Startup YC malformed raw-evidence CLI regression now validates its blocked
  shape-check output against the shape-check result schema.
- `startup-yc-validation-plan.schema.json` now anchors the Startup YC
  validation plan, including the required promotion gates, multi-seed floor,
  publication boundary, and explicit `network_absorbable` prohibition.
- Creator-system CI now validates the saved Startup YC `validation_plan.json`
  against the validation-plan schema before running raw-evidence and suite
  schema checks.
- Startup YC saved fixture notes now distinguish source-report recompute checks
  from full external benchmark reruns, so the artifact text matches the current
  `startup_yc_external_v1` provenance boundary.
- `creator-run-smoke` output now includes `evidence_mode` (`saved` or
  `recomputed`), and tool-operation checks reject `--recompute` command packets
  whose parsed smoke result still claims saved evidence.
- `creator-mission-status` now carries smoke `evidence_mode` into canonical,
  Builder, and Telegram read-only views so product surfaces can distinguish
  saved evidence from recomputed evidence without parsing raw smoke packets.
- Spawner, Canvas, and Kanban mission-status projections now preserve the same
  `evidence_mode`, with a recomputed-mode regression covering the full
  read-only adapter set.
- Product-flow docs now require downstream surfaces to preserve
  `evidence_mode` rather than parsing raw smoke or treating saved evidence as a
  fresh recompute.
- Startup YC external recompute docs now mark adapter selection as implemented
  and leave standalone rerun provenance packets plus promotion gates as the
  remaining work.
- `creator-mission-status.schema.json` now rejects Canvas and Kanban
  projections that drop `evidence_mode` from their read-only mission views.
- `CREATOR_SYSTEM_MULTI_DOMAIN_VALIDATION_PLAN.md` now defines the long-running
  matrix for generated artifact-quality, tool-operation, MiroFish content,
  doctor/security, Startup YC operator, and retrieval/memory creator systems.
- `BENCHMARK_GENERATION_HONESTY_STANDARD.md` now defines the generated benchmark
  honesty contract: case oracles, failure modes, lane results, anti-gaming
  checks, provenance hashes, and explicit Swarm claim boundaries.
- Generator acceptance now requires generated benchmark manifests to expose
  target capability, lane counts, promotion rules, aggregation policy, and
  anti-gaming checks.
- `domain-chip-manifest.schema.json` and `hook-smoke-result.schema.json` now
  anchor the generated domain-chip contract. Generated chip manifests must keep
  a local-only publication boundary, while hook-smoke pass packets require all
  four generated hook surfaces to pass.
- `specialization-path-manifest.schema.json` and
  `autoloop-simulation-result.schema.json` now anchor generated path and
  keep/revert loop evidence. Generated paths stay gated at candidate review,
  and autoloop simulations must include both keep and revert proof.
- `benchmark-report.schema.json` and `absorption-summary.schema.json` now
  anchor generated and source-linked saved evidence reports. The schemas require
  visible provenance sources and input hashes so saved reports stay separable
  from freshly recomputed evidence.
- `scoring-hooks.schema.json` and `benchmark-case.schema.json` now anchor the
  generated benchmark input side. Scoring hooks must either be deterministic
  generated hooks with trap regression blocking or source-linked hook paths,
  and generated trap cases must stay adversarial, high-risk, and uncalibrated.
- `benchmark-pack-manifest.schema.json` now accepts both generated proof-domain
  benchmark families and the source-linked Startup YC manifest shape while
  requiring generated aggregation policies to expose lane and seed failure
  blocking.
- `swarm-contribution-packet.schema.json` now requires report-backed evidence
  fields and keeps `network_publication_allowed=false` as a schema-level
  invariant for generated and Startup YC contribution packets.
- `loop-policy-manifest.schema.json` now requires
  `network_publication_allowed=false`, so autoloop policies cannot silently
  become network publication policies.
- `creator-intent.schema.json` now requires
  `constraints.network_publication_allowed=false`, so generated creator runs
  start below the network publication boundary at the intent layer.
- `created-artifact-manifest.schema.json` now keeps artifact manifests local
  only and rejects `published` artifact statuses for creator-run evidence.
- `creator-run-smoke --recompute` now verifies generated lane results and blocks
  tampered benchmark manifests through report provenance hashes.
- `run_multi_seed_generator_validation` now creates a generated 36-row
  multi-seed matrix across six domain families, three brief variants per family,
  and two seeds per variant.
- `generated-multi-seed-run` now exposes the generated matrix runner as a CLI
  command from a briefs JSON file for manual or scheduled validation jobs.
- Generator acceptance now proves failed seed rows block the aggregate and
  expose blocker names instead of being hidden behind passing rows.
- `validate_multi_seed_generator_summary` now recomputes saved generated
  multi-seed summaries and blocks tampered summary rows or stale underlying run
  reports.
- `generated-multi-seed-summary-check` now exposes that recompute path as a CLI
  command for manual or scheduled validation jobs, with `--fail-on-blocked`
  support.
- `generated-multi-seed-summary.schema.json` and
  `generated-multi-seed-summary-check.schema.json` now anchor the generic
  generated multi-seed summary and recompute-check packet shapes.
- Generator acceptance now includes a retrieval/memory boundary domain and
  requires every generated domain family to emit a schema-valid recomputed
  `creator-mission-status` packet.
- `creator-mission-status --generated-multi-seed` now projects generated
  multi-seed summaries into read-only Builder, Telegram, Spawner, Canvas, and
  Kanban views, including row counts, failed seed IDs, hidden-failure status,
  and the explicit `network_absorbable=false` boundary.
- Generated runs now emit `reports/operator_review_packet.json`, and
  `operator-review-check` blocks incomplete or unsafe human/operator
  calibration, privacy, rollback, and publication review evidence while keeping
  `network_absorbable=false`.
- `operator-review-packet.schema.json` and `operator-review-check.schema.json`
  now anchor the generic Phase 5 generated-domain review packet and check
  shapes.
- Creator-system CI now includes `tests/test_operator_review.py` and focused
  lint for `src/chip_labs/operator_review.py`, keeping the generic review
  packet/check boundary under automated coverage.
- Creator-system CI now writes the strict Startup YC smoke packet and validates
  it against `smoke-result.schema.json`, including the saved evidence-mode
  boundary.
- Creator-system CI now has a manual `workflow_dispatch` path with
  `run_generated_multi_seed=true` that runs `generated-multi-seed-run` against
  `docs/creator_system/examples/generated-multi-domain-briefs.json`, then
  recompute-checks and schema-validates the generated multi-seed summary.
- The same manual path now emits a product-safe
  `creator-mission-status --generated-multi-seed` packet for the generated
  matrix and validates it against `creator-mission-status.schema.json`.
- Manual generated-matrix workflow logs now include a compact verdict,
  passed-run count, mission-status run count, and `network_absorbable=false`
  readout for operators.
- Artifact-quality benchmark manifests now support `case_expectations` for
  baseline, candidate, and trap artifacts. Benchmark reports emit expectation
  checks plus `calibration_verdict`, and failed expectations force `revert`
  rather than letting a positive score delta hide calibration drift.
- Artifact-quality benchmark manifests now support
  `reviewer_calibration_cases` across PR writeups, design docs, mission
  handoffs, and traps. Failed reviewer rows block calibration and the
  calibration source files are included in benchmark provenance hashes.
- `artifact-quality-report.schema.json`,
  `artifact-quality-benchmark-manifest.schema.json`, and
  `artifact-quality-benchmark-result.schema.json` now anchor the local
  design-doc/PR reviewer contract. Saved reports must keep the local
  review-only claim boundary and unsafe-claim caveat, while benchmark pass
  results must align with calibration pass, zero trap regressions, and a `keep`
  decision.
- MiroFish content simulation results now emit calibration checks for
  multi-RLM judge coverage, persona-segment coverage, row-count coherence,
  weak-segment inspection, and optional expected-winner oracles. Single-judge
  or wrong-winner runs remain ranked but carry `calibration_verdict=blocked`.
- `mirofish-content-multi-seed` now runs deterministic local simulator reruns
  across explicit seeds, records top-candidate stability, and blocks calibration
  when the batch has fewer than two seeds or no stable top candidate. The saved
  `examples/mirofish-content/multi-seed-result.json` remains
  `candidate_review` and `network_absorbable=false`.
- `mirofish-content-route.schema.json`,
  `mirofish-content-simulation-result.schema.json`, and
  `mirofish-content-multi-seed-result.schema.json` now anchor the local content
  simulator contract. Route packets preserve the candidate-review boundary,
  simulation results expose calibration blockers, and multi-seed results reject
  accidental `network_absorbable=true` claims before real outcome calibration.
- `mirofish-provider-adapter-check` now validates future MiroFish RLM judge
  adapter slots without making live provider calls or accepting credentials.
- `mirofish-provider-adapter-manifest.schema.json` and
  `mirofish-provider-adapter-check.schema.json` now require disabled network
  calls, disabled live credentials, row-level output contracts, explicit
  forbidden claims, and `network_absorbable=false`.
- `mirofish-outcome-calibration-check` now blocks insufficient or vanity-only
  real content outcome evidence as `inconclusive` instead of treating likes or
  impressions as calibration support.
- `mirofish-outcome-calibration-evidence.schema.json` and
  `mirofish-outcome-calibration-check.schema.json` now anchor denominator,
  downstream-signal, qualitative-review, forbidden-claim, and
  `network_absorbable=false` requirements for real outcome calibration.
- `SPARK_CREATOR_PUBLIC_REPO_DECISION.md` now records that public
  `spark-creator` extraction stays deferred until schema compatibility,
  provenance, transfer evidence, and product read-only contracts stabilize.
- The root README now points technical users to the creator-system beta
  quickstart, release checklist, and golden path.
- `USER_QUICKSTART_BETA.md` and `RELEASE_READINESS_CHECKLIST_BETA.md` now make
  install, first commands, evidence tiers, non-goals, fresh-clone verification,
  and pre-release gates explicit.
- The package now exposes a `chip-labs` console entrypoint for fresh-clone
  users in addition to `python -m chip_labs.cli`.
- Startup YC operator-validation examples now include a saved
  `network_absorption_review_blocked.json` aggregate review packet. CI validates
  that the saved packet and freshly generated packet remain blocked with
  `network_absorbable=false` while external provenance or required approval
  evidence is missing.
- Manual `Creator System` workflow dispatch with `run_generated_multi_seed=true`
  passed the generated multi-domain matrix in CI: `verdict=candidate_review`,
  `passed=36/36`, `mission_run_count=36`, and `network_absorbable=false`.
- Tool-operation checks now require successful parsed operations to declare
  `expected_postconditions`; stdout and plausible success packets are not
  enough for mission-control state updates.
- Tool-operation checks now support `mirofish-content-multi-seed` packets and
  verify calibration verdict, minimum seed count, stable top-candidate evidence,
  and `network_absorbable=false` before mission-control state can trust the
  result.
- Tool-operation checks now support `creator-run-doctor-adversarial-sweep`
  packets and verify minimum case count, empty failed case ids, required
  schema-family coverage, and `network_absorbable=false` before a mission trace
  can trust the sweep result.
- `tool-operation-manifest.schema.json`, `tool-operation-packet.schema.json`,
  and `tool-operation-check.schema.json` now anchor the local mission-control
  safety boundary. Saved fixtures and fresh check outputs validate against the
  schemas, while incoherent blocked/allowed states and
  `network_absorbable=true` postconditions are rejected.
- `creator-run-doctor` now emits `repair_calibration`, which verifies that
  blocking smoke checks are covered by specific repair steps or quarantine
  findings and that blocked runs require recompute replay before repair advice
  is complete.
- `creator-run-doctor-adversarial-sweep` now runs isolated adapter-map,
  candidate-report, absorption-summary, Swarm-packet, and evidence-ladder
  mutations from `examples/doctor-security/adversarial_schema_sweep.json`, and
  requires the doctor to block with calibrated repair or quarantine coverage
  while keeping `network_absorbable=false`.
- `doctor-adversarial-sweep-manifest.schema.json` and
  `doctor-adversarial-sweep-result.schema.json` now anchor the sweep manifest
  and result packets, rejecting malformed mutation evidence and
  `network_absorbable=true` sweep outputs.
- Retrieval-memory checks now emit `calibration_verdict` and block packets when
  `provenance.source_path` is not one of the exact `source_refs`, so coherent
  saved recall cannot hide a source-path mismatch.
- `retrieval-memory-packet.schema.json` and
  `retrieval-memory-check.schema.json` now anchor the local memory-lane adapter
  boundary. The fixture suite validates correct prior recall, stale memory,
  contradiction, residue, network-review, and malformed
  `network_absorbable=true` packet shapes without wiring a production memory
  runtime.
- Startup YC held-out founder-advice evidence now must list covered operator moves,
  avoided rejected claims, observed privacy lane, promotion tier ceiling, and an
  advice artifact reference. Boolean pass flags alone cannot pass.
- Startup YC now includes saved held-out founder-advice evidence in
  `held_out_founder_advice_evidence.json`, wired through `validation_plan.json`.
  The held-out gate can pass locally while the validation suite remains blocked
  by the remaining promotion gates.
- Creator-system CI now has a weekly scheduled generated-matrix run in addition
  to `workflow_dispatch run_generated_multi_seed=true`, keeping heavy
  multi-domain drift checks out of normal push CI while still making them
  executable.
- Generic operator-review packet schemas now reject
  `evidence_tier=network_absorbable`. The requested claim can still be
  `network_absorbable`, and publication approval can still be recorded as one
  review gate, but the packet itself remains review evidence only.
- Adapter-map, smoke-result, and doctor-result schemas now constrain
  `evidence_tier` to the executable creator-run tier ladder, so fake tiers are
  rejected by both runtime smoke and saved schema validation.
- Creator-intent, autoloop policy, and created-artifact manifest schemas now
  constrain local creator-run tier fields to known evidence tiers and reject
  fake tier names.
- Those local-only schemas now cap tier claims at `transfer_supported`, blocking
  `network_absorbable` and `standard_update` claims until a future network
  publication schema is explicitly introduced with the required promotion gates.
- `creator-run-smoke` now enforces the same local tier ceiling without requiring
  runtime JSON Schema dependencies, blocking local intent, created-artifact, and
  autoloop policy fields that try to claim `network_absorbable`.
- `creator-run-smoke` now also enforces the created-artifact manifest's
  `local_only` publication boundary, so `github_pr` and `swarm_shared` remain
  product/mission-status request modes rather than created-artifact claims.
- `creator-run-smoke` now rejects `published` created-artifact statuses at
  runtime, matching the schema boundary that local creator-run artifacts are
  only `planned`, `created`, `validated`, or `blocked`.
- `creator-run-smoke` now rejects unknown created-artifact `kind` values at
  runtime while still allowing optional schema kinds such as `report`,
  `absorption_bundle`, and `standard_change`.
- `creator-run-smoke` now requires the created-artifact manifest's exact
  `adaptive_creator_loop.created_artifact_manifest.v1` schema version instead
  of accepting future-looking prefix matches.
- `creator-run-smoke` now validates created-artifact manifest `repo` provenance
  metadata shape when present, blocking non-object repo blocks and non-string
  `path`, `remote`, `branch`, or `commit` fields.
- `creator-run-smoke` now rejects non-string created-artifact manifest
  `creator_run_id`, artifact `path`, and artifact string metadata instead of
  coercing malformed values into apparently valid local evidence.
- `creator-run-smoke` now requires the exact
  `adaptive_creator_loop.creator_intent.v1` creator-intent schema version
  instead of accepting future-looking prefix matches.
- `creator-run-smoke` now validates autoloop policy schema version, required
  loop fields, lineage requirement, and `network_publication_allowed=false`
  before treating saved loop policy evidence as coherent.
- `creator-run-smoke` now validates creator-intent required source/domain/privacy
  fields and `network_publication_allowed=false`, blocking local intent packets
  that try to behave like publication approvals.
- `creator-run-smoke` now validates adapter-map evidence against the exact
  schema version, non-empty `run_id`, and required `swarm_adapter.evidence_tier`
  instead of defaulting absent adapter evidence to a passing prototype claim.
- `creator-run-smoke` now validates Swarm contribution packets against the exact
  packet schema, creator-run lineage, disabled network publication, report-path
  evidence, and numeric packet baseline/candidate scores before accepting
  elevated saved evidence.
- `creator-run-smoke` now cross-checks Swarm packet baseline/candidate scores
  against the saved benchmark reports, blocking coherent-looking packet scores
  that no longer match the run evidence bundle.
- `creator-run-smoke` now verifies that Swarm packet `evidence.report_paths`
  exist inside the creator run, so packets cannot cite absent evidence files.
- `creator-run-smoke` now cross-checks Swarm packet transfer result fields
  against `reports/transfer_summary.json`, blocking packet-level transfer
  claims that drift away from the saved transfer report.
- `creator-run-smoke` now checks broad-transfer `scenario_results` against
  top-level `min_delta` and `negative_scenarios`, blocking aggregate summaries
  that no longer match row-level saved evidence.
- Broad-transfer saved evidence now also cross-checks positive and flat scenario
  counts against row-level deltas, so broad-transfer summaries cannot inflate
  wins while the underlying rows disagree.
- `startup-yc-external-provenance-packet` now emits a standalone recompute
  provenance packet with linked smoke verdict, external source hashes, visible
  blockers for missing/stale/unpinned inputs, and `network_absorbable=false`.
- The Startup YC transfer summary now pins hashes for its external Startup
  Bench suite, selector report, and evidence doc so provenance packets do not
  have to treat those available sources as unpinned.
- The external provenance packet schema now rejects forged `passed` packets
  that hide missing, stale, or unpinned source inputs behind an empty blocker
  list.
- `startup-yc-network-absorption-review` now emits a conservative review packet
  that combines the validation suite, required approval gates, and external
  provenance state while keeping `network_absorbable=false`.
- `startup-yc-network-absorption-review.schema.json` rejects premature network
  absorption claims and incoherent `review_ready` packets with visible blockers.
- Artifact-quality benchmark manifests now reject unknown `case_expectations`
  roles at runtime, so misspelled or hallucinated benchmark lanes cannot be
  silently ignored while producing a passing report.
- Artifact-quality benchmark manifests now also reject unknown fields inside
  known `case_expectations` roles, blocking typos like `minimum_score` from
  being silently skipped.
- Artifact-quality benchmark manifests now reject unknown fields inside
  `reviewer_calibration_cases`, so human/operator calibration rows cannot hide
  misspelled expectation keys.
- Artifact-quality benchmark manifests now require every reviewer calibration
  row to include `case_id`, `artifact_path`, `artifact_kind`, and
  `reviewer_verdict`, matching the schema before any benchmark report is
  generated.
- Artifact-quality benchmark manifests now reject invalid `reviewer_verdict`
  values at parse time instead of converting malformed human calibration input
  into ordinary failed benchmark rows.
- Artifact-quality benchmark manifests now validate `case_expectations`
  score bounds and trap-flag list shapes at parse time, so malformed benchmark
  oracles cannot be evaluated as ordinary passing or failing checks.
- Artifact-quality benchmark manifests now validate reviewer calibration score
  bounds plus trap-flag and missing-check list shapes at parse time, keeping
  human/operator calibration rows schema-coherent before reports are generated.
- Artifact-quality benchmark manifests now reject invalid `schema_version`
  values and unknown top-level fields at runtime, matching the strict
  `additionalProperties: false` schema boundary.
- Full `src/chip_labs` and `tests` ruff cleanup is now committed. The Creator
  System workflow enforces `python -m ruff check src/chip_labs tests` on
  relevant pushes and pull requests instead of relying on a narrow focused lint
  list.
- `creator-release-gate` now emits a stronger-release gate packet that
  aggregates generated multi-seed validation, Startup YC network-absorption
  review, and product runtime integration review evidence. Missing phase
  evidence is a blocker, supplied inputs are hashed, and the schema keeps
  `network_absorbable=false`.
- Creator System CI now runs `creator-release-gate` in the strict Startup YC
  path and validates the blocked packet against
  `creator-release-gate.schema.json`. The manual and scheduled generated
  matrix path also emits `/tmp/generated-release-gate.json`, proving the
  generated multi-seed phase can pass while product runtime and Startup YC
  network-absorption blockers remain visible.
- `creator-system-beta-check` now gives users and CI a one-command local beta
  readiness packet. It aggregates template validation, strict Startup YC smoke,
  raw validation-evidence shape, network-absorption boundary checks, and the
  stronger-release gate while preserving `network_absorbable=false`.
- `creator-system-beta-check.schema.json` anchors that packet so a future beta
  handoff cannot hide broken local workflows or accidentally convert blocked
  release evidence into publication approval.
- `product-runtime-review-template` and `product-runtime-review-check` now
  define the product runtime review evidence packet for Builder, Telegram,
  Spawner, Canvas, and Kanban. The check requires reviewer evidence,
  blocked-state visibility, `evidence_mode` preservation, rollback refs, and
  disabled creator controls in this methodology repo.
- Saved product runtime review fixtures now include an open blocked review and
  a read-only review-complete packet. The complete packet satisfies only the
  product runtime phase of `creator-release-gate`; generated multi-seed,
  Startup YC network-absorption, publication, and `network_absorbable` gates
  remain blocked.
- Extended generated-domain validation now has a recorded 54-row local run:
  three seeds across the six proof-domain families, recompute check `pass`,
  and `network_absorbable=false`.
- `startup-yc-production-gate-workbench` now runs the Startup YC production
  gate rehearsal end to end in a chosen workspace. It writes the individual
  gate outputs, promotion evidence bundle, validation suite, and
  network-absorption review packet together, then emits a schema-anchored
  summary that records clean-workspace status and preserves
  `network_absorbable=false`.
- Creator System CI now runs that production-gate workbench during the strict
  Startup YC path and validates the summary against
  `startup-yc-production-gate-workbench.schema.json`, so the rehearsal cannot
  drift out of release evidence.
- `creator-system-beta-check` now also runs the fresh Startup YC production-gate
  workbench in a temporary clean workspace and requires the expected blocked
  rehearsal state before returning `pass`.
- `creator-system-release-evidence` now emits a machine-readable technical beta
  release packet with repo branch, commit, clean-worktree status, beta-check
  summary, required rerun commands, release docs, and the explicit
  `network_absorbable=false` promotion boundary. Dirty checkouts block release
  evidence instead of silently passing as release-ready.
- Creator System CI now uploads the clean-checkout
  `creator-system-release-evidence` JSON as a workflow artifact, giving users
  and Spark agents a downloadable release packet instead of requiring job-log
  scraping.

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
python -m ruff check src/chip_labs tests
python -m pytest tests/test_creator_release_gate.py tests/test_product_runtime_review.py -q
python -m pytest tests/test_creator_mission_adapter.py tests/test_creator_system_docs.py tests/test_startup_yc_operator_validation.py tests/test_tool_operation.py tests/test_artifact_quality.py tests/test_mirofish_content_simulation.py tests/test_operator_review.py tests/test_creator_generator_acceptance.py tests/test_creator_run.py tests/test_creator_run_examples.py tests/test_retrieval_memory.py -q
python -m chip_labs.cli creator-run-smoke docs/creator_system/examples/startup-yc-creator-run --fail-on-blocked --fail-on-warn
python -m chip_labs.cli creator-run-template-check --fail-on-blocked
```

Latest focused creator-system suite result before CI push: `262 passed`.
