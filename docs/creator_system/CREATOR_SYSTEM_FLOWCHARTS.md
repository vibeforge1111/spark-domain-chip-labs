# Spark Creator System Flowcharts

Status: Draft v1
Date: 2026-04-30
Home: `spark-domain-chip-labs/docs/creator_system/`

This document gives Spark agents and human builders the diagram layer for the creator ecosystem. Use it with `CREATOR_SYSTEM_PRD_V1.md`, `CREATOR_SYSTEM_RESEARCH_LEDGER.md`, and `AGENT_CREATOR_PLAYBOOK.md`.

## 1. End-to-end lifecycle

```mermaid
flowchart TD
  U["User goal"] --> I["Creator intent packet"]
  I --> P["Creator plan"]
  P --> M["Spawner mission"]
  M --> A["Artifact generation"]
  A --> V["Validation runner"]
  V --> R{"Gates passed?"}
  R -->|No| D["Diagnosis and patch loop"]
  D --> A
  R -->|Yes| W{"Publish beyond workspace?"}
  W -->|No| L["Workspace learning report"]
  W -->|Yes| G["GitHub PR contribution packet"]
  G --> S["Spark Swarm review"]
  S --> C{"Accepted?"}
  C -->|No| B["Backlog with evidence"]
  C -->|Yes| N["Network absorbable packet"]
```

## 2. Repo ownership map

```mermaid
flowchart LR
  TG["spark-telegram-bot"] --> B["spark-intelligence-builder"]
  B --> SP["spawner-ui"]
  B --> DCL["spark-domain-chip-labs"]
  SP --> CAN["Canvas and Kanban"]
  SP --> TR["Creator trace store"]
  DCL --> DOC["Creator docs and schemas"]
  B --> GEN["Artifact generators"]
  GEN --> DC["Domain chip repos"]
  GEN --> BM["Benchmark repos"]
  GEN --> PATH["Specialization path repos"]
  GEN --> LOOP["Autoloop modules"]
  DC --> VAL["Validation runner"]
  BM --> VAL
  PATH --> VAL
  LOOP --> VAL
  VAL --> SW["spark-swarm"]
```

Ownership rule: Builder decides what should be built. Spawner coordinates how it runs. Domain repos own domain artifacts. Benchmark repos own scoring surfaces. Spark Swarm owns network absorption.

## 3. Telegram to mission-control flow

```mermaid
sequenceDiagram
  participant User
  participant Telegram as spark-telegram-bot
  participant Builder as spark-intelligence-builder
  participant Spawner as spawner-ui
  participant Repo as Target repos
  participant Swarm as spark-swarm

  User->>Telegram: "Create a startup YC specialization path"
  Telegram->>Builder: Normalize creator intent
  Builder-->>Telegram: Missing constraints or intent packet
  Telegram->>Spawner: Create creator mission
  Spawner-->>Telegram: Mission id and review URL
  User->>Telegram: "Run it"
  Telegram->>Spawner: Execute mission
  Spawner->>Repo: Generate artifacts
  Spawner->>Repo: Run validation commands
  Repo-->>Spawner: Scores, traces, diffs
  Spawner-->>Telegram: Human summary and blockers
  Telegram->>Swarm: Publish only after approved contribution packet
```

## 4. Creator mission state machine

```mermaid
stateDiagram-v2
  [*] --> Planned
  Planned --> AwaitingApproval
  AwaitingApproval --> Running
  Running --> Blocked
  Blocked --> Running
  Running --> Validating
  Validating --> Failed
  Failed --> Diagnosing
  Diagnosing --> Planned
  Validating --> WorkspaceValidated
  WorkspaceValidated --> PublishCandidate
  PublishCandidate --> PRSubmitted
  PRSubmitted --> NetworkAbsorbable
  WorkspaceValidated --> [*]
  NetworkAbsorbable --> [*]
```

State labels matter because the UI should never collapse "generated", "validated", and "publishable" into one vague success state.

## 5. Artifact generation DAG

```mermaid
flowchart TD
  I["Creator intent packet"] --> C["Capability definition"]
  C --> CHIP["Domain chip scaffold"]
  C --> BENCH["Benchmark pack scaffold"]
  CHIP --> PATH["Specialization path scaffold"]
  BENCH --> PATH
  PATH --> LOOP["Autoloop scaffold"]
  BENCH --> LOOP
  CHIP --> LOOP
  LOOP --> TRACE["Creator trace"]
  PATH --> TRACE
  BENCH --> TRACE
  CHIP --> TRACE
```

No autoloop should be generated before the benchmark pack and mutation boundaries exist.

## 6. Evidence ladder

```mermaid
flowchart BT
  O["Observation"] --> S["Signal"]
  S --> P["Pattern"]
  P --> D["Doctrine"]
  D --> K["Skill"]
  K --> M["Mastery candidate"]
  M --> C["Canonical network packet"]
```

Promotion requirements:

