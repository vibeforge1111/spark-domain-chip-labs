# Spark Systems Analysis: spark-researcher and spark-swarm

## Comprehensive Architecture, Recursive Loop, and Intelligence Pipeline Report

**Prepared:** 2026-03-20
**Repositories analyzed:**
- `spark-researcher` -- cloned to `C:\Users\USER\Desktop\researcher-analysis-temp\spark-researcher\`
- `spark-swarm` -- cloned to `C:\Users\USER\Desktop\researcher-analysis-temp\spark-swarm\`

---

## Table of Contents

1. [spark-researcher Architecture](#1-spark-researcher-architecture)
   - 1.1 Core Loop
   - 1.2 Configuration and Project Model
   - 1.3 Trial Execution Engine
   - 1.4 Candidate Suggestion System
   - 1.5 Domain Chip Integration
   - 1.6 Belief Promotion and Contradiction Tracking
   - 1.7 Memory System
   - 1.8 Advisory and Research Pipeline
   - 1.9 Verifier Pipeline
   - 1.10 Self-Edit System
   - 1.11 Collective Intelligence Emission
2. [spark-swarm Architecture](#2-spark-swarm-architecture)
   - 2.1 Monorepo Shape
   - 2.2 Type System (Contracts)
   - 2.3 API Layer
   - 2.4 Collective Service
   - 2.5 Intelligence Derivation
   - 2.6 Bridge Layer
   - 2.7 Workspace and Agent Model
3. [Recursive Loop Mechanics](#3-recursive-loop-mechanics)
   - 3.1 The Core Recursive Cycle
   - 3.2 Feedback Timescales
   - 3.3 Bottlenecks and Failure Modes
   - 3.4 Ideal Loop Design
   - 3.5 Swarm-Orchestrated Self-Improvement
4. [Full Intelligence Pipeline](#4-full-intelligence-pipeline)
   - 4.1 End-to-End Data Flow
   - 4.2 Evidence Quality Ladder
   - 4.3 Cross-Repository Knowledge Transfer
   - 4.4 Pipeline Diagram
5. [Effective vs. Ineffective Loops](#5-effective-vs-ineffective-loops)
6. [Key Findings and Observations](#6-key-findings-and-observations)

---

## 1. spark-researcher Architecture

### 1.1 Core Loop

spark-researcher is described in its README as a "careful lab assistant" that runs repeatable experiments against a project and records what works. The fundamental loop is:

```
config -> run -> score -> ledger -> memory -> next decision
```

**Key file:** `spark-researcher/src/spark_researcher/runner.py`

The `run_once()` function (line 365) is the atomic unit of work:

1. Copies the project tree to an isolated workspace directory
2. Applies mutations (parameter changes) from a candidate trial
3. Executes the command (training script, benchmark, etc.)
4. Parses metrics from the command's log output
5. Computes a verdict by comparing against baseline or best-known metric
6. Builds and persists a record to the JSONL ledger (immutable append-only log)
7. Writes a spark-swarm collective payload for external sync
8. Refreshes chip working memory if applicable
9. Records failures for surprise analysis

```python
# runner.py line 432-451 (verdict, record, persist)
verdict = metric_verdict(numeric_metric, baseline_value, config.eval_goal,
                         config.guardrails.near_best_tolerance)
record = build_record(config, command_name, command_result, run_dir,
                      log_path, metrics, baseline_value, verdict, trial,
                      applied_mutations, chip_result=chip_result)
ensure_parent(run_dir / "result.json")
(run_dir / "result.json").write_text(json.dumps(record, indent=2, sort_keys=True))
append_jsonl(ledger_path(runtime_root), record)
write_spark_swarm_collective_payload(config_path.parent.resolve(),
                                     runtime_root, config, record)
```

Verdicts are one of: `improved`, `regressed`, `flat`, `baseline`, `near_best`, `unknown`.

### 1.2 Configuration and Project Model

**Key file:** `spark-researcher/src/spark_researcher/config.py`

The `ProjectConfig` dataclass is the schema for `spark-researcher.project.json`:

| Field | Purpose |
|-------|---------|
| `commands` | Named command specs (args, cwd, log_name, kind) |
| `metrics` | Named metric specs (pattern regex, goal: minimize/maximize) |
| `candidate_trials` | Pre-defined trials with mutation sets and summaries |
| `mutable_parameters` | Parameters the system is allowed to change |
| `guardrails` | Safety limits: `max_loop_iterations=8`, `consecutive_discard_limit=3`, `near_best_tolerance=0.03` |
| `self_edit` | Self-edit settings: mutable targets, backend agent, review gates |
| `memory` | Memory configuration |
| `chip` | Chip manifest path, frontier settings |
| `intent` | Intent brief and mission statement |

Command kinds include regular commands and `chip-evaluate`, which delegates scoring to a domain chip's evaluate hook.

### 1.3 Trial Execution Engine

**Key file:** `spark-researcher/src/spark_researcher/runner.py`

`run_loop()` iterates through configured candidate trials sequentially:

```python
# runner.py -- run_loop pattern
for trial in config.candidate_trials:
    record = run_once(config_path, command_name, trial=trial)
    if record["verdict"] == "improved":
        consecutive_discards = 0
    elif _row_counts_as_discard(record):
        consecutive_discards += 1
    if consecutive_discards >= discard_limit:
        return results, True  # stop early
