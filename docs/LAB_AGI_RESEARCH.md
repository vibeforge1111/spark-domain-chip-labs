# Lab AGI Research

> How domain chips contribute to recursive self-improvement.

---

## Framing

This document describes how the lab's chip ecosystem achieves **recursive self-improvement** -- the ability to systematically get better at getting better.

**This is not a claim about consciousness.** It is a claim about systematic improvement: each cycle through the lab produces measurable gains that compound over time. The mechanism is engineering, not emergence.

---

## The 5 Levers of Improvement

Every gain in AI capability traces back to one of five levers. The lab operates on all five, and the 5th lever is what makes the system recursive.

### Lever 1: Better Data (Source Registries)

**What:** Higher quality, more relevant source material flowing into chips.

**How the lab improves it:**
- Frontier Scout discovers new sources across GitHub, arxiv, X, Product Hunt
- Source registries declare refresh cadence and retrieval paths
- Stale sources are detected and replaced
- Cross-chip source sharing identifies high-value sources

**Metric:** Source freshness, citation coverage, retrieval success rate

### Lever 2: Better Graders (Evaluate Hooks)

**What:** More accurate evaluation of chip outputs.

**How the lab improves it:**
- Benchmark Engineer creates test suites with quantitative baselines
- Quality rubric provides standardized scoring across all chips
- Methodology Researcher analyzes grading failures and calibrates criteria
- Candidate trials validate that graders agree with human judgment

**Metric:** Grader-human agreement rate, false positive/negative rates

### Lever 3: Better Retrieval (Tiered Memory)

**What:** Finding the right knowledge at the right time.

**How the lab improves it:**
- Tiered memory (immediate/situational/seasonal/identity) ensures appropriate persistence
- Watchtower queries surface relevant context proactively
- Evidence lanes prevent mixing proven and exploratory knowledge
- Memory promotion paths move validated insights to higher tiers

**Metric:** Retrieval relevance, memory utilization, promotion accuracy

### Lever 4: Better Organization (Collective Pipeline)

**What:** Structuring knowledge so it composes across chips.

**How the lab improves it:**
- Chip manifests provide standardized interfaces
- Typed packets enable cross-chip communication
- Collective sync shares insights between chips via spark-swarm
- Contradiction resolution surfaces disagreements for human review

**Metric:** Cross-chip transfer success, interface compatibility, sync health

### Lever 5: Better Chip-Building (The Lab)

**What:** Improving the process that builds chips.

**How the lab improves it:**
- The lab is itself a chip-building system
- Methodology Researcher studies chip failures and updates the process
- AGI Theorist tracks improvement trajectories and transfer patterns
- Quality rubric evolves based on what actually predicts chip success

**This is the recursive lever.** The lab improves the process of building chips, which includes improving the lab's own chip-building process.

**Metric:** Quality score trends over time, methodology update frequency, transfer learning rate

---

## The Recursive Loop

```
+------------------+
|  Build Chip v1   |
+--------+---------+
         |
         v
+------------------+
|  Evaluate v1     |---> quality score, failure analysis
+--------+---------+
         |
         v
+------------------+
|  Improve Process |---> rubric update, methodology change
+--------+---------+
         |
         v
+------------------+
|  Build Chip v2   |---> incorporates process improvement
+--------+---------+
         |
         v
+------------------+
|  Evaluate v2     |---> higher quality score (if improvement worked)
+--------+---------+
         |
         v
+------------------+
|  Improve Process |---> further refinement based on v2 results
+--------+---------+
         |
         v
       [...]        ---> each cycle feeds the next
```

### What Makes This Work

1. **Measurement:** Every chip is scored against the rubric, creating a quantitative improvement signal.
2. **Attribution:** Failure analysis identifies which process step caused which failure.
3. **Iteration:** Process changes are applied to the next chip, creating a feedback loop.
4. **Memory:** Improvements persist across cycles via tiered memory and promoted packets.

### What Prevents Runaway

