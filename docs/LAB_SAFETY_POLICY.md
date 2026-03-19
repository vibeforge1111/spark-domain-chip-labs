# Lab Safety Policy

> Non-negotiable human gates, bounded autonomy, and governance.

---

## Core Principle

The lab is a tool that helps humans build better chips. It is not an autonomous agent with independent goals. Every safety mechanism in this document exists to maintain that relationship.

---

## Non-Negotiable Human Gates

These gates require explicit human approval. No automation, no bypass, no exception.

| Gate | What Requires Approval | Why |
|------|----------------------|-----|
| **Chip Graduation** | Promoting a prototype to production chip | Graduated chips enter the ecosystem and affect other systems |
| **Methodology Changes** | Modifications to the master chip architect prompt | The master prompt shapes all future chips |
| **Evolution Mode Upgrades** | Changing a repo's evolution mode (e.g., locked -> guarded) | Evolution modes control what the lab can modify in each repo |
| **Cross-Repo Upgrades** | Pushing changes from the lab to spark-researcher or spark-swarm | Changes to other repos have downstream effects the lab cannot fully predict |

### Gate Enforcement

```
Lab proposes change
       |
       v
  [Human Review]
       |
   +---+---+
   |       |
Approve  Reject
   |       |
   v       v
Execute  Log rejection
           + reason
```

There is no "auto-approve" mode. There is no timeout that converts pending to approved. Human gates are human gates.

---

## Contradiction-Based Safety

The lab uses contradiction detection as a safety signal. When the system disagrees with itself, it stops and asks.

### How Contradictions Work

A contradiction occurs when:
- A new finding conflicts with an existing promoted insight
- Two chips produce incompatible claims about the same domain
- A methodology change would invalidate existing quality scores
- An improvement in one dimension degrades another

### Contradiction Severity Levels

| Severity | Definition | Action |
|----------|-----------|--------|
| **Advisory** | Minor inconsistency, may resolve with more data | Log, continue, flag for review |
| **Warning** | Meaningful disagreement requiring attention | Block promotion of the conflicting packet |
| **Critical** | Fundamental conflict that undermines trust | Block all promotions in the affected domain until resolved |

### Critical Contradiction Rules

Critical contradictions are the strongest automatic safety mechanism:

1. **Block promotion:** No packet in the affected domain can be promoted to a higher memory tier
2. **Flag for human review:** The contradiction is surfaced in the watchtower and requires human resolution
3. **Preserve both sides:** Neither the existing insight nor the contradicting finding is deleted
4. **Require resolution record:** The human resolution must document why one side was chosen

---

## Bounded Autonomy

The lab operates within explicit bounds. These bounds are enforced by the loop implementation, not by trust.

### Loop Bounds

| Bound | Value | Enforcement |
|-------|-------|-------------|
| Max iterations per pass | 8 | Loop counter in the flywheel; hard stop at 8 |
| Max conditional stage duration | 10 minutes | Timeout per conditional stage execution |
| Max always-on stage duration | 2 minutes | Timeout per always-on stage |
| Minimum cycle interval | 30 seconds | Rate limiter prevents tight loops |
| Memory write retry limit | 3 | Fail fast on persistent storage failures |

### Why 8 Iterations

8 is chosen because:
- It is enough for meaningful progress (7 workstreams + 1 for follow-up)
- It is small enough that a human can review the full pass output
- It prevents the loop from running indefinitely on edge cases
- Each iteration produces a cycle record, so the audit trail stays manageable

### What Happens at the Bound

When the loop reaches 8 iterations:
1. The current iteration completes (no mid-iteration abort)
2. A pass summary is generated
3. The lab stops and waits for the next trigger
4. No state is lost -- the next pass picks up where this one left off

---

## Self-Edit Protocol

The lab can propose modifications to its own configuration and methodology, but cannot directly execute them.

### Proposal-First Rule

```
Lab identifies improvement
       |
       v
  [Generate Proposal]
  - What to change
  - Why (evidence)
  - Expected impact
  - Risk assessment
       |
       v
  [Proposal Stored]
  - In pending_proposals queue
  - Visible in watchtower
  - Tagged with evidence lane
       |
       v
  [Human Reviews]
       |
   +---+---+
   |       |
Approve  Reject
   |       |
   v       v
Execute  Log with
change   rationale
```