```

The discard limit (`consecutive_discard_limit=3` by default) acts as a circuit breaker: if three consecutive trials fail to improve, the loop stops rather than wasting compute.

### 1.4 Candidate Suggestion System

**Key file:** `spark-researcher/src/spark_researcher/candidates.py`

The suggestion engine uses multiple strategies layered by sophistication:

| Strategy | Source | Description |
|----------|--------|-------------|
| **Failure-guided** | `candidates.py` | Analyzes failed combos, isolates failing components, suggests recovery to known-good values |
| **Neighborhood** | `candidates.py` | Probes numeric neighbors around the best observed parameter values |
| **Combination** | `candidates.py` | Merges beneficial single-parameter primitives into multi-parameter combos |
| **Chip-based** | `candidates.py` -> `chips.py` | Delegates to the domain chip's `suggest` hook |
| **Frontier (LLM)** | `frontier.py` | LLM-powered bounded mutation proposals with web search context |

`run_autoloop()` (line 611) orchestrates multi-round experimentation:

```
Round 1: Run all pending trials -> Suggest new trials -> Append to queue
Round 2: Run newly appended trials -> Suggest more -> Append
...
Until: No pending trials AND no new suggestions, OR round limit reached
```

`run_continuous_autoloop()` (line 694) wraps autoloop in an infinite outer loop with pauses between productive and unproductive passes, enabling long-running autonomous research.

### 1.5 Domain Chip Integration

**Key file:** `spark-researcher/src/spark_researcher/chips.py`

Domain chips are external, self-contained modules that follow two contracts:

- **Schema:** `spark-chip.v1` (manifest structure)
- **Protocol:** `spark-hook-io.v1` (subprocess invocation)

Four hooks are defined:

| Hook | Purpose | When Called |
|------|---------|------------|
| `evaluate` | Score a run using domain-specific rubric | During `chip-evaluate` command kind |
| `suggest` | Propose domain-informed candidate trials | During suggestion phase |
| `packets` | Emit domain knowledge documents (research, doctrine, boundaries) | During memory sync |
| `watchtower` | Generate Obsidian-compatible pages for monitoring | On demand |

Chip invocation (`invoke_chip_hook()`, line 368) follows a strict subprocess protocol:
1. Serialize input payload to a temp JSON file
2. Run the chip's hook command with `--input` and `--output` flags
3. Read and validate the output JSON
4. Return parsed result

```python
# chips.py line 368-446 -- invoke_chip_hook (simplified)
def invoke_chip_hook(config_path, hook_name, payload):
    # Write payload to temp input file
    # Run subprocess: chip_command --input input.json --output output.json
    # Parse and return output JSON
```

Chips are discovered by manifest path in the project config. The manifest declares:
- `schema_version: spark-chip.v1`
- `domain`, `version`, `hooks` (with command paths)
- `frontier` config: `allowed_mutations`, `open_mutation_fields`, `field_patterns`

### 1.6 Belief Promotion and Contradiction Tracking

**Key file:** `spark-researcher/src/spark_researcher/beliefs.py`

The belief system transforms raw experimental results into epistemic claims:

**Promotion Policy** (from `build_beliefs()`, line 276):

1. **Durable belief**: A mutation signature with 2+ improved runs (replicated) AND no active contradictions
2. **Provisional belief**: The single best-observed candidate with no regressions for that signature (not yet replicated)
3. **Contradicted**: Two promoted beliefs for the same command disagree on a shared mutation value -- both demoted to provisional

```python
# beliefs.py line 358-362 -- promotion_policy in manifest
"promotion_policy": [
    "Promote repeated improvements ... as durable only when no active contradiction remains.",
    "Allow a single-run promotion only when it is the current best observed candidate ...",
    "If two promoted lessons ... disagree on a shared mutation value, mark both as provisional ..."
]
```

Belief outputs:
- Individual belief markdown files in `docs/beliefs/`
- `INDEX.md` listing all beliefs with status
- `CONTRADICTIONS.md` listing all active contradictions with conflicting field values
- `manifest.json` with counts: `durable_belief_count`, `provisional_belief_count`, `contradiction_count`

### 1.7 Memory System

**Key file:** `spark-researcher/src/spark_researcher/memory.py`

Memory is a local file-based system with tiered priorities. `sync_memory()` (line 537) rebuilds all memory documents from multiple sources:

| Source | Memory Tier | Priority |
|--------|-------------|----------|
| Run records from JSONL ledger | `raw_run` | 10 |
| Belief documents | `belief` | 20 |
| Self-edit proposals + reviews | `raw_outcome` | 12 |
| Working memory (current state) | `state_snapshot` | 15 |
| Episode memory (session history) | `state_snapshot` | 15 |
| Outcomes (aggregated run summaries) | `raw_outcome` | 12 |
| Chip packets (domain knowledge) | Varies by kind | Varies |

Chip packets can declare their own memory tiers:
- `research_grounded` (priority 28)
- `grounded_doctrine` (priority 30, highest)
- `grounded_boundary` (priority 26)
- `benchmark_evidence` (priority 22)
- `exploratory_frontier` (priority 8)

`search_memory()` (line 677) provides local lexical search with scoring:
- Term frequency matching
- Title bonus for keyword matches
- Phrase bonus for exact multi-word matches
- Kind/tier priority weighting

### 1.8 Advisory and Research Pipeline

**Key files:**
- `spark-researcher/src/spark_researcher/advisory.py`
- `spark-researcher/src/spark_researcher/research.py`

The advisory system builds evidence-backed AI briefs:

`build_advisory()` (advisory.py, line 158) assembles:
1. Packet search results from memory
2. Intent brief (mission statement)
3. Epistemic status classification:
   - **grounded**: Has packets + guidance + boundary documents
   - **partial**: Has some evidence but incomplete
   - **under_supported**: Lacks sufficient evidence
4. Failure priorities from surprise analysis
5. Packet stability tracking: `durable_supported`, `provisional_only`, `no_belief_packets`

`execute_with_research()` (research.py, line 160) extends advisories with web research:
1. Run initial verifier pass
2. If result indicates `research_needed`, perform bounded web search via DuckDuckGo
3. Create follow-up advisory with research notes as citations
4. Re-run verifier with enriched context

### 1.9 Verifier Pipeline

**Key file:** `spark-researcher/src/spark_researcher/verifier.py`

`execute_with_verifier()` (line 372) implements a multi-draft verification flow:

```
Draft A (primary answer)
  |
