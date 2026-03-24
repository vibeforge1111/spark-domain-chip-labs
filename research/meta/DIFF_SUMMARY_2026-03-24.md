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

## Batch 18

MiroFish enterprise choice conversion:

- infer graph-level `choice_score` from proof-heavy workflow cues
- add a narrow choice-aware awareness boost for interested and evaluating personas
- rerun the enterprise cluster playoff under the explicit choice-conversion logic
- show that questionnaire and renewal stay above the benchmark median
- show that RFP gets closer to the benchmark line while compliance evidence still fails to retain after stronger choice

## Batch 19

MiroFish validation determinism fix:

- replace the cooldown path's process-randomized `hash()` usage with deterministic md5-based pair bucketing
- rerun the planned enterprise validation artifact after restoring replay stability
- confirm that same-spec same-seed enterprise replays match across fresh Python processes
- show that questionnaire remains the strongest enterprise ensemble candidate
- show that renewal stays narrowly above the benchmark median while RFP stays narrowly below it

## Batch 20

MiroFish portfolio runtime fix:

- add adjacency indexing for graph edge lookup used during persona expertise assignment
- index signals by domain once per round during simulation
- cache effective awareness within a round so churn and retention reuse the same awareness family
- confirm the tiny full-universe portfolio harness now completes in interactive time

## Batch 21

MiroFish portfolio interactive readout:

- run the full 515-domain universe through the repo-local portfolio CLI with a thin interactive harness
- save the portfolio packet and derived readout under research/meta
- record that the harness completes operationally but collapses absolute adoption and choice values to zero
- treat the batch as an execution checkpoint rather than the final trusted portfolio verdict

## Batch 22

MiroFish portfolio medium checkpoint:

- run the full 515-domain universe through the repo-local portfolio CLI with a medium interactive harness
- recover non-zero ensemble and choice signal after the zeroed checkpoint
- save the medium packet and derived readout under research/meta
- record that the result is more informative but still not the final trusted portfolio verdict

## Batch 23

MiroFish portfolio stop condition:

- test one final simulation-side runtime optimization after the medium checkpoint
- reject the uncommitted signal-decay precompute idea after the tiny full-universe benchmark regresses to `78.8s`
- rerun the regression pair after reverting the failed experiment
- record that the committed medium checkpoint remains the correct portfolio handoff

## Batch 24

MiroFish portfolio operator handoff:

- add an operator-facing note that names the medium checkpoint as the canonical current portfolio read
- preserve the current overall, enterprise, and `v4` priority slices in one concise artifact
- update the March 24 day summary to reflect the completed 515-domain rerun and stop condition
- update the March 25 focus doc so it starts from the actual handoff instead of the already-finished methodology plan

## Batch 25

MiroFish portfolio rerun decision:

- state explicitly that another deeper full-universe rerun should not be launched from the current March 24 state
- define the minimum harness, runtime-budget, and success-criterion contract required to reopen that path
- keep the medium checkpoint as canonical until a future rerun clearly beats it on usefulness

## Batch 26

MiroFish portfolio export:

- add a markdown formatter for saved portfolio readout packets
- expose a repo-local `mirofish-portfolio-export` CLI command
- generate the medium-checkpoint markdown export under `research/meta/`
- verify the new exporter with the focused portfolio regression suite

## Batch 27

MiroFish dashboard surface:

- wire the canonical medium checkpoint into the watchtower observatory surface
- add a `MiroFish Portfolio` page that prefers the saved markdown export and falls back to the saved readout packet
- link the new page from the main watchtower pages
- verify the surface with focused tests and a direct generation check

## Batch 28

MiroFish watchtower snapshot:

- generate a repo-local watchtower page set under `research/meta/`
- save the generated page list as a result packet
- confirm that `MiroFish Portfolio.md` resolves to the canonical medium export artifact

## Batch 29

MiroFish watchtower refresh command:

- add a dedicated `mirofish-watchtower-snapshot` CLI command
- generate a refreshable `research/meta/watchtower_latest` surface from that command
- save the emitted page list as a latest-result packet
- keep the refresh workflow repo-local and bounded

## Batch 30

MiroFish discovery program:

- add a staged multi-agent discovery-program packet and CLI path
- add scale-readiness metrics so smoke and pilot runs recommend the next stage explicitly
- save a smoke-trial program packet, canonicalized result, hybrid spec, and hybrid run
- document that the next stage is the 100-agent pilot rather than a direct jump to the full 1,000-agent sweep

## Batch 31

MiroFish discovery pilot scaffold:

- add a dedicated scaffold builder for the real 100-agent pilot packet
- expose it through `mirofish-discovery-program-scaffold`
- generate the actual pilot intake packet with cluster allocation and per-agent briefs
- keep the next-stage artifact truthful by generating a scaffold rather than a fake filled result

## Batch 32

MiroFish discovery pilot cluster packets:

- split the real 100-agent scaffold into `10` operator-facing cluster packets
- add a markdown brief generator for discovery scaffolds and cluster bundles
- expose the new split and brief flows through repo-local CLI commands
- generate the actual cluster bundle and readable pilot brief under `research/meta/`

## Batch 33

MiroFish discovery pilot recombine:

- add a repo-local merge step that recombines cluster packets into one program input packet
- preserve `cluster_plan` and `collection_rules` across the split and merge round-trip
- generate the actual recombined pilot packet under `research/meta/`
- tighten the discovery regression slice after fixing the first metadata-loss bug in the recombine flow

