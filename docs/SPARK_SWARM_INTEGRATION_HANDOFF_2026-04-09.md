# Spark Swarm Integration Handoff: 2026-04-09

## Purpose

This document is the direct handoff for continuing the Spark Swarm + domain-chip integration work tomorrow without re-deriving what happened today.

It covers:

- what changed
- what was verified
- what is still incomplete
- what should be done next

## Repos Touched In The Workstream

Core and site:

- `C:\Users\USER\Desktop\spark-researcher`
- `C:\Users\USER\Desktop\spark-swarm`
- `C:\Users\USER\Desktop\startup-bench`

Active chips:

- `C:\Users\USER\Desktop\domain-chip-startup-yc`
- `C:\Users\USER\Desktop\domain-chip-trading-crypto`
- `C:\Users\USER\Desktop\domain-chip-xcontent`

## Most Important Technical Fix

The key fix was in `spark-researcher`.

Old unsafe payload path shape:

- `evolution-path:research`

Correct payload path shape now:

- `evolution-path:startup-yc:research`
- `evolution-path:trading-crypto:research`
- `evolution-path:xcontent:research`

Why this matters:

- Spark Swarm lane identity depends on path identity being specialization-scoped
- if multiple chips share one generic path id, live state can be misattributed across lanes

## What Was Verified Today

### A. Local preview wiring

Verified:

- `http://127.0.0.1:4178/health`

Expected result:

- `service: spark-swarm-web-local-proxy`
- `apiOrigin: http://127.0.0.1:8787`

Meaning:

- localhost preview is now pointed at local API, not production

### B. Signed-out bootstrap lane set

Verified:

- `http://127.0.0.1:4178/api/workspace/bootstrap`

Expected visible specialization paths:

- `startup-operator`
- `startup-yc`
- `trading-crypto`
- `xcontent`

No longer expected in the curated set:

- `trading-crypto-evolution`

### C. Signed-out `/live` page

Visually verified:

- `No live session`
- `Available Lanes`
- cards for:
  - `Startup Operator`
  - `Startup YC`
  - `Crypto Trading`
  - `XContent`

Evidence screenshot:

- [live-page-waited.png](/C:/Users/USER/Desktop/spark-researcher/live-page-waited.png)

### D. Chip readiness and payload regeneration

The following chip repos were regenerated and republished:

- `startup-yc`
- `trading-crypto`
- `xcontent`

Each was brought to:

- `ready: true`
- `hosted_ready: true`

### E. Startup benchmark connection

`startup-yc` is benchmark-grounded through `Startup Bench`, not merely advisory.

Important benchmark-layer improvements from this workstream:

- richer benchmark component preservation in `startup-bench`
- richer benchmark metrics carried in `startup-yc`
- benchmark context surfaced into Spark Swarm payloads

### F. Trading scorecards

`Crypto Trading` now supports standardized score plus domain-specific factor readout.

The site can explain trading outcomes with:

- `profitability_score`
- `win_rate`
- `paper_trade_readiness`
- `holdout_profitability`
- `walk_forward_consistency`
- `stress_resilience`
- `max_drawdown`

## Repo Heads To Start From Tomorrow

- `spark-researcher`: `5939eea`
- `spark-swarm`: `e611c28`
- `startup-bench`: `6bafefa`
- `domain-chip-startup-yc`: `309577b`
- `domain-chip-trading-crypto`: `79dfde757`
- `domain-chip-xcontent`: `acf4efc`

## What Is Actually Done

Done:

- specialization-scoped path ids in Spark Researcher
- readiness diagnostics for stale payloads
- payload regeneration and republish for the three main chips
- localhost preview re-pointed to local API
- signed-out `/live` lane preview fixed
- curated lane set visible on localhost
- `Crypto Trading` label and attribution aligned

## What Is Not Done

Not done yet:

- verified signed-in `/live` walkthrough end to end
- stronger `Crypto Trading` evaluator quality
- stronger `XContent` lane substance
- additional `Startup YC` benchmark wins beyond integration correctness

## Recommended Starting Sequence Tomorrow

### 1. Verify signed-in `/live`

Open:

- `http://127.0.0.1:4178/live`

Confirm:

- active lane is understandable
- lane switching is understandable
- scorecards remain attributed to the correct specialization

### 2. Improve `Crypto Trading`

Focus on:

- better candidate quality
- better evaluator outcomes
- not just prettier scorecards

### 3. Improve `XContent`

Focus on:

- doctrine quality
- promotion discipline
- lane readability

### 4. Continue `Startup YC`

Focus on:

- weak-track benchmark iteration
- targeted benchmark work, not general integration work

## Commands Worth Reusing

Payload readiness and publish:

```powershell
$env:PYTHONPATH='C:\Users\USER\Desktop\spark-researcher\src;src'
python -m spark_researcher.cli collective ready --config <chip>\spark-researcher.project.json
python -m spark_researcher.cli collective spark-swarm-payload --config <chip>\spark-researcher.project.json
python -m spark_researcher.cli collective publish --config <chip>\spark-researcher.project.json
python -m spark_researcher.cli collective ready --config <chip>\spark-researcher.project.json
```

Localhost checks:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:4178/health
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:4178/api/workspace/bootstrap
```

Candidate suggestion:

```powershell
$env:PYTHONPATH='C:\Users\USER\Desktop\spark-researcher\src;src'
python -m spark_researcher.cli candidates suggest --config <chip>\spark-researcher.project.json --command research --limit 5
```

## Important Operational Cautions

### 1. Do not reopen the bridge problem unless the signed-in live view is actually wrong

The bridge work is good enough now. It is easy to lose time on more integration polish when the real remaining gaps are lane quality and operator comprehension.

### 2. Keep `Crypto Trading Evolution` out of the curated localhost lane set for now

That lane should not return to the main visible set until it has the same level of runtime evidence and operator clarity as the main three.

### 3. Treat `Startup Operator` as the umbrella lane, not the only startup lane

`Startup YC` is now a first-class lane and should remain visible as such.

## If You Need A One-Sentence Summary Tomorrow

The Spark Swarm bridge is now good enough; tomorrow should start with signed-in localhost validation and then move immediately into `Crypto Trading`, `XContent`, and targeted `Startup YC` quality work.
