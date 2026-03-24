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
