# Tomorrow Focus: 2026-03-26

## Goal

Finish one clean curated-frontier simulation path and turn the old graph UI into a trustworthy winner map rather than a compressed source-pool view.

## Where We Stand

At the end of March 25:

1. the old graph UI is back and working
2. the curated `500` source pool is rebuilt and materially better than the synthetic frontier pool
3. the committed `500` localhost page is still heuristic-compressed and should not be treated as a final selection result
4. the first curated `180` run path is contaminated by stale artifacts and must not be used as tomorrow's baseline

Trusted surface to start from:

- source-pool localhost view:
  - `http://localhost:8890/MIROFISH_CURATED_FRONTIER_VIZ_500_2026-03-25.html`

Do not trust as selection outputs:

- [MIROFISH_HYBRID_RUN_CURATED_FRONTIER_TRANCHE_180_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_HYBRID_RUN_CURATED_FRONTIER_TRANCHE_180_2026-03-25.json)
- [MIROFISH_FRONTIER_READOUT_CURATED_TRANCHE_180_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_FRONTIER_READOUT_CURATED_TRANCHE_180_2026-03-25.json)
- [MIROFISH_FRONTIER_EXPORT_CURATED_TRANCHE_180_2026-03-25.md](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_FRONTIER_EXPORT_CURATED_TRANCHE_180_2026-03-25.md)
- [MIROFISH_CURATED_FRONTIER_VIZ_180_2026-03-25.html](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_CURATED_FRONTIER_VIZ_180_2026-03-25.html)

## Tomorrow: Tasks We Can Actually Finish

### 1. Validate the fresh curated-frontier run and use it as tomorrow's only trusted evaluation lane

Why this is worth doing:

- This is the missing piece between a good source pool and a real selection map.
- The current `500` page is compressed because it is not backed by a trustworthy scored run.
- The stale `180` run already proved that filename collisions and artifact reuse are a real risk.

Already-prepared fresh lane:

- [MIROFISH_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json)
- [MIROFISH_HYBRID_SPEC_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_HYBRID_SPEC_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json)
- [MIROFISH_HYBRID_RUN_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json](/C:/Users/USER/Desktop/spark-domain-chip-labs/research/meta/MIROFISH_HYBRID_RUN_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json)

Current quick-check state:

- ids are the rebuilt curated ids
- `adoption_probability` spans `0.0` to `0.1`
- `agent_choice_signal` spans `0.0` to `0.2`

Exact rerun command if the file needs to be regenerated:

```powershell
python -m chip_labs.cli mirofish-hybrid-run `
  --input research/meta/MIROFISH_HYBRID_SPEC_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json `
  --output research/meta/MIROFISH_HYBRID_RUN_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json `
  --seed 42
```

Definition of done:

- the fresh run remains reproducible
- the ids in that run are the new curated ids, not old suffix-family ids

### 2. Build readout, export, and graph only from the fresh run

Why this is worth doing:

- The graph is only as good as the run packet behind it.
- We already have the right UI surface.
- What is missing is a trustworthy scored packet, not a new frontend.

Concrete follow-up commands:

```powershell
python -m chip_labs.cli mirofish-frontier-readout `
  --input research/meta/MIROFISH_HYBRID_RUN_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json `
  --output research/meta/MIROFISH_FRONTIER_READOUT_CURATED_TRANCHE_120_FRESH_2026-03-26.json
```

```powershell
python -m chip_labs.cli mirofish-frontier-export `
  --input research/meta/MIROFISH_FRONTIER_READOUT_CURATED_TRANCHE_120_FRESH_2026-03-26.json `
  --output research/meta/MIROFISH_FRONTIER_EXPORT_CURATED_TRANCHE_120_FRESH_2026-03-26.md
```

```powershell
python -m chip_labs.cli mirofish-frontier-viz `
  --input research/meta/MIROFISH_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json `
  --output-json research/meta/MIROFISH_CURATED_FRONTIER_VIZ_120_FRESH_2026-03-26.json `
  --output-html research/meta/MIROFISH_CURATED_FRONTIER_VIZ_120_FRESH_2026-03-26.html `
  --run-input research/meta/MIROFISH_HYBRID_RUN_CURATED_FRONTIER_TRANCHE_120_FRESH_2026-03-25.json `
  --title "MiroFish Curated Frontier 120 Fresh"
```

Definition of done:

- localhost shows a scored graph with meaningful spread
- scores are no longer all packed between roughly `2.5%` and `3.0%`

### 3. Decide whether to scale from fresh `120` to fresh `180` or fresh `500`

Why this is worth doing:

- The clean `120` run is the proof point.
- Scaling should happen only after the spread looks real and the artifacts are clean.

Decision rule:

- if fresh `120` shows clear score separation and clean ids, scale to `180`
- if fresh `120` is still too compressed, fix selection methodology before scaling

Definition of done:

- there is an explicit go/no-go note for scaling beyond the fresh tranche

### 4. Clean or quarantine stale artifacts instead of mixing them into tomorrow's view

Why this is worth doing:

- stale files already caused confusion once
- tomorrow should have one clean lane, not mixed generations

Files to treat as stale or quarantine candidates:

- `research/meta/MIROFISH_HYBRID_RUN_CURATED_FRONTIER_TRANCHE_180_2026-03-25.json`
- `research/meta/MIROFISH_FRONTIER_READOUT_CURATED_TRANCHE_180_2026-03-25.json`
- `research/meta/MIROFISH_FRONTIER_EXPORT_CURATED_TRANCHE_180_2026-03-25.md`
- `research/meta/MIROFISH_CURATED_FRONTIER_VIZ_180_2026-03-25.json`
- `research/meta/MIROFISH_CURATED_FRONTIER_VIZ_180_2026-03-25.html`

Definition of done:

- tomorrow's trusted lane is obvious from filenames and notes

## Not Tomorrow

- another large synthetic discovery expansion
- more watchtower or markdown presentation work before the fresh run exists
- trusting the current compressed `500` graph as a final verdict
- mixing stale `180` outputs into the new curated evaluation lane

## Preferred Order

1. finish or rerun the fresh `120` curated hybrid run
2. validate that the ids are truly from the rebuilt curated pool
3. build readout/export/viz from that fresh run only
4. inspect the new localhost graph for real spread
5. decide whether to scale to `180` or `500`

## Remaining Repo Noise To Ignore Tomorrow

Pre-existing modified files that were not part of this work:

- [personas.py](/C:/Users/USER/Desktop/spark-domain-chip-labs/src/chip_labs/mirofish/personas.py)
- [simulation.py](/C:/Users/USER/Desktop/spark-domain-chip-labs/src/chip_labs/mirofish/simulation.py)

Other untracked noise currently in the worktree:

- old tuned tranche artifacts under `research/meta/`
- untracked `viz/*.json`
- `nul`

Do not confuse those with the trusted curated-frontier lane.
