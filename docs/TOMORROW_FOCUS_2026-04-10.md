# Tomorrow Focus: 2026-04-10

## Goal

Use the now-working Spark Swarm lane setup to do product-quality work rather than more integration churn.

Tomorrow should not be another bridge day unless a signed-in live bug appears. The main integration loop is already good enough to support quality iteration.

## Where We Stand

At the end of April 9:

1. `Startup YC`, `Crypto Trading`, and `XContent` are all visible on localhost `Spark Swarm`
2. the localhost preview on `127.0.0.1:4178` now points to local API `127.0.0.1:8787`
3. signed-out `/live` shows the curated available-lane set cleanly
4. specialization-scoped path ids are now part of the Spark Researcher contract
5. the weakest remaining issues are lane quality, not lane existence

Trusted current surfaces:

- `http://127.0.0.1:4178/live`
- `http://127.0.0.1:4178/api/workspace/bootstrap`
- `http://127.0.0.1:4178/health`

## Tomorrow: Tasks We Can Actually Finish

### 1. Verify the signed-in `/live` state in the browser

Why this is worth doing:

- signed-out preview is now correct
- what matters next is whether the signed-in live surface is equally coherent
- this is the shortest path to finding the next real product bug

Definition of done:

- signed-in `/live` clearly shows the active lane
- lane switching is understandable
- scorecard attribution remains specialization-correct
- no trading scorecard looks like it belongs to startup

What to specifically check:

- `Startup YC` shows startup benchmark context
- `Crypto Trading` shows trading scorecard factors
- `XContent` appears as a lane and does not look like a dead stub

### 2. Push `Crypto Trading` from honest reject lane toward useful evaluator lane

Why this is worth doing:

- bridge quality is already sufficient
- `Crypto Trading` is the most credibility-sensitive lane after `Startup YC`
- right now it is legible, but still weak

Concrete targets:

- improve strategy/backtest quality, not just score presentation
- focus on candidate families that can improve:
  - `profitability_score`
  - `paper_trade_readiness`
  - `walk_forward_consistency`
  - `stress_resilience`
- keep `max_drawdown` visible and honest

Definition of done:

- at least one trading run produces a materially more respectable scorecard
- the lane stops feeling like a dashboard for losing strategies

### 3. Tighten `XContent` into a stronger lane

Why this is worth doing:

- `XContent` is already visible and connected
- it still needs stronger runtime substance to justify its lane

Concrete targets:

- improve doctrine promotion discipline
- reduce noisy belief churn
- make `useful_reach_score` more legible in scorecards and lane summaries

Definition of done:

- one clearly useful promoted doctrine packet path
- one scorecard and lane summary that is easy to explain to another person

### 4. Continue `Startup YC` only on weak-track improvement

Why this is worth doing:

- `Startup YC` is already the strongest lane
- integration work here has diminishing returns compared to benchmark improvement

Concrete targets:

- continue weak-track candidate runs
- use benchmark components to target weak areas rather than broad random iteration
- keep `boundary_detection` pressure on

Definition of done:

- fresh benchmarked run evidence tied to a deliberately chosen weak track

## Not Tomorrow

- another broad Spark Swarm plumbing pass unless a signed-in live bug forces it
- expanding the visible lane set beyond the four curated lanes
- adding new chip specializations before the current three are stronger
- more scorecard abstraction without corresponding lane-quality improvement

## Preferred Order

1. verify signed-in localhost `/live`
2. improve `Crypto Trading`
3. improve `XContent`
4. continue targeted `Startup YC` benchmark improvement

## Concrete Commands To Start From

For `startup-yc`:

```powershell
$env:PYTHONPATH='C:\Users\USER\Desktop\spark-researcher\src;src'
python -m spark_researcher.cli candidates suggest --config C:\Users\USER\Desktop\domain-chip-startup-yc\spark-researcher.project.json --command research --limit 5
```

For `trading-crypto`:

```powershell
$env:PYTHONPATH='C:\Users\USER\Desktop\spark-researcher\src;src'
python -m spark_researcher.cli candidates suggest --config C:\Users\USER\Desktop\domain-chip-trading-crypto\spark-researcher.project.json --command research --limit 5
```

For `xcontent`:

```powershell
$env:PYTHONPATH='C:\Users\USER\Desktop\spark-researcher\src;src'
python -m spark_researcher.cli collective ready --config C:\Users\USER\Desktop\domain-chip-xcontent\spark-researcher.project.json
```

For localhost verification:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:4178/health
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:4178/api/workspace/bootstrap
```

## Remaining Noise To Ignore Tomorrow

In `spark-swarm`, there were pre-existing unrelated working-tree changes during this pass, including:

- `apps/web/src/routes/ProfilePage.tsx`
- `apps/web/src/routes/RuntimePage.tsx`
- `apps/web/local-preview.log`

Do not confuse those with the curated-lane integration work.
