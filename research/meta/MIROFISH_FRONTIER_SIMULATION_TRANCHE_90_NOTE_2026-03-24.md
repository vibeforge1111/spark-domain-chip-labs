# MiroFish Frontier Simulation Tranche 90

This tranche converts the fully canonicalized `1000`-agent frontier into a diversity-preserving simulation packet and runs the first bounded MiroFish evaluation on that smaller set.

Runtime boundary:

- a direct full-frontier bounded hybrid spec on the full `1000` accepted candidates expanded to roughly `482 MB`
- the corresponding full-frontier hybrid run did not produce a run packet within the runtime budget and was stopped
- the practical evaluation surface for this turn is therefore the `90`-domain simulation tranche, not the full `1000`

Simulation tranche construction:

- selected `5` accepted candidates per frontier cluster
- total simulation tranche size: `90`
- preserved representation across all `18` clusters

Saved artifacts:

- `research/meta/MIROFISH_DISCOVERY_PROGRAM_FRONTIER_1000_SIMULATION_TRANCHE_90_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_SPEC_FRONTIER_TRANCHE_90_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_FRONTIER_TRANCHE_90_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_DIAGNOSTIC_FRONTIER_TRANCHE_90_2026-03-24.json`

Top-line read:

- top choice-signal domain: `defi_yield_rotation_loop`
- top choice signal: `0.10`
- top final-adoption domain: `defi_yield_rotation_loop`
- top final adoption: `0.00`
- top ensemble domain: `defi_yield_rotation_loop`
- top ensemble mean adoption: `0.00`

Interpretation:

- the tranche produced live attention and choice separation, especially in crypto and selected creator / builder surfaces
- retained adoption remains effectively zero under this thin bounded harness
- the dominant diagnostic pattern is `interest_to_choice_friction`, not lack of top-of-funnel interest

Why this matters:

- the repo now has a real full-frontier-to-simulation checkpoint instead of only a raw intake surface
- the next methodology question is no longer whether we have enough domains; it is how to get frontier interest to convert into choice and retained adoption under MiroFish
