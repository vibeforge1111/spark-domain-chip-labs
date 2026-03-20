# Deep Dive: Recursive Intelligence Pipeline

**Date**: 2026-03-20
**Source**: spark-researcher + spark-swarm code analysis
**Scope**: How the full recursive improvement pipeline works, bottlenecks, and what makes loops productive

---

## The Three Feedback Cycles

### Cycle A -- Local Trial Loop (seconds to minutes)
- spark-researcher runs an experiment
- Metrics parsed and compared to baseline
- Improved mutations retained, regressed ones discarded
- Next trial suggested based on results
- **Tightest loop**, entirely within a single researcher instance

### Cycle B -- Belief Promotion Loop (minutes to hours)
- After multiple runs, beliefs computed from the ledger
- Replicated improvements become **durable beliefs** (2+ improved runs)
- Contradictions between beliefs detected and flagged
- Memory synced with proper tier assignments
- Domain chips receive updated working memory
- **Accumulates knowledge over time**

### Cycle C -- Collective Intelligence Loop (hours to days)
- Researcher publishes collective payload to spark-swarm
- Swarm absorbs insights into masteries
- Masteries reviewed and approved
- Upgrades derived and delivered (as PRs or auto-applied)
- Outcomes from delivered upgrades feed back into next cycle
- **Slowest loop but most durable improvements**

---

## Knowledge Promotion Pipeline

```
Raw Run (ledger entry)
    |
    v  [Gate: improved metric + no regression]
Provisional Belief
    |
    v  [Gate: replicated improvement (2+ runs)]
Durable Belief
    |
    v  [Gate: collective sync to spark-swarm]
Insight (status: captured)
    |
    v  [Gate: absorbInsight() with review]
Mastery (status: provisional_mastery)
    |
    v  [Gate: reviewMastery(approve)]
Shared Mastery (status: shared_mastery)
    |
    v  [Gate: derive upgrade from mastery]
Upgrade (status: draft -> queued)
    |
    v  [Gate: deliverUpgrade() per evolution mode]
Upgrade Delivery (PR or auto-apply)
    |
    v  [Gate: CI checks + review]
Applied Change (merged/applied)
    |
    v  [Gate: measure outcome]
Outcome (verdict: improved/flat/regressed)
```

Each gate requires stronger evidence than the previous one.

---

## Candidate Suggestion Strategy Layers

The trial suggestion engine (`candidates.py`) implements a layered strategy:

| Layer | Strategy | When Used |
|-------|----------|-----------|
| 1 | Failure-guided | When trials have failed; suggests recovery paths |
| 2 | Combine beneficial primitives | If mutations A and B each improved, try A+B |
| 3 | Neighborhood numeric exploration | Local search around best known values |
| 4 | Retest best primitives | Replication check on best mutations |
| 5 | Chip suggest hook | Domain-specific ideas from chip |
| 6 | Frontier sidecar (LLM) | Last resort; web research + bounded generation |

Critical: **signature deduplication** prevents infinite loops. Every tested combination is tracked and never re-suggested.

---

## Five Identified Bottlenecks

### 1. Signature Space Explosion
The candidate system generates mutations combinatorially. For N fields with M values each, space is M^N. Deduplication prevents re-testing but doesn't guide search efficiently.

### 2. Belief Promotion Requires Replication
Durable beliefs need 2+ improved runs with the same signature. For expensive experiments, this doubles confirmation time. Provisional beliefs fill the gap but carry less weight.

### 3. Collective Sync is Batch, Not Streaming
`build_spark_swarm_collective_payload()` builds a complete snapshot each time. No incremental sync -- every publish sends all entities. Increasingly expensive as workspace grows.

### 4. Absorb is Manual
The `absorb()` function creates review PRs for human approval. Even with `automerge`, there's latency between discovery and application.

### 5. Cross-Researcher Coordination
Multiple researchers publishing to same workspace can create contradictions. System detects them but resolving contradictions is manual.

---

## Productive vs. Wasteful Loop Patterns

### Productive Patterns

