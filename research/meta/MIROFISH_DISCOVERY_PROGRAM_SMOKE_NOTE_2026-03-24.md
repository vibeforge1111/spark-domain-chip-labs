# MiroFish Discovery Program Smoke Note: 2026-03-24

## Scope

Run the first staged multi-agent discovery trial using the new discovery-program contract, then push the accepted set through the hybrid bridge once to decide the next scale step.

Artifacts:

- `research/meta/MIROFISH_DISCOVERY_PROGRAM_SMOKE_2026-03-24.json`
- `research/meta/MIROFISH_DISCOVERY_PROGRAM_SMOKE_RESULT_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_SPEC_DISCOVERY_PROGRAM_SMOKE_2026-03-24.json`
- `research/meta/MIROFISH_HYBRID_RUN_DISCOVERY_PROGRAM_SMOKE_2026-03-24.json`

## What Worked

The multi-agent intake surface itself worked.

Smoke metrics:

- participating agents: `5`
- raw candidates: `6`
- accepted candidates: `3`
- merged duplicates: `1`
- rejected candidates: `2`
- clear domains: `2`
- proto domains: `1`
- acceptance rate: `50%`
- merge rate: `16.67%`

Accepted set:

1. `vendor-security-review-copilot`
2. `dental-insurance-appeals-ai`
3. `hvac-maintenance-planner-ai` (`proto_domain_chip`)

That means the staged discovery-program contract is good enough to continue using.

## What Did Not Work

The smoke evaluation did not produce a benchmark-threatening discovered domain yet.

Hybrid smoke read:

- top ensemble benchmark: `startup-yc` at `1.34%`
- strongest discovered ensemble domain: `vendor-security-review-copilot` at `0.00%`
- strongest discovered trial domain: `vendor-security-review-copilot` at `1.34%`

Interpretation:

- the intake contract can produce plausible candidates
- the first smoke set does not yet produce a discovered candidate that survives the benchmark panel on retained adoption
- this is a reason to scale the discovery search carefully, not to skip ahead to the full 1,000-agent sweep

## Decision

Proceed to the `100`-agent pilot.

Do not jump straight to `250` or `1,000` agents yet.

Why:

- the smoke pass proves the intake surface
- duplicate pressure is manageable
- vague rejection is not dominating
- but the first accepted set is still weak against the benchmark panel

## 100-Agent Pilot Rules

Use the same program contract, and judge the pilot by:

- acceptance rate
- merge rate
- too-vague rate
- clear-domain count
- how many accepted candidates look worth a focused hybrid comparison

Pass gate to `250` agents:

- acceptance rate remains healthy
- duplicate pressure stays manageable
- the pilot yields several clear domains
- at least one cluster looks strong enough for a focused benchmark panel

## Full Program Rule

The `1,000`-agent / `500`-domain program should only happen after:

1. the `100`-agent pilot passes
2. the `250`-agent pilot passes
3. the pilot outputs show real cluster quality rather than only raw intake volume
