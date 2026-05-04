# Agent Creator Playbook

## Purpose

This is the procedure a Spark agent should follow when a user asks to create or improve a domain chip, benchmark, specialization path, autoloop, tool operator, or recursive intelligence system.

The playbook is intentionally concrete. It is meant to be loaded by an agent before it starts creating files or running loops.

## Fresh Agent Boot Sequence

When you enter this repo cold, do this before creating artifacts:

1. Load `docs/creator_system/README.md`, `USER_QUICKSTART_BETA.md`,
   `CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md`,
   `CREATOR_RUN_GOLDEN_PATH_V1.md`, and this playbook.
2. Run `git status --short` and do not stage or overwrite unrelated dirty or
   untracked files.
3. Verify the local creator-system contract:

   ```bash
   python -m chip_labs.cli creator-run-template-check --fail-on-blocked
   python -m chip_labs.cli creator-system-beta-check --fail-on-blocked
   python -m chip_labs.cli creator-system-production-readiness --fail-on-blocked
   ```

4. Treat `ready_for_swarm_packet` as an artifact-review state, not as network
   publication approval.
5. Keep `network_absorbable=false` unless the separate promotion bundle passes
   multi-seed validation, human/operator calibration, privacy review, rollback
   review, publication approval, and product runtime review.

This beta is designed so agents can understand the repo by following executable
contracts instead of reading every historical design note. If a doc and a CLI
result disagree, trust the CLI result and update the doc.

For the complete user value path, read
`CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md`. It is the canonical map for how
users and agents move through intent, adapter map, domain chip, benchmark pack,
specialization path, autoloop policy, evidence ladder, local Swarm packet,
mission status, and release evidence.

## Creator Modes

| User intent | Creator mode | Primary owner |
| --- | --- | --- |
| "Make Spark good at X" | domain chip + benchmark | Domain Chip Creator |
| "Make a learning path for X" | specialization path | Specialization Path Creator |
| "Make sure it is actually improving" | benchmark + validation | Benchmark Creator |
| "Let it self-improve safely" | autoloop policy | Autoloop Creator |
| "Let me run this from Telegram" | read-only mission-status projection for now | Telegram + Builder |
| "Track the work visually" | read-only mission-status projection for now | Spawner UI + Canvas/Kanban |
| "Share this with other agents" | local Swarm contribution packet, not network absorption | Spark Swarm |

## Step 1: Convert User Intent Into A Creator Intent Packet

Before creating artifacts, produce an `adaptive_creator_loop.creator_intent.v1`
packet. Prefer `creator-run-init` and then fill the generated file:

```bash
python -m chip_labs.cli creator-run-init \
  --output-dir runs/<run-name> \
  --domain "<domain>" \
  --goal "<goal>" \
  --source-channel local
```

Minimum intent shape:

```json
{
  "schema_version": "adaptive_creator_loop.creator_intent.v1",
  "run_id": "creator-run-YYYY-MM-DD-domain-slug",
  "source_channel": "telegram|builder|spawner|local|swarm",
  "domain": {
    "name": "",
    "short_slug": "",
    "target_operator": "",
    "target_agent": ""
  },
  "goal": {
    "plain_language_goal": "",
    "capability_to_improve": "",
    "expected_user_value": "",
    "non_goals": []
  },
  "constraints": {
    "privacy_boundary": "workspace_only",
    "network_publication_allowed": false,
    "auth_or_secret_requirements": [],
    "human_review_required": true
  },
  "success_criteria": {
    "minimum_evidence_tier": "prototype",
    "benchmark_target": "",
    "trap_regression_policy": "no_new_trap_regressions",
    "stop_ship_conditions": []
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
| Network contribution | all above + local Swarm contribution packet + GitHub review path |
| UI/user-facing workflow | all above + read-only mission-status packet; product wiring stays deferred |

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

4. Product-surface validation:
   - produce `creator-mission-status` from saved smoke/recompute evidence
   - preserve `publication.network_absorbable=false`
   - keep Telegram, Builder, Spawner, Canvas, and Kanban read-only unless a
     separate product-runtime review explicitly approves more
   - do not wire live runtime controls from this repo-local beta

5. Swarm validation:
   - collective payload validates
   - evidence lane is correct
   - insight/mastery boundaries are present
   - GitHub PR or local review mode is explicit
   - network publication remains blocked without the promotion bundle

## Standard Agent Creation Workflow

For a new user-requested domain, a helpful agent should usually execute this
path:

1. Create a local run with `creator-run-init`.
2. Fill intent, adapter map, benchmark pack, specialization path, autoloop
   policy, artifact manifest, and evidence ladder from the templates in
   `docs/creator_system/templates/creator-run/`.
3. Run `creator-run-smoke`; if blocked, run `creator-run-doctor` and repair the
   reported paths.
4. Run at least one benchmark baseline and one keep/revert autoloop simulation.
5. Create a Swarm contribution packet only after the evidence tier supports it.
6. Run strict smoke:

   ```bash
   python -m chip_labs.cli creator-run-smoke runs/<run-name> --fail-on-blocked --fail-on-warn
   ```

7. Summarize what was created, what passed, what remains blocked, and the
   weakest honest evidence tier.

If the user asks for a broad domain, narrow the first benchmark. A small
truthful creator system is better than a large system with vague evidence.

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
  "network_absorbable": false,
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