### What the Lab CAN Self-Edit (After Approval)

- Source registry entries (add/remove/update sources)
- Benchmark test cases (expand coverage)
- Watchtower thresholds (adjust alert sensitivity)
- Internal documentation (update docs to reflect current state)

### What the Lab CANNOT Self-Edit (Even After Approval)

- The safety policy itself (this document)
- Human gate definitions
- Evolution mode constraints
- Loop bound values

Changes to these require direct human modification of the source files.

---

## Owner Governance via spark-swarm

The lab participates in spark-swarm's evolution mode system. Evolution modes are set by the repo owner and control what the lab can do.

### Evolution Modes

| Mode | Lab Can | Lab Cannot |
|------|---------|------------|
| **Locked** | Read repo state, run benchmarks | Propose any changes |
| **Guarded** | Propose changes via packets | Push changes without approval |
| **Supervised** | Execute pre-approved change types | Execute unapproved change types |
| **Autonomous** | Execute within defined bounds | Exceed bounds or modify bounds |

### The Lab Cannot Bypass a Repo's Evolution Mode

This is a hard invariant. If spark-researcher is in `locked` mode:
- The lab cannot push methodology updates to it
- The lab cannot modify its chip manifests
- The lab cannot trigger upgrades
- The lab CAN still read its state and run benchmarks against it

The evolution mode is the repo owner's sovereign decision. The lab respects it unconditionally.

### Mode Change Protocol

Evolution mode changes flow through spark-swarm governance:

1. Owner (human) decides to change mode
2. Mode change is recorded in spark-swarm
3. The lab detects the new mode on next sync
4. The lab adjusts its behavior accordingly
5. No negotiation -- the lab does not argue for a different mode

---

## Audit Trail

Every action the lab takes is recorded.

### What Gets Logged

| Action | Logged Fields |
|--------|--------------|
| Loop iteration | Cycle ID, timestamp, stages executed, bottleneck detected, outputs |
| Packet creation | Packet ID, kind, evidence lane, content hash |
| Packet promotion | Packet ID, from tier, to tier, promotion reason |
| Contradiction detection | Contradiction ID, severity, affected domain, conflicting packets |
| Human gate request | Gate type, proposed change, requestor, timestamp |
| Human gate decision | Gate type, decision (approve/reject), reviewer, rationale |
| Self-edit proposal | Proposal ID, target, proposed change, evidence, risk assessment |
| Evolution mode check | Target repo, current mode, action attempted, allowed/blocked |

### Log Retention

- Cycle records: retained indefinitely (they are small)
- Packet records: retained while packet exists in memory
- Gate decisions: retained indefinitely (audit requirement)
- Contradiction records: retained until resolution + 90 days

---

## Failure Modes

What happens when things go wrong.

| Failure | Response | Recovery |
|---------|----------|----------|
| Loop exceeds max iterations | Hard stop, pass summary generated | Next pass picks up from current state |
| Memory write failure | Retry 3x, then fail the cycle | Alert human, continue with cached state |
| Source unavailable | Use cached data, log staleness warning | Retry on next research refresh |
| Human gate timeout | Proposal stays in pending queue | Reminder surfaced in watchtower |
| Contradiction detected | Block affected promotions | Human resolution required |
| Integration failure | Log health report, block cross-repo actions | Integration Specialist investigates |

---

## Summary of Safety Invariants

1. **Human gates are human gates.** No bypass. No auto-approve. No timeout-to-approve.
2. **Critical contradictions block promotion.** The system stops when it disagrees with itself.
3. **Loops are bounded.** Maximum 8 iterations. No exception.
4. **Self-edit is proposal-first.** The lab proposes, humans dispose.
5. **Evolution modes are sovereign.** The lab cannot override a repo owner's governance decision.
6. **Everything is logged.** Actions, decisions, contradictions, failures -- all recorded.
7. **The safety policy cannot be self-edited.** Only humans modify this document directly.
