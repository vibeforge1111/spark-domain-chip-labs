# Creator System Proof Domains

Date: 2026-05-01

This document turns the current generator acceptance domains into standardized
examples that Spark can build out step by step.

The goal is not to create disconnected demos. The goal is to prove that the
creator-run standard can generate useful systems across different shapes of
work, while preserving evidence boundaries, recompute provenance, rollback, and
publication discipline.

Current proof level:

- Artifact verdict: `ready_for_swarm_packet`
- Evidence tier: `candidate_review`
- Publication boundary: `local_only`
- Network absorption: not claimed

Every domain below should move through the same ladder:

1. Generate a local creator-run workspace from a brief.
2. Pass hook smoke, benchmark baseline, specialization path, autoloop keep/revert, Swarm packet, and `creator-run-smoke --recompute`.
3. Replace deterministic acceptance stubs with real adapters for the existing Spark system.
4. Add transfer probes only after local candidate review is stable.
5. Add human/operator calibration.
6. Add privacy, rollback, malicious-packet, and publication review.
7. Only then consider `transfer_supported` or stronger claims.

## Layer 1: Artifact Quality

Purpose:

Help Spark improve design documents, PR descriptions, implementation handoffs,
and mission-control packets.

Current generated proof:

- Domain: `Design Doc PR Quality`
- Family: `artifact_quality`
- Benchmark family: `artifact_quality_review`
- Mission flow: `brief -> plan -> implementation trace -> PR review packet`

Useful Spark outcomes:

- Better Builder and mission-control design docs.
- PR summaries that include evidence, tests, risk, and rollback.
- Less polished-but-unproven documentation.

Acceptance cases:

- Review a design document for missing acceptance gates.
- Turn implementation notes into a concise PR-ready summary.
- Reject a polished document that lacks runnable proof.

Current executable local scorer:

```bash
python -m chip_labs.cli artifact-quality-score \
  --input docs/creator_system/examples/artifact-quality/good_design_pr.md \
  --artifact-kind pr_writeup \
  --output reports/artifact-quality.json \
  --markdown-output reports/artifact-quality.md
```

Creator-run benchmark reports can be generated from
`benchmark/artifact_quality_manifest.json`:

```bash
python -m chip_labs.cli artifact-quality-benchmark runs/<run-name>
python -m chip_labs.cli creator-run-smoke runs/<run-name> --recompute --fail-on-blocked
```

Current fixtures:

- `good_design_pr.md`: review-ready report with acceptance gates, runnable
  evidence, tests, risks, rollback, claim boundary, and mission handoff.
- `weak_design_pr.md`: sparse note that needs repair actions.
- `polished_unproven_trap.md`: polished prose that must block because it lacks
  runnable proof and rollback evidence.

Next real adapters:

- Feed real design docs and PR notes from Spark workspaces.
- Score against the creator-run evidence ladder, ship checklist, and review rules.
- Compare generated PR summaries against human-edited summaries.

Do not claim:

- That document polish equals product correctness.
- That a generated PR summary replaces human review.

## Layer 2: Tool Operation

Purpose:

Teach Spark to operate local tools safely, especially creator-run commands,
tests, dry-runs, and verification commands.

Current generated proof:

- Domain: `Spark Tool Operation`
- Family: `tool_operation`
- Benchmark family: `tool_operation_dry_run`
- Mission flow: `mission intent -> tool plan -> dry-run -> verification -> rollback note`

Useful Spark outcomes:

- Safer command selection.
- Clear dry-run and protected-tool boundaries.
- Tool results that are verified before mission-control state changes.

Acceptance cases:

- Plan a creator-run smoke command and required verification.
- Attach rollback notes to a failed local tool operation.
- Reject workflows that ask an operator to paste secrets into docs.

Current executable local checker:

```bash
python -m chip_labs.cli tool-operation-manifest
python -m chip_labs.cli tool-operation-check --input operation-packet.json --fail-on-blocked
```

An operation packet includes `command`, `exit_code`, parsed JSON `result`, and
an optional `rollback_note`. The checker blocks stdout-only evidence, protected
commands such as `git push`, and requests to paste tokens or secrets into docs.
It also supports `expected_postconditions` so a clean exit cannot silently move a
mission to the wrong state.

Current replay fixtures:

- `blocked_smoke_with_rollback.json`: blocked smoke with rollback note.
- `stale_evidence_recompute.json`: stale saved report caught by recompute.
- `missing_artifacts_expected_swarm.json`: clean smoke exit that fails the
  expected `ready_for_swarm_packet` postcondition.
- `unsafe_secret_request.json`: secret/token paste workflow blocked before state
  update.

Next real adapters:

- Connect to local CLI command manifests.
- Record expected postconditions for each operation.
- Add failure replay cases for blocked smoke, failing tests, stale evidence, and missing artifacts.

Do not claim:

- That Spark may push, publish, or mutate network state without review.
- That stdout alone proves a tool operation succeeded.

## Layer 3: MiroFish Content Simulation

Purpose:

Use MiroFish-style simulation whenever Spark needs to choose among content
ideas, titles, hooks, drafts, or angles.

This is the most product-useful simulator-heavy proof domain. Instead of asking
one model for taste, Spark can run simulated audience batches and multi-RLM judge
panels, then explain which option is best and which audience segment resisted it.

Current generated proof:

- Domain: `MiroFish Content Simulation`
- Family: `simulator_heavy`
- Benchmark family: `mirofish_content_simulation`
- Mission flow: `content candidates -> simulated audience batches -> multi-RLM judge aggregation -> best option with weak-row diagnosis`

Invocation triggers:

- content idea selection
- title or hook ranking
- draft comparison
- angle testing

Current simulator protocol:

- Simulator name: `mirofish-content-arena`
- Mode: `persona_batch_multi_rlm_judging`
- Agent batch size: `24`
- Persona segments:
  - founder-builders
  - technical-operators
  - creator-economy-readers
  - skeptical-experts
- RLM judges:
  - spark-local-judge
  - frontier-reasoning-judge
  - fast-taste-judge
- Aggregation rule: rank by median predicted save/share/reply intent, then inspect weak segments.

Current executable local harness:

```bash
python -m chip_labs.cli mirofish-content-simulate \
  --input content-candidates.json \
  --output reports/mirofish-content-simulation.json \
  --markdown-output reports/mirofish-content-simulation.md
```

Agents can also invoke the harness without a temporary JSON file:

```bash
python -m chip_labs.cli mirofish-content-simulate \
  --task "Pick the best post title." \
  --candidate "7 benchmark mistakes that make AI agent demos look better than they are" \
  --candidate "How to prove an agent workflow actually improved before you ship it"
```

The helper layer should evoke this simulator when a task asks Spark to choose,
rank, compare, or test content ideas, titles, hooks, angles, or drafts.

For Spark-facing routing, ask for a route packet first:

```bash
python -m chip_labs.cli mirofish-content-route \
  --task "Pick the best post title." \
  --candidate "7 benchmark mistakes that make AI agent demos look better than they are" \
  --candidate "How to prove an agent workflow actually improved before you ship it" \
  --no-simulation
```

Route mode returns `invoke` or `skip`, the reason, candidate count, claim
boundary, and the target local command. Omit `--no-simulation` when the caller
also wants the embedded local simulation result.

Saved examples:

- `examples/mirofish-content/route-invoke.json`
- `examples/mirofish-content/simulation-result.json`
- `examples/mirofish-content/simulation-result.md`

The read-only product-surface fixture also references
`examples/mirofish-content/route-invoke.json` as a `content_route` source
packet. This makes the Canvas adapter show the content simulator as evidence
without granting Builder, Telegram, Spawner, Canvas, or Kanban runtime authority.

Example input:

```json
{
  "candidates": [
    {
      "id": "specific",
      "text": "7 benchmark mistakes that make AI agent demos look better than they are"
    },
    {
      "id": "operator",
      "text": "How to prove an agent workflow actually improved before you ship it"
    }
  ],
  "persona_segments": [
    "founder-builders",
    "technical-operators",
    "creator-economy-readers",
    "skeptical-experts"
  ],
  "rlm_judges": [
    "spark-local-judge",
    "frontier-reasoning-judge",
    "fast-taste-judge"
  ]
}
```

The current harness is deterministic. The judge names represent future adapter
slots, not live provider calls yet.

Scoring dimensions:

- predicted save intent
- predicted share intent
- reply likelihood
- audience specificity
- weak-segment regression

Acceptance cases:

- Rank five post titles for expected saves, shares, and replies across simulated audience segments.
- Choose the strongest angle from several content ideas and explain weak segment resistance.
- Reject a viral claim based only on one RLM judge or one aggregate score.

Next real adapters:

- Accept a list of titles, hooks, post ideas, or drafts as the benchmark input.
- Run batches across multiple model judges when provider adapters are available.
- Save per-persona and per-judge rows, not only aggregate scores.
- Compare simulator predictions against actual post outcomes when available.
- Use outcome deltas to calibrate persona weights and judge reliability.

Do not claim:

- That simulated virality equals real distribution.
- That one model's ranking proves content quality.
- That high aggregate score is safe when a critical audience segment regresses.

## Layer 4: Doctor Adversarial And Security

Purpose:

Improve Spark's doctor system so it can diagnose fake evidence, unsafe
promotion, missing provenance, and weak repair plans.

Current generated proof:

- Domain: `Spark Doctor Adversarial`
- Family: `adversarial_security`
- Benchmark family: `doctor_security_regression`
- Mission flow: `blocked run -> doctor diagnosis -> repair step -> re-smoke proof`

Useful Spark outcomes:

- Better detection of stale or fake report evidence.
- Repair plans tied to exact failed checks.
- Stronger refusal to promote candidate-review evidence as network absorption.

Acceptance cases:

- Flag a report whose saved score does not match provenance.
- Generate repair steps tied to exact failed checks.
- Reject network absorption from candidate-review evidence.