| From | To | Required proof |
| --- | --- | --- |
| Observation | Signal | Repeat or score. |
| Signal | Pattern | Multiple cases, seeds, or tasks. |
| Pattern | Doctrine | Mechanism, boundary, counterexample. |
| Doctrine | Skill | Better behavior in benchmark or tool use. |
| Skill | Mastery candidate | Held-out, simulator, trap, or fresh-agent evidence. |
| Mastery candidate | Canonical | Review, replay command, rollback, trust-tier approval. |

## 7. Benchmark tiering

```mermaid
flowchart LR
  SM["Smoke suite"] --> FX["Fixed validation suite"]
  FX --> HO["Held-out suite"]
  HO --> TR["Trap suite"]
  TR --> SI["Simulator transfer"]
  SI --> AB["Fresh-agent absorption"]
  AB --> AD["Adversarial arena"]
  AD --> NC["Network candidate"]
```

Use only the tiers needed for the claim:

- A syntax scaffold needs smoke tests.
- A domain chip needs fixed and trap validation.
- A specialization path needs absorption validation.
- A mastery claim needs held-out, simulator, trap, and absorption evidence.
- A Swarm canonical packet needs review and rollback.

## 8. Autoloop governance

```mermaid
flowchart TD
  BASE["Baseline artifact"] --> MUT["Propose mutation"]
  MUT --> SCHEMA["Schema gate"]
  SCHEMA --> LINEAGE["Lineage gate"]
  LINEAGE --> BENCH["Benchmark gate"]
  BENCH --> TRANSFER["Transfer gate"]
  TRANSFER --> COMPLEX["Complexity gate"]
  COMPLEX --> MEMORY["Memory hygiene gate"]
  MEMORY --> KEEP{"Keep?"}
  KEEP -->|No| REJ["Reject with reason"]
  KEEP -->|Yes| COMMIT["Commit locally"]
  COMMIT --> REPORT["Emit trace and summary"]
  REPORT --> NEXT{"More rounds?"}
  NEXT -->|Yes| MUT
  NEXT -->|No| DONE["Stop with evidence"]
```

Autoloops are not score chasers. They are controlled experiments over declared mutation surfaces.

## 9. Workspace lane vs network lane

```mermaid
flowchart TD
  RUN["Local creator run"] --> PRIVATE["Private workspace artifact"]
  PRIVATE --> WV["Workspace validated"]
  WV --> LOCAL["Local agent can use it"]
  WV --> WANT{"User wants to share?"}
  WANT -->|No| STOP["Keep private"]
  WANT -->|Yes| PACK["Package contribution"]
  PACK --> PR["GitHub PR"]
  PR --> REV["Review and replay"]
  REV --> TRUST{"Trust gates passed?"}
  TRUST -->|No| NEEDS["Needs changes"]
  TRUST -->|Yes| ABSORB["Network absorbable"]
  ABSORB --> SWARM["Spark Swarm collective"]
```

This is the answer to the security and speed tension: local CLI and workspace loops can be fast; network contribution must be structured and reviewed.

## 10. Startup YC golden reference flow

```mermaid
flowchart TD
  CHIP["domain-chip-startup-yc"] --> PACK["Validated doctrine packets"]
  BENCH["startup-bench"] --> SCORE["Operational startup scores"]
  SIM["agentic-startup-simulator"] --> TRANSFER["Long-horizon transfer"]
  ARENA["founder-arena"] --> ADV["Adversarial pressure"]
  PACK --> PATH["specialization-path-startup-yc"]
  SCORE --> PATH
  TRANSFER --> PATH
  ADV --> PATH
  PATH --> ABS["Fresh-agent absorption"]
  ABS --> SW["spark-swarm Startup YC card"]
  SW --> UI["Insights, masteries, upgrades"]
```

Current truth: Startup YC has promising validated-pack uplift and useful operational packets, but it still needs stronger trap, held-out, simulator, and arena validation before we should call it canonical mastery.

## 11. Creator validation sequence

```mermaid
flowchart TD
  ART["Generated artifacts"] --> FS["Filesystem and schema check"]
  FS --> SM["Smoke run"]
  SM --> UNIT["Unit or contract tests"]
  UNIT --> BENCH["Benchmark validation"]
  BENCH --> ABS["Fresh-agent absorption"]
  ABS --> RISK["Risk and trust review"]
  RISK --> REP["Creator report"]
```

The report must include:

- What changed.
- What passed.
- What failed.
- What the agent can now do better.
- Where the result should not be trusted yet.
- Whether it is workspace-only or network-ready.

## 12. Future creator UI frame

```mermaid
flowchart LR
  GOAL["Goal pane"] --> PLAN["Plan pane"]
  PLAN --> GRAPH["Task graph"]
  GRAPH --> RUN["Run controls"]
  RUN --> EVID["Evidence pane"]
  EVID --> DIFF["Repo diff pane"]
  EVID --> PUBLISH["Publish readiness"]
  PUBLISH --> PR["PR package"]
```

The UI should make high-quality work easier without making the evidence invisible.
