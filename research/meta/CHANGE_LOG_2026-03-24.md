# Change Log: 2026-03-24

## Tranche: MiroFish v4 Engine Rebalance

### Files Changed

- `src/chip_labs/mirofish/personas.py`
- `src/chip_labs/mirofish/simulation.py`
- `src/chip_labs/mirofish/report.py`
- `research/meta/MIROFISH_V4_ENGINE_REBALANCE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_v4_engine_rebalance.json`

### Why

The latest committed MiroFish v4 run had effectively collapsed into near-zero final adoption across the 515-domain universe. The output made it look like agents never chose anything, even though curve inspection showed meaningful mid-run attention and trial behavior.

### What Changed

- Reduced threshold inflation by limiting learning-based threshold adjustments to retained stages only
- Stopped counting `trial` as full adoption inside the fatigue penalty
- Relaxed retention and fallback gates so exploratory behavior has time to convert into retained adoption
- Added peak trajectory metrics and `agent_choice_signal` so reports preserve what agents actually tried during the run

### Verification

- `python -m pytest tests/test_trend_prediction.py -q`
- 30-domain validation slice comparing:
  - threshold drift
  - final adoption
  - peak adoption
  - peak active signal

### Notes

- `tests/test_simulation.py` still carries pre-existing expectations from the older simulation contract:
  - 6 adoption stages
  - exact requested ensemble run count even though v4 enforces a minimum
- Those mismatches predate this rebalance tranche.

## Tranche: MiroFish Discovery Factory Plan

### Files Changed

- `docs/MIROFISH_DISCOVERY_FACTORY_PLAN.md`
- `docs/EXECUTION_PLAN_2026-03-21.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_factory_plan.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The current MiroFish system can compare seeded domain-chip universes, but it cannot yet discover candidate domain chips from real specialization, mastery, and demand signals without being handed a menu first.

### What Changed

- Added a discovery-first hybrid architecture plan
- Defined the hard boundary between:
  - discovery
  - canonicalization
  - evaluation
  - promotion
- Defined the first implementation tranche:
  - discovery schema
  - output classes
  - canonicalization rules
  - one manual discovery batch
  - one smaller hybrid evaluation pass
- Linked the main repo execution plan to the new MiroFish discovery-factory plan

### Verification

- Manual consistency review against:
  - current MiroFish docs
  - current CLI/runtime structure
  - current execution plan

### Notes

- This tranche is planning-only.
- The next tranche should implement the discovery contract and repo-local packet scaffolding.

## Tranche: MiroFish Discovery Contract

### Files Changed

- `src/chip_labs/mirofish/discovery.py`
- `src/chip_labs/cli.py`
- `docs/MIROFISH_DISCOVERY_CONTRACT.md`
- `research/meta/MIROFISH_DISCOVERY_BATCH_TEMPLATE_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_BATCH_TEMPLATE_RESULT_2026-03-24.json`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_contract.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The discovery-first architecture had been planned, but there was still no concrete contract for what a valid discovered domain chip looks like, how noisy candidates get classified, or how operators should run the first packet-first intake flow.

### What Changed

- Added a discovery contract document that defines:
  - what counts as a domain chip
  - required candidate fields
  - classification outcomes
  - canonicalization rules
  - packet shape
  - operator workflow
- Added deterministic batch canonicalization code in `mirofish/discovery.py`
- Added a repo-local CLI command to canonicalize raw discovery batches
- Added a starter discovery batch packet that exercises:
  - accepted candidates
  - alias duplicates
  - workflow-only candidates
  - persona-only candidates
  - existing benchmark duplicates
  - too-vague candidates
- Saved the emitted canonicalized result packet for direct inspection and downstream handoff

### Verification

- Run `python -m chip_labs.cli mirofish-discovery-batch` on the starter packet
- Inspect the emitted accepted, merged, and rejected candidate groups

### Notes

- This tranche still stops before simulation.
- The next tranche should translate accepted discovery packets into a hybrid evaluation run spec with a stable benchmark panel.

## Tranche: MiroFish Hybrid Evaluation Spec

### Files Changed

- `src/chip_labs/mirofish/hybrid.py`
- `src/chip_labs/cli.py`
- `docs/MIROFISH_HYBRID_EVALUATION_SPEC.md`
- `research/meta/MIROFISH_HYBRID_SPEC_TEMPLATE_2026-03-24.json`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_hybrid_spec.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The discovery contract now produced accepted candidates, but there was still no repo-local bridge for turning those candidates into simulation-ready opportunities that could be compared against a stable benchmark panel.

### What Changed

- Added a hybrid bridge module that:
  - infers conservative static priors for discovered candidates
  - selects a benchmark panel
  - ranks the combined universe
  - builds graph, signal, and scenario inputs
  - emits harness configuration for flagship and ensemble runs
- Added a `mirofish-hybrid-spec` CLI command
- Added an operator doc for the hybrid bridge
- Saved a sample hybrid spec from the starter discovery packet

### Verification

- Run `python -m chip_labs.cli mirofish-hybrid-spec` on the canonical starter packet
- Inspect:
  - `discovered_count`
  - `benchmark_count`
  - `combined_domain_count`
  - `signal_count`
  - `shock_count`

### Notes

- The hybrid spec is simulation-ready but still exploratory.
- The next tranche can run the starter hybrid spec through simulation and save a report artifact.

## Tranche: MiroFish Hybrid Starter Run

### Files Changed

- `src/chip_labs/mirofish/hybrid.py`
- `src/chip_labs/cli.py`
- `docs/MIROFISH_HYBRID_EVALUATION_SPEC.md`
- `research/meta/MIROFISH_HYBRID_RUN_TEMPLATE_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_hybrid_run.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The repo could already build a hybrid evaluation spec, but it still needed one saved end-to-end example showing how a discovered candidate actually performs against the benchmark panel under the current harness.