Draft B (alternative, different structure)
  |
Critique (compare both, select stronger, identify issues)
  |
Revision (rewrite selected draft based on critique)
  |
Citation enforcement (check research note usage)
  |
Research escalation (if needed, trigger bounded web search)
```

This A/B comparison with critique ensures the system does not simply accept the first answer but actively stress-tests its own outputs.

### 1.10 Self-Edit System

**Key file:** `spark-researcher/src/spark_researcher/self_edit.py`

Self-edit is a proposal-first system for code changes with strict safety:

**Proposal phase** (`propose()`, line 294):
1. Copy repo to isolated workspace
2. Run backend agent (e.g., Claude) to generate edits
3. Collect diffs as the proposal
4. Store proposal JSON without applying anything

**Review phase** (`review_proposal()`, line 373) requires:
- Decision: approve/reject/defer
- `root_lesson`: What the system learned
- 3 `lineage_failures`: "What could go wrong if this breaks"
- `counterfactual`: "What would happen if we didn't do this"
- `rollback_condition`: When to revert

**Apply phase** (`apply_proposal()`, line 434):
- Creates a git branch
- Applies the diff
- Commits with metadata
- Optionally pushes

The AGENTS.md contract enforces hard boundaries: only edit mutable targets, only work in copied workspace, proposal-first always.

### 1.11 Collective Intelligence Emission

**Key file:** `spark-researcher/src/spark_researcher/collective.py`

After each run, `build_spark_swarm_collective_payload()` (line 121) constructs a payload conforming to the `SparkResearcherCollectiveSyncPayload` contract:

```python
# collective.py line 222-288 -- payload structure
{
    "workspaceId": workspace_id,
    "agentId": agent_id,
    "runtimeSource": { kind, version, loopKind, chipKey, chipLabel },
    "specialization": { id, key, label, memoryPolicy },
    "runtimePulse": { agentId, repoId, runtimeState, passNumber, stageKey, ... },
    "intelligencePulse": { specializationId, activeEvolutionPathId, newestInsightId, ... },
    "evolutionPaths": [...],
    "insights": [...],
    "masteries": [...],
    "contradictions": [...],
    "upgrades": [],
    "upgradeDeliveries": [],
    "outcomes": [...],
    "artifactRefs": [...],
    "emittedAt": timestamp
}
```

Evidence lane classification:
- `benchmark_evidence`: When chip_result has `comparison_class == "benchmark_grounded"`
- `live_evidence`: All other runs (default)

Insight generation rules:
- If `status == "ok"` and `verdict not in {regressed, unknown}` -> create an insight
- If benchmark_evidence AND insight exists -> create a provisional mastery
- If `status != "ok"` or `verdict in {regressed, unknown}` -> create a contradiction

Additionally, `publish_latest()` creates portable **capsules** in `.autoresearch/capsules/` with both a markdown summary and a JSON manifest, enabling cross-repo knowledge transfer. The `absorb()` function (line 699) implements this transfer via draft PRs with review files (ABSORB_PLAN.md, AI_REVIEW.md, PR_BODY.md).

---

## 2. spark-swarm Architecture

### 2.1 Monorepo Shape

```
spark-swarm/
  apps/
    api/          # Hono (TypeScript) -- collective intelligence API
    web/          # React -- observatory dashboard
    bridge/       # Python CLI -- local operations, state, sync
  packages/
    contracts/    # Shared TypeScript types
