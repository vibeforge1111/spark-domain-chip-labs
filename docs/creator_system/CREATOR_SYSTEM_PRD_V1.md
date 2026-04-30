# Spark Creator System PRD v1

Status: Draft v1
Date: 2026-04-30
Home: `spark-domain-chip-labs/docs/creator_system/`

## One-line thesis

Spark Creator System turns a user's intent into benchmark-backed, reusable agent capability: domain chips, benchmarks, specialization paths, autoloops, tools, and Swarm contribution packets that work locally first and only become network knowledge after evidence clears the right gates.

## Why this matters

Spark users will not all be benchmark engineers. They will say things like:

- "Make my Spark great at startup operations."
- "Create a domain chip for enterprise sales."
- "Build a recursive loop around my tool so agents improve it."
- "Let my Telegram bot coordinate this safely."
- "Publish the useful discoveries to Spark Swarm."

The system has to translate that into a reliable build plan, create the right artifacts, run the right validation, and explain what improved without confusing benchmark gaming with real intelligence.

The Startup YC work exposed the full shape of the problem. We had real pieces working: Startup Bench, `domain-chip-startup-yc`, the Startup YC specialization path, absorption runs, Spawner missions, Telegram commands, and Spark Swarm payloads. We also saw the failure modes: single-run overconfidence, UI summaries that sounded like benchmark tuning instead of startup learning, repeated access-token friction, weak distinction between local workspace learning and network-wide contribution, and benchmarks that can become too coupled to the loop they are supposed to judge.

This PRD defines the product and system needed to make those lessons reusable for every domain.

## Product goal

Create a guided creator layer that can produce and validate five artifact families:

| Artifact family | What it creates | Why it matters |
| --- | --- | --- |
| Domain chip | Domain doctrine, scoring hooks, skill graph, examples, anti-patterns, retrieval packets | Gives an agent structured expertise and operator rules. |
| Benchmark pack | Cases, scoring rubric, tools, traps, held-out suites, calibration notes | Proves capability instead of trusting claims. |
| Specialization path | Runtime path, absorption plan, mission sequence, memory policy, promotion policy | Turns a chip and bench into a staged mastery path. |
| Autoloop | Mutation surface, benchmark gates, keep/reject policy, rollback policy, summary emitters | Allows recursive improvement without fake progress. |
| Tool/product integration | Local tool actions, API hooks, trace schema, UI panels, Telegram/Spawner controls | Makes the system usable in real workflows. |

The output must be usable by both:

- A local Spark agent improving one user's private workspace.
- Spark Swarm, after review, as network knowledge that other agents can absorb.

## Users

| User | Needs |
| --- | --- |
| Non-technical operator | Express a goal in Telegram or UI, get a guided plan, approve runs, understand results. |
| Builder agent | Convert intent into artifact manifests, write repo files, run validation, preserve provenance. |
| Domain expert | Add doctrine, examples, traps, red-team cases, and calibration judgments. |
| Benchmark designer | Create reliable scoring surfaces with hidden, held-out, simulator, and adversarial layers. |
| Swarm reviewer | Decide whether a contribution is safe and useful enough to promote beyond a private workspace. |
| Future Spark agent | Read the docs and artifacts and reproduce the same workflow without chat history. |

## Non-goals

- Do not make one monolithic repo own all creator logic.
- Do not let benchmark score gains automatically become canonical knowledge.
- Do not publish private workspace learnings directly to the network.
- Do not treat one successful run as mastery.
- Do not turn every domain into Startup YC. Startup YC is the reference implementation, not the schema.

## Product principles

1. Capability starts with a falsifiable task.
   A domain chip is not "knowledge about X"; it is a set of behaviors the agent can execute and prove.

2. Benchmarks must test transfer, not memorization.
   A good loop improves fresh cases, held-out cases, traps, and long-horizon simulations, not only the one visible score.

3. Local learning and network contribution are different trust lanes.
   Local workspace runs can move fast. Network absorption must be reviewable, provenance-rich, replayable, and reversible.

