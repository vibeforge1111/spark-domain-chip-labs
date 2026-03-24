# MiroFish Portfolio Operator Handoff: 2026-03-24

## Canonical Portfolio Checkpoint

Use the medium full-universe checkpoint as the current canonical portfolio read:

- `research/meta/MIROFISH_PORTFOLIO_RUN_515_MEDIUM_2026-03-24.json`
- `research/meta/MIROFISH_PORTFOLIO_READOUT_515_MEDIUM_2026-03-24.json`
- commit `6eb669b` `MiroFish: save medium portfolio checkpoint`

The later stop-condition tranche confirms that no post-checkpoint runtime experiment beat this state:

- `research/meta/MIROFISH_PORTFOLIO_STOP_CONDITION_NOTE_2026-03-24.md`
- commit `c5d5457` `MiroFish: record portfolio stop condition`

## How To Read This Checkpoint

Treat rank order as more trustworthy than absolute magnitude.

Important cautions:

- many rows still end with `final_adoption_rate=0.0`
- ensemble adoption is back, but still thin
- direct choice and trial are often more informative than final retained adoption in this checkpoint
- this is good enough for operator prioritization, not good enough for a dashboard refresh

## Portfolio Priorities

### Overall watchlist

1. `defi-architect`
2. `mcp-server-builder`
3. `tiktok-creator`
4. `discord-community`
5. `last-mile-delivery-ai`

Interpretation:

- `defi-architect` and `mcp-server-builder` lead the medium-harness ensemble read, but both still show visible interest-to-choice friction
- `last-mile-delivery-ai` is the highest-ranked newly discovered `v4` candidate in the overall slice

### Choice and retention outliers

1. `ai-npc-dialog`
2. `chronic-disease-mgr`
3. `hvac-optimizer-ai`
4. `roblox-development`

Interpretation:

- `ai-npc-dialog` leads direct choice and flagship retained adoption in the medium checkpoint
- `chronic-disease-mgr` and `hvac-optimizer-ai` show that some `v4` domains can win actual choice even when the ensemble layer still looks thin

### Enterprise watchlist

1. `chronic-disease-mgr`
2. `legal-ops`
3. `workplace-ai-trainer`
4. `addiction-recovery-ai`
5. `quality-inspection-ai`

Interpretation:

- `chronic-disease-mgr` is the cleanest enterprise-facing `v4` name in the current full-universe checkpoint
- `legal-ops` remains the strongest legacy enterprise holdover
- the enterprise slice is more informative than the zeroed interactive checkpoint, but still not strong enough for maintained benchmark claims

### Newly discovered `v4` watchlist

1. `last-mile-delivery-ai`
2. `voice-assistant-senior`
3. `chronic-disease-mgr`
4. `hvac-optimizer-ai`
5. `remote-job-matcher`

Interpretation:

- `last-mile-delivery-ai` is the current best `v4` overall signal
- `chronic-disease-mgr` is the most interesting `v4` enterprise candidate
- `remote-job-matcher` keeps showing up in the `v4` slice and is worth preserving in future comparison sets

## Operating Rules From Here

- Do not refresh dashboard or export from this checkpoint
- Do not read small differences in absolute adoption as robust portfolio truth
- Use this checkpoint for prioritization and for deciding whether one more bounded rerun is worth the cost
- If a deeper rerun is attempted later, define the runtime budget and success criterion before launching it