```

The system follows a **one agent per workspace** model. Each workspace has one agent, which can be attached to many repos. The spark-researcher runtime is the intelligence engine.

### 2.2 Type System (Contracts)

**Key file:** `spark-swarm/packages/contracts/src/index.ts` (~487 lines)

The contracts package defines the complete domain vocabulary:

**State types:**

| Type | Values |
|------|--------|
| `RuntimeState` | idle, running, sleeping, blocked, offline |
| `EvolutionMode` | observe_only, review_required, checked_auto_merge, trusted_auto_apply |
| `MemoryPolicy` | isolated, selective, shared |
| `EvidenceLane` | source_evidence, benchmark_evidence, live_evidence |
| `InsightStatus` | captured, distilled, queued_for_test, benchmark_supported, live_supported, contradicted |
| `MasteryStatus` | provisional_mastery, shared_mastery, quarantined, contradicted, retired |
| `UpgradeDeliveryStatus` | recommendation_only, draft_pr_opened, pr_opened, awaiting_checks, awaiting_review, merged, applied, rolled_back, rejected |

**Core record interfaces:**

| Interface | Key Fields |
|-----------|------------|
| `InsightRecord` | id, specializationId, summary, mechanism, boundary, confidence, evidenceLane, status |
| `MasteryRecord` | id, derivedFromInsightId, shareScope, status, supportCount, contradictionCount, benchmarkStrength, liveStrength |
| `EvolutionPathRecord` | id, scope (workspace/specialization/network), status (open/expired/resolved), assignedAgentId |
| `UpgradeRecord` | id, derivedFromMasteryId, targetRepoId, changeKind, riskLevel, status |
| `UpgradeDeliveryRecord` | id, upgradeId, evolutionMode, deliveryMode, status, prUrl, mergeState, checksState |
| `ContradictionRecord` | id, targetType, targetId, severity, summary |
| `OutcomeRecord` | id, targetType, targetId, evidenceLane, verdict, metricName, metricValue |

**Key payload interface:**

`SparkResearcherCollectiveSyncPayload` (line 463) is the bridge between spark-researcher and spark-swarm, containing all intelligence records emitted by a single run.

### 2.3 API Layer

**Key file:** `spark-swarm/apps/api/src/index.ts`

The API is a Hono-based HTTP server with Supabase for persistence:

| Route | Purpose |
|-------|---------|
| `/health` | Health check |
| `/api/.../collective/sync` | Receive collective payloads from spark-researcher |
| `/api/.../activity` | Activity feed |
| `/api/.../repos` | Repo management |
| `/api/.../graphs` | Graph projections |
| `/api/.../live` | Live session projections |
| `/api/.../runtime` | Runtime pulse |
| `/api/.../observatory` | Dashboard overview |
| `/api/.../auth` | GitHub OAuth, session management |
| `/api/.../repo-verifications` | Repo verification state |
| `/api/.../session` | Session management |

All routes requiring workspace access use Supabase service role key for data persistence and GitHub App credentials for repo verification.

### 2.4 Collective Service

**Key file:** `spark-swarm/apps/api/src/collective/service.ts` (~753 lines)

`createCollectiveService()` (line 273) provides the core intelligence operations:

**`syncCollective()`** -- Persists the entire collective sync payload from spark-researcher:
```typescript
async syncCollective(accessToken, workspaceId, payload) {
  await requireWorkspace(authClient, repository, accessToken, workspaceId)
  await repository.persistCollectiveSync(workspaceId, payload)
  return { accepted: true, workspaceId, recordedAt: nowIso() }
}
```

**`absorbInsight()`** -- Promotes an insight to mastery:
1. Loads insight and parent specialization
2. Creates a `MasteryRecord` with derived share scope and evidence strengths
3. Creates a `MasteryReviewRecord` with approve decision
4. Updates insight status to "distilled"
5. Saves both records

**`reviewMastery()`** -- Applies a review decision to a mastery:
- `approve` -> status becomes `shared_mastery`
- `reject` -> status becomes `retired`
- `defer` -> status unchanged (remains `provisional_mastery`)

**`setEvolutionMode()`** -- Updates a specialization's evolution mode, governing how upgrades are delivered.

**`deliverUpgrade()`** -- Creates an upgrade delivery based on the evolution mode:

```typescript
// service.ts line 141-176 -- deriveDeliveryPlan
function deriveDeliveryPlan(evolutionMode: EvolutionMode) {
  switch (evolutionMode) {
    case "observe_only":
      return { deliveryMode: "recommendation", deliveryStatus: "recommendation_only", ... }
    case "checked_auto_merge":
      return { deliveryMode: "auto_merge", deliveryStatus: "awaiting_checks", ... }
    case "trusted_auto_apply":
      return { deliveryMode: "auto_apply", deliveryStatus: "applied", ... }
    default: // review_required
      return { deliveryMode: "pull_request", deliveryStatus: "awaiting_review", ... }
  }
}
```

**`syncUpgradeDeliveryStatus()`** -- Syncs delivery status with GitHub PR state (merged, closed, checks passing/failing).

### 2.5 Intelligence Derivation

**Key file:** `spark-swarm/apps/api/src/collective/derive.ts`

**`deriveCollectiveIntelligencePulse()`** (line 244) -- Produces a real-time intelligence summary:
- Finds the active evolution path (open status, or most recently updated)
- Identifies the newest insight and strongest mastery
- Recommends the next absorb target (supported insight not blocked by negative outcomes)
- Recommends the next upgrade (actionable status: draft/queued/opened/awaiting_review)
- Counts pending contradictions and upgrades
- Derives evidence from outcomes, masteries, and insights

Evidence strength ranking:

```typescript
// derive.ts line 72-79
function supportRankForMastery(mastery: MasteryRecord) {
  return (
    (mastery.liveStrength ?? 0) * 3 +
    (mastery.benchmarkStrength ?? 0) * 2 +
    mastery.supportCount -
    mastery.contradictionCount * 2
  )
}
```

**`buildEvolutionInbox()`** -- Constructs a prioritized action queue:

| Item Kind | Source | Priority Logic |
|-----------|--------|----------------|
| `absorb` | Supported insights | live_supported = high, benchmark_supported = medium |
| `review_mastery` | Provisional masteries | supportCount > 1 = high, else medium |
| `resolve_contradiction` | Active contradictions | critical = high, warn = medium, info = low |
| `review_upgrade` | Actionable upgrades | high risk = high, else medium |

**`deriveCollectiveGraphProjection()`** -- Builds a graph visualization with:
- Node kinds: agent, specialization, repo, run, evolution_path, insight, mastery, upgrade, contradiction, outcome
- Edge kinds: attached, lineage, specializes_in, advances, produced, absorbed, blocked_by, proposed, delivered_to, validated_by

### 2.6 Bridge Layer

**Key files:**
- `spark-swarm/apps/bridge/src/spark_swarm_bridge/state.py`
- `spark-swarm/apps/bridge/src/spark_swarm_bridge/collective.py`
- `spark-swarm/apps/bridge/src/spark_swarm_bridge/manifest.py`

The bridge is a Python CLI for local operations:

**State management** (`state.py`):
- Stores bridge state in `~/.spark-swarm/bridge-state.json`
- Fields: `agent_name`, `repo_name`, `repo_path`, `workspace_id`, `api_url`, `onboarding_url`, `last_handoff_url`

**Collective sync** (`collective.py`):
- `post_collective_sync()` sends HTTP POST to `/api/workspaces/{id}/collective/sync` with bearer token auth
- URL resolution chain: explicit param -> bridge state -> `SPARK_SWARM_API_URL` env -> `SPARKSWARM_API_URL` env -> `http://127.0.0.1:8787`
- Access token from: explicit param -> `SPARK_SWARM_ACCESS_TOKEN` env -> `SPARKSWARM_ACCESS_TOKEN` env