4. Autoloops mutate within declared boundaries.
   The loop must name what it is allowed to change, what it is not allowed to change, and how rollback works.

5. User experience must hide mechanical pain without hiding evidence.
   Users should not keep pasting tokens or wiring imports, but they should see what was learned, what was proven, and what is still weak.

6. Spark Swarm should absorb usable intelligence, not residue.
   Conversational residue, pretty summaries, and one-off hunches are not enough. A promoted packet needs lineage, tests, and scope boundaries.

## Existing surfaces

| Surface | Current role | PRD direction |
| --- | --- | --- |
| `spark-telegram-bot` | User-facing command entry and mission runner. | Becomes the conversational creator front door: plan, run, status, approve, publish. |
| `spark-intelligence-builder` | Intent parsing and creator planning. | Owns creator intent packet v1, artifact manifests, validation plan assembly, and generator orchestration. |
| `spawner-ui` | Mission control, Canvas/Kanban, run endpoint, trace. | Owns visual orchestration, execution traces, state, retries, and review UX. |
| `spark-domain-chip-labs` | Methodology hub and experimental lab. | Owns source-of-truth docs, schemas, reference examples, and design doctrine. |
| `spark-swarm` | Collective registry, specialization cards, insights/masteries/upgrades. | Owns network contribution, collective payload display, trust tiers, and absorption rules. |
| Domain chip repos | Domain-specific expertise. | Own chip artifacts, examples, scoring hooks, and domain-local tests. |
| Benchmark repos | Evaluation surfaces. | Own cases, tools, scorers, calibration notes, hidden/fresh packs, and simulation hooks. |
| Specialization path repos | Runtime mastery path. | Own stepwise learning plan, absorption protocol, packs, runbooks, and reports. |

## Required object model

### 1. Creator intent packet

Every run starts with a normalized intent packet:

```json
{
  "intent_id": "creator-intent-...",
  "user_goal": "Make Spark excellent at startup operations",
  "domain": "startup_yc",
  "artifact_targets": ["domain_chip", "benchmark_pack", "specialization_path", "autoloop"],
  "usage_surface": ["telegram", "spawner_ui", "local_cli", "spark_swarm"],
  "privacy_lane": "workspace_private",
  "success_claim": "Spark can diagnose and operate early-stage startup decisions better on fresh cases",
  "capabilities_to_prove": [
    "prioritize retention over shallow acquisition",
    "detect default-dead risk",
    "choose narrow design partners",
    "avoid premature hiring before PMF"
  ],
  "benchmark_requirements": {
    "visible_cases": 20,
    "held_out_cases": true,
    "trap_cases": true,
    "simulator_transfer": true,
    "fresh_agent_absorption": true
  },
  "network_contribution_policy": "github_pr_required"
}
```

The packet is the contract between Telegram, Builder, Spawner, repo generators, and Spark Swarm.

### 2. Artifact manifest

Every generated system must emit a manifest:

```json
{
  "artifact_id": "startup-yc-specialization-path-v1",
  "artifact_type": "specialization_path",
  "repo": "specialization-path-startup-yc",
  "inputs": ["creator-intent-...", "domain-chip-startup-yc", "startup-bench"],
  "outputs": ["docs/", "packs/", "scripts/", "benchmarks/"],
  "validation_commands": [
    "python scripts/run_startup_yc_absorption_pilot.py --suite smoke",
    "python scripts/run_startup_yc_absorption_pilot.py --suite validation"
  ],
  "promotion_gates": ["schema_gate", "lineage_gate", "benchmark_gate", "transfer_gate", "memory_hygiene_gate"],
  "rollback_plan": "revert artifact commit and remove packet from promotion ledger"
}
```

This allows Spawner, Builder, and Swarm to reason about generated work without parsing arbitrary prose.

### 3. Creator trace

Each mission execution should produce a trace:

```json
{
  "trace_id": "creator-trace-...",
  "intent_id": "creator-intent-...",
  "tasks": [
    {
      "task_id": "benchmark-pack",
      "status": "passed",
      "evidence": ["startup-bench validation score 0.6863"],
      "risk": ["trap regression remains open"]
    }
  ],
  "repo_changes": [],
  "benchmarks": [],
  "publish_readiness": "workspace_validated"
}
```

