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
| Startup Bench compatible broad probe | 0.6885 | 0.6734 | -0.0151 | n/a | defer broad transfer |

## Current Claim

This is a transfer-supported Startup YC mastery packet, not a final mastery claim. The current positive transfer proof covers one fresh Startup Bench 0-to-1 activation scenario. A compatible 10-scenario Startup Bench probe underperformed the resilient baseline by `-0.0151`, so broad transfer is deferred until track-specific tool scripts/adapters improve.

## Smoke Gate

Run:

```bash
python -m chip_labs.cli creator-run-smoke docs/creator_system/examples/startup-yc-creator-run
```

Expected verdict: `ready_for_swarm_packet`.