### What Changed

- Added a `mirofish-hybrid-run` CLI command
- Added a hybrid runner that:
  - runs dual-context simulation from a saved hybrid spec
  - runs the builder ensemble
  - emits a compact evaluation artifact
- Saved the starter hybrid run JSON
- Added a compact run note summarizing the first outcome

### Verification

- Run `python -m chip_labs.cli mirofish-hybrid-run` on the saved starter spec
- Inspect:
  - `top_line`
  - `builder_ensemble_summary`
  - discovered candidate placement against the benchmark panel

### Notes

- In the current starter run, `cursor-copilot` leads the benchmark panel.
- The discovered `ai-meeting-prep-copilot` candidate ranks second by ensemble mean adoption, which is enough to justify a broader discovery batch.

## Tranche: MiroFish Expanded Discovery Batch

### Files Changed

- `src/chip_labs/mirofish/hybrid.py`
- `docs/MIROFISH_HYBRID_EVALUATION_SPEC.md`
- `research/meta/MIROFISH_DISCOVERY_BATCH_EXPANDED_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_BATCH_EXPANDED_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_SPEC_EXPANDED_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_EXPANDED_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_EXPANDED_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_expanded_batch.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The repo needed a larger discovery batch to see whether newly proposed operator domains could survive canonicalization and stay competitive once they were compared against the benchmark panel under the hybrid harness.

### What Changed

- Added the first expanded manual discovery batch with 17 raw candidates
- Canonicalized that batch into:
  - 12 accepted candidates
  - 2 merged candidates
  - 3 rejected candidates
- Generated and ran the hybrid harness on the expanded set
- Tightened the default breakout shock so it only targets the top 3 discovered candidates instead of all discovered candidates at once
- Saved a research note describing the discovered-domain cluster read from the results

### Verification

- Run `python -m chip_labs.cli mirofish-discovery-batch` on the expanded raw packet
- Run `python -m chip_labs.cli mirofish-hybrid-spec` on the expanded canonical packet
- Run `python -m chip_labs.cli mirofish-hybrid-run` on the expanded spec
- Inspect the discovered-only leaderboard from the builder ensemble

### Notes

- Benchmarks still lead overall after the scenario correction.
- The strongest discovered cluster is now:
  - compliance / enterprise evidence
  - founder communication
  - sales / partner preparation

## Tranche: MiroFish Focused Benchmark Batch

### Files Changed

- `research/meta/MIROFISH_DISCOVERY_BATCH_FOCUSED_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_BATCH_FOCUSED_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_SPEC_FOCUSED_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_FOCUSED_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_FOCUSED_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_focused_batch.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The expanded discovery batch found a promising cluster, but it still needed a narrower benchmark comparison to see whether the strongest discovered domains could outrun relevant incumbents rather than only look decent inside a broad mixed panel.

