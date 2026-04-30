# Benchmark And Autoloop Protocol

## Purpose

This protocol defines how Spark should create benchmarks and autoloops that produce real improvement instead of score theater.

The basic rule:

> An autoloop is only useful if its mutations are evaluated by a benchmark that is harder to fool than the mutation surface.

## Benchmark Design Principles

### 1. Benchmark The Capability, Not The Story

Do not benchmark whether the agent can explain a domain. Benchmark whether it can perform a useful operation in that domain.

Examples:

- Bad: "Does the startup answer sound YC-ish?"
- Better: "Given a startup scenario, does the agent choose the right next constraint to attack?"
- Bad: "Does the prompt engineering chip know prompt terms?"
- Better: "Does it produce prompts that outperform a baseline on held-out tasks?"

### 2. Separate Evidence Lanes

Every benchmark result must declare its lane:

| Lane | Meaning | Promotion strength |
| --- | --- | --- |
| `source_evidence` | Based on credible external material | useful context, not enough alone |
| `benchmark_evidence` | Passed a reproducible evaluation | strong local proof |
| `live_evidence` | Worked in real usage | strongest after trace review |
| `exploratory_frontier` | Interesting but unproven | never promote as doctrine |

Never promote exploratory or operational residue as durable intelligence.

### 3. Use Held-Out Cases

The autoloop may see training cases, but promotion requires held-out cases.

Minimum pack:

- 5 development cases
- 5 held-out cases
- 3 adversarial cases
- 1 no-op regression case

For early prototypes, a tiny pack is acceptable, but the result must be labeled `prototype`.

### 4. Measure Components

Single scores hide failure. Benchmarks should return component scores.

Startup YC example:

```json
{
  "overall": 0.67,
  "components": {
    "customer_pain": 0.80,
    "retention_logic": 0.72,
    "revenue_quality": 0.48,
    "runway_risk": 0.76,
    "focus": 0.61
  },
  "weakest_track": "revenue_quality"
}
```

Autoloops should target the weakest track instead of randomly stacking doctrines.

### 5. Add Anti-Gaming Checks

Every benchmark should detect at least:

- format inflation
- keyword stuffing
- overfitting to public cases
- confidence increase without decision improvement
- regression on no-op cases
- unsafe broadening of mutation surface

## Benchmark Families

### Fixed-Case Rubric

Use when decisions can be scored from scenario answers.

Required:

- stable cases
- rubric dimensions
- expected failure traps
- judge calibration if an LLM judge is used

Best for:

- startup operator judgment
- prompt quality
- marketing strategy
- security review

### Simulator Benchmark

Use when the agent must act across changing state.

Required:

- state model
- action space
- transition rules
- scoring horizon
- replay seed

Best for:

- Founder Arena
- genetic startup simulator
- trading
- growth experiments
- multi-step tool ops

### Tool-Operation Benchmark

Use when the domain is tool execution.

Required:

- task script
- observable output
- trace validation
- forbidden action checks
- recovery cases

Best for:

- browser use
- Telegram bot operation
- Spawner missions
- repo maintenance
- data import/export

### Artifact Benchmark

Use when the output is a concrete artifact.

Required:

- artifact schema
- visual or structural checks
- quality rubric
- regression fixtures

Best for:

- landing pages
- docs
- pitch decks
- code generators
- design systems

### Collective Benchmark

Use when testing whether Swarm intelligence actually helps another agent.

Required:

- agent A produces insight
- insight syncs to Swarm
- agent B runs without and with the insight
- compare held-out result

Best for:

- proving network effects
- validating shared mastery
- testing cross-workspace transfer

## Autoloop Contract

An autoloop must define:

```json
{
  "schema_version": "spark-autoloop-policy.v1",
  "loop_key": "",
  "target_capability": "",
  "mutation_surface": [],
  "benchmark_manifest": "",
  "baseline_report": "",
  "candidate_report": "",
  "held_out_report": "",
  "allowed_actions": [],
  "forbidden_actions": [],
  "max_rounds_before_review": 8,
  "keep_condition": "",
  "rollback_condition": "",
  "promotion_condition": "",
  "lineage_required": true
}
```

## Autoloop Stages

### Stage 0: Readiness

Do not start if:

- active chip missing
- benchmark missing
- mutation target missing
- forbidden surface overlaps mutation surface
- Swarm sync is expected but auth/payload is not ready

### Stage 1: Baseline

Run the benchmark before mutation.

Save:

- score
- component scores
- trace
- prompt/config version
- cases used

### Stage 2: Candidate Generation

Use the chip's `suggest` hook or specialization path policy.

Each candidate must include:

- hypothesis
- mutated file or setting
- expected score movement
- risk
- rollback

Reject candidates with no causal mechanism.

### Stage 3: Candidate Evaluation

Run the benchmark against the candidate.

Keep only if:

- primary score improves
- held-out score does not regress
- anti-gaming checks pass
- complexity does not rise without measured gain

### Stage 4: Diagnosis

If zero keeps:

- report weakest component
- report whether suggest produced candidates
- report whether benchmark is too saturated
- report whether mutation surface is too narrow
- report whether scoring is unable to see the intended change

Do not loosen gates automatically.

### Stage 5: Promotion

Promotion requires:

- benchmark result
- lineage
- boundary conditions
- contradiction scan
- evidence lane
- Swarm-ready packet

## Recursive Evolution Gates

Apply these gates before accepting a loop mutation:

| Gate | Pass condition |
| --- | --- |
| schema gate | candidate output matches active schemas |
| lineage gate | mutation has a concrete failure or weak-track lineage |
| complexity gate | complexity stays flat or measured gain justifies it |
| transfer gate | cross-domain transfer has explicit label mapping |
| memory hygiene gate | no operational residue is promoted as intelligence |
| autonomy gate | loop has review mode, rollback, and measurable window |

Any failed gate blocks promotion.

## Stop Conditions

Stop the loop when:

- no improvement after N rounds
- repeated candidates converge on the same pattern
- held-out cases regress
- anti-gaming check fails
- mutation surface needs expansion
- benchmark cannot distinguish candidate quality
- user or policy requires review

Stopping is not failure. A well-stopped loop tells the next agent what to fix.

## What To Publish To Spark Swarm

Publish:

- benchmark-backed insight
- mastery candidate
- upgrade suggestion with repo path
- contradiction
- weak-track diagnosis

Do not publish:

- raw logs
- unreviewed hypotheses
- access tokens
- private user data
- "I ran the loop" as an insight
- confidence-only changes

## Minimum Valid Result

A result is minimally valid when it answers:

1. What changed?
2. Why should that change improve the target capability?
3. Which benchmark proved it?
4. Did held-out or adversarial cases pass?
5. What are the boundaries?
6. Can another agent use the lesson?