The trace should be visible in Spawner UI and summarized by Telegram.

## Benchmark architecture

The creator system must support multiple benchmark families because different domains need different proof shapes.

| Benchmark family | Tests | Example |
| --- | --- | --- |
| Fixed case suite | Repeatable baseline and regression detection. | Startup Bench public 20-case suite. |
| Held-out suite | Generalization beyond visible examples. | Private Startup Bench packs. |
| Trap suite | Whether the agent resists plausible wrong moves. | Vanity metrics, premature hiring, fake PMF. |
| Simulator suite | Long-horizon adaptation under changing state. | Agentic Startup Simulator. |
| Adversarial suite | Competitive pressure, market conflict, red-team moves. | Founder Arena after balance harness. |
| Absorption suite | Whether a fresh agent can use the produced pack. | No-pack vs pack vs validated-pack run. |
| Tool-use suite | Whether the agent can operate real tools safely. | CLI/API/browser tool tasks. |
| Human calibration suite | Whether domain experts agree the scores mean anything. | Expert-rated startup decisions. |

The system should not require every benchmark family on day one. It should require the right minimum tier for the artifact's claim.

## Evidence ladder

| Tier | Meaning | Allowed use |
| --- | --- | --- |
| Observation | A run produced an interesting event. | UI feed, debug, local notes. |
| Signal | Repeated or scored event with evidence. | Workspace learning candidate. |
| Pattern | Signal held across multiple cases or seeds. | Specialization path memory candidate. |
| Doctrine | Pattern has named mechanism, boundary, and counterexample. | Domain chip packet candidate. |
| Skill | Doctrine improves behavior in tool or benchmark use. | Agent runtime retrieval candidate. |
| Mastery candidate | Skill transfers to held-out, simulator, and fresh-agent absorption. | Swarm review candidate. |
| Canonical | Reviewed, replayable, rollback-safe network knowledge. | Spark Swarm absorbable packet. |

Startup YC currently has signals, patterns, and some validated-pack uplift. It is not yet a fully proven canonical mastery loop because trap regressions and broader held-out transfer still need more work.

## Autoloop governance

Every autoloop must follow the recursive evolution protocol:

| Gate | Requirement |
| --- | --- |
| Schema gate | Mutation outputs fit declared contracts. |
| Lineage gate | Every kept change references its source run, diff, benchmark, and evidence. |
| Complexity gate | The loop does not add complexity without measured benefit. |
| Transfer gate | Gains appear beyond the exact visible case that produced the mutation. |
| Memory hygiene gate | No residue, unscored hunches, or unbounded claims enter memory. |
| Autonomy gate | The loop cannot expand mutation rights without human or policy approval. |
| Rollback gate | A kept change can be undone cleanly. |

Allowed mutation surfaces must be explicit:

- Prompt or packet wording.
- Tool script constants.
- Retrieval ranking.
- Benchmark case generation.
- Domain chip examples.
- Specialization path steps.
- UI summaries.

Disallowed by default:

- Hidden benchmark answers.
- Score functions without review.
- Trust tier escalation.
- Network publication.
- External side effects.
- Unscoped memory writes.

## Core user flows

### Flow A: Telegram creator mission

1. User says: "Create a startup YC specialization path."
2. Telegram asks for missing high-value constraints only.
3. Builder emits a creator intent packet.
4. Spawner creates a mission with tasks, gates, and repo targets.
5. User reviews plan in Telegram or Spawner.
6. Spawner executes local repo work.
7. Builder/runner validates artifacts.
8. Telegram summarizes: what was created, what passed, what failed, what is safe to publish.

### Flow B: Local workspace improvement

1. User points Spark at a local repo or tool.
2. Spark creates a private creator intent packet.
3. Autoloop runs local benchmarks and proposes changes.
4. Kept changes remain private unless the user chooses contribution.
5. Private reports can improve that user's agent without entering the network.

### Flow C: Network contribution