### What Changed

- Added a focused discovery batch centered on:
  - enterprise response loops
  - founder communication loops
  - sales / partner preparation loops
- Canonicalized that batch into:
  - 7 accepted candidates
  - 2 merged candidates
  - 3 rejected candidates
- Ran the focused set against a custom benchmark panel:
  - `compliance-shield`
  - `legal-ops`
  - `startup-yc`
  - `indie-hacker`
  - `cursor-copilot`
- Saved a focused run note highlighting the strongest discovered candidate

### Verification

- Run `python -m chip_labs.cli mirofish-discovery-batch` on the focused raw packet
- Run `python -m chip_labs.cli mirofish-hybrid-spec` with the custom benchmark list
- Run `python -m chip_labs.cli mirofish-hybrid-run` on the focused spec
- Inspect the discovered-only leaderboard and compare it to the benchmark domains

### Notes

- `ai-security-questionnaire-copilot` is now the strongest discovered candidate under a relevant benchmark comparison.
- It outruns `startup-yc`, `compliance-shield`, and `legal-ops` on builder ensemble mean adoption inside this focused panel.

## Tranche: MiroFish Promotion Review

### Files Changed

- `src/chip_labs/mirofish/hybrid.py`
- `src/chip_labs/cli.py`
- `docs/MIROFISH_PROMOTION_REVIEW.md`
- `docs/MIROFISH_HYBRID_EVALUATION_SPEC.md`
- `docs/MIROFISH_DISCOVERY_FACTORY_PLAN.md`
- `research/meta/MIROFISH_PROMOTION_BRIEF_ENTERPRISE_RESPONSE_2026-03-24.json`
- `research/meta/MIROFISH_PROMOTION_BRIEF_ENTERPRISE_RESPONSE_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_promotion_review.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The focused enterprise-response run identified a likely promotion candidate, but the repo still lacked a reproducible way to convert a saved hybrid run into a benchmark-review recommendation without manual re-reading.

### What Changed

- Added a promotion-brief builder on top of saved hybrid run packets
- Added a `mirofish-promotion-brief` CLI command
- Documented the operator workflow for promotion review
- Linked the promotion-review step back into the hybrid evaluation and discovery-factory docs
- Saved the first enterprise-response promotion brief and note
- Recommended `ai-security-questionnaire-copilot` for first maintained benchmark review

### Verification

- Run `python -m chip_labs.cli mirofish-promotion-brief` on the focused hybrid run with the selected enterprise-response domains
- Run `python -m pytest tests/test_trend_prediction.py -q`
- Inspect that the saved brief exposes:
  - benchmark median
  - benchmark wins
  - a single human-review recommendation
  - a no-auto-promotion governance note

### Notes

- The promotion brief is a review layer only; it does not mutate benchmark membership.
- `ai-security-questionnaire-copilot` is the only current enterprise-response candidate that clears the explicit `review_now` bar.

## Tranche: MiroFish Benchmark Review Run

### Files Changed

- `src/chip_labs/mirofish/hybrid.py`
- `src/chip_labs/cli.py`
- `docs/MIROFISH_PROMOTION_REVIEW.md`
- `docs/MIROFISH_HYBRID_EVALUATION_SPEC.md`
- `research/meta/MIROFISH_HYBRID_SPEC_BENCHMARK_REVIEW_ENTERPRISE_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_BENCHMARK_REVIEW_ENTERPRISE_2026-03-24.json`
- `research/meta/MIROFISH_BENCHMARK_REVIEW_ENTERPRISE_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_benchmark_review_run.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The promotion brief nominated `ai-security-questionnaire-copilot`, but that read still came from a discovery-favored run. The repo needed one validation pass where the candidate was treated like a benchmark-review member rather than a discovered candidate.

