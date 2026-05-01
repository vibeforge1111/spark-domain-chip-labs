# Startup YC Creator Run

Run ID: `creator-run-2026-05-01-startup-yc`  
Date: 2026-05-01  
Domain: Startup YC  
Evidence tier claimed: `transfer_supported`
Verdict target: `ready_for_swarm_packet`

## Intent

This example binds the adaptive creator-loop standard to the existing Startup YC specialization work. It is meant to prove that a real specialization path can expose its domain chip, benchmark, autoloop, absorption, reports, and Swarm packet in a standard creator-run shape.

## Evidence

| Suite | Baseline | Candidate | Delta | Trap regressions | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| Full 20-case absorption | 0.6803 | 0.7003 | +0.0200 | 0 | no-pack vs validated-pack |
| Weak-5 repeat | n/a | n/a | +0.0053 | n/a | focused pattern only |
| False-demand patch | n/a | n/a | +0.0092 / +0.0122 | n/a | focused mechanism improved |
| Reliability patch | n/a | n/a | +0.0044 | n/a | focused mechanism improved |
| Startup YC fresh validation suite | 0.7139 | 0.7699 | +0.0560 | 0 negative rows | 12/12 fresh scenarios won across six tracks |

## Current Claim

This is a transfer-supported Startup YC mastery packet, not a final mastery claim. The current positive transfer proof covers the 20-case fresh-agent absorption suite plus a 12-scenario Startup YC fresh validation suite across GTM, Finance, Product, People, Board, and Scale. It does not claim `network_absorbable` because multi-seed validation, human/operator calibration, privacy review, rollback review, and publication approval are still open gates.

## Smoke Gate

Run:

```bash
python -m chip_labs.cli creator-run-smoke docs/creator_system/examples/startup-yc-creator-run
```

Expected verdict: `ready_for_swarm_packet`.
