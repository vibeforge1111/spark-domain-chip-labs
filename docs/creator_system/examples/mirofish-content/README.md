# MiroFish Content Examples

These saved examples show how Spark should route and run local MiroFish-style
content simulation for candidate review.

Files:

- `route-invoke.json`: route packet for an explicit title-selection task. It
  returns `invoke` and includes the simulation packet that would be passed to
  the local simulator.
- `simulation-result.json`: deterministic local simulation result generated
  from the same candidate batch.
- `simulation-result.md`: operator-facing readout generated from the simulation
  result.
- `multi-seed-result.json`: deterministic three-seed simulator batch proving
  that the local top candidate is stable across seeded reruns.
- `provider-adapters.json`: future RLM judge adapter slots that are safe for
  local simulation metadata only; no live calls or credentials are enabled.

Claim boundary:

- These examples prove only `candidate_review local simulator protocol`.
- They do not prove real virality, real audience fit, or live provider
  calibration.
- Stronger claims require multi-seed simulator reruns, human/operator
  calibration, privacy and publication review, and comparison against actual
  content outcomes.

Recompute:

```bash
python -m chip_labs.cli mirofish-content-route \
  --task "Pick the best title for a post about agent benchmark honesty." \
  --candidate "7 benchmark mistakes that make AI agent demos look better than they are" \
  --candidate "The ultimate secret to amazing AI content" \
  --candidate "How to prove an agent workflow actually improved before you ship it" \
  --no-simulation \
  --output docs/creator_system/examples/mirofish-content/route-invoke.json

python -m chip_labs.cli mirofish-content-simulate \
  --task "Pick the best title for a post about agent benchmark honesty." \
  --candidate "7 benchmark mistakes that make AI agent demos look better than they are" \
  --candidate "The ultimate secret to amazing AI content" \
  --candidate "How to prove an agent workflow actually improved before you ship it" \
  --output docs/creator_system/examples/mirofish-content/simulation-result.json \
  --markdown-output docs/creator_system/examples/mirofish-content/simulation-result.md

python -m chip_labs.cli mirofish-content-multi-seed \
  --task "Pick the best title for a post about agent benchmark honesty." \
  --candidate "7 benchmark mistakes that make AI agent demos look better than they are" \
  --candidate "The ultimate secret to amazing AI content" \
  --candidate "How to prove an agent workflow actually improved before you ship it" \
  --seed 1 \
  --seed 2 \
  --seed 3 \
  --output docs/creator_system/examples/mirofish-content/multi-seed-result.json \
  --fail-on-blocked

python -m chip_labs.cli mirofish-provider-adapter-check \
  --input docs/creator_system/examples/mirofish-content/provider-adapters.json \
  --fail-on-blocked
```