1. A local pattern becomes a candidate.
2. Spark packages it as a GitHub PR with manifest, trace, evidence, scope, and rollback.
3. Swarm reviewer or policy checks it.
4. If accepted, the packet becomes network absorbable.
5. Spark Swarm card displays the promoted doctrine, not only benchmark score text.

### Flow D: Startup YC reference path

1. Domain chip defines YC doctrine, traps, packets, and scoring alignment.
2. Startup Bench gives fixed and held-out operational cases.
3. Agentic Startup Simulator tests long-horizon transfer.
4. Founder Arena tests adversarial pressure after its balance harness is ready.
5. Specialization path runs no-pack, pack, and validated-pack fresh-agent absorption.
6. Swarm displays insights, masteries, and upgrades with evidence tier labels.

## UX requirements

### Telegram

- `/creator plan <goal>` creates or updates an intent packet.
- `/creator run <mission>` starts a mission through Spawner.
- `/creator status <mission>` shows current task, last evidence, blockers, and next action.
- `/creator publish <mission>` starts network contribution packaging.
- The bot should not require repeated token pasting once an authenticated local bridge or saved workspace auth exists.

### Spawner UI

- Mission overview with task graph, status, and evidence.
- Canvas nodes for artifacts, validations, and publish gates.
- Kanban cards for planned, running, blocked, review, done.
- Run, retry, pause, and export controls.
- Error boundaries for dynamic route failures.
- Clear difference between "created", "validated", and "publishable".

### Spark Swarm UI

- Separate benchmark-backed events from doctrine-backed lessons.
- Display evidence tier, benchmark suite, scope, and limits.
- Avoid summaries that read only like "score improved from X to Y".
- Show what the agent learned in operational terms.

Example improved Startup YC display:

```text
Startup YC learned: retention pressure beats acquisition theater when revenue quality is weak.
Evidence: validated across 8 Startup Bench cases and 2 fresh-agent absorption runs.
Current limit: still vulnerable to premature hiring traps in long-horizon simulations.
Next test: simulator transfer with hiring/capital pressure.
```

## Reliability requirements

1. Every generated artifact must have at least one validation command.
2. Every benchmark must include scoring rationale and failure examples.
3. Every promoted packet must define:
   - Mechanism.
   - Boundary.
   - Counterexample.
   - Evidence.
   - Replay command.
   - Rollback plan.
4. Every autoloop must log rejected mutations, not only kept mutations.
5. Every network contribution must use a reviewable GitHub route by default.
6. Every UI summary must preserve evidence tier and known limits.

## Security and trust

Spark should support two lanes:

| Lane | Purpose | Rules |
| --- | --- | --- |
| Workspace lane | Private local work, fast iteration, user-specific learning. | Can run CLI/local tools, store local auth, keep private traces. |
| Network lane | Shared Swarm contribution. | Requires PR, provenance, review, scope, and rollback. |

This protects the network from malicious or low-quality packets while keeping the local user experience fast.

Network absorption must never read arbitrary workspace output as canonical knowledge. It should ingest only structured, reviewed packets.

## Acceptance criteria

### PRD acceptance

- A fresh Spark agent can read this docs folder and explain the creator ecosystem accurately.
- The docs distinguish domain chip, benchmark, specialization path, autoloop, and tool integration responsibilities.
- The docs define how local workspace learning differs from Swarm contribution.
- The docs give enough artifact contracts to implement generators without guessing.

### Product acceptance

- A user can start from Telegram, create a mission in Spawner, and produce a creator trace.
- Builder can emit a creator intent packet and artifact manifests.
- Spawner can run or delegate validation commands and display results.
- Startup YC can act as the golden reference implementation.
- A new domain can be scaffolded with a chip, benchmark, path, and loop using the same contracts.

### Intelligence acceptance

- Benchmark gains must hold on fresh or held-out cases.
- A fresh agent using the generated pack must outperform a no-pack baseline.
- The system must identify at least one boundary where the new doctrine does not apply.
- The UI must show useful operational lessons, not only score deltas.

## Metrics

