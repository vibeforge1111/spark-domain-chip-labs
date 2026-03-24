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

## Tranche: MiroFish Enterprise Cluster Playoff

### Files Changed

- `research/meta/MIROFISH_HYBRID_SPEC_ENTERPRISE_CLUSTER_PLAYOFF_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_PLAYOFF_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_PLAYOFF_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_enterprise_cluster_playoff.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The proposal tranche still mixed roles inside the enterprise cluster. The repo needed one stable playoff where all four enterprise-response domains occupied the same lane so their relative ordering could be trusted.

### What Changed

- Generated a symmetric enterprise cluster playoff spec with:
  - no discovered domains
  - no proposed benchmark domains
  - all four enterprise-response domains in `promotion_review_domain_ids`
- Ran the cluster playoff harness
- Saved a note concluding that:
  - no enterprise domain earns maintained benchmark admission yet
  - `ai-security-questionnaire-copilot` becomes first cluster priority
  - `ai-renewal-risk-briefing-copilot` becomes second cluster priority

### Verification

- Run `python -m chip_labs.cli mirofish-hybrid-spec` on the enterprise proposal packet with all four enterprise domains in `--promote-domains`
- Run `python -m chip_labs.cli mirofish-hybrid-run` on the cluster playoff spec
- Inspect that:
  - `discovered_domain_ids` is empty
  - all four enterprise domains appear in `promotion_review_domain_ids`
  - the note states that maintained admission remains deferred
  - the note ranks first and second cluster priority

### Notes

- In the cluster playoff, `startup-yc` still beats the entire enterprise cluster on builder ensemble adoption.
- `ai-security-questionnaire-copilot` wins the cluster on flagship choice signal and finishes only slightly behind `ai-renewal-risk-briefing-copilot` on ensemble adoption.
- `ai-rfp-response-copilot` falls to the bottom of the enterprise cluster under symmetric conditions.

## Tranche: MiroFish Enterprise Cluster Diagnostic

### Files Changed

- `src/chip_labs/mirofish/hybrid.py`
- `src/chip_labs/cli.py`
- `docs/MIROFISH_DIAGNOSTICS.md`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_enterprise_cluster_diagnostic.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The cluster playoff ranked the enterprise domains, but the next tranche required a methodology read explaining where the conversion failures actually happen.

### What Changed

- Added a run-diagnostic brief builder on top of saved hybrid runs
- Added a `mirofish-run-diagnostic` CLI command
- Documented the diagnostic workflow
- Saved a focused diagnostic brief for the enterprise cluster playoff
- Saved a note concluding that:
  - questionnaire and renewal mainly fail between choice and retained adoption
  - RFP mainly fails between interest and actual choice
  - compliance evidence suffers from both conversion friction and below-median ensemble adoption

### Verification

- Run `python -m chip_labs.cli mirofish-run-diagnostic` on the enterprise cluster playoff run with the four enterprise domains
- Run `python -m pytest tests/test_trend_prediction.py -q`
- Inspect that:
  - benchmark median reference is present
  - each focus domain has diagnostic tags and summaries
  - the note distinguishes conversion-stage bottlenecks across the cluster

### Notes

- The enterprise cluster does not have one generic weakness.
- Questionnaire and renewal need better choice-to-retention persistence.
- RFP and compliance evidence need better interest-to-choice conversion before admission should be reconsidered.

## Tranche: MiroFish Enterprise Graph Tuning

### Files Changed

- `src/chip_labs/mirofish/graph.py`
- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_PLAYOFF_TUNED_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_TUNED_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_GRAPH_TUNING_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_enterprise_graph_tuning.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The cluster diagnostic exposed different bottlenecks, but the graph layer was still feeding the simulation domain nodes without explicit behavioral fit tags or retention priors. That made the enterprise ranking more brittle than it should be.

### What Changed

- Added inferred `domain_tags` to graph domain nodes from domain text, candidate context, and related chips
- Added inferred `retention_score` to graph domain nodes from sticky workflow cues
- Reran the symmetric enterprise cluster playoff after the graph enrichment
- Built a tuned enterprise-cluster diagnostic brief from the rerun
- Saved a methodology note concluding that:
  - `ai-security-questionnaire-copilot` now leads the enterprise cluster on ensemble adoption
  - `ai-renewal-risk-briefing-copilot` now leads the enterprise cluster on attention signal
  - `ai-rfp-response-copilot` clears the benchmark median but remains a conversion problem
  - `startup-yc` still beats the enterprise cluster on ensemble adoption, so admission remains deferred

### Verification

- Run `python -m chip_labs.cli mirofish-hybrid-run --input research/meta/MIROFISH_HYBRID_SPEC_ENTERPRISE_CLUSTER_PLAYOFF_2026-03-24.json --output research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_PLAYOFF_TUNED_2026-03-24.json`
- Run `python -m chip_labs.cli mirofish-run-diagnostic --input research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_PLAYOFF_TUNED_2026-03-24.json --domains ai-security-questionnaire-copilot,ai-renewal-risk-briefing-copilot,ai-compliance-evidence-copilot,ai-rfp-response-copilot --output research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_TUNED_2026-03-24.json`
- Run `python -m pytest tests/test_trend_prediction.py -q`
- Inspect that:
  - graph domain nodes now include `domain_tags` and `retention_score`
  - the tuned playoff ranks `ai-security-questionnaire-copilot` above the other enterprise domains on ensemble adoption
  - the tuned diagnostic shows renewal as the strongest enterprise attention domain but still a persistence problem

### Notes

- This tranche changes methodology confidence more than it changes promotion status.
- The earlier enterprise cluster playoff should now be treated as under-specified because it lacked explicit graph-level fit semantics.
- `ai-rfp-response-copilot` and `ai-compliance-evidence-copilot` remain primarily interest-to-choice conversion problems.
- `ai-security-questionnaire-copilot` is now the clearest ensemble-stable enterprise candidate, but it still trails `startup-yc`.

## Tranche: MiroFish Enterprise Signal Symmetry

### Files Changed

- `src/chip_labs/mirofish/simulation.py`
- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_SIGNAL_SYMMETRY_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_SIGNAL_SYMMETRY_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_SIGNAL_SYMMETRY_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_enterprise_signal_symmetry.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The graph-tuning tranche improved domain semantics, but churn and retention were still using weaker raw-awareness checks than the ones that drove adoption. That asymmetry could artificially punish enterprise domains after they had already won persona attention.

### What Changed

- Added shared macro-aware awareness helpers in the simulation
- Applied fit-adjusted awareness to churn and retention checks
- Reran the symmetric enterprise cluster playoff under the new signal-symmetry logic
- Built a fresh enterprise-cluster diagnostic brief from the replay
- Saved a methodology note concluding that:
  - `ai-security-questionnaire-copilot` remains the strongest enterprise ensemble domain
  - `ai-rfp-response-copilot` strengthens materially and becomes the clearest improved challenger
  - `ai-compliance-evidence-copilot` also improves, but still remains below the benchmark median
  - `startup-yc` still beats the enterprise cluster on ensemble adoption, so admission remains deferred

### Verification

- Run `python -m chip_labs.cli mirofish-hybrid-run --input research/meta/MIROFISH_HYBRID_SPEC_ENTERPRISE_CLUSTER_PLAYOFF_2026-03-24.json --output research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_SIGNAL_SYMMETRY_2026-03-24.json`
- Run `python -m chip_labs.cli mirofish-run-diagnostic --input research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_SIGNAL_SYMMETRY_2026-03-24.json --domains ai-security-questionnaire-copilot,ai-renewal-risk-briefing-copilot,ai-compliance-evidence-copilot,ai-rfp-response-copilot --output research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_SIGNAL_SYMMETRY_2026-03-24.json`
- Run `python -m pytest tests/test_trend_prediction.py -q`
- Inspect that:
  - retention-side checks now use fit-aware awareness instead of raw awareness
  - `ai-rfp-response-copilot` and `ai-compliance-evidence-copilot` improve relative to the graph-only tuned replay
  - the note keeps maintained benchmark admission deferred

### Notes

- This tranche is a methodology fix, not a promotion verdict.
- Signal symmetry helps the enterprise-response cluster, but it does not solve the gap to `startup-yc`.
- `ai-renewal-risk-briefing-copilot` still reads as a persistence problem more than a benchmark-admission candidate.

## Tranche: MiroFish Enterprise Conversion Tuning

### Files Changed

- `src/chip_labs/mirofish/personas.py`
- `src/chip_labs/mirofish/simulation.py`
- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_CONVERSION_TUNING_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_CONVERSION_TUNING_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CONVERSION_TUNING_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_enterprise_conversion_tuning.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The signal-symmetry tranche still left the enterprise cluster heavily bottlenecked in interested and evaluating. The next narrow hypothesis was that sticky recurring workflows should be easier to justify trying once interest already exists.

### What Changed

- Added a retention-aware threshold easing inside persona stage advancement for the interested and evaluating stages
- Passed graph `retention_score` through simulation calls into persona evaluation
- Reran the symmetric enterprise cluster playoff under the conversion-tuned logic
- Built a fresh diagnostic brief from the replay
- Saved a methodology note concluding that:
  - `ai-security-questionnaire-copilot` and `ai-renewal-risk-briefing-copilot` are the main beneficiaries
  - `ai-rfp-response-copilot` and `ai-compliance-evidence-copilot` do not materially benefit
  - the enterprise cluster still does not beat `startup-yc`, so admission remains deferred

### Verification

- Run `python -m chip_labs.cli mirofish-hybrid-run --input research/meta/MIROFISH_HYBRID_SPEC_ENTERPRISE_CLUSTER_PLAYOFF_2026-03-24.json --output research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_CONVERSION_TUNING_2026-03-24.json`
- Run `python -m chip_labs.cli mirofish-run-diagnostic --input research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_CONVERSION_TUNING_2026-03-24.json --domains ai-security-questionnaire-copilot,ai-renewal-risk-briefing-copilot,ai-compliance-evidence-copilot,ai-rfp-response-copilot --output research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_CONVERSION_TUNING_2026-03-24.json`
- Run `python -m pytest tests/test_trend_prediction.py -q`
- Inspect that:
  - questionnaire and renewal improve relative to the signal-symmetry replay
  - RFP and compliance evidence do not receive the same uplift
  - the note keeps maintained benchmark admission deferred

### Notes

- This tranche is useful because it separates sticky recurring workflows from pure choice-conversion problems.
- Renewal becomes much more credible as a methodology target, but still not a maintained benchmark admission.
- RFP and compliance evidence now need a different next hypothesis than questionnaire and renewal.

## Tranche: MiroFish Enterprise Choice Conversion

### Files Changed

- `src/chip_labs/mirofish/graph.py`
- `src/chip_labs/mirofish/simulation.py`
- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_CHOICE_CONVERSION_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_CHOICE_CONVERSION_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CHOICE_CONVERSION_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_enterprise_choice_conversion.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The sticky-workflow tranche clarified that RFP and compliance evidence still lacked a domain-specific reason for interested personas to convert into actual choice. The next narrow hypothesis was that proof-heavy enterprise workflows should stay more decisive once a persona is already in the funnel.

### What Changed

- Added inferred graph-level `choice_score` for proof-heavy workflows such as RFP, questionnaire, evidence, controls, audit, and procurement packaging
- Applied that choice prior as a narrow awareness boost only for personas already at `interested` or `evaluating`
- Reran the symmetric enterprise cluster playoff under the explicit choice-conversion logic
- Built a fresh diagnostic brief from the replay
- Saved a methodology note concluding that:
  - `ai-security-questionnaire-copilot` remains the strongest enterprise ensemble domain and improves further
  - `ai-renewal-risk-briefing-copilot` remains the strongest direct-choice enterprise lane and also improves on ensemble adoption
  - `ai-rfp-response-copilot` moves closer to the benchmark median, but still fails to produce convincing direct-choice signal
  - `ai-compliance-evidence-copilot` can win more direct choice without turning that into durable ensemble adoption

### Verification

- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-hybrid-run --input research/meta/MIROFISH_HYBRID_SPEC_ENTERPRISE_CLUSTER_PLAYOFF_2026-03-24.json --output research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_CHOICE_CONVERSION_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-run-diagnostic --input research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_CHOICE_CONVERSION_2026-03-24.json --domains ai-security-questionnaire-copilot,ai-renewal-risk-briefing-copilot,ai-compliance-evidence-copilot,ai-rfp-response-copilot --output research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_CHOICE_CONVERSION_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_trend_prediction.py -q`
- Inspect that:
  - questionnaire and renewal both remain above the benchmark median
  - RFP closes part of the gap to the benchmark floor
  - compliance evidence shows whether stronger choice alone is enough
  - the note keeps maintained benchmark admission deferred

