# MiroFish Discovery Factory Plan

## Objective

Shift MiroFish from a purely seeded ranking harness into a two-stage system:

1. agents discover candidate domain chips from demand, specialization intent, and mastery intent
2. MiroFish evaluates the resulting candidate set with a controlled simulation harness

The goal is not to abandon the existing 515-chip universe. The goal is to stop treating a hand-curated list as the only way new domain chips can enter the system.

## Product Decision

Use a hybrid architecture:

- upstream: open-ended discovery
- downstream: closed evaluation

This keeps exploration open while preserving calibration, deduplication, and repeatable ranking.

## Why This Is Better

### What the current seeded system is good at

- comparing a fixed set of domain chips
- testing simulation mechanics under controlled conditions
- producing repeatable rankings and confidence intervals
- benchmarking one run against another

### What the current seeded system misses

- domains we did not think to include
- shifts in what users want to specialize in
- shifts in what users want to master
- emerging wedges that are not yet in the 515-chip portfolio

### What a fully open system would get wrong if used alone

- duplicate domains with slightly different names
- vague lifestyle "wants" mixed with real domain-chip candidates
- self-fulfilling scoring where agents invent and then immediately validate the same idea
- poor comparability across runs

## Target Architecture

### Stage A: Frontier Discovery

Purpose:

- discover candidate domain chips without giving agents the 515-chip list first

Input:

- user-intent patterns
- specialization intent
- mastery intent
- recurring pain
- repeated adjacent behaviors
- existing repo knowledge

Output:

- raw candidate domain observations
- evidence-backed candidate hypotheses

Artifact lane:

- `exploratory_frontier`

### Stage B: Candidate Canonicalization

Purpose:

- turn noisy discovered ideas into a clean candidate domain-chip universe

Input:

- raw discovery candidates

Output:

- canonical domain IDs
- labels
- descriptions
- tags
- specialization rationale
- mastery rationale
- evidence links or evidence summaries
- duplicate/alias mapping

Artifact lane:

- `research_grounded` once evidence is stable enough

### Stage C: Evaluation Harness

Purpose:

- run MiroFish on the discovered candidate set after canonicalization

Input:

- canonical candidate universe
- graph relationships
- signals
- shocks
- macro context

Output:

- final retained adoption
- peak active choice signal
- peak interest signal
- trial/churn/retention behavior
- ensemble confidence intervals

Artifact lane:

- `exploratory_frontier`

### Stage D: Promotion Layer

Purpose:

- decide which discovered candidates deserve to enter the maintained benchmark universe

Promotion outcomes:

- `watchlist`
- `evaluate next`
- `needs more evidence`
- `reject / duplicate / too vague`

Operator path:

- focused hybrid run
- promotion-review packet
- human benchmark-review decision

## Hard Boundary

Discovery and evaluation must stay separate.

Bad pattern:

- "agent invents a domain"
- "same agent immediately scores it"
- "system treats that as evidence"

Good pattern:

- discovery proposes
- canonicalizer cleans
- evaluator ranks
- human reviews promotion

## Candidate Definition

A discovered domain chip should only survive canonicalization if it answers all three:

1. what is the repeated thing the user wants help doing?
2. what is the repeated thing the user wants to specialize in?
3. what is the repeated thing the user wants to master?

If a candidate cannot answer those cleanly, it is not a domain chip yet.

## Data Contract For Discovered Candidates

Each canonical candidate should have:

- `domain_id`
- `label`
- `description`
- `specialization_surface`
- `mastery_surface`
- `user_value_loop`
- `domain_tags`
- `evidence_sources`
- `evidence_summary`
- `demand_signals`
- `adjacent_domains`
- `duplicate_aliases`
- `confidence_read`
- `promotion_status`

## Discovery Questions Agents Must Answer

Each discovery worker should explicitly answer:

1. what job is the user trying to get done?
2. what skill or operating edge are they trying to build?
3. what repeated workflow would justify a specialized chip?
4. what proof suggests this is recurring rather than decorative?
5. what nearby domains should this be merged with or separated from?

## Discovery Output Classes

Discovery results should be classified into exactly one of these:

- `clear_domain_chip`
- `proto_domain_chip`
- `workflow_not_domain`
- `persona_only_not_domain`
- `duplicate_of_existing`
- `too_vague_to_keep`

This keeps the system from promoting generic aspiration language into fake chips.