**Manifest generation** (`manifest.py`):
- Creates `AUTORESEARCH.md` files declaring the one-agent-per-workspace model:
```yaml
agent:
  name: {agent_name}
  model: one-agent-per-workspace
repo:
  name: {repo_name}
  role: attached-specialization
runtime:
  core: spark-researcher
  chip: none
```

### 2.7 Workspace and Agent Model

The spark-swarm model is:
- **One agent per workspace** -- a workspace is an organizational unit
- **Many repos per agent** -- an agent can be attached to multiple repos, each as an "attached-specialization"
- **Specializations** -- each repo attachment can have its own specialization with memory policy and evolution mode
- **Memory policies**: `isolated` (no sharing), `selective` (controlled sharing), `shared` (open sharing)

---

## 3. Recursive Loop Mechanics

### 3.1 The Core Recursive Cycle

The system implements a multi-level recursive improvement loop:

```
LEVEL 1 -- Inner Loop (spark-researcher, single run):
  config -> mutations -> run -> score -> verdict -> ledger

LEVEL 2 -- Suggestion Loop (spark-researcher, multi-round):
  ledger history -> analyze -> suggest new trials -> run trials -> repeat

LEVEL 3 -- Belief Loop (spark-researcher, cross-run):
  ledger evidence -> promote to beliefs -> feed beliefs into advisories
    -> advisories guide frontier suggestions -> new trials -> new evidence

LEVEL 4 -- Collective Loop (spark-researcher -> spark-swarm -> spark-researcher):
  local evidence -> collective payload -> swarm API -> intelligence pulse
    -> evolution inbox -> absorb/review/deliver -> cross-repo transfer
    -> absorbed knowledge -> new beliefs in target repo -> new experiments

LEVEL 5 -- Self-Edit Loop (spark-researcher, code modification):
  advisory evidence -> self-edit proposal -> review gate -> apply if approved
    -> new experiment with modified code -> new evidence
```

### 3.2 Feedback Timescales

| Loop Level | Timescale | Trigger |
|------------|-----------|---------|
| Level 1 (single run) | Seconds to minutes | Each `run_once()` call |
| Level 2 (autoloop) | Minutes to hours | `run_autoloop()` rounds |
| Level 3 (belief) | Hours to days | `build_beliefs()` after accumulated runs |
| Level 4 (collective) | Days to weeks | Collective sync + human/auto review |
| Level 5 (self-edit) | Days to weeks | Human-in-the-loop review gate |

### 3.3 Bottlenecks and Failure Modes

**Bottleneck 1: Discard spiral**
When the `consecutive_discard_limit` (default 3) is repeatedly hit, the system stops exploring. This is a safety feature but can cause premature convergence if the initial search space is poorly defined.