### Notes

- This tranche improves the enterprise read without becoming a broad enterprise boost.
- The main new information is that compliance evidence is not just a pre-choice problem.
- `startup-yc` still leads the cluster overall, so the next step remains a stable validation replay rather than admission.

## Tranche: MiroFish Validation Determinism Fix

### Files Changed

- `src/chip_labs/mirofish/simulation.py`
- `research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_VALIDATION_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_VALIDATION_2026-03-24.json`
- `research/meta/MIROFISH_ENTERPRISE_VALIDATION_STABILITY_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_validation_determinism_fix.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The planned stable enterprise validation replay was not actually stable. The cooldown path used Python's built-in `hash()` for persona-domain variation, which changes across Python processes and made same-spec same-seed replays drift.

### What Changed

- Replaced the process-randomized cooldown hash with a deterministic md5-based persona-domain bucket
- Rebuilt the planned enterprise validation replay after the fix
- Rebuilt the diagnostic brief from the stable validation replay
- Confirmed that the same replay now matches across fresh Python processes with different `PYTHONHASHSEED` values
- Saved a methodology note concluding that:
  - questionnaire remains the strongest enterprise ensemble candidate
  - renewal remains barely above the benchmark median and still looks like a retention-side issue
  - RFP remains just below the benchmark median
  - compliance evidence remains clearly below the benchmark median

### Verification

- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-hybrid-run --input research/meta/MIROFISH_HYBRID_SPEC_ENTERPRISE_CLUSTER_PLAYOFF_2026-03-24.json --output research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_VALIDATION_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-run-diagnostic --input research/meta/MIROFISH_HYBRID_RUN_ENTERPRISE_CLUSTER_VALIDATION_2026-03-24.json --domains ai-security-questionnaire-copilot,ai-renewal-risk-briefing-copilot,ai-compliance-evidence-copilot,ai-rfp-response-copilot --output research/meta/MIROFISH_ENTERPRISE_CLUSTER_DIAGNOSTIC_VALIDATION_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_trend_prediction.py tests/test_mirofish_portfolio.py -q`
- Run the same `run_hybrid_evaluation(..., seed=42)` replay in fresh Python processes with different `PYTHONHASHSEED` values and confirm that the focus metrics match exactly