### What Changed

- Added support for moving selected discovered candidates into a benchmark-review lane during hybrid spec generation
- Added a CLI option to promote selected discovered domain IDs into that lane
- Documented the benchmark-review validation path
- Generated and ran a benchmark-review spec where `ai-security-questionnaire-copilot` no longer received discovery breakout support
- Saved a note comparing the review-run result to the earlier promotion brief

### Verification

- Run `python -m chip_labs.cli mirofish-hybrid-spec` on the focused discovery packet with `--promote-domains ai-security-questionnaire-copilot`
- Run `python -m chip_labs.cli mirofish-hybrid-run` on the benchmark-review spec
- Run `python -m pytest tests/test_trend_prediction.py -q`
- Inspect that:
  - `promotion_review_domain_ids` contains `ai-security-questionnaire-copilot`
  - the breakout shock no longer targets that candidate
  - the saved note makes the admission decision explicit

### Notes

- `ai-security-questionnaire-copilot` remains a valid benchmark-review candidate, but it does not yet earn maintained benchmark admission.
- Removing discovery breakout support dropped its builder ensemble mean adoption from `4.83%` to `2.64%`.

## Tranche: MiroFish Enterprise-Only Review

### Files Changed

- `research/meta/MIROFISH_DISCOVERY_BATCH_ENTERPRISE_REVIEW_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_SPEC_ENTERPRISE_ONLY_REVIEW_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_ONLY_REVIEW_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_ONLY_REVIEW_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_enterprise_only_review.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The prior benchmark-review run was still too broad and mixed. It showed that the questionnaire lane remained promising, but it did not cleanly answer whether that wedge outruns the closest enterprise-response challenger under a tighter panel.

### What Changed

- Narrowed the canonical packet to:
  - `ai-security-questionnaire-copilot`
  - `ai-rfp-response-copilot`
- Generated an enterprise-only hybrid review spec
- Ran the enterprise-only hybrid harness against:
  - `compliance-shield`
  - `legal-ops`
  - `startup-yc`
  - `cursor-copilot`
- Saved a note concluding that `ai-rfp-response-copilot` is strong enough to become a co-review candidate, but the benchmark admission decision still remains open

### Verification

- Run `python -m chip_labs.cli mirofish-hybrid-spec` on the narrowed enterprise packet with `--promote-domains ai-security-questionnaire-copilot`
- Run `python -m chip_labs.cli mirofish-hybrid-run` on the enterprise-only spec
- Inspect that:
  - the narrowed packet contains only the two enterprise-response domains
  - the questionnaire lane stays in `promotion_review_domain_ids`
  - the note records the remaining breakout asymmetry

### Notes

- `ai-rfp-response-copilot` slightly outruns `ai-security-questionnaire-copilot` on builder ensemble mean adoption in this narrower run (`4.35%` vs `3.97%`).
- `ai-security-questionnaire-copilot` still has the stronger flagship choice signal (`20.0%` vs `6.67%`).
- The next clean comparison should treat both enterprise-response domains as benchmark-review candidates with no discovery-breakout favoritism for either one.

## Tranche: MiroFish Enterprise Symmetric Review

### Files Changed

- `research/meta/MIROFISH_HYBRID_SPEC_ENTERPRISE_SYMMETRIC_REVIEW_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_SYMMETRIC_REVIEW_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_SYMMETRIC_REVIEW_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_enterprise_symmetric_review.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The enterprise-only review still left one asymmetry: `ai-rfp-response-copilot` remained in the discovery lane and therefore kept breakout support. The repo needed one final symmetric comparison before naming the first enterprise-response domain for maintained benchmark admission.