| Pattern | Why It Works |
|---------|-------------|
| Diverse mutation exploration | Each trial tests genuinely different configurations |
| Fast feedback (short commands) | More trials per unit time; continuous autoloop adapts sleep |
| Evidence accumulation toward durable beliefs | Replicated improvements > single improvements |
| Cross-pollination via collective absorb | Findings from one researcher accelerate others |
| Chip-guided search | Domain chips narrow search space with informed suggestions |

### Wasteful Patterns

| Anti-Pattern | Why It Fails |
|-------------|-------------|
| Signature exhaustion without progress | System stuck; autoloop keeps trying with increasing sleep |
| Contradicting beliefs accumulating | Noisy metrics or non-deterministic evaluation |
| Stale working memory | Chip suggestions based on outdated context |
| Absorb without local validation | Importing knowledge that doesn't apply locally |
| Upgrade delivery CI failures | Effort spent on promotion/review/delivery wasted |

---

## Self-Edit System (3-Phase)

### Phase 1 -- Propose
- Copy repo to temporary workspace
- Render `request.md` with: mutable targets, hard rules, improvement request
- Run backend command (Codex/AI agent)
- Collect diffs, validate they stay within mutable scope

### Phase 2 -- Review (the guardrail layer)
Requires:
- **Decision**: approve, defer, or reject
- **Root lesson**: what insight drove this change
- **3 lineage failures**: three specific past failures motivating the change
- **Counterfactual**: what happens if change is NOT applied
- **Ghost improvement check**: verify improvement is real, not artifact
- **Rollback condition**: when should this be reverted

### Phase 3 -- Apply
- Copy modified files back to original repo
- Optionally create git branch, commit, push
- Only point where researcher modifies its own source

---

## Evidence Quality Tiers (Memory System)

| Tier | Priority | Meaning |
|------|----------|---------|
| `grounded_doctrine` | 30 | Highest confidence, well-replicated |
| `research_grounded` | 28 | Supported by web research |
| `grounded_boundary` | 26 | Known limits and constraints |
| `benchmark_evidence` | 22 | Benchmark-supported results |
| `exploratory_frontier` | 18 | Promising but unconfirmed |
| `state_snapshot` | 12 | Current system state |
| `raw_outcome` | 8 | Unprocessed results |
| `raw_run` | 4 | Raw execution data |

Memory search scoring uses: term match count, title bonus, phrase bonus, kind priority (beliefs > episodes > raw runs), and tier priority.

---

## Evolution Modes (Progressive Autonomy)

| Mode | Behavior |
|------|----------|
| `observe_only` | System watches but takes no action |
| `review_required` | Proposes changes but requires human approval |
| `checked_auto_merge` | Auto-merges if CI checks pass |
| `trusted_auto_apply` | Applies changes without review |

---

## Where Domain Chips Participate

1. **Evaluation**: Chip `evaluate` hook replaces/supplements default metric parsing with domain-specific scoring
2. **Suggestion**: Chip `suggest` hook provides domain-informed mutation ideas after algorithmic strategies exhausted
3. **Knowledge packets**: Chip `packets` hook provides methodology documents at research_grounded/benchmark_evidence tier
4. **Watchtower**: Chip `watchtower` hook generates Obsidian pages for human review (the human-in-the-loop path)

---

## Implications for Chip Factory

### What the scaffold engine enables for recursive loops:
1. **Instant chip creation** means every new domain can immediately participate in Cycle A (local trial loop)
2. **Pre-wired hooks** mean domain chips can be grounded by spark-researcher from day one
3. **Category templates** provide domain-appropriate mutation axes, reducing signature space exploration waste

### What still needs to be built:
1. **RecursiveLoopController** that wires scaffold → researcher → evaluate → gap_analyze → fix → re-evaluate
2. **Streaming collective sync** to reduce Cycle C latency from hours to minutes
3. **Auto-contradiction resolution** using evidence strength ranking
4. **Cross-chip mutation sharing** at the trial level, not just mastery level
5. **Chip learning from outcomes** so suggestion quality improves based on which suggestions led to improvements