### Notes

- This is a replay-integrity fix, not another enterprise uplift.
- The main outcome is that the next full portfolio rerun can now be trusted.
- The correct next step is the repo-local `515`-domain rerun, not another methodology mutation.

## Tranche: MiroFish Portfolio Runtime Fix

### Files Changed

- `src/chip_labs/mirofish/graph.py`
- `src/chip_labs/mirofish/simulation.py`
- `research/meta/MIROFISH_PORTFOLIO_RUNTIME_FIX_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_portfolio_runtime_fix.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The repo-local 515-domain wrapper was functionally correct but too slow to complete interactively. Profiling showed structural waste in graph edge lookup during persona expertise assignment and in repeated awareness recomputation during simulation rounds.

### What Changed

- Added adjacency indexing inside `DomainGraph` so `get_edges_for()` no longer scans the full edge list every call
- Indexed signals by domain once per round inside the simulation
- Added a round-local awareness cache so churn and retention checks reuse already-computed awareness
- Profiled the tiny full-universe harness before and after the fixes
- Saved a runtime note concluding that:
  - persona edge scanning was one major hotspot
  - repeated awareness-family recomputation was the other major hotspot
  - the tiny full-universe harness now finishes in interactive time

### Verification

- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_trend_prediction.py tests/test_mirofish_portfolio.py -q`
- Run `$env:PYTHONPATH='src'; python -c "from chip_labs.mirofish.portfolio import run_full_portfolio_evaluation; import time; t=time.time(); run_full_portfolio_evaluation(max_rounds=2, flagship_count_per_type=1, ensemble_runs=1, ensemble_count_per_type=1, min_runs=1, bootstrap_resamples=5); print(round(time.time()-t,2))"`
- Use `py-spy dump -p <tiny-run-pid>` during the timing harness to confirm the hotspot moved away from full graph scans

### Notes

- This tranche changes execution cost, not domain methodology.
- The next step is still the full-universe rerun and readout.
- The interactive harness should now be able to finish with materially less wasted CPU.

## Tranche: MiroFish Portfolio Interactive Readout

### Files Changed

- `research/meta/MIROFISH_PORTFOLIO_RUN_515_2026-03-24.json`
- `research/meta/MIROFISH_PORTFOLIO_READOUT_515_2026-03-24.json`
- `research/meta/MIROFISH_PORTFOLIO_INTERACTIVE_READOUT_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_portfolio_interactive_readout.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

After the runtime-fix tranche, the immediate need was to prove the repo-local 515-domain path could complete end to end and produce a readout packet inside the session. That required an explicitly interactive harness.

### What Changed

- Ran the full 515-domain universe through the repo-local portfolio CLI with a small interactive harness
- Saved the portfolio packet and derived readout under `research/meta/`
- Saved a note concluding that:
  - the repo-local full-universe path now completes end to end
  - the thin harness collapses absolute adoption and direct-choice values to zero
  - the result is an execution checkpoint and coarse interest skeleton, not the final trusted portfolio verdict

### Verification

- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-portfolio-run --rounds 4 --flagship-count-per-type 2 --ensemble-runs 3 --min-runs 3 --ensemble-count-per-type 1 --bootstrap-resamples 10 --output research/meta/MIROFISH_PORTFOLIO_RUN_515_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-portfolio-readout --input research/meta/MIROFISH_PORTFOLIO_RUN_515_2026-03-24.json --output research/meta/MIROFISH_PORTFOLIO_READOUT_515_2026-03-24.json`
- Inspect that the full-universe packet completes and the readout is generated under `research/meta/`

### Notes

- This checkpoint proves execution, not final portfolio confidence.
- The next meaningful step is to raise harness depth enough to recover non-zero adoption signal without reintroducing runaway runtime.
- Dashboard and export refresh should still wait for that deeper rerun.

## Tranche: MiroFish Portfolio Medium Checkpoint

### Files Changed

- `research/meta/MIROFISH_PORTFOLIO_RUN_515_MEDIUM_2026-03-24.json`
- `research/meta/MIROFISH_PORTFOLIO_READOUT_515_MEDIUM_2026-03-24.json`
- `research/meta/MIROFISH_PORTFOLIO_MEDIUM_CHECKPOINT_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_portfolio_medium_checkpoint.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The interactive full-universe checkpoint proved execution but collapsed to zero on adoption and choice. The next step was to recover non-zero full-universe signal without falling back into runaway runtime.

### What Changed

- Ran the full 515-domain universe through the repo-local portfolio CLI with a medium-depth harness
- Saved the medium packet and derived readout under `research/meta/`
- Saved a note concluding that:
  - non-zero full-universe signal is back
  - `defi-architect` leads the medium-harness ensemble read
  - `ai-npc-dialog` leads direct choice and flagship retained adoption
  - enterprise and v4 slices are now more informative than the zeroed checkpoint, but still too thin for a final verdict

### Verification

- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-portfolio-run --rounds 6 --flagship-count-per-type 4 --ensemble-runs 4 --min-runs 4 --ensemble-count-per-type 2 --bootstrap-resamples 10 --output research/meta/MIROFISH_PORTFOLIO_RUN_515_MEDIUM_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-portfolio-readout --input research/meta/MIROFISH_PORTFOLIO_RUN_515_MEDIUM_2026-03-24.json --output research/meta/MIROFISH_PORTFOLIO_READOUT_515_MEDIUM_2026-03-24.json`
- Inspect that the top-line ensemble read is no longer uniformly zero

### Notes

- This is a better checkpoint than the earlier thin interactive readout.
- It is still not the final trusted portfolio verdict.
- Dashboard and export refresh should still wait for one more deeper pass.

## Tranche: MiroFish Portfolio Operator Handoff

### Files Changed

- `docs/TODAY_SUMMARY_2026-03-24.md`
- `docs/TOMORROW_FOCUS_2026-03-25.md`
- `research/meta/MIROFISH_PORTFOLIO_OPERATOR_HANDOFF_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_portfolio_operator_handoff.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The repo had a validated medium full-universe checkpoint and a committed stop condition, but the day-level summary docs still described the earlier pre-rerun plan. That made the actual handoff state harder to recover than it should be.

### What Changed

- Added one operator-facing note naming the medium checkpoint as the current canonical portfolio read
- Preserved the current:
  - overall watchlist
  - choice and retention outliers
  - enterprise watchlist
  - newly discovered `v4` watchlist
- Updated the March 24 summary so it records:
  - the completed enterprise validation replay
  - the repo-local 515-domain runtime path
  - the interactive and medium checkpoints
  - the final stop condition
- Updated the March 25 focus so it starts from the medium checkpoint rather than from already-completed methodology work

### Verification

- Manual consistency review against:
  - `research/meta/MIROFISH_PORTFOLIO_READOUT_515_MEDIUM_2026-03-24.json`
  - `research/meta/MIROFISH_PORTFOLIO_MEDIUM_CHECKPOINT_NOTE_2026-03-24.md`
  - `research/meta/MIROFISH_PORTFOLIO_STOP_CONDITION_NOTE_2026-03-24.md`

### Notes

- This tranche does not change MiroFish logic.
- The main purpose is to make the current trusted handoff obvious from the repo docs.

## Tranche: MiroFish Portfolio Rerun Decision

### Files Changed

- `research/meta/MIROFISH_PORTFOLIO_RERUN_DECISION_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_portfolio_rerun_decision.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The repo already had a medium checkpoint, a stop-condition note, and an operator handoff, but it still did not contain one explicit artifact saying whether another deeper rerun should happen now.