Current executable local harness:

```bash
python -m chip_labs.cli creator-run-doctor runs/<run-name> --recompute
```

Recompute-mode doctor output includes `repair_replay` and `quarantine` fields.
The replay command is the proof boundary: repair advice is not complete until
`creator-run-smoke --recompute --fail-on-blocked` passes after the repair.

Current adversarial fixtures:

- `doctor-security/stale_candidate_report_score.json`: mutates a saved
  candidate report so recompute mode must block and quarantine stale evidence.
- `doctor-security/malicious_network_absorption_packet.json`: mutates a Swarm
  packet so candidate-review evidence falsely claims `network_absorbable`.

Next real adapters:

- Build fixtures from real `creator-run-doctor` output packets.
- Add broader malicious packet quarantine examples.
- Add more repair replay checks across provenance, packet, and privacy failures.

Do not claim:

- That doctor pass equals publication approval.
- That repair advice is valid without rerun evidence.

## Layer 5: Startup YC Operator

Purpose:

Make Spark better at startup and business advice while preserving evidence
boundaries.

Startup YC remains both a golden reference and a future product capability: Spark
should become a strong startup operator, but it must not claim broad mastery from
local or single-seed evidence.

Current generated proof:

- Domain: `Startup YC Operator`
- Family: `startup_founder_advice`
- Benchmark family: `startup_yc_operator`
- Mission flow: `founder question -> diagnosis -> advice packet -> follow-up benchmark`

Useful Spark outcomes:

- Sharper founder advice.
- Better separation between urgent customer pain and vague interest.
- More useful narrow-wedge suggestions.

Acceptance cases:

- Diagnose whether a founder has urgent customer pain.
- Suggest the narrowest useful wedge for a broad product idea.
- Reject traction claims backed only by vanity metrics.

Current validation pack:

- `startup-yc-operator-validation/validation_plan.json`: promotion gates,
  current claim, prohibited claims, and minimum multi-seed plan.
- `startup-yc-operator-validation/held_out_founder_advice_cases.jsonl`:
  held-out founder prompts for demand reality, vanity metrics, narrow wedge,
  default-alive pressure, and privacy boundaries.
- `startup-yc-operator-validation/human_operator_calibration_checklist.md`:
  human/operator review gates.
- `startup-yc-operator-validation/privacy_rollback_publication_review.md`:
  privacy, rollback, and publication approval boundaries.

Next real adapters:

- Connect held-out founder-advice cases to a scoring harness.
- Run multi-seed validation across GTM, Finance, Product, People, Board, and Scale.
- Add human/operator calibration on real founder advice examples.
- Keep `transfer_supported` separate from `network_absorbable`.

Do not claim:

- That Startup YC is network absorbable without multi-seed validation, calibration,
  privacy review, rollback review, and publication approval.

## Layer 6: Retrieval And Memory

Purpose:

Eventually prove that Spark can retrieve the right prior context without turning
workflow residue into memory truth.

Status:

Local contract fixtures exist. Production memory wiring remains deferred until
the memory system is ready to plug into this benchmark flow.

Likely acceptance cases:

- Retrieve the right prior decision for a current task.
- Refuse stale or contradicted memory.
- Keep private, local, and network-shareable memory lanes separate.
- Detect memory contamination from conversational residue.

Current executable local harness:

```bash
python -m chip_labs.cli retrieval-memory-check \
  --input docs/creator_system/examples/retrieval-memory/correct_prior_decision.json \
  --fail-on-blocked
```

Current fixtures:

- `retrieval-memory/correct_prior_decision.json`: local workspace memory with
  exact source refs and provenance.
- `retrieval-memory/stale_memory.json`: stale context blocked until revalidated.
- `retrieval-memory/contradicted_memory.json`: recalled context blocked by newer
  contradictory artifacts.
- `retrieval-memory/residue_contamination.json`: conversational residue blocked
  from durable memory truth.
- `retrieval-memory/network_without_review.json`: network-shareable context
  blocked without review approval.

Claim boundary:

This is a local memory-lane contract only. It does not wire production memory,
prove recall quality, or authorize network-shareable memory.

Next real adapters:

- Connect to Spark's memory store once stable.
- Add provenance and freshness checks for retrieved memories.
- Add contradiction and privacy-boundary probes.

Do not claim:

- That retrieval success equals safe memory promotion.
- That conversational residue is evidence.

## Documentation Standard For Future Proof Domains

Every new proof domain should include:

- domain id, name, and family
- mission-control flow
- invocation triggers
- useful-to-Spark outcomes
- benchmark family
- acceptance cases, including at least one trap
- mutation axes
- operating principles
- unsafe claims
- known limits
- next real adapters
- explicit evidence tier and publication boundary

Every generated proof must pass:

```bash
python -m pytest tests/test_creator_generator_acceptance.py -q
python -m chip_labs.cli creator-run-smoke <generated-run> --recompute --fail-on-blocked
```

Every stronger claim requires additional proof beyond this document.