## Proposed Harnesses

### 1. Discovery Harness

This is the new harness to build first.

Configuration:

- no seeded 515-chip menu presented to discovery agents
- multiple discovery passes over the same intent space
- outputs stored as candidate packets, not rankings
- one run should produce:
  - raw candidates
  - merged candidates
  - rejected candidates with reasons

Suggested first operating shape:

- 4 discovery roles
  - demand scout
  - specialization scout
  - mastery scout
  - duplicate hunter
- 1 canonicalization pass
- 1 human-review packet

### 2. Evaluation Harness

Use the current MiroFish structure after canonicalization.

Configuration for the first hybrid version:

- candidate set size target: `50` to `150` discovered candidates per cycle
- flagship simulation: `15 persona types x 30 each = 450 agents`
- rounds: `20`
- ensemble: `15` to `30` runs
- report rank should include:
  - `agent_choice_signal`
  - `peak_interest_probability`
  - `final_adoption_rate`

Reason:

- this is large enough to be informative
- still small enough to debug and inspect
- avoids immediately pushing the 515-scale cost into the first hybrid iteration

### 3. Benchmark Harness

Keep a fixed comparison panel.

Purpose:

- compare discovered candidates against a stable benchmark set
- detect whether discovery is finding anything better than known strong chips

Suggested benchmark panel:

- top existing leadership chips
- several mid-tier chips
- several low-quality chips
- a handful of newly discovered candidates

## Implementation Phases

### Phase 1: Discovery Contract

Deliverables:

- candidate schema doc
- discovery classification rules
- canonicalization rules
- promotion statuses

Definition of done:

- we can run discovery without pretending every idea is already a valid chip

### Phase 2: Packet-First Discovery Pipeline

Deliverables:

- `research/meta/` discovery packet format
- one manual batch that produces:
  - raw candidates
  - merged candidates
  - rejected candidates

Definition of done:

- we can inspect discovered chips as evidence artifacts before simulation

### Phase 3: Canonical Candidate Builder

Deliverables:

- transform discovery packets into a canonical candidate universe
- alias merge rules
- duplicate rejection rules

Definition of done:

- discovered candidates can feed graph/signal generation without hand-cleaning every time

### Phase 4: Hybrid MiroFish Runner

Deliverables:

- run MiroFish on the discovered candidate universe
- output rankings that preserve:
  - final retention
  - peak active signal
  - peak interest

Definition of done:

- we can answer both:
  - what agents noticed and tried
  - what survived to retained adoption

### Phase 5: Promotion Review

Deliverables:

- compare discovered winners against the fixed benchmark panel
- mark candidates:
  - keep watching
  - add to benchmark set
  - reject

Definition of done:

- the benchmark universe evolves from evidence instead of only manual curation

## First Tranche To Build Now

Do not start with a full autonomous factory.

Start with this narrower tranche:

1. define the discovery candidate schema
2. define discovery output classes
3. define canonicalization and duplicate rules
4. run one manual discovery batch
5. feed the cleaned candidates into a smaller MiroFish evaluation run

This gives the shortest path to truth without a large architectural leap.

## Concrete Deliverables For The Next Session

### Deliverable 1

A discovery contract document that locks:

- what counts as a domain chip
- what counts as noise
- what evidence is required

### Deliverable 2

A packet format in `research/meta/` for discovered candidates.

### Deliverable 3

One manually curated discovery batch with:

- accepted candidates
- merged candidates
- rejected candidates

### Deliverable 4

One hybrid evaluation note comparing:

- discovered candidates
- a small stable benchmark panel

## Success Criteria

We should be able to say all of the following honestly:

- the system can discover candidate domain chips without being handed the 515 list first
- the system does not confuse vague desires with valid domain chips
- the evaluator does not score raw noise directly
- the resulting report shows both choice signal and retained adoption
- newly discovered candidates can be compared against a stable benchmark set

## Failure Modes To Watch

- discovery produces motivational fluff instead of domains
- canonicalization merges truly distinct domains into one blob
- evaluation rewards novelty rather than evidence-backed demand
- open discovery drifts too far from specialization/mastery use cases
- humans stop being able to audit why a candidate entered the universe

## Recommendation

Build the hybrid discovery-first pipeline now.

Do not replace the seeded universe.
Make the seeded universe the benchmark layer, and make discovery the intake layer.