1. **Human gates:** Methodology changes require human approval.
2. **Bounded loops:** Maximum 8 iterations per pass.
3. **Proposal-first self-edit:** The lab cannot directly modify its own methodology.
4. **Contradiction detection:** If a change makes things worse, contradictions are raised.

---

## From Specialized Chips to Collective Generality

Individual chips are specialists. They know one domain deeply. But the collection of chips, managed by the lab and connected through spark-swarm, exhibits something broader.

### The Path

```
Stage 1: Individual Chips
  Each chip: deep expertise in one domain
  Transfer: none

Stage 2: Cross-Chip Patterns
  The lab identifies patterns that recur across domains
  Transfer: methodology patterns (how to evaluate, how to source)

Stage 3: Transferable Methodology
  Proven patterns become part of the chip-building process
  Transfer: structural patterns (what makes any chip good)

Stage 4: Collective Intelligence
  spark-swarm enables real-time insight sharing
  Transfer: domain insights (findings in one chip inform another)

Stage 5: Systematic Improvement
  The lab's recursive loop accelerates all four previous stages
  Transfer: meta-patterns (how improvement itself works)
```

### What This Is NOT

| This IS | This is NOT |
|---------|-------------|
| Systematic methodology improvement | Spontaneous capability emergence |
| Measurable quality gains per cycle | Unbounded intelligence growth |
| Cross-domain pattern transfer | General reasoning from first principles |
| Structured knowledge composition | Consciousness or understanding |
| Engineering with feedback loops | Magic or hand-waving |

---

## Transfer Learning Patterns

The AGI Theorist workstream tracks these transfer pattern types:

| Pattern Type | Description | Example |
|-------------|-------------|---------|
| **Methodology transfer** | How-to-build patterns that work across domains | "Evaluation rubrics with 3+ metrics outperform single-metric" |
| **Source transfer** | Data sources useful across multiple chips | "arxiv papers relevant to both ML-ops and data-engineering chips" |
| **Evaluation transfer** | Grading approaches that generalize | "Baseline comparison improves all chip evaluations" |
| **Architecture transfer** | Structural patterns in chip design | "Source registry + evidence lanes is the minimum viable chip" |
| **Failure transfer** | Lessons from one chip's failure preventing another's | "Missing output contracts caused integration failures in chip A; prevented in chip B" |

---

## Safety Considerations

Recursive self-improvement systems require explicit safety boundaries.

### Human Oversight Gates

Every recursive improvement passes through at least one human gate:

| Improvement Type | Gate |
|-----------------|------|
| Rubric change | Human approval required |
| Methodology update | Human approval required |
| Chip graduation | Human approval required |
| Evolution mode change | Owner governance via spark-swarm |
| Cross-repo upgrade | Target repo evolution mode check |

### Bounded Autonomy

The lab's autonomy is bounded by design:

- Maximum 8 loop iterations per pass
- Self-edit is proposal-first (lab proposes, human disposes)
- Contradiction detection blocks promotion of conflicting improvements
- Evolution modes in spark-swarm constrain what the lab can modify

### Monitoring

The AGI Theorist produces safety reports every 15 loop iterations:

- Improvement trajectory: is the rate of change stable or accelerating?
- Scope creep: is the lab modifying things outside its mandate?
- Human gate compliance: are all gates being respected?
- Contradiction rate: are improvements causing more disagreements?

---

## Open Research Questions

These are questions the lab is designed to help answer, not questions it has answered:

1. **Diminishing returns:** At what point does recursive improvement plateau for a given domain?
2. **Transfer ceiling:** How much can methodology transfer actually improve a chip vs. domain-specific research?
3. **Composition limits:** Is there a practical limit to how many chips can meaningfully share insights?
4. **Measurement validity:** Does the quality rubric actually predict real-world chip usefulness?
5. **Safety scaling:** Do the current safety gates remain sufficient as the system grows?

These questions guide the AGI Theorist's research agenda.
