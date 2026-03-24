# Today Summary: 2026-03-25

## Goal

Recover the strong old MiroFish graph workflow, stop over-trusting synthetic discovery scaffolding, and get back to a realistic path for selecting hot domain chips from a curated pool.

## What We Accomplished

### 1. Proved the broad synthetic frontier path was the wrong source of truth

- We pushed the frontier-discovery path all the way through large-scale intake, tranche building, readouts, shortlist surfaces, and watchtower pages.
- That work did produce useful simulator plumbing and export helpers.
- But it also made the core problem obvious:
  - the synthetic `1000`-agent candidate pool was too templated
  - many names were near-duplicates
  - the simulator was choosing from noisy source material
  - the resulting UI looked busy rather than decision-grade

Key conclusion:

- the frontier-discovery path should not remain the primary source for a `500`-chip simulator run

### 2. Restored the old graph workflow as the right presentation target

- We confirmed that the old `viz` graph surface was still the correct operator-facing experience.
- We stopped treating watchtower markdown and shortlist pages as the main way to inspect outcomes.
- We rebuilt repo-local support for generating old-style graph surfaces directly from MiroFish packets.

Key conclusion:

- the right UI is still the old graph-style surface, not the markdown/watchtower detour

### 3. Rebuilt the curated source path around a true unique `500`

Commit:

- `4adb715` `MiroFish: rebuild curated frontier 500`

What changed:

- rebuilt [curated_frontier.py](/C:/Users/USER/Desktop/spark-domain-chip-labs/src/chip_labs/mirofish/curated_frontier.py)
- generated a curated `500`-domain source packet in:
  - [MIROFISH_CURATED_FRONTIER_500_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_CURATED_FRONTIER_500_2026-03-25.json)
  - [MIROFISH_CURATED_FRONTIER_500_2026-03-25.md](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_CURATED_FRONTIER_500_2026-03-25.md)
- enforced hard validation:
  - no duplicate ids
  - no suffix-family spam such as `-copilot`, `-engine`, `-loop`, `-lab`, `-os`
  - exactly `10` clusters and `500` unique ideas

Key result:

- we now have a much better source pool than the synthetic frontier expansion

### 4. Fixed the graph renderer so it uses packet personas rather than stale hardcoded personas

What changed:

- updated [hybrid.py](/C:/Users/USER/Desktop/spark-domain-chip-labs/src/chip_labs/mirofish/hybrid.py)
- the frontier viz renderer now hydrates persona metadata from the packet instead of a stale built-in persona list

Key result:

- the old graph surface can now render curated-frontier packets without collapsing into the obviously wrong old persona model

### 5. Produced a live curated `500` localhost surface

Artifacts:

- [MIROFISH_CURATED_FRONTIER_VIZ_500_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_CURATED_FRONTIER_VIZ_500_2026-03-25.json)
- [MIROFISH_CURATED_FRONTIER_VIZ_500_2026-03-25.html](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_CURATED_FRONTIER_VIZ_500_2026-03-25.html)

Localhost:

- `http://localhost:8890/MIROFISH_CURATED_FRONTIER_VIZ_500_2026-03-25.html`

Verification:

- graph packet contains `500` domains, `508` nodes, and `500` edges
- tests passed:
  - `python -m pytest tests/test_mirofish_discovery.py tests/test_mirofish_hybrid.py -q`
  - `19 passed in 0.50s`

## What We Learned

### 1. The current curated `500` localhost page is a source-pool view, not a trusted winner map

The page is live and useful for inspecting the candidate pool shape, but its score spread is too compressed to treat as a real simulator verdict.

Observed score compression in the committed graph packet:

- `builder_adoption` min: `2.48%`
- `builder_adoption` median: `2.80%`
- `builder_adoption` max: `3.02%`

Observed source compression:

- `composite_score`: `0.7637` to `0.8087`
- `community_demand`: `0.94` to `0.95`

Meaning:

- the committed `500` graph is still mostly reflecting fallback source heuristics
- it is not yet a differentiated agent-selection outcome

### 2. The earlier curated `180` simulation artifacts are stale and should not be trusted

Fresh and trustworthy inputs:

