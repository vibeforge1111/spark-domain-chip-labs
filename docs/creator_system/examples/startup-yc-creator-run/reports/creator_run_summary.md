# Startup YC Creator Run Fixture Summary

Verdict target: `ready_for_swarm_packet`

This fixture proves that the adaptive creator-run smoke gate can recognize an existing specialization path with all required artifact classes present.

Evidence referenced:

- Full 20-case fresh-agent absorption proof.
- Mean no-pack score: `0.6803`.
- Mean validated-pack score: `0.7003`.
- Mean validated-pack delta: `+0.0200`.
- Startup Bench fresh 0-to-1 transfer delta: `+0.0169`.
- Startup Bench compatible 10-scenario broad probe delta: `-0.0151`.
- Case count: `20`.
- Trap band case count: `5`.
- Mastery readiness from source proof: `candidate_review`.
- Creator-run evidence tier: `transfer_supported`.

Known limits:

- This fixture references source repos instead of copying full benchmark corpora.
- The current smoke gate checks artifact presence and schema only.
- Broad transfer is not proven yet. The compatible 10-scenario probe shows the current Startup YC script is too 0-to-1-specific and needs track-specific tool scripts/adapters.