## Batch 34

MiroFish discovery pilot cluster directory:

- add a repo-local materialization step that writes the cluster bundle into per-cluster working files
- generate a `README.md` index plus `10` cluster packet JSON files under `research/meta/`
- save the written-file manifest for the materialized directory
- make the `100`-agent pilot directly assignable without editing the combined bundle by hand

## Batch 35

MiroFish discovery pilot progress surface:

- add a repo-local command that reads the materialized cluster directory and reports fill progress
- generate JSON and markdown progress snapshots for the empty pilot baseline
- make cluster collection status visible without opening each packet manually
- preserve the truthful starting state of `0 / 100` filled agents before collection begins

## Batch 36

MiroFish discovery security tranche:

- add a repo-local bundle rebuild step so the materialized directory can feed back into merge and canonicalization
- fill the first three security-cluster agents with evidence-grounded candidates
- refresh the progress, recombined packet, and canonicalized partial pilot result
- run a bounded hybrid validation pass plus diagnostic and promotion briefs for the first collected slice

## Batch 37

MiroFish discovery security tranche 2:

- extend the security cluster from `3` to `6` filled agents
- refresh the partial pilot result to `6` accepted clear-domain candidates
- correct the stale parallel-generated hybrid spec by rerunning the spec and hybrid read from the updated result
- record `compensating-control-justification-copilot` as the current top watchlist candidate inside the security frontier slice

## Batch 38

MiroFish discovery security tranche 3:

- extend the security cluster from `6` to `9` filled agents
- refresh the partial pilot result to `9` accepted clear-domain candidates
- rerun the bounded hybrid read from the corrected `9`-candidate result
- record that `trust-document-access-workflow-copilot` now also clears the benchmark median while the wedge stays in frontier/watchlist

## Batch 39

MiroFish discovery viral pivot:

- replace the default `100`-agent discovery scaffold with viral-first, X-native clusters
- add X persona archetypes and social-spread guidance to the scaffolded agent brief
- update the discovery-program tests and operator doc to match the new default
- generate a fresh `pilot_100_viral` scaffold, cluster bundle, brief, materialized directory, and zero-state progress surface

## Batch 40

MiroFish discovery viral creator tranche 1:

- fill the first `3` creator-growth agents with evidence-linked viral/X-native creator candidates
- refresh the viral pilot progress, bundle, recombined packet, and canonicalized result
- run a bounded hybrid creator-tranche read plus diagnostic and promotion brief
- correct the malformed duplicate `raw_candidates` key that briefly broke the first cluster bundle during refresh

## Batch 41

MiroFish discovery viral creator tranche 2:

- extend the creator-growth cluster from `3` to `6` filled agents
- add packaging-test, audience-comment, and brand-deal creator loops
- refresh the viral pilot result to `6` accepted clear-domain candidates
- record that intake quality now supports `run_250_agent_pilot` while bounded hybrid evaluation still keeps the wedge in frontier

## Batch 42

MiroFish discovery viral creator tranche 3:

- extend the creator-growth cluster from `6` to `9` filled agents
- add creator shopping, fan-community activation, and creator-collab pipeline loops
- refresh the viral pilot result to `9` accepted clear-domain candidates
- record that `creator-collab-pipeline-copilot` now leads the bounded creator frontier read while the whole slice remains below the benchmark floor

## Batch 43

MiroFish discovery viral creator tranche 4:

- extend the creator-growth cluster from `9` to `12` filled agents
- add trend-riff, virtual-creator, and interactive-format creator loops
- refresh the viral pilot result to `12` accepted clear-domain candidates
- mark the end of micro-tranche collection so the next step can move at wedge scale

## Batch 44

MiroFish discovery diverse frontier fast path:

- add a scalable `diverse_frontier` discovery scaffold profile and expose it in the CLI
- document the new operating rule: broad diverse intake first, simulation later
- generate a full `1000`-agent diverse-frontier scaffold and materialized cluster directory
- use same-persona sub-agents in parallel to generate the first `60` provisional domain ideas for the broad intake path

## Batch 45

MiroFish discovery same-persona seed groups:

- persist the first `60` provisional frontier ideas into `4` grouped JSON intake artifacts
- split them across creator/media/social, gaming/community, agent-startup-productivity, and crypto-consumer-career wedges
- add a short note and request packet so the broad frontier can keep moving without reopening simulation

## Batch 46

MiroFish discovery frontier initial fill:

- push the first frontier seed pool into the live `1000`-agent materialized cluster directory
- fill `57` agent slots across `11` diverse clusters instead of staying in a zero-state scaffold
- rebuild the combined cluster bundle and regenerate the frontier progress surface at `57 / 1000`

## Batch 47

MiroFish discovery frontier phase 1 empty wedge activation:

- activate the `7` wedges that were still empty after the initial fill
- add first seed candidates for education, health, dating, ecommerce, local, finance, and developer-distribution clusters
- move the live frontier from `57 / 1000` to `78 / 1000` with all `18` clusters now represented

## Batch 48

MiroFish discovery frontier phase 2 densification:

- deepen the highest-priority interesting wedges instead of spreading into more new categories
- move creator to `14`, gaming to `20`, agentic builders to `12`, startup to `12`, and crypto to `14`
- move the live frontier from `78 / 1000` to `109 / 1000`