### What Changed

- Added a rerun-decision note stating that another deeper full-universe rerun should be deferred from the current March 24 state
- Defined the minimum reopen contract:
  - declared harness
  - declared runtime budget
  - declared success criterion
  - explicit rejection rule if the new run does not beat the medium checkpoint
- Kept dashboard and export work downstream of that decision

### Verification

- Manual consistency review against:
  - `research/meta/MIROFISH_PORTFOLIO_MEDIUM_CHECKPOINT_NOTE_2026-03-24.md`
  - `research/meta/MIROFISH_PORTFOLIO_STOP_CONDITION_NOTE_2026-03-24.md`
  - `research/meta/MIROFISH_PORTFOLIO_OPERATOR_HANDOFF_2026-03-24.md`

### Notes

- This tranche is decision logging, not another runtime or methodology mutation.

## Tranche: MiroFish Portfolio Export

### Files Changed

- `src/chip_labs/mirofish/portfolio.py`
- `src/chip_labs/cli.py`
- `tests/test_mirofish_portfolio.py`
- `research/meta/MIROFISH_PORTFOLIO_EXPORT_515_MEDIUM_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_portfolio_export.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The repo could already produce raw portfolio run packets and JSON readouts, but it still lacked a clean human-facing export artifact for the current canonical medium checkpoint.

### What Changed

- Added `format_portfolio_readout_markdown()` so saved portfolio readouts can be rendered as operator-facing markdown
- Added a plain-text output helper in the CLI
- Added the `mirofish-portfolio-export` command
- Added focused coverage for the new markdown formatter
- Generated the medium-checkpoint markdown export artifact under `research/meta/`

### Verification

- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_trend_prediction.py tests/test_mirofish_portfolio.py -q`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-portfolio-export --input research/meta/MIROFISH_PORTFOLIO_READOUT_515_MEDIUM_2026-03-24.json --output research/meta/MIROFISH_PORTFOLIO_EXPORT_515_MEDIUM_2026-03-24.md --title "MiroFish Portfolio Medium Export: 2026-03-24"`

### Notes

- The export path is downstream of the saved readout packet and does not introduce a second ranking algorithm.
- This tranche makes the medium checkpoint easier to consume without reopening the rerun question.

## Tranche: MiroFish Dashboard Surface

### Files Changed

- `src/chip_labs/lab_hooks/watchtower.py`
- `tests/test_watchtower.py`
- `research/meta/MIROFISH_DASHBOARD_SURFACE_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_dashboard_surface.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The medium checkpoint already had a canonical export artifact, but there was still no in-repo dashboard surface consuming it inside the current mutable-target contract.

### What Changed

- Added a `MiroFish Portfolio.md` watchtower page
- Linked that page from the core watchtower surfaces
- Made the new page prefer the saved markdown export artifact
- Added a fallback that renders directly from the saved JSON readout packet if the markdown export is missing
- Added a clear stub when no saved MiroFish portfolio artifact exists yet

### Verification

- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_watchtower.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q`
- Run `$env:PYTHONPATH='src'; python -c "from chip_labs.watchtower import generate_watchtower_pages; pages=generate_watchtower_pages({}, chip_search_dir='.'); page=next(p for p in pages if p['path']=='MiroFish Portfolio.md'); print(page['content'][:1200])"`

### Notes

- This tranche deliberately uses the watchtower surface instead of the legacy `viz/` path.
- The watchtower page is a downstream surface over the canonical checkpoint, not a new ranking source.

## Tranche: MiroFish Watchtower Snapshot

### Files Changed

- `research/meta/watchtower_2026-03-24/Lab Home.md`
- `research/meta/watchtower_2026-03-24/Portfolio Dashboard.md`
- `research/meta/watchtower_2026-03-24/MiroFish Portfolio.md`
- `research/meta/watchtower_2026-03-24/Agent Team Status.md`
- `research/meta/watchtower_2026-03-24/Graduation Pipeline.md`
- `research/meta/watchtower_2026-03-24/Trend Predictions.md`
- `research/meta/MIROFISH_WATCHTOWER_SNAPSHOT_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_WATCHTOWER_SNAPSHOT_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_watchtower_snapshot.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The watchtower surface could already render the canonical MiroFish checkpoint, but the repo still did not contain a generated observatory snapshot under mutable targets.

### What Changed

- Ran the watchtower command with `vault_dir=research/meta/watchtower_2026-03-24`
- Saved the generated page list as a result packet
- Confirmed that the generated `MiroFish Portfolio.md` page resolves to the canonical medium export artifact

### Verification

- Run `$env:PYTHONPATH='src'; $env:SPARK_CHIP_SEARCH_DIR='.'; python -m chip_labs.cli watchtower --input research/meta/REQUEST_PACKET_2026-03-24_mirofish_watchtower_snapshot.json --output research/meta/MIROFISH_WATCHTOWER_SNAPSHOT_RESULT_2026-03-24.json`
- Inspect `research/meta/watchtower_2026-03-24/MiroFish Portfolio.md`

### Notes

- This snapshot keeps the observatory export inside the mutable-target contract.
- The generated page set is a concrete review surface for the current checkpoint, not a new evaluation run.

## Tranche: MiroFish Watchtower Refresh Command

### Files Changed

- `src/chip_labs/cli.py`
- `research/meta/watchtower_latest/Lab Home.md`
- `research/meta/watchtower_latest/Portfolio Dashboard.md`
- `research/meta/watchtower_latest/MiroFish Portfolio.md`
- `research/meta/watchtower_latest/Agent Team Status.md`
- `research/meta/watchtower_latest/Graduation Pipeline.md`
- `research/meta/watchtower_latest/Trend Predictions.md`
- `research/meta/MIROFISH_WATCHTOWER_LATEST_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_WATCHTOWER_REFRESH_COMMAND_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_watchtower_refresh_command.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The watchtower surface was now correct, but refreshing it still depended on a manual packet-driven sequence. That made the surface less reusable than it should be.

### What Changed

- Added a dedicated `mirofish-watchtower-snapshot` CLI command
- Used it to generate a refreshable latest surface under `research/meta/watchtower_latest`
- Saved the page list in a latest-result packet
- Documented the new refresh path in a dedicated note

### Verification

- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_watchtower.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-watchtower-snapshot --vault-dir research/meta/watchtower_latest --output research/meta/MIROFISH_WATCHTOWER_LATEST_RESULT_2026-03-24.json`

### Notes

- This tranche improves regeneration ergonomics, not portfolio methodology.
- The refresh command remains downstream of the canonical medium checkpoint export.

## Tranche: MiroFish Discovery Program

### Files Changed

