# Spark Creator System Research Ledger

Status: Draft v1
Date: 2026-04-30
Home: `spark-domain-chip-labs/docs/creator_system/`

This ledger captures what our existing systems taught us. It is intentionally practical: what worked, what is weak, and what the creator system must do differently because of that evidence.

## Summary

The strongest pattern across the work is this:

> Spark becomes more intelligent when a domain chip, benchmark, specialization path, and autoloop are tied together by evidence contracts.

The weakest pattern is this:

> The system can look smarter than it is if we let benchmark-specific score gains, nice summaries, or single-run outputs become doctrine too quickly.

The creator system should therefore optimize for evidence-bearing reusable capability, not artifact generation alone.

## Research table

| System | What worked | What is lacking | Creator-system implication |
| --- | --- | --- | --- |
| `domain-chip-startup-yc` | Encoded YC doctrine into structured packets and score alignment hooks. Produced useful patterns such as retention over acquisition, default alive risk, design partner focus, and avoiding premature hiring. | Alignment can saturate or overfit if scoring is too forgiving. Packets can sound like benchmark manipulation unless summaries translate them into operational startup judgment. | Domain chips need doctrine, examples, traps, counterexamples, and evidence tiers. UI copy must explain the startup lesson, not only the score effect. |
| `specialization-path-startup-yc` | Created a staged absorption path and fresh-agent comparison: no-pack vs pack vs validated-pack. This is the clearest proof that a generated pack can improve another agent. | Uplift is promising but not final mastery. Trap regressions and occasional execution failures show that validated packs still need hardening. | Specialization paths must include absorption benchmarks, failure ledgers, and promotion rules. Mastery requires more than one uplift run. |
| `startup-bench` | Provides stateful, tool-based startup operations tests with programmatic scoring across revenue quality, risk, product health, customer health, team health, strategic coherence, and cash efficiency. | If used alone, loops can overfit the visible scoring surface. Human calibration and hidden/fresh packs are required for high-ceiling claims. | Benchmark Creator should support fixed, hidden, trap, calibration, and tool-use suites. Visible scores are necessary but insufficient. |
| `agentic-startup-simulator` | Adds long-horizon startup dynamics, changing conditions, hidden/fresh problems, archetypes, sectors, challenge families, and multi-run ranking. This is closer to real operational transfer than fixed cases alone. | More complex to integrate, slower to run, and harder to explain. Needs clear scenario contracts so scores do not become opaque. | Simulator benchmarks should be a mastery tier, not the first gate. They test transfer after fixed suites prove basic competence. |
| `founder-arena` | Converts simulator runs into a multiplayer/adversarial shell with turn packets, decision packets, and spectator views. Useful for replay, pressure, and human-understandable failure analysis. | Current design needs shared-market competition, ranked objective consistency, action cleanup, and balance harnesses before it can be a reliable mastery benchmark. | Founder Arena should become an adversarial benchmark layer after balance fixes. It should not block initial creator-system scaffolds. |
| `spark-swarm` | Gives the collective surface for insights, masteries, upgrades, and specialization cards. The workspace vs network contribution split is conceptually right. | UI can currently make benchmark-backed mutation text feel like score optimization instead of real domain learning. Contribution safety needs strict trust tiers. | Swarm display must show evidence tier, operational lesson, known limits, replay link, and trust lane. Network absorption should default to GitHub PR. |
| `spawner-ui` creator missions | Mission route, execute endpoint, Kanban run action, Canvas graph, and creator trace concept create the right orchestration shell. | It still needs deeper generator execution, persistent validation traces, richer gate display, retry handling, and publish-readiness packaging. | Spawner should own execution, task graph state, validation display, and trace storage. Builder should not become the UI runtime. |
| `spark-telegram-bot` | Provides a low-friction conversational entry point and can trigger creator mission runs. This is likely the front door for many users. | Repeated token/import friction and sparse guided creator UX make it feel mechanical. It needs status, approval, publish, and recovery flows. | Telegram should own guided commands and summaries, but delegate planning to Builder and execution to Spawner. Auth persistence is a product requirement. |
| `spark-intelligence-builder` | Has the early creator intent packet logic and can infer domains, artifact targets, privacy, risk, and known systems. | Intent inference is still heuristic. It needs schemas, examples, validation, artifact manifests, and generator orchestration. | Builder should own normalized intent, artifact manifests, generator selection, and validation plan assembly. |
| `spark-domain-chip-labs` | Good home for methodology, docs, experiments, and reference designs. Keeps creator doctrine independent from one production app. | It has many research docs and experiments, but needed a clear PRD and diagram source-of-truth for future agents. | Keep this folder as the agent-readable methodology hub. Build schemas and examples here or linked from here. |