- [MIROFISH_CURATED_FRONTIER_TRANCHE_180_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_CURATED_FRONTIER_TRANCHE_180_2026-03-25.json)
- [MIROFISH_HYBRID_SPEC_CURATED_FRONTIER_TRANCHE_180_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_HYBRID_SPEC_CURATED_FRONTIER_TRANCHE_180_2026-03-25.json)

Untrustworthy output:

- [MIROFISH_HYBRID_RUN_CURATED_FRONTIER_TRANCHE_180_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_HYBRID_RUN_CURATED_FRONTIER_TRANCHE_180_2026-03-25.json)

Reason:

- the run output still contains stale old suffix-family ids from earlier work, so any readout/export/viz derived from that file should be treated as contaminated

Affected derived artifacts to distrust:

- [MIROFISH_FRONTIER_READOUT_CURATED_TRANCHE_180_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_FRONTIER_READOUT_CURATED_TRANCHE_180_2026-03-25.json)
- [MIROFISH_FRONTIER_EXPORT_CURATED_TRANCHE_180_2026-03-25.md](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_FRONTIER_EXPORT_CURATED_TRANCHE_180_2026-03-25.md)
- [MIROFISH_CURATED_FRONTIER_VIZ_180_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_CURATED_FRONTIER_VIZ_180_2026-03-25.json)
- [MIROFISH_CURATED_FRONTIER_VIZ_180_2026-03-25.html](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_CURATED_FRONTIER_VIZ_180_2026-03-25.html)

## What We Did Not Finish Yet

- We did complete a fresh curated-frontier hybrid run under clean filenames, but we did not yet build and validate the readout/export/viz layer from that fresh run.
- We did not produce a trustworthy scored localhost page that shows what the agents actually picked from the curated pool.
- We did not clean up the stale untracked tranche artifacts under `research/meta/`.
- We did not touch the pre-existing unrelated dirty files in:
  - [personas.py](/C:/Users/USER/Desktop/spark-domain-chip-labs/src/chip_labs/mirofish/personas.py)
  - [simulation.py](/C:/Users/USER/Desktop/spark-domain-chip-labs/src/chip_labs/mirofish/simulation.py)

That was intentional. The correct next step is a clean fresh run, not another round of UI drift.

## Deliverables Created Today

Main commits from March 25:

- `88134f8` `MiroFish: save deeper frontier tranche 180`
- `d1f4535` `MiroFish: add frontier watchtower surface`
- `cfc8261` `MiroFish: add frontier shortlist`
- `d494a9f` `MiroFish: add frontier shortlist watchtower surface`
- `336df39` `MiroFish: add frontier localhost shortlist`
- `670a2d7` `MiroFish: add frontier 500 viz surface`
- `7e3226c` `MiroFish: add curated frontier 500 source`
- `4adb715` `MiroFish: rebuild curated frontier 500`

Trusted current March 25 source artifacts:

- [MIROFISH_CURATED_FRONTIER_500_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_CURATED_FRONTIER_500_2026-03-25.json)
- [MIROFISH_CURATED_FRONTIER_500_2026-03-25.md](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_CURATED_FRONTIER_500_2026-03-25.md)
- [MIROFISH_CURATED_FRONTIER_VIZ_500_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_CURATED_FRONTIER_VIZ_500_2026-03-25.json)
- [MIROFISH_CURATED_FRONTIER_VIZ_500_2026-03-25.html](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_CURATED_FRONTIER_VIZ_500_2026-03-25.html)

Fresh-run lane prepared today:

- [MIROFISH_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json)
- [MIROFISH_HYBRID_SPEC_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_HYBRID_SPEC_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json)
- [MIROFISH_HYBRID_RUN_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_HYBRID_RUN_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json)

Quick validation on the fresh run:

- it contains the new curated ids, not the stale suffix-family ids
- `adoption_probability` ranges from `0.0` to `0.1`
- `agent_choice_signal` ranges from `0.0` to `0.2`

That means the fresh run lane is materially healthier than the contaminated curated `180` lane, but its readout/export/viz surface still needs to be built and checked tomorrow.

## End-of-Day Status

- The old graph UI path has been recovered.
- The curated source pool is much healthier than the synthetic frontier pool.
- The repo now has a better `500` source set, but not yet a trustworthy scored `500` simulation surface.
- The next blocker is no longer "invent more chips" or "polish another dashboard."
- The next blocker is a clean curated-frontier hybrid run that can produce a real winner map without stale artifact contamination.