**Bottleneck 2: Human review gates**
In `review_required` evolution mode, all upgrades wait for human approval. The evolution inbox accumulates items but nothing progresses without human intervention.

**Bottleneck 3: Evidence lane narrowness**
Only two evidence lanes are actively used in practice:
- `benchmark_evidence` (from chip-evaluate with benchmark_grounded comparison class)
- `live_evidence` (everything else)

The `source_evidence` lane exists in the type system but is not generated by the current collective payload builder.

**Bottleneck 4: Belief promotion threshold**
Durable beliefs require 2+ replicated improvements. For expensive experiments (long training runs), reaching this threshold is slow. Provisional beliefs are weaker signals that may not trigger mastery promotion.

**Bottleneck 5: Absorb latency**
Cross-repo transfer via `absorb()` requires:
1. Source repo publishes a capsule
2. Human or system reviews the capsule
3. Draft PR is created in target repo
4. PR is reviewed and merged
5. Target repo rebuilds beliefs with absorbed knowledge

Each step introduces latency and potential abandonment.

**Failure Mode 1: Contradiction deadlock**
If two beliefs contradict, both are demoted to provisional. If the system cannot resolve which is correct (e.g., context-dependent truths), the contradictions persist and block promotion indefinitely.

**Failure Mode 2: Metric gaming**
The fixed-evaluator model (config declares metric) means the system optimizes exactly what is measured. If the metric does not capture true quality, the system can find parameter configurations that score well but do not represent genuine improvements.

**Failure Mode 3: Frontier suggestion quality**
LLM-generated frontier suggestions (from `frontier.py`) are bounded by `allowed_mutations` grammar but may still propose low-quality mutations. Without chip domain knowledge, the system falls back to less informed suggestions.

### 3.4 Ideal Loop Design

Based on the architecture analysis, the ideal recursive loop would:

1. **Start with domain chip** -- provides evaluate, suggest, packets, watchtower hooks that ground all decisions in domain expertise
2. **Run benchmark-grounded experiments first** -- generates `benchmark_evidence` which has higher confidence (0.8 vs 0.65 for live_evidence) and automatically creates mastery candidates
3. **Use autoloop for breadth, then continuous autoloop for depth** -- autoloop explores the suggestion space; continuous autoloop mines for incremental improvements
4. **Sync memory frequently** -- `sync_memory()` should run after each autoloop round to keep advisory evidence current
5. **Build beliefs after each batch** -- enables the suggestion engine to distinguish durable knowledge from provisional claims
6. **Emit collective payloads continuously** -- each run already does this (line 451 of runner.py), enabling the swarm to track progress in real time
7. **Set evolution mode progressively**: `observe_only` initially -> `review_required` once confident -> `checked_auto_merge` for established domains -> `trusted_auto_apply` only for low-risk, well-tested changes

### 3.5 Swarm-Orchestrated Self-Improvement

The swarm layer enables a form of distributed self-improvement:

```
Agent A (repo X) discovers insight I
  -> Collective sync pushes I to swarm
  -> Intelligence pulse recommends absorbing I
  -> Agent B (repo Y) absorbs I via draft PR
  -> Agent B runs experiments with absorbed knowledge
  -> Agent B confirms/contradicts I with new evidence
  -> Updated evidence flows back to swarm
  -> Strengthened mastery becomes available to Agent C, D, ...
```

The evolution mode governs the autonomy of this cycle:
- `observe_only`: Swarm only records; no action taken
- `review_required`: Swarm recommends actions; human decides
- `checked_auto_merge`: Swarm opens PRs that auto-merge after CI passes
- `trusted_auto_apply`: Swarm directly applies changes without PR

---

## 4. Full Intelligence Pipeline

### 4.1 End-to-End Data Flow

```
RAW DATA (experiment execution)
  |
  v
METRICS (parsed from log output via regex patterns)
  |
  v
VERDICT (improved/regressed/flat/baseline/near_best/unknown)
  |
  v
LEDGER RECORD (immutable JSONL append)
  |
  +---> BELIEFS (promoted from replicated improvements)
  |       |
  |       +---> ADVISORY (evidence-backed briefs with epistemic status)
  |       |       |
  |       |       +---> FRONTIER SUGGESTIONS (LLM-bounded proposals)
  |       |       +---> RESEARCH (web search when evidence insufficient)
  |       |       +---> VERIFIER (A/B draft comparison with critique)
  |       |
  |       +---> MEMORY DOCUMENTS (tiered, prioritized, searchable)
  |
  +---> CHIP INTEGRATION
  |       |
  |       +---> EVALUATE (domain-specific scoring)
  |       +---> SUGGEST (domain-informed trial proposals)
  |       +---> PACKETS (domain knowledge documents)
  |       +---> WATCHTOWER (monitoring pages)
  |
  +---> COLLECTIVE PAYLOAD (per-run emission)
          |
          v
        SPARK-SWARM API (Hono + Supabase persistence)
          |
          +---> INTELLIGENCE PULSE (real-time summary)
          +---> EVOLUTION INBOX (prioritized action queue)
          +---> GRAPH PROJECTIONS (visual intelligence map)
          |
          +---> ABSORB FLOW
          |       |
          |       +---> Insight -> Mastery promotion
          |       +---> Mastery -> Upgrade derivation
          |       +---> Upgrade -> Delivery (mode-dependent)
          |       +---> Delivery -> Cross-repo PR
          |
          +---> OUTCOME TRACKING
                  |
                  +---> Verdict classification
                  +---> Evidence strength derivation
                  +---> Contradiction detection
                  +---> Rollback triggering
```

