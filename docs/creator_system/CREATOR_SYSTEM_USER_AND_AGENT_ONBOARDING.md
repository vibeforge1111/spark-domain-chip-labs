# Creator System User And Agent Onboarding

This guide is the canonical first-read for people and Spark agents using the
creator-system beta.

It explains how to move from a user's goal to a domain chip, benchmark pack,
specialization path, autoloop policy, local Swarm packet, and honest release
verdict without relying on old chat context or unfinished product surfaces.

## Current Promise

This repo can help a user create local, benchmarked creator systems and prove
whether the artifacts are coherent.

It does not approve network absorption. `network_absorbable` stays `false`
until multi-seed validation, human/operator calibration, privacy review,
rollback review, publication approval, and product runtime review all pass.

## First Five Minutes

Start from a clean mental model:

1. Install and verify the CLI from `USER_QUICKSTART_BETA.md`.
2. Run `git status --short` before editing. Do not overwrite unrelated dirty
   or untracked files.
3. Verify the local contract:

   ```bash
   python -m chip_labs.cli creator-run-template-check --fail-on-blocked
   python -m chip_labs.cli creator-system-beta-check --fail-on-blocked
   python -m chip_labs.cli creator-system-production-readiness --fail-on-blocked
   ```

4. Create or inspect one run with `creator-run-init`, `creator-run-smoke`, and
   `creator-run-doctor`.
5. Claim only the weakest evidence tier supported by the passing gates.

## User Value By System Part

| Part | What The User Gets | What The Agent Must Do | What Proves It |
| --- | --- | --- | --- |
| Creator intent | A shared definition of the domain, goal, constraints, and evidence target. | Convert vague goals into `adaptive_creator_loop.creator_intent.v1`; ask only for missing benchmark-critical facts. | `creator-intent.json` exists and smoke can read it. |
| Adapter map | A safe map from the run to local repos, product surfaces, and future Swarm paths. | Keep Builder, Telegram, Spawner, Canvas, and Kanban read-only in this beta. | `adapter-map.json` preserves local paths and no live product mutation. |
| Domain chip | Domain-specific hooks, doctrine, refusal boundaries, scoring hooks, and routing hints. | Build actual hooks and tests, not a prompt-only wrapper. | Hook smoke passes and `domain-chip/chip.manifest.json` is present. |
| Benchmark pack | A way to tell whether the chip improves a real task. | Write cases, traps, scoring rules, calibration notes, and a baseline report. | `benchmark/manifest.json`, `cases.jsonl`, traps, rubric, and baseline report pass checks. |
| Specialization path | A staged path for an agent to load, practice, receive feedback, and emit packets. | Bind the path to the benchmark and define mastery gates. | `specialization-path/path.manifest.json` and path contract pass smoke. |
| Autoloop policy | A safe recursive improvement loop with keep/revert rules. | Limit mutation surfaces, run one keep and one revert simulation, and record rollback. | `autoloop/policy.json` plus simulation result are present and coherent. |
| Evidence ladder | A plain-language claim boundary. | Tie every claim to the weakest passing gate. | `reports/evidence_ladder.md` states safe and unsafe claims. |
| Reports | Saved proof for baseline, candidate, absorption, transfer, and known gaps. | Keep provenance and source hashes; use `--recompute` where supported. | Normal smoke is coherent; recompute smoke distinguishes saved from rerun evidence. |
| Swarm packet | A local contribution packet other agents can review. | Create it only after evidence supports it; keep `network_publication_allowed=false`. | `swarm/contribution_packet.json` matches reports and rollback policy. |
| Mission status | A product-safe status packet for dashboards and operators. | Summarize readiness without wiring runtime creator controls. | `creator-mission-status` output keeps `publication.network_absorbable=false`. |
| Release evidence | A clean-checkout verdict for sharing the beta. | Run beta, production-readiness, and release-evidence checks before public claims. | `creator-system-release-evidence` passes in a clean checkout or CI. |

## Step-By-Step User Flow

### 1. Name The Job

The user should describe one capability:

```text
Create a creator system that helps agents review design docs and PR writeups.
```

The agent should turn this into:

```bash
python -m chip_labs.cli creator-run-init \
  --output-dir runs/artifact-quality-demo \
  --domain "Artifact Quality" \
  --goal "Review design docs and PR writeups for actionable quality" \
  --source-channel local
```

If the request is broad, narrow the first benchmark before creating many files.
Good first scopes are one task, one tool operation, one content decision, one
doctor failure class, or one founder-advice scenario.