## What Startup YC proved

Startup YC is the first real reference lane because it connected multiple layers:

1. A domain chip with doctrine and scoring alignment.
2. A benchmark with tool-based startup cases.
3. A specialization path with fresh-agent absorption.
4. Autoloop runs that proposed and kept mutations.
5. Swarm card output with discoveries and patterns.
6. UI and Telegram flows for running and reviewing work.

That is enough to prove the architecture is directionally right.

It does not yet prove complete startup mastery. The current evidence says:

- Validated packs can improve fresh-agent behavior in some runs.
- The system can discover repeatable startup doctrine patterns.
- UI summaries need to show actual startup insight, not just benchmark movement.
- Trap failures and weak transfer tests are still the main risk.

## What Startup YC did not prove yet

| Gap | Why it matters | Needed fix |
| --- | --- | --- |
| Trap resistance | A startup agent that falls for plausible vanity moves can score okay while still being dangerous. | Add explicit trap packs and require no-regression gates. |
| Held-out generalization | Visible case improvements can be memorized or overfit. | Add private/fresh cases and rotate suites. |
| Simulator transfer | Real startup operation is long-horizon and stateful. | Run agentic-startup-simulator as a mastery tier. |
| Adversarial pressure | Markets have competitors, capital constraints, timing, and strategic conflict. | Use Founder Arena after ranked/balance redesign. |
| Human calibration | Programmatic scoring can encode wrong assumptions. | Add expert review on representative cases. |
| Summary quality | Humans and agents need reusable lessons, not only mutation-score prose. | Emit mechanism, boundary, counterexample, and next test. |

## Design rules extracted

### 1. Always name the capability first

Bad:

```text
Improve startup score.
```

Good:

```text
Detect when acquisition growth is hiding weak retention and choose a narrower activation/retention intervention.
```

Benchmark design starts from the capability, not the metric.

### 2. Require multiple proof shapes

A serious capability needs at least three of these:

- Fixed repeatable benchmark.
- Held-out or fresh cases.
- Trap cases.
- Simulator transfer.
- Fresh-agent absorption.
- Tool-use proof.
- Human calibration.

### 3. Promote mechanisms, not slogans

A packet should say:

- Mechanism: why it works.
- Boundary: when it stops working.
- Counterexample: a case where the opposite is better.
- Evidence: what proved it.
- Replay: how to test it.

### 4. Separate private speed from public safety

Private workspace loops can be fast because the blast radius is local. Network contribution must be slower because other agents may absorb it.

The default network route should be:

```text
workspace_validated -> contribution packet -> GitHub PR -> review -> network_absorbable
```

### 5. Never let the autoloop edit its own judge casually

Autoloops can mutate prompts, packets, retrieval, examples, and bounded tool scripts. They should not mutate hidden answers, trust tiers, promotion gates, or scoring functions without a separate review lane.

### 6. Preserve rejected mutations

Rejected mutations teach the system where the local search is failing. A loop that only records wins creates a false history.

### 7. Show operational insight in the UI

The Startup YC card should say:

```text
Spark learned to prioritize retention repair over acquisition pushes when revenue quality is weak.
```

It should not only say:

```text
Mutation improved scenario_score from 0.6141 to 0.6313.
```

Scores are evidence. They are not the lesson.

## Anti-patterns found or anticipated