### 4.2 Evidence Quality Ladder

Evidence quality increases as it moves through the pipeline:

```
Tier 1: RAW
  raw_run (priority 10)          -- Single run result
  raw_outcome (priority 12)      -- Aggregated outcome

Tier 2: CONTEXTUAL
  state_snapshot (priority 15)   -- Working/episode memory
  exploratory_frontier (8)       -- Frontier suggestions (lowest priority)

Tier 3: GROUNDED
  belief (priority 20)           -- Promoted from evidence
  benchmark_evidence (22)        -- Chip benchmark results
  grounded_boundary (26)         -- Known limits
  research_grounded (28)         -- Web research backed
  grounded_doctrine (30)         -- Strongest: established principles

Tier 4: COLLECTIVE
  Insight (captured -> distilled -> benchmark_supported -> live_supported)
  Mastery (provisional -> shared -> potentially quarantined/retired)
  Upgrade (draft -> queued -> opened -> merged OR rejected OR rolled_back)
```

Evidence lanes in the collective:
- `source_evidence`: From source code analysis
- `benchmark_evidence`: From chip-evaluate with benchmark_grounded comparison class
- `live_evidence`: From production or live experiment runs

Evidence support levels:
- `weak`: Single observation, no replication
- `moderate`: Replicated or benchmark-backed
- `strong`: Live-confirmed or multiple benchmark replications

### 4.3 Cross-Repository Knowledge Transfer

The transfer mechanism operates through two channels:

**Channel 1: Capsule publishing** (`collective.py`, `publish_latest()`)
- Creates `.md` and `.manifest.json` files in `.autoresearch/capsules/`
- Capsules are portable, self-contained knowledge units
- Can be absorbed by other repos via `absorb()` which creates draft PRs

**Channel 2: Collective sync** (`collective.py`, `build_spark_swarm_collective_payload()`)
- Real-time emission of intelligence records after each run
- Bridge posts payload to swarm API
- Swarm persists, derives intelligence, and presents actions via evolution inbox

The swarm's `SharedMasteryFeed` interface enables cross-workspace discovery:
```typescript
// contracts/src/index.ts line 436-446
export interface SharedMasteryFeedItem {
  mastery: MasteryRecord
  sourceSpecializationId: string | null
  compatibleSpecializationIds: string[]
  recommendedAbsorb: boolean
  evidence: EvidenceStrengthSummary[]
}
```

### 4.4 Pipeline Diagram (Text Form)

```
+-------------------+     +------------------+     +-------------------+
|                   |     |                  |     |                   |
|  PROJECT CONFIG   |---->|  RUNNER          |---->|  JSONL LEDGER     |
|  (commands,       |     |  (run_once)      |     |  (immutable       |
|   metrics,        |     |  - copy project  |     |   append-only)    |
|   trials,         |     |  - apply mutns   |     |                   |
|   guardrails)     |     |  - execute cmd   |     +--------+----------+
|                   |     |  - parse metrics |              |
+-------------------+     |  - compute verdt |              |
        ^                 +------------------+              |
        |                                                   |
        |  +------------------------------------------------+
        |  |                    |                    |
        |  v                   v                    v
        |  +-------------+  +-------------+  +------------------+
        |  |  BELIEFS    |  |  MEMORY     |  |  COLLECTIVE      |
        |  |  - durable  |  |  - tiered   |  |  PAYLOAD         |
        |  |  - provisnl |  |  - scored   |  |  - insights      |
        |  |  - contradn |  |  - indexed  |  |  - masteries     |
        |  +------+------+  +------+------+  |  - contradicts   |
        |         |                |          |  - outcomes      |
        |         v                v          +--------+---------+
        |  +---------------------------+              |
        |  |  ADVISORY                 |              |
        |  |  - packet search          |              v
        |  |  - epistemic status       |     +------------------+
        |  |  - failure priorities     |     |  BRIDGE          |
        |  +-----------+---------------+     |  (HTTP POST to   |
        |              |                     |   swarm API)     |
        |              v                     +--------+---------+
        |  +---------------------------+              |
        |  |  SUGGESTION ENGINE        |              v
        |  |  - failure-guided         |     +------------------+
        |  |  - neighborhood           |     |  SPARK-SWARM     |
        |  |  - combination            |     |  API             |
        |  |  - chip suggest           |     |  - persist sync  |
        |  |  - frontier (LLM)         |     |  - derive pulse  |
        |  +-----------+---------------+     |  - build inbox   |
        |              |                     |  - graph project |
        +<-------------+                     +--------+---------+
       (new trials)                                   |
                                                      v
                                             +------------------+
                                             |  EVOLUTION       |
                                             |  ACTIONS         |
                                             |  - absorb        |
                                             |  - review mastery|
                                             |  - deliver upgrd |
                                             |  - resolve contr |
                                             +------------------+
                                                      |
                                                      v
                                             +------------------+
                                             |  CROSS-REPO      |
                                             |  TRANSFER        |
                                             |  - capsule PRs   |
                                             |  - absorbed      |
                                             |    knowledge     |
                                             +--------+---------+
                                                      |
                                                      v
                                             (feeds back into
                                              target repo's
                                              beliefs and
                                              experiments)
```

