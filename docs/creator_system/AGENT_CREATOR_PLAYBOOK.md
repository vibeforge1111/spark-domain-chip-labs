# Agent Creator Playbook

## Purpose

This is the procedure a Spark agent should follow when a user asks to create or improve a domain chip, benchmark, specialization path, autoloop, tool operator, or recursive intelligence system.

The playbook is intentionally concrete. It is meant to be loaded by an agent before it starts creating files or running loops.

## Creator Modes

| User intent | Creator mode | Primary owner |
| --- | --- | --- |
| "Make Spark good at X" | domain chip + benchmark | Domain Chip Creator |
| "Make a learning path for X" | specialization path | Specialization Path Creator |
| "Make sure it is actually improving" | benchmark + validation | Benchmark Creator |
| "Let it self-improve safely" | autoloop policy | Autoloop Creator |
| "Let me run this from Telegram" | gateway flow | Telegram + Builder |
| "Track the work visually" | mission flow | Spawner UI + Canvas/Kanban |
| "Share this with other agents" | collective sync | Spark Swarm |

## Step 1: Convert User Intent Into A Creator Intent Packet

Before creating artifacts, produce this packet:

```json
{
  "schema_version": "spark-creator-intent.v1",
  "user_goal": "",
  "target_domain": "",
  "target_operator_surface": "",
  "expected_agent_capability": "",
  "success_examples": [],
  "failure_examples": [],
  "tools_in_scope": [],
  "data_sources_allowed": [],
  "risk_level": "low|medium|high",
  "privacy_mode": "local_only|github_pr|swarm_shared",
  "desired_outputs": {
    "domain_chip": true,
    "specialization_path": true,
    "benchmark_pack": true,
    "autoloop_policy": true,
    "telegram_flow": true,
    "spawner_mission": true
  }
}
```

If the user is vague, ask only for missing information that affects benchmark truth:

- What should the agent be able to do better?
- What examples would prove it?
- What examples should it reject?
- Should results stay local, go through GitHub PR, or sync to Spark Swarm?

## Step 2: Choose The Minimum Useful Artifact Set

Do not create all modules by default.

Use this decision table:

| Need | Build |
| --- | --- |
| Better domain reasoning only | domain chip + packet docs + smoke benchmark |
| Better tool operation | domain chip + tool-operation benchmark + trace checks |
| Real specialization/mastery | domain chip + benchmark + specialization path + autoloop policy |
| Network contribution | all above + Swarm promotion packet + GitHub path |
| UI/user-facing workflow | all above + Spawner mission + Canvas/Kanban trace |

## Step 3: Create The Domain Chip

Domain chip output must include:

- `spark-chip.json`
- `evaluate` hook
- `suggest` hook
- `packets` hook
- `watchtower` hook
- router keywords and topics
- tests proving hooks execute
- README with domain boundary

The chip should be able to answer:

- What domain capability does this add?
- What does it refuse?
- What score does it optimize?
- What evidence lanes can it emit?
- What benchmark should validate it?

Do not accept a chip that is only a prompt wrapper.

## Step 4: Create The Benchmark Pack

Benchmark output must include:

- `benchmark-manifest.json`
- baseline cases
- adversarial cases
- scoring function or judge rubric
- expected output schema
- baseline score report
- known limitations

The benchmark should prove one precise capability. If the domain is broad, create a small benchmark first.

Example for Startup YC:

- narrow case: "zero to one design partner decision"
- score dimensions: customer pain, retention, revenue quality, runway risk, focus
- adversarial traps: vanity metrics, fundraising theater, premature hiring, broad ICP

## Step 5: Create The Specialization Path

Specialization path output must include:

- `specialization-path.json`
- default scenario path
- mutation target path
- collective sync path
- operator guide
- benchmark path
- expected mastery ladder

Minimum `specialization-path.json`:

```json
{
  "schema_version": "spark-specialization-path.v1",
  "path_key": "startup-yc",
  "label": "Startup YC",
  "default_scenario_path": "benchmarks/scenarios/default.json",
  "default_mutation_target_path": "benchmarks/candidate.json",
  "collective_sync_path": ".spark-swarm/collective-sync.json"
}
```

The path should be explicit enough for Builder, Telegram, and Spark Swarm to resolve without guessing.

## Step 6: Create The Autoloop Policy

Autoloop output must include:

- mutation surface
- allowed files
- forbidden files
- benchmark gate
- rollback condition
- max rounds before review
- promotion condition
- fail/flat diagnosis path

Minimum loop policy:

```json
{
  "schema_version": "spark-autoloop-policy.v1",
  "loop_key": "startup-yc-default",
  "mutation_surface": [
    "benchmarks/candidate.json",
    "research/packets/*.json"
  ],
  "forbidden_surfaces": [
    "spark-chip.json",
    "secrets",
    ".env",
    "auth",
    "user_identity"
  ],
  "max_rounds_before_review": 8,
  "keep_condition": "candidate_score > baseline_score and held_out_score >= baseline_held_out_score",
  "rollback_condition": "candidate_score <= baseline_score or anti_gaming_check_failed",
  "promotion_condition": "replicated_delta >= 0.03 over 3 runs"
}
```

## Step 7: Run Validation In This Order

1. Structural validation:
   - manifests parse
   - hooks execute
   - required docs exist
   - no secret files committed

2. Benchmark validation:
   - baseline runs
   - candidate runs
   - adversarial cases run
   - score report is saved

3. Loop validation:
   - one revert case works
   - one keep case works
   - status file is written
   - no forbidden file changed

4. Runtime validation:
   - Builder can attach the chip
   - `swarm doctor` or equivalent readiness passes
   - Telegram can invoke the relevant action
   - Spawner trace shows mission state if the workflow is UI-driven

5. Swarm validation:
   - collective payload validates
   - evidence lane is correct
   - insight/mastery boundaries are present
   - GitHub PR or local publish mode is explicit

## Step 8: Emit The Final Creator Report

Every creator run should end with:

```json
{
  "schema_version": "spark-creator-report.v1",
  "created_artifacts": [],
  "repo_paths": [],
  "tests_run": [],
  "benchmark_results": [],
  "loop_results": [],
  "swarm_readiness": {
    "payload_ready": false,
    "api_ready": false,
    "publish_mode": "none"
  },
  "remaining_blockers": [],
  "recommended_next_run": ""
}
```

## What Good Looks Like

A good creator output is:

- runnable
- benchmarked
- traceable
- narrow enough to avoid fake improvement
- rich enough to improve actual agent behavior
- safe enough to share through GitHub PR or Spark Swarm

A bad creator output is:

- a folder of docs with no hooks
- a loop with no benchmark
- a benchmark with no adversarial cases
- a chip with generic router keywords
- a Swarm packet with no reproducible evidence
- a UI flow that hides blocked states