- `src/chip_labs/mirofish/discovery.py`
- `src/chip_labs/cli.py`
- `tests/test_mirofish_discovery.py`
- `docs/MIROFISH_DISCOVERY_PROGRAM.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_SMOKE_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_SMOKE_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_SMOKE_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_SMOKE_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_TEMPLATE_100_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_SMOKE_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_program.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The repo already had a single-batch discovery contract, but the next strategic need was a staged path toward a large multi-agent discovery sweep. Jumping directly to a 1,000-agent run would repeat the earlier mistake of scaling before the intake surface was proven.

### What Changed

- Added a staged multi-agent discovery-program canonicalizer
- Added scale-readiness metrics and next-stage recommendations
- Added a `mirofish-discovery-program` CLI command
- Added focused tests for the new path
- Added a staged program doc and a 100-agent pilot template
- Ran a smoke discovery-program trial and bridged it into one hybrid evaluation pass
- Saved a note concluding that the correct next stage is the 100-agent pilot, not an immediate jump to 250 or 1,000 agents

### Verification

- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_mirofish_discovery.py tests/test_watchtower.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program --input research/meta/MIROFISH_DISCOVERY_PROGRAM_SMOKE_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_SMOKE_RESULT_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-hybrid-spec --input research/meta/MIROFISH_DISCOVERY_PROGRAM_SMOKE_RESULT_2026-03-24.json --output research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_SMOKE_2026-03-24.json --rounds 8 --flagship-count-per-type 8 --ensemble-runs 4 --ensemble-count-per-type 4 --scenario-label mirofish-discovery-program-smoke`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-hybrid-run --input research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_SMOKE_2026-03-24.json --output research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_SMOKE_2026-03-24.json`

### Notes

- The smoke pass proves the staged intake surface, not the final quality of a 1,000-agent frontier sweep.
- The hybrid smoke read shows that the accepted discoveries are still weak against the benchmark panel, which is why the next stage remains the 100-agent pilot.

## Tranche: MiroFish Discovery Pilot Scaffold

### Files Changed

- `src/chip_labs/mirofish/discovery.py`
- `src/chip_labs/cli.py`
- `tests/test_mirofish_discovery.py`
- `docs/MIROFISH_DISCOVERY_PROGRAM.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SCAFFOLD_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_program_pilot_100.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

After the smoke pass, the next honest artifact was the real 100-agent pilot scaffold, not a synthetic filled pilot result.

### What Changed

- Added a scaffold builder with a default 100-agent cluster allocation
- Added a CLI command to generate that scaffold directly
- Generated the actual 100-agent pilot intake packet
- Added a note explaining why the scaffold is the right next-stage artifact

### Verification

- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-scaffold --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SCAFFOLD_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_mirofish_discovery.py tests/test_watchtower.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q`

### Notes

- This tranche prepares the real pilot collection surface.
- It does not claim that the 100-agent pilot has already been run.

## Tranche: MiroFish Discovery Pilot Cluster Packets

### Files Changed

- `src/chip_labs/mirofish/discovery.py`
- `src/chip_labs/cli.py`
- `tests/test_mirofish_discovery.py`
- `docs/MIROFISH_DISCOVERY_PROGRAM.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_BRIEF_2026-03-24.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_program_pilot_100_clusters.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The real pilot scaffold existed, but it was still one large JSON packet. The next operator need was to break that into workable cluster tranches and expose the allocation in a readable brief.

### What Changed

- Added a scaffold splitter that emits per-cluster collection packets
- Added a markdown exporter for discovery scaffolds, cluster bundles, and canonicalized program packets
- Added CLI commands for split and brief generation
- Generated the actual `10`-cluster pilot packet bundle and markdown brief under `research/meta/`

### Verification

- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-split --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SCAFFOLD_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-brief --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json --title "MiroFish Discovery Pilot 100 Brief" --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_BRIEF_2026-03-24.md`
- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_mirofish_discovery.py tests/test_watchtower.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q`

### Notes

- This tranche still does not fabricate a filled `100`-agent result.
- It makes the real pilot executable in cluster-sized collection slices.

## Tranche: MiroFish Discovery Pilot Recombine

### Files Changed

- `src/chip_labs/mirofish/discovery.py`
- `src/chip_labs/cli.py`
- `tests/test_mirofish_discovery.py`
- `docs/MIROFISH_DISCOVERY_PROGRAM.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RECOMBINED_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RECOMBINE_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_program_pilot_100_recombine.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The split packet made the pilot collectible in batches, but there was still no repo-local step to merge completed cluster packets back into one program packet for canonicalization.

### What Changed

- Added a cluster-packet merge helper and CLI command
- Preserved `cluster_plan` and `collection_rules` across the split and merge round-trip
- Generated the recombined `100`-agent pilot packet under `research/meta/`
- Tightened the regression slice after catching and fixing a metadata-loss issue in the first recombine pass

### Verification

- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-split --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SCAFFOLD_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-merge --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RECOMBINED_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_mirofish_discovery.py tests/test_watchtower.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q`

### Notes

- This tranche completes the repo-local pilot round-trip without inventing any new discoveries.
- The recombined packet is ready for canonicalization once the cluster packets are filled with real submissions.

## Tranche: MiroFish Discovery Pilot Cluster Directory

### Files Changed

- `src/chip_labs/cli.py`
- `tests/test_mirofish_discovery.py`
- `docs/MIROFISH_DISCOVERY_PROGRAM.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_DIRECTORY_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_DIRECTORY_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_program_pilot_100_cluster_directory.json`
- `research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24/README.md`
- `research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24/01_security-compliance-response.json`
- `research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24/02_healthcare-revenue-cycle.json`
- `research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24/03_hvac-field-maintenance.json`
- `research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24/04_insurance-claims-appeals.json`
- `research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24/05_vendor-procurement-ops.json`
- `research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24/06_legal-audit-evidence.json`
- `research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24/07_workplace-training-compliance.json`
- `research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24/08_industrial-quality-inspection.json`
- `research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24/09_finance-reconciliation-backoffice.json`
- `research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24/10_logistics-last-mile-ops.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The pilot cluster bundle existed, but the actual collection step still needed a directory of concrete files that could be assigned and filled cluster-by-cluster.

### What Changed

- Added a materialization command that writes per-cluster packet files plus a README index
- Generated the repo-local working directory for the `100`-agent pilot
- Saved a manifest of the written files under `research/meta/`

### Verification

- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-materialize --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json --output-dir research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24 --index-title "MiroFish Discovery Pilot 100 Clusters" --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_DIRECTORY_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_mirofish_discovery.py tests/test_watchtower.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q`

### Notes

- This tranche creates the practical working surface for collection.
- It still does not fabricate a filled pilot result.

## Tranche: MiroFish Discovery Pilot Progress Surface

### Files Changed

- `src/chip_labs/cli.py`
- `tests/test_mirofish_discovery.py`
- `docs/MIROFISH_DISCOVERY_PROGRAM.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_program_pilot_100_progress.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

Once the pilot directory existed, the next operator need was a truthful progress surface over that directory so collection could be tracked without opening every cluster packet by hand.

### What Changed

- Added a repo-local progress command for materialized discovery directories
- Added markdown rendering for the progress surface
- Generated the initial empty baseline showing `0 / 100` filled agents and `0` raw candidates

### Verification

- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-progress --input-dir research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.json --markdown-output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.md --title "MiroFish Discovery Pilot 100 Progress"`
- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_mirofish_discovery.py tests/test_watchtower.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q`

### Notes

- The saved progress snapshot is intentionally empty because the pilot collection has not started yet.
- This tranche creates the status surface needed for real collection work.

## Tranche: MiroFish Discovery Security Tranche

### Files Changed

- `src/chip_labs/cli.py`
- `tests/test_mirofish_discovery.py`
- `docs/MIROFISH_DISCOVERY_PROGRAM.md`
- `research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24/01_security-compliance-response.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RECOMBINED_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.md`
- `research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_DIAGNOSTIC_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_PROMOTION_BRIEF_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_SECURITY_TRANCHE_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_program_security_tranche.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The pilot plumbing was complete, so the next honest step was to start real collection in one cluster and see whether the first tranche survived both discovery intake and early MiroFish evaluation.