| Metric | Why it matters |
| --- | --- |
| Time from user goal to intent packet | Measures creator UX friction. |
| Time from intent packet to runnable mission | Measures Builder/Spawner integration. |
| Artifact validation pass rate | Measures generator quality. |
| Fresh-agent absorption delta | Measures whether the system creates reusable intelligence. |
| Held-out benchmark delta | Measures generalization. |
| Trap regression count | Measures robustness. |
| Rejected mutation rate and reasons | Measures loop honesty. |
| Network PR acceptance rate | Measures contribution quality. |
| User-readable insight quality | Measures whether results are meaningful to humans. |

## Phased build plan

### Phase 0: Reference evidence

Status: mostly done.

- Startup YC domain chip exists.
- Startup Bench exists.
- Agentic Startup Simulator exists.
- Founder Arena exists but needs competitive-system tightening.
- Specialization path and absorption runs exist.
- Spawner creator missions exist.
- Telegram can trigger creator mission runs.

### Phase 1: Source-of-truth creator docs

Status: this PRD package.

- Create PRD.
- Create flowcharts.
- Create research ledger.
- Keep docs in `spark-domain-chip-labs/docs/creator_system/`.

### Phase 2: Creator schemas

Build:

- `creator_intent.schema.json`
- `artifact_manifest.schema.json`
- `creator_trace.schema.json`
- `benchmark_pack.schema.json`
- `promotion_packet.schema.json`

Add validation tests in Builder and Spawner.

### Phase 3: Generator scaffolds

Build generator modules for:

- Domain chip repo scaffold.
- Benchmark pack scaffold.
- Specialization path scaffold.
- Autoloop scaffold.
- Tool integration scaffold.
- Swarm contribution packet scaffold.

Each generator must emit a manifest and validation command.

### Phase 4: Validation runner

Build a shared runner that can:

- Execute declared validation commands.
- Normalize scores.
- Detect failed gates.
- Store traces.
- Produce Telegram and Spawner summaries.

### Phase 5: Startup YC golden reference

Tighten Startup YC until it is the complete example:

- 20-case fixed suite.
- Held-out suite.
- Trap suite.
- Simulator transfer suite.
- Fresh-agent absorption suite.
- Swarm card that shows operational lessons and evidence tiers.

### Phase 6: Creator UI and Telegram UX

Add:

- Guided mission creation.
- Missing-constraint prompts.
- Auth persistence and local bridge improvements.
- Evidence viewer.
- Publish-readiness panel.
- Error boundary improvements.

### Phase 7: Network contribution lane

Add:

- PR packaging.
- Review checklist.
- Trust-tier display.
- Absorption preview.
- Rollback controls.

### Phase 8: General-domain expansion

Use the same system to create at least three non-startup examples:

- Tool operator chip.
- Researcher/intelligence chip.
- Product-building specialization path.

The goal is to prove the creator system is not overfit to Startup YC.

## Open decisions

1. Should Builder own generator execution, or should it only produce plans that Spawner executes?
   Recommendation: Builder owns intent and manifests; Spawner owns execution and trace.

2. Should Domain Chip Creator and Autoloop Creator live in one repo?
   Recommendation: separate repos or modules, contract-bound. Domain Chip Creator can emit loop hooks, but Autoloop Creator owns loop policy and gates.

3. Should network contribution ever skip GitHub PR?
   Recommendation: only for admin/system-owned packets with equivalent review logs. Default should be PR.

4. Should Founder Arena be part of the default benchmark tier?
   Recommendation: no. Use it as an adversarial/mastery tier after the balance harness is fixed.

5. Should simulator benchmarks count as mastery alone?
   Recommendation: no. Simulator transfer is powerful, but mastery also needs fresh-agent absorption and trap resistance.

## Immediate next implementation targets

1. Add creator schemas to `spark-intelligence-builder`.
2. Make Spawner persist creator traces from executed missions.
3. Add validation command execution to Spawner creator missions.
4. Turn Startup YC into the golden reference pack using this PRD.
5. Improve Spark Swarm card copy so it displays operational insights, evidence tier, and limits.
6. Add PR packaging for network contribution packets.
