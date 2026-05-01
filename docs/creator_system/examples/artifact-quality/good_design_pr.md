# Creator Route Mode PR Writeup

## Summary

This change adds a local route packet for MiroFish content simulation so Spark
can decide whether a content-selection prompt should invoke the simulator.

## Acceptance Gates

- The route returns `invoke` only when at least two candidates are present.
- The route returns `skip` for unrelated prompts and selection prompts without
  candidates.
- The JSON report includes candidate count, route reason, and claim boundary.

## Evidence And Commands

- `python -m pytest tests/test_mirofish_content_simulation.py -q` passed.
- `python -m pytest tests/test_mirofish_content_simulation.py tests/test_creator_generator_acceptance.py tests/test_creator_run.py tests/test_creator_run_examples.py -q` passed.
- `python -m chip_labs.cli creator-run-smoke docs/creator_system/examples/startup-yc-creator-run --fail-on-blocked --fail-on-warn` passed.

## Risk Boundary

This is a local simulator route only. It does not prove real content outcomes,
audience fit, or calibrated model-judge reliability.

## Rollback Plan

Revert the route helper, CLI command, docs, and tests if route packets produce
false invokes or hide the claim boundary.

## Claim Boundary

Safe claim: Spark can produce a local route packet for content-selection tasks.

Do not claim: route mode proves virality or replaces human editorial review.

## Mission Handoff

Next action: feed route packets into the future tool-operation phase as a local
command contract, before any product-surface wiring.