### What Changed

- Added a bundle rebuild step so edits in the materialized cluster directory feed back into merge and canonicalization
- Filled the first three security-cluster agents with evidence-grounded candidates
- Refreshed the pilot progress read, partial pilot result, and bounded hybrid evaluation artifacts
- Saved the resulting diagnostic and promotion briefs for the first real collection slice

### Verification

- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-progress --input-dir research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.json --markdown-output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.md --title "MiroFish Discovery Pilot 100 Progress"`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-bundle --input-dir research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-merge --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RECOMBINED_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RECOMBINED_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-hybrid-spec --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.json --output research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json --rounds 8 --flagship-count-per-type 8 --ensemble-runs 4 --ensemble-count-per-type 4 --scenario-label mirofish-discovery-pilot-100-security-tranche`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-hybrid-run --input research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json --output research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-run-diagnostic --input research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_DIAGNOSTIC_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-promotion-brief --input research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_PROMOTION_BRIEF_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_mirofish_discovery.py tests/test_watchtower.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q`

### Notes

- This tranche starts real collection, but it is still only `3 / 100` agents filled.
- The security slice is promising enough to keep collecting, but not strong enough yet for promotion review.

## Tranche: MiroFish Discovery Security Tranche 2

### Files Changed

- `research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24/01_security-compliance-response.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RECOMBINED_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.md`
- `research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_DIAGNOSTIC_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_PROMOTION_BRIEF_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_SECURITY_TRANCHE_2_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_program_security_tranche_2.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The first three collected security candidates were good enough to justify one more small expansion of the same wedge before opening a new cluster.

### What Changed

- Added three more evidence-grounded candidates to the security cluster
- Refreshed the partial pilot result to `6` accepted clear-domain candidates
- Corrected the bounded hybrid read so it evaluates all `6` discovered domains instead of the stale `3`-domain spec
- The corrected read elevates `compensating-control-justification-copilot` to the current top security frontier candidate

### Verification

- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-progress --input-dir research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.json --markdown-output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.md --title "MiroFish Discovery Pilot 100 Progress"`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-bundle --input-dir research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-merge --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RECOMBINED_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RECOMBINED_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-hybrid-spec --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.json --output research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json --rounds 8 --flagship-count-per-type 8 --ensemble-runs 4 --ensemble-count-per-type 4 --scenario-label mirofish-discovery-pilot-100-security-tranche`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-hybrid-run --input research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json --output research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-run-diagnostic --input research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_DIAGNOSTIC_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-promotion-brief --input research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_PROMOTION_BRIEF_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_mirofish_discovery.py tests/test_watchtower.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q`

### Notes

- The corrected hybrid artifacts are the valid read for this tranche; the earlier parallel-generated `3`-domain spec should be ignored.
- The wedge is stronger, but the current recommendation is still frontier/watchlist rather than promotion review.

## Tranche: MiroFish Discovery Security Tranche 3

### Files Changed

- `research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24/01_security-compliance-response.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RECOMBINED_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.md`
- `research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_DIAGNOSTIC_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_PROMOTION_BRIEF_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_SECURITY_TRANCHE_3_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_program_security_tranche_3.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The security wedge was already producing the strongest frontier signal in the pilot, so the next most useful test was one more expansion inside the same cluster.

### What Changed

- Added three more evidence-grounded security-review candidates
- Refreshed the partial pilot result to `9` accepted clear-domain candidates
- Reran the bounded hybrid validation from the corrected `9`-candidate result
- The updated read now shows `trust-document-access-workflow-copilot` also clearing the benchmark median, while `questionnaire-answer-drift-copilot` is very close

### Verification

- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-progress --input-dir research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.json --markdown-output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.md --title "MiroFish Discovery Pilot 100 Progress"`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-bundle --input-dir research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-merge --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RECOMBINED_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RECOMBINED_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-brief --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.json --title "MiroFish Discovery Pilot 100 Result" --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.md`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-hybrid-spec --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.json --output research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json --rounds 8 --flagship-count-per-type 8 --ensemble-runs 4 --ensemble-count-per-type 4 --scenario-label mirofish-discovery-pilot-100-security-tranche`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-hybrid-run --input research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json --output research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-run-diagnostic --input research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_DIAGNOSTIC_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-promotion-brief --input research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SECURITY_TRANCHE_PROMOTION_BRIEF_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_mirofish_discovery.py tests/test_watchtower.py tests/test_mirofish_portfolio.py tests/test_trend_prediction.py -q`

### Notes

- The security cluster is now strong enough that the open question is saturation, not viability.
- Promotion status still remains frontier/watchlist rather than formal benchmark review.

## Tranche: MiroFish Discovery Program Viral Pivot

### Files Changed

- `src/chip_labs/mirofish/discovery.py`
- `tests/test_mirofish_discovery.py`
- `docs/MIROFISH_DISCOVERY_PROGRAM.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_SCAFFOLD_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CLUSTER_PACKETS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_BRIEF_2026-03-24.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CLUSTER_DIRECTORY_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_PROGRESS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_PROGRESS_2026-03-24.md`
- `research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24/README.md`
- `research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24/01_creator-growth-systems.json`
- `research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24/02_gaming-npc-community.json`
- `research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24/03_agentic-builders.json`
- `research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24/04_startup-founder-systems.json`
- `research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24/05_productivity-builder-ops.json`
- `research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24/06_career-status-social-proof.json`
- `research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24/07_consumer-agent-utilities.json`
- `research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24/08_crypto-defi-trading.json`
- `research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24/09_x-native-persona-tools.json`
- `research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24/10_design-remix-aesthetics.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_VIRAL_PIVOT_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_program_viral_pivot.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The earlier discovery pilot proved the mechanics, but it was too enterprise-adjacent for the current growth thesis. The next frontier should bias toward what ambitious online users actually care about now: creator growth, gaming/community, AI agents, startups, productivity, careers, consumer utilities, crypto, and X-native status loops.

### What Changed

- Replaced the default pilot cluster plan with a viral-first, X-native wedge allocation
- Added X-native persona archetypes and social-spread guidance to the scaffolded agent brief
- Updated tests and operator docs to match the new default scaffold
- Generated a fresh `pilot_100_viral` scaffold, bundle, brief, materialized cluster directory, and zero-state progress snapshot without overwriting the earlier security tranche artifacts

### Verification

- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_mirofish_discovery.py -q`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-scaffold --program-id mirofish-discovery-program-pilot-100-viral --stage-label pilot_100_viral --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_SCAFFOLD_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-split --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_SCAFFOLD_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CLUSTER_PACKETS_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-brief --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CLUSTER_PACKETS_2026-03-24.json --title "MiroFish Discovery Pilot 100 Viral Brief" --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_BRIEF_2026-03-24.md`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-materialize --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CLUSTER_PACKETS_2026-03-24.json --output-dir research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24 --index-title "MiroFish Discovery Pilot 100 Viral Clusters" --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CLUSTER_DIRECTORY_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-progress --input-dir research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_PROGRESS_2026-03-24.json --markdown-output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_PROGRESS_2026-03-24.md --title "MiroFish Discovery Pilot 100 Viral Progress"`