### 2. Fill The Core Templates

Use `docs/creator_system/templates/creator-run/` in this order:

1. `creator-intent.template.json`
2. `adapter-map.template.json`
3. `created-artifact-manifest.template.json`
4. `benchmark-pack.template.md`
5. `specialization-path-contract.template.md`
6. `autoloop-policy.template.json`
7. `evidence-ladder.template.md`
8. `swarm-contribution-packet.template.json`
9. `creator-run-summary.template.md`

The artifact manifest is the user's progress tracker. Keep it updated whenever
an artifact moves from planned to created, validated, or blocked.

### 3. Build The Domain Chip

Create the smallest chip that can improve the target capability:

- `domain-chip/chip.manifest.json`
- doctrine or operating guide
- evaluate hook
- suggest hook
- packets hook
- watchtower or failure-detection hook
- hook smoke result

The agent should explain the chip's boundary in user language:

- what it helps with
- what it refuses
- what benchmark measures it
- what evidence tier it can support today

### 4. Build The Benchmark Pack

Create a benchmark that is harder to game than the mutation surface:

- `benchmark/manifest.json`
- `benchmark/cases.jsonl`
- adversarial or trap cases
- scoring rubric or deterministic scorer
- calibration examples
- baseline report

The benchmark should measure useful behavior, not whether an agent can recite
the doctrine. A content-simulation benchmark should test candidate ranking. A
tool-operation benchmark should test expected postconditions and rollback. A
doctor-security benchmark should test stale evidence and unsafe promotion.

### 5. Build The Specialization Path

Create a path that tells an agent how to load, practice, improve, and emit
evidence:

- path manifest
- path contract
- mastery ladder
- operator guide
- benchmark binding
- mutation boundary
- Swarm boundary

The path should answer four questions:

- How does an agent load this domain?
- How does it practice?
- How does it receive feedback?
- What can it safely share?

### 6. Build The Autoloop Policy

Create an autoloop only after the benchmark exists:

- mutation surface
- forbidden surfaces
- max rounds before review
- keep condition
- revert condition
- stop conditions
- promotion condition

Run one simulation where the candidate is kept and one where it is reverted.
This proves the loop can reject bad mutations instead of only celebrating wins.

### 7. Run Smoke And Doctor Repeatedly

Run smoke after each major artifact group:

```bash
python -m chip_labs.cli creator-run-smoke runs/<run-name>
```

If blocked, run:

```bash
python -m chip_labs.cli creator-run-doctor runs/<run-name>
```

For provenance-sensitive evidence, run:

```bash
python -m chip_labs.cli creator-run-smoke runs/<run-name> --recompute --fail-on-blocked
python -m chip_labs.cli creator-run-doctor runs/<run-name> --recompute
```

Normal smoke checks saved evidence coherence. Recompute smoke proves supported
saved reports still match current source artifacts.

### 8. Prepare The Local Swarm Packet

Create `swarm/contribution_packet.json` only after reports support the claim.
The packet should contain:

- packet kind
- evidence tier
- baseline and candidate scores
- absorption or transfer deltas when available
- source report paths
- provenance hashes
- rollback or deprecation policy
- known limits

In this beta, a Swarm packet is reviewable local evidence. It is not automatic
network absorption.

### 9. Create Product-Safe Status

When a user wants dashboard, Telegram, Builder, Spawner, Canvas, or Kanban
visibility, generate or pass around `creator-mission-status`.

The correct beta behavior is read-only:

- show verdict, evidence tier, blocked checks, warnings, next command, and
  generated-matrix status
- preserve `publication.network_absorbable=false`
- do not add live runtime creator controls
- do not publish to Spark Swarm from product surfaces

### 10. Share Or Release Honestly

Before sharing a result, run:

```bash
python -m chip_labs.cli creator-run-smoke runs/<run-name> --fail-on-blocked --fail-on-warn
python -m chip_labs.cli creator-run-doctor runs/<run-name>
```

Before sharing the repo beta, run:

```bash
python -m chip_labs.cli creator-system-beta-check --fail-on-blocked
python -m chip_labs.cli creator-system-production-readiness --fail-on-blocked
python -m chip_labs.cli creator-system-release-evidence --fail-on-blocked --output /tmp/creator-system-release-evidence.json
```

If release evidence blocks because the local worktree is dirty, use a clean
checkout or CI artifact for the public verdict.

## Spark Agent Operating Contract

When a Spark agent sees these docs, it should act like a careful operator:

1. Load `README.md`, `USER_QUICKSTART_BETA.md`,
   `CREATOR_RUN_GOLDEN_PATH_V1.md`, `AGENT_CREATOR_PLAYBOOK.md`, and this
   onboarding guide.
2. Run `git status --short` before edits.
3. Use `creator-run-init` instead of hand-scaffolding the initial workspace.
4. Build the smallest artifact set that proves the user's target capability.
5. Run smoke and doctor after each meaningful stage.
6. Use benchmark results and evidence tiers as the source of truth.
7. Preserve dirty unrelated files and product-surface boundaries.
8. Report what passed, what is blocked, what the weakest evidence tier is, and
   what command should run next.

The agent should not:

- claim `network_absorbable`
- publish to Spark Swarm automatically
- treat `ready_for_swarm_packet` as network approval
- rewrite benchmark expectations to make a candidate win
- widen autoloop mutation surfaces without review
- turn conversational residue into memory or doctrine
- wire Builder, Telegram, Spawner, Canvas, or Kanban runtime controls from this
  repo-local beta

## Proof-Domain Examples

Use these domains as starter patterns:

| Domain | Best First User Value | Benchmark Shape | Extra Gate |
| --- | --- | --- | --- |
| Artifact quality | Better design docs, PRs, handoffs, and mission packets. | Score actionable clarity, evidence, decisions, risks, and reviewability. | Human review still owns final product judgment. |
| Tool operation | Safer Spark tool use and clearer rollback. | Validate command intent, output, postconditions, secret boundaries, and rollback notes. | No network mutation or publish authority. |
| MiroFish content simulation | Rank titles, posts, hooks, and content ideas before publishing. | Multi-seed simulated audiences compare candidates and explain tradeoffs. | Outcome calibration must block vanity-only claims. |
| Doctor security | Catch fake readiness, stale evidence, unsafe packets, and overclaims. | Adversarial sweep mutates schema families and expects doctor blocks. | Publication stays blocked until external reviews pass. |
| Startup YC founder advice | Improve startup operating judgment and advice quality. | Fresh-agent absorption, held-out founder cases, traps, and transfer probes. | Network absorption still needs full promotion bundle. |
| Retrieval memory | Keep useful memories while blocking stale, contradicted, or residue context. | Memory-lane checks classify source, recency, contradiction, and network-share safety. | No production memory runtime wiring in this beta. |

## Documentation Map

Use the docs by job:

| Job | Read |
| --- | --- |
| Install and first run | `USER_QUICKSTART_BETA.md` |
| Contribute a new creator domain | `CONTRIBUTING_CREATOR_DOMAINS.md` |
| Agent procedure | `AGENT_CREATOR_PLAYBOOK.md` |
| End-to-end CLI flow | `CREATOR_RUN_GOLDEN_PATH_V1.md` |
| Finish the reusable Swarm path | `CREATOR_SYSTEM_SWARM_REUSE_END_TO_END_PLAN.md` |
| Read reusable Swarm execution evidence | `CREATOR_SYSTEM_SWARM_REUSE_EXECUTION_EVIDENCE_2026-05-05.md` |
| Align creator runs with Spark Swarm launch | `CREATOR_SYSTEM_SPARK_SWARM_ALIGNMENT_AND_LAUNCH_TASKS.md` |
| Swarm reuse task ledger | `CREATOR_SYSTEM_SWARM_REUSABILITY_TASKS.md` |
| Package a local Swarm review bundle | `SWARM_REUSABLE_CREATOR_PATH.md` |
| Evidence tier meaning | `PROMOTION_GATES_AND_EVIDENCE_TIERS.md` |
| Benchmark and autoloop design | `BENCHMARK_AND_AUTOLOOP_PROTOCOL.md` |
| Benchmark honesty | `BENCHMARK_GENERATION_HONESTY_STANDARD.md` |
| All schemas | `schemas/README.md` |
| All templates | `templates/creator-run/README.md` |
| Product read-only integration | `PRODUCT_SURFACE_READ_ONLY_ADAPTERS.md` |
| Release readiness | `RELEASE_READINESS_CHECKLIST_BETA.md` |

## Final Answer Shape For Agents

When an agent finishes a creator-system task, it should answer with:

- what artifacts were created or updated
- which commands/tests ran
- the smoke verdict
- the evidence tier
- whether recompute was run or why it was not supported
- what remains blocked
- the exact next command or review needed

The answer should be useful to a user who has not read the repo, while staying
strict enough that another agent can continue the run without old chat context.