| Anti-pattern | Description | Guardrail |
| --- | --- | --- |
| Score-chasing prose | The insight describes how to improve the benchmark, not how to operate in the domain. | Require mechanism and operational translation. |
| Single-run mastery | One strong run is treated as durable intelligence. | Evidence ladder and repeated/fresh validation. |
| Visible-suite overfit | The loop adapts to known cases. | Held-out, trap, simulator, and absorption gates. |
| Residue promotion | Chat leftovers become memory or doctrine. | Memory hygiene gate and packet schema. |
| Schema wall | Generated artifacts look good but cannot be consumed by downstream systems. | Artifact manifests and schema validation. |
| Trust-lane collapse | Private workspace results publish directly to network. | PR-based contribution and trust tiers. |
| UI truth blur | Users cannot tell created from validated from publishable. | Mission state machine and evidence tier labels. |
| Generator theater | The creator produces files but no runnable validation. | Every artifact needs validation commands. |

## Benchmark design implications

Benchmark Creator should generate at least:

1. Case schema.
2. Scoring rubric.
3. Failure taxonomy.
4. Trap set.
5. Calibration examples.
6. Hidden/fresh case strategy.
7. Replay command.
8. Score normalization rules.
9. Human review hooks.
10. Promotion threshold.

For Startup YC, this means Startup Bench should remain the fixed operational base, agentic-startup-simulator should test transfer, and Founder Arena should test adversarial pressure after its competitive redesign is complete.

## Domain chip design implications

Domain Chip Creator should generate:

1. Doctrine map.
2. Skill graph.
3. Positive examples.
4. Negative examples.
5. Traps and anti-patterns.
6. Tool-use guidance.
7. Benchmark alignment hooks.
8. Retrieval packets.
9. Evidence ledger.
10. Promotion policy.

For Startup YC, doctrine must be expressed as operating judgment:

- Make something people want.
- Prefer retention proof over acquisition theater.
- Stay default alive or know the funding milestone.
- Do not hire before PMF.
- Use design partners to compress learning.
- Talk to users with specific painful workflows.

## Specialization path design implications

Specialization Path Creator should generate:

1. Learning stages.
2. Absorption packets.
3. Practice tasks.
4. Benchmark schedule.
5. Fresh-agent comparison protocol.
6. Memory promotion rules.
7. Failure ledger.
8. Swarm publication boundary.

The path is where knowledge becomes behavior. If a fresh agent cannot use the pack to perform better, the path has not created reusable intelligence yet.

## Autoloop design implications

Autoloop Creator should generate:

1. Mutation surface.
2. Baseline command.
3. Candidate generation rules.
4. Keep/reject gate.
5. Stop condition.
6. Rollback rule.
7. Rejected mutation ledger.
8. Summary emitter.
9. Trust-tier policy.
10. Network contribution packaging.

The autoloop should answer:

```text
What changed?
Why might it improve behavior?
What evidence supports it?
Where did it fail?
Can it transfer?
Can we undo it?
Who can absorb it?
```

## Tool and product integration implications

Tool creators need a different benchmark shape:

- Does the agent call the right tool?
- Does it pass safe inputs?
- Does it handle errors?
- Does it preserve user intent?
- Does it avoid destructive actions without approval?
- Does it produce useful outputs?
- Does it recover when the tool is unavailable?

The same creator system can support tools if Benchmark Creator can generate tool-use evals and Autoloop Creator can mutate bounded operator behavior.

## What should be built next

1. Creator schemas and validators.
2. Persistent Spawner creator traces.
3. Validation runner that executes manifest commands.
4. Startup YC golden reference pack.
5. Swarm UI insight translation.
6. Network contribution PR packaging.
7. Founder Arena balance harness before using it as a mastery gate.

## Research-backed answer to "are we overengineering?"

The full system is large, but the core is not optional if the goal is real, reusable intelligence:

- Domain chip without benchmarks becomes advice.
- Benchmark without specialization path becomes a scoreboard.
- Autoloop without gates becomes score chasing.
- Specialization path without absorption becomes documentation.
- Swarm contribution without review becomes a contamination risk.
- UI without evidence tiers makes users trust the wrong thing.

The pragmatic move is to build these as thin contracts first, not heavy platforms. Schemas, manifests, traces, and reference examples give us the structure. Automation can deepen over time.