### Notes

- The earlier security-pilot artifacts remain valid historical evidence; this tranche creates a separate viral-first lane instead of overwriting them.
- The next useful collection order is `creator-growth-systems`, then `gaming-npc-community`, then `agentic-builders`.

## Tranche: MiroFish Discovery Program Viral Creator Tranche 1

### Files Changed

- `research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24/01_creator-growth-systems.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_PROGRESS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_PROGRESS_2026-03-24.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CLUSTER_PACKETS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RECOMBINED_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RESULT_2026-03-24.md`
- `research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_DIAGNOSTIC_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_PROMOTION_BRIEF_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_VIRAL_CREATOR_TRANCHE_1_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_program_viral_creator_tranche_1.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The viral-first pilot had a clean scaffold but no real collection yet. The next necessary step was to test the first creator-growth slice with evidence-linked, X-native candidates and see whether that wedge survives canonicalization and produces any early frontier signal.

### What Changed

- Filled the first `3` creator-growth agents with evidence-linked candidates around hook testing, clip repurposing, and creator memberships
- Refreshed the viral pilot progress and canonicalized result packet
- Ran a bounded hybrid creator tranche read plus diagnostic and promotion brief
- Corrected a malformed duplicated `raw_candidates` key in the first creator agent packet after an earlier refresh briefly produced a broken bundle/result surface

### Verification

- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-progress --input-dir research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_PROGRESS_2026-03-24.json --markdown-output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_PROGRESS_2026-03-24.md --title "MiroFish Discovery Pilot 100 Viral Progress"`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-bundle --input-dir research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CLUSTER_PACKETS_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-merge --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CLUSTER_PACKETS_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RECOMBINED_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RECOMBINED_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RESULT_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-brief --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RESULT_2026-03-24.json --title "MiroFish Discovery Pilot 100 Viral Result" --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RESULT_2026-03-24.md`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-hybrid-spec --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RESULT_2026-03-24.json --output research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json --rounds 8 --flagship-count-per-type 8 --ensemble-runs 4 --ensemble-count-per-type 4 --scenario-label mirofish-discovery-pilot-100-viral-creator-tranche`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-hybrid-run --input research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json --output research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-run-diagnostic --input research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_DIAGNOSTIC_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-promotion-brief --input research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_PROMOTION_BRIEF_2026-03-24.json`

### Notes

- All three current creator candidates survive canonicalization as `clear_domain_chip`.
- `creator-membership-flywheel-copilot` leads the bounded creator frontier read, but the entire slice still remains below the current benchmark floor and stays in `hold_in_frontier`.

## Tranche: MiroFish Discovery Program Viral Creator Tranche 2

### Files Changed

- `research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24/01_creator-growth-systems.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_PROGRESS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_PROGRESS_2026-03-24.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CLUSTER_PACKETS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RECOMBINED_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RESULT_2026-03-24.md`
- `research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_DIAGNOSTIC_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_PROMOTION_BRIEF_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_VIRAL_CREATOR_TRANCHE_2_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_program_viral_creator_tranche_2.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The first creator tranche showed a real frontier wedge, but it was still too small to tell whether creator-growth would keep producing concrete chips or collapse back into vague creator tooling. The next step was to deepen the creator cluster before opening gaming.

### What Changed

- Filled three more creator-growth agents with evidence-linked candidates around packaging tests, audience-comment mining, and creator brand-deal fit
- Refreshed the pilot progress, canonical result, and bounded creator-tranche hybrid read
- Increased the creator cluster to `6 / 16` filled agents and the pilot to `6 / 100`
- Reached `6` accepted `clear_domain_chip` candidates, pushing the pilot-level recommendation to `run_250_agent_pilot`

### Verification

- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-progress --input-dir research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_PROGRESS_2026-03-24.json --markdown-output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_PROGRESS_2026-03-24.md --title "MiroFish Discovery Pilot 100 Viral Progress"`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-bundle --input-dir research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CLUSTER_PACKETS_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-merge --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CLUSTER_PACKETS_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RECOMBINED_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RECOMBINED_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RESULT_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-brief --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RESULT_2026-03-24.json --title "MiroFish Discovery Pilot 100 Viral Result" --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RESULT_2026-03-24.md`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-hybrid-spec --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RESULT_2026-03-24.json --output research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json --rounds 8 --flagship-count-per-type 8 --ensemble-runs 4 --ensemble-count-per-type 4 --scenario-label mirofish-discovery-pilot-100-viral-creator-tranche`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-hybrid-run --input research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json --output research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-run-diagnostic --input research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_DIAGNOSTIC_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-promotion-brief --input research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_PROMOTION_BRIEF_2026-03-24.json`

### Notes

- Intake and bounded evaluation are now telling slightly different things:
  - intake quality says the creator wedge is strong enough to keep scaling
  - bounded hybrid evaluation still keeps the wedge in `hold_in_frontier`
- `creator-membership-flywheel-copilot` still leads the creator set, while the packaging loop candidates now form the next strongest slice.

## Tranche: MiroFish Discovery Program Viral Creator Tranche 3

### Files Changed

- `research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24/01_creator-growth-systems.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_PROGRESS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_PROGRESS_2026-03-24.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CLUSTER_PACKETS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RECOMBINED_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RESULT_2026-03-24.md`
- `research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_DIAGNOSTIC_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_PROMOTION_BRIEF_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_VIRAL_CREATOR_TRANCHE_3_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_program_viral_creator_tranche_3.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The creator wedge was still producing good intake quality after six agents. The next step was to add community, shopping, and collaboration loops and see whether the frontier leader changed once those creator-business surfaces were included.

### What Changed

- Extended the creator cluster from `6` to `9` filled agents
- Added creator shopping, fan-community activation, and creator-collab pipeline loops
- Refreshed the viral pilot result to `9` accepted `clear_domain_chip` candidates
- Recorded that `creator-collab-pipeline-copilot` now leads the bounded creator frontier read, even though the slice still remains below the benchmark floor

### Notes

- The creator wedge still looks healthy on intake and is close to being fully characterized.
- The correct next move is to finish creator first, then compare against a second wedge in gaming.

## Tranche: MiroFish Discovery Program Viral Creator Tranche 4

### Files Changed

- `research/meta/mirofish_discovery_pilot_100_viral_clusters_2026-03-24/01_creator-growth-systems.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_PROGRESS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_PROGRESS_2026-03-24.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CLUSTER_PACKETS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RECOMBINED_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_RESULT_2026-03-24.md`
- `research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_DIAGNOSTIC_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_VIRAL_CREATOR_TRANCHE_PROMOTION_BRIEF_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_VIRAL_CREATOR_TRANCHE_4_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_program_viral_creator_tranche_4.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The creator wedge was still productive, but the process itself had become too slow. This tranche broadens the creator frontier with trend, virtual-creator, and interactive-format loops while marking the end of micro-tranche collection.

### What Changed

- Extended the creator cluster from `9` to `12` filled agents
- Added trend-riff, virtual-creator, and interactive-format creator loops
- Refreshed the viral pilot result to `12` accepted `clear_domain_chip` candidates
- Recorded that the creator wedge now spans a broader set of viral sub-slices, while still staying below the bounded benchmark floor

### Notes

- Creator-growth is now broad enough that the remaining work should be done in wedge-sized batches rather than another chain of small tranches.

## Tranche: MiroFish Discovery Diverse Frontier Fast Path