### What Changed

- Generated a symmetric enterprise review spec with:
  - no discovered candidates
  - both `ai-security-questionnaire-copilot` and `ai-rfp-response-copilot` in `promotion_review_domain_ids`
- Ran the symmetric enterprise hybrid harness
- Saved a note recommending `ai-rfp-response-copilot` for first maintained benchmark admission while keeping `ai-security-questionnaire-copilot` immediately behind it in the benchmark-review lane

### Verification

- Run `python -m chip_labs.cli mirofish-hybrid-spec` on the narrowed enterprise packet with both enterprise-response domains in `--promote-domains`
- Run `python -m chip_labs.cli mirofish-hybrid-run` on the symmetric spec
- Inspect that:
  - `discovered_domain_ids` is empty
  - both enterprise-response domains are in `promotion_review_domain_ids`
  - the breakout shock is absent
  - the note names the first maintained benchmark admission recommendation

### Notes

- In the symmetric run, `ai-rfp-response-copilot` leads `ai-security-questionnaire-copilot` on builder ensemble mean adoption (`3.20%` vs `2.93%`).
- `ai-security-questionnaire-copilot` still leads on flagship choice signal (`20.0%` vs `6.67%`).
- The recommendation is therefore based on stable ensemble behavior, not on direct single-run choice signal.

## Tranche: MiroFish Enterprise Benchmark Proposal

### Files Changed

- `src/chip_labs/mirofish/hybrid.py`
- `src/chip_labs/cli.py`
- `docs/MIROFISH_PROMOTION_REVIEW.md`
- `docs/MIROFISH_HYBRID_EVALUATION_SPEC.md`
- `research/meta/MIROFISH_DISCOVERY_BATCH_ENTERPRISE_BENCHMARK_PROPOSAL_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_SPEC_ENTERPRISE_BENCHMARK_PROPOSAL_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_BENCHMARK_PROPOSAL_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_BENCHMARK_PROPOSAL_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_enterprise_benchmark_proposal.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The symmetric two-domain review recommended `ai-rfp-response-copilot`, but the repo still lacked a clean way to test a maintained benchmark proposal without directly editing the benchmark library first.

### What Changed

- Added a provisional benchmark lane to the hybrid spec builder
- Exposed that lane through the CLI as `--proposed-benchmarks`
- Documented the maintained benchmark proposal workflow
- Generated a broader enterprise proposal packet with:
  - `ai-rfp-response-copilot` as the provisional benchmark member
  - `ai-security-questionnaire-copilot` as the first review challenger
  - `ai-compliance-evidence-copilot` and `ai-renewal-risk-briefing-copilot` as secondary enterprise context domains
- Ran the broader enterprise proposal harness
- Saved a note deferring the maintained benchmark library edit because the narrow RFP recommendation did not survive the broader panel strongly enough

### Verification

- Run `python -m pytest tests/test_trend_prediction.py -q`
- Run `python -m chip_labs.cli mirofish-hybrid-spec` on the broader enterprise proposal packet with `--proposed-benchmarks ai-rfp-response-copilot`
- Run `python -m chip_labs.cli mirofish-hybrid-run` on the proposal spec
- Inspect that:
  - `ai-rfp-response-copilot` appears in `proposed_benchmark_domain_ids`
  - `ai-security-questionnaire-copilot` appears in `promotion_review_domain_ids`
  - the note states that the maintained benchmark library edit is deferred

### Notes

- In the broader enterprise proposal run, `ai-rfp-response-copilot` falls behind `ai-security-questionnaire-copilot`, `ai-compliance-evidence-copilot`, and `ai-renewal-risk-briefing-copilot` on builder ensemble adoption.
- The enterprise-response wedge still clearly beats the incumbent enterprise benchmarks, but the first maintained benchmark admission is not stable enough yet for a library edit.
