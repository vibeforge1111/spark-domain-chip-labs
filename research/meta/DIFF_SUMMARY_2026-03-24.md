# Diff Summary: 2026-03-24

## Batch 1

MiroFish v4 engine rebalance:

- reduce threshold inflation
- reduce exploratory self-choking from `trial`
- soften retention collapse
- expose peak choice metrics in simulation and reports

## Batch 2

MiroFish discovery-factory planning:

- define discovery-first hybrid architecture
- preserve fixed benchmark universe as comparison layer
- specify first implementation tranche and harness shape

## Batch 3

MiroFish discovery contract and packet scaffolding:

- add deterministic discovery canonicalization module
- expose batch canonicalization in the CLI
- define the operator-facing discovery contract
- add a starter discovery batch packet for verification

## Batch 4

MiroFish hybrid evaluation spec bridge:

- infer conservative priors for accepted discovery candidates
- add a stable benchmark panel
- emit graph, signals, scenario, and harness inputs
- expose hybrid spec generation in the CLI

## Batch 5

MiroFish hybrid starter run:

- add a repo-local hybrid runner
- save an end-to-end starter evaluation artifact
- summarize how the first discovered candidate performed against the panel

## Batch 6

MiroFish expanded discovery batch:

- add the first broader manual discovery intake
- run the expanded accepted set through the hybrid harness
- tighten breakout-shock targeting to avoid intake-wide favoritism
- summarize the strongest discovered domain cluster

## Batch 7

MiroFish focused benchmark batch:

- narrow discovery around the strongest cluster
- run a custom enterprise-response benchmark panel
- identify the strongest discovered candidate under relevant comparison

## Batch 8

MiroFish promotion review:

- add a promotion-brief CLI for focused hybrid runs
- document the promotion-review operator workflow
- emit the first enterprise-response promotion brief
- recommend the first candidate for maintained benchmark review without auto-promoting it

## Batch 9

MiroFish benchmark-review validation:

- allow selected discovered candidates to move into a benchmark-review lane
- rerun the nominated enterprise candidate without discovery breakout support
- save the benchmark-review spec and run artifacts
- record that the candidate remains promising but does not yet earn maintained benchmark admission

## Batch 10

MiroFish enterprise-only review:

- narrow the enterprise-response comparison to questionnaire vs RFP
- rerun against the tighter maintained benchmark panel
- record that RFP becomes a co-review candidate rather than a resolved loser
- keep maintained benchmark admission open pending a symmetric no-breakout comparison

## Batch 11

MiroFish enterprise symmetric review:

- move both enterprise-response domains into benchmark review
- remove the final discovery-breakout asymmetry
- rerun the tight enterprise panel under symmetric conditions
- recommend the first maintained benchmark admission based on ensemble stability

## Batch 12

MiroFish enterprise benchmark proposal:

- add a provisional benchmark lane without editing the maintained library
- test RFP as a proposed benchmark member on a broader enterprise panel
- confirm that the narrow RFP recommendation does not yet survive the broader context
- defer the maintained benchmark library edit and keep the enterprise wedge in cluster review

## Batch 13

MiroFish enterprise cluster playoff:

- move all four enterprise-response domains into symmetric benchmark review
- remove proposal and discovery-lane asymmetry from the cluster
- rank first and second cluster priority under the cleanest comparison
- confirm that maintained benchmark admission is still premature

## Batch 14

MiroFish enterprise cluster diagnostic:

- add a diagnostic brief command for saved hybrid runs
- measure where enterprise domains lose conversion across the funnel
- show that questionnaire and renewal mainly leak after choice
- show that RFP mainly fails before choice, at interest-to-choice conversion

## Batch 15

MiroFish enterprise graph tuning:

- infer behavioral `domain_tags` from domain text and candidate context
- infer graph-level `retention_score` from sticky workflow cues
- rerun the symmetric enterprise cluster playoff with richer graph semantics
- show that questionnaire becomes the strongest enterprise ensemble domain
- show that renewal becomes the strongest enterprise attention domain
- show that RFP improves on ensemble adoption but remains a conversion problem

## Batch 16

MiroFish enterprise signal symmetry:

- add shared macro-aware awareness helpers in the simulation
- align churn and retention checks with fit-aware signals
- rerun the enterprise cluster playoff under signal symmetry
- show that questionnaire remains the strongest enterprise ensemble domain
- show that RFP and compliance evidence improve once retention-side checks stop using weaker semantics

## Batch 17

MiroFish enterprise conversion tuning:

- add a retention-aware conversion prior for interested and evaluating stages
- pass graph retention scores into persona evaluation
- rerun the enterprise cluster playoff under the conversion-tuned logic
- show that questionnaire and renewal benefit from the sticky-workflow prior
- show that RFP and compliance evidence still need a different choice-conversion hypothesis