### Files Changed

- `src/chip_labs/mirofish/discovery.py`
- `src/chip_labs/cli.py`
- `tests/test_mirofish_discovery.py`
- `docs/MIROFISH_DISCOVERY_PROGRAM.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_SCAFFOLD_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_CLUSTER_PACKETS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_BRIEF_2026-03-24.md`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_CLUSTER_DIRECTORY_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_PROGRESS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_PROGRESS_2026-03-24.md`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/README.md`
- `research/meta/MIROFISH_DISCOVERY_DIVERSE_FRONTIER_FAST_PATH_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_diverse_frontier_fast_path.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The discovery process had slowed down because too much effort was going into hand-curating small recommendation tranches before the intake surface had been fully exercised. The right response was to broaden intake, preserve diversity, and let selection happen later.

### What Changed

- Added a `diverse_frontier` discovery scaffold profile that scales beyond the smaller viral pilot
- Added scaffold profile selection to the CLI
- Updated discovery docs to make the new rule explicit: broad intake first, simulation later
- Generated a full `1000`-agent diverse-frontier scaffold, split bundle, brief, materialized directory, and zero-state progress surface
- Used same-persona sub-agents in parallel to generate the first `60` provisional domain ideas as seed material for the broad intake path

### Verification

- Run `$env:PYTHONPATH='src'; python -m pytest tests/test_mirofish_discovery.py -q`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-scaffold --profile diverse_frontier --program-id mirofish-discovery-program-frontier-1000-diverse --target-agent-count 1000 --stage-label frontier_1000_diverse --output research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_SCAFFOLD_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-split --input research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_SCAFFOLD_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_CLUSTER_PACKETS_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-brief --input research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_CLUSTER_PACKETS_2026-03-24.json --title "MiroFish Discovery Frontier 1000 Diverse Brief" --output research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_BRIEF_2026-03-24.md`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-materialize --input research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_CLUSTER_PACKETS_2026-03-24.json --output-dir research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24 --index-title "MiroFish Discovery Frontier 1000 Diverse Clusters" --output research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_CLUSTER_DIRECTORY_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-progress --input-dir research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_PROGRESS_2026-03-24.json --markdown-output research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_PROGRESS_2026-03-24.md --title "MiroFish Discovery Frontier 1000 Diverse Progress"`

### Notes

- Simulation is intentionally deferred in this path.
- The broad frontier should be collected first, then canonicalized, then evaluated.

## Tranche: MiroFish Discovery Seed Groups

### Files

- `research/meta/MIROFISH_DISCOVERY_FRONTIER_1000_SEED_GROUP_CREATOR_MEDIA_SOCIAL_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_FRONTIER_1000_SEED_GROUP_GAMING_COMMUNITY_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_FRONTIER_1000_SEED_GROUP_AGENT_STARTUP_PRODUCTIVITY_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_FRONTIER_1000_SEED_GROUP_CRYPTO_CONSUMER_CAREER_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_FRONTIER_1000_SEED_GROUPS_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_seed_groups.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The first same-persona discovery pool already existed conceptually, but it had not yet been persisted into repo-local intake artifacts. The broad `1000`-agent frontier path needed those seeds saved in reviewable chunks so collection can accelerate without reopening simulation.

### What Changed

- Packaged the first `60` provisional same-persona ideas into `4` grouped JSON seed artifacts
- Split the ideas by natural wedge instead of one oversized file
- Added a short tranche note and request packet for the grouped seed pool
- Kept the operating rule unchanged: broad intake first, simulation later

### Verification

- Manual consistency review against the same-persona outputs referenced in the frontier fast-path note

### Notes

- This tranche is additive only.
- No simulation or canonicalization was rerun here.

## Tranche: MiroFish Discovery Frontier Initial Fill

### Files

- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/01_creator-growth-systems.json`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/02_gaming-npc-community.json`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/03_agentic-builders.json`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/04_startup-founder-systems.json`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/05_productivity-builder-ops.json`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/06_career-status-social-proof.json`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/07_consumer-agent-utilities.json`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/08_crypto-defi-trading.json`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/09_x-native-persona-tools.json`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/10_design-remix-aesthetics.json`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/16_fandom-collectibles-communities.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_CLUSTER_PACKETS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_PROGRESS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_PROGRESS_2026-03-24.md`
- `research/meta/MIROFISH_DISCOVERY_FRONTIER_1000_INITIAL_FILL_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_frontier_initial_fill.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

The broad frontier had a scaffold and seed groups, but the live materialized directory was still mostly empty. To move faster toward the full `500`-chip / `1000`-agent intake, the first frontier seeds needed to be pushed directly into the actual cluster packets.

### What Changed

- Filled `57` agent slots across `11` diverse frontier clusters
- Spread the first same-persona seed ideas across creator, gaming, agentic builders, startup, productivity, crypto, consumer, career, X-native, design, and fandom wedges
- Rebuilt the combined frontier cluster bundle from the materialized directory
- Regenerated the frontier progress artifacts to reflect the live fill state of `57 / 1000`

### Verification

- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-bundle --input-dir research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_CLUSTER_PACKETS_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-progress --input-dir research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_PROGRESS_2026-03-24.json --markdown-output research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_PROGRESS_2026-03-24.md --title "MiroFish Discovery Frontier 1000 Diverse Progress"`

### Notes

- This tranche prioritizes breadth of live intake over early recommendation selectivity.
- Simulation remains intentionally deferred.

## Tranche: MiroFish Discovery Frontier Phase 1 Empty Wedge Activation

### Files

- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/11_education-skill-acceleration.json`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/12_health-fitness-self-systems.json`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/13_dating-social-signal.json`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/14_ecommerce-merchant-growth.json`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/15_local-discovery-experiences.json`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/17_finance-money-ops.json`
- `research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24/18_developer-distribution-tools.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_CLUSTER_PACKETS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_PROGRESS_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_PROGRESS_2026-03-24.md`
- `research/meta/MIROFISH_DISCOVERY_FRONTIER_1000_PHASE_1_EMPTY_WEDGE_ACTIVATION_NOTE_2026-03-24.md`
- `research/meta/REQUEST_PACKET_2026-03-24_mirofish_discovery_frontier_phase_1_empty_wedge_activation.json`
- `research/meta/CHANGE_LOG_2026-03-24.md`
- `research/meta/DIFF_SUMMARY_2026-03-24.md`

### Why

After the initial fill, the broad frontier still had several completely empty wedges. That left the intake surface biased toward the first interesting clusters rather than the full portfolio we want to test later.

### What Changed

- Activated `7` previously empty wedges with an initial seed tranche
- Added education, health, dating, ecommerce, local, finance, and developer-distribution candidates
- Regenerated the frontier bundle and progress surface to confirm the broader coverage
- Moved the live frontier from `57 / 1000` to `78 / 1000`

### Verification

- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-bundle --input-dir research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_CLUSTER_PACKETS_2026-03-24.json`
- Run `$env:PYTHONPATH='src'; python -m chip_labs.cli mirofish-discovery-program-progress --input-dir research/meta/mirofish_discovery_frontier_1000_diverse_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_PROGRESS_2026-03-24.json --markdown-output research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_DIVERSE_PROGRESS_2026-03-24.md --title "MiroFish Discovery Frontier 1000 Diverse Progress"`

### Notes

- All `18` frontier clusters now have at least one live candidate.
- Simulation remains intentionally deferred.