```
+-------------------------------------------------------------------+
|                     DOMAIN CHIP INTEGRATION                        |
|                                                                    |
|   +----------+    +----------+    +----------+    +------------+   |
|   | evaluate |    | suggest  |    | packets  |    | watchtower |   |
|   | (score   |    | (domain  |    | (emit    |    | (Obsidian  |   |
|   |  runs)   |    |  trials) |    |  docs)   |    |  pages)    |   |
|   +----+-----+    +----+-----+    +----+-----+    +-----+------+   |
|        |               |               |                |          |
|        v               v               v                v          |
|   chip-evaluate    suggestion      memory sync      monitoring     |
|   command kind     phase           phase            on demand      |
+-------------------------------------------------------------------+
```

---

## 5. Effective vs. Ineffective Loops

### Effective Research Loops

| Pattern | Why Effective |
|---------|---------------|
| Chip-evaluate with benchmark_grounded | Highest evidence confidence (0.8), auto-creates mastery candidates, uses domain rubric |
| Failure-guided suggestions after regressions | Directly addresses what went wrong; isolates failing components |
| Belief-informed frontier suggestions | LLM proposals are grounded in what has already been proven to work |
| Continuous autoloop with productive/unproductive pauses | Self-regulating pace: fast when finding improvements, slow when stuck |
| Advisory with epistemic status check | Prevents acting on under_supported evidence; ensures grounded decisions |

### Ineffective Research Loops

| Pattern | Why Ineffective |
|---------|-----------------|
| Autoloop without chip domain knowledge | Falls back to generic frontier suggestions; no domain scoring |
| Running without beliefs first | Advisory has no evidence to ground suggestions; epistemic status is `under_supported` |
| Single-run provisional beliefs driving upgrades | Unreplicated evidence may not generalize; upgrades based on noise |
| observe_only evolution mode with no review | Intelligence accumulates but nothing is ever acted upon |
| Absorb without validation runs in target | Knowledge transfer assumed correct without empirical confirmation |
| Self-edit without sufficient belief grounding | Code changes based on weak evidence risk introducing regressions |

---

## 6. Key Findings and Observations

### Architecture Strengths

1. **Immutable ledger**: The JSONL append-only log ensures no evidence is ever lost or silently modified. Every decision can be traced back to specific run records.

2. **Epistemic honesty**: The system explicitly tracks belief status (durable vs. provisional), contradiction state, and evidence strength. It does not pretend to know more than it does.

3. **Graduated autonomy**: The evolution mode spectrum (observe -> review -> checked_auto -> trusted_auto) allows progressive trust as the system proves itself.

4. **Workspace isolation**: Each run operates on a copy of the project tree, preventing experiments from corrupting the source.

5. **Domain chip extensibility**: The 4-hook chip interface allows domain experts to inject scoring, suggestions, knowledge, and monitoring without modifying core spark-researcher code.

6. **Evidence-first upgrades**: Upgrades must derive from masteries, which derive from insights, which derive from experimental evidence. There is no shortcut.

### Architecture Risks

1. **Single-metric fixation**: The `eval_metric` + `eval_goal` model optimizes one number. Real quality is multi-dimensional. Chip evaluate hooks mitigate this somewhat.

2. **Temporal coherence gap**: The collective payload is a snapshot per run, not a stream. If runs happen faster than sync, the swarm's view may lag.

3. **Contradiction resolution is manual**: The system detects contradictions but has no automated resolution mechanism. Human or future AI intervention is required.

4. **Memory priority system is static**: Tier priorities (e.g., `grounded_doctrine=30`) are hardcoded. Different domains might need different priority weightings.

5. **Bridge is a single point of failure**: The Python bridge CLI is the only path from spark-researcher to spark-swarm. If it fails silently, intelligence is lost.

6. **No rollback automation for trusted_auto_apply**: In the highest autonomy mode, the system applies changes and marks them as merged immediately (line 159-166 of service.ts). If something goes wrong, there is no automatic rollback -- only manual `rolled_back` status updates.

### Overall Assessment

spark-researcher and spark-swarm together form a sophisticated recursive intelligence system. spark-researcher handles the experimental loop with careful evidence gathering, belief promotion, and safety guardrails. spark-swarm aggregates intelligence across workspaces, derives actionable recommendations, and enables cross-repository knowledge transfer.

The recursive loop is most effective when grounded by domain chips (providing evaluate, suggest, and packets hooks), when beliefs are built from replicated evidence, and when the evolution mode matches the system's maturity. The main bottlenecks are human review gates, contradiction resolution, and the inherent latency of cross-repo transfer via PRs.

The system is designed for *cautious progress* -- it would rather stop (discard limit) or flag uncertainty (provisional beliefs, contradictions) than proceed with weak evidence. This conservative posture is appropriate for a system that can modify its own code and propagate knowledge across repositories.
