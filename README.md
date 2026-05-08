# Spark Domain Chip Labs

Public creator standards for Spark domain chips, benchmark packs, specialization paths, autoloop policies, and review packets.

This repo is the place where Spark learns how to create specialist systems properly. It is not the live Spark Swarm runtime, not a hosted workspace, and not an automatic network-publishing surface.

## What You Can Do Here

- Design a domain chip for a field such as QA, security questionnaires, startup advising, crypto trading, content, or research.
- Create the matching benchmark pack so the chip can be scored instead of only sounding good.
- Define a specialization path that tells Spark how the chip should improve over time.
- Define an autoloop policy with mutation limits, stop conditions, rollback notes, and evidence gates.
- Package local evidence for future review without claiming it is official Spark Swarm doctrine.

The default lane is local and private. Generated runs, workspace payloads, private repo evidence, secrets, transcripts, and unpublished benchmark data stay with the user unless they are intentionally prepared for review.

## Current Public Status

| Surface | Status | Notes |
| --- | --- | --- |
| Creator standards | Public now | Schemas, templates, examples, docs, and local gates. |
| `chip-labs` CLI | Public now | Local creator-run init, smoke, doctor, template, beta, and release checks. |
| Domain chip examples | Mixed | Some are public, local, private, or generated workspaces. Check each repo. |
| Telegram recursive Builder chip loops | Public local path | Runs through the Spark Telegram starter stack without Spark Swarm. |
| Spark Swarm Workspace and network submission | Private/upcoming | Do not require public users to install Spark Swarm yet. |
| Spawner UI creator controls | Private/upcoming | Connected internally, not required for this public beta. |

Network absorption remains blocked by default. A local creator run can become a review candidate only after benchmark proof, privacy review, rollback review, and explicit human/operator approval.

## Creator-System Beta Quickstart

This beta is for local and repo-based creator-run workflows. It does not approve `network_absorbable`, publish to Spark Swarm automatically, or make a generated system official network doctrine.

```bash
git clone https://github.com/vibeforge1111/spark-domain-chip-labs.git
cd spark-domain-chip-labs
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .

chip-labs creator-run-template-check --fail-on-blocked
chip-labs creator-system-beta-check --fail-on-blocked
```

Create a local creator run:

```bash
chip-labs creator-run-init \
  --output-dir runs/qa-operator-demo \
  --domain "QA Operator" \
  --goal "Create a Spark QA specialist that tests Telegram, Workspace sync, creator missions, and readable reports" \
  --source-channel local

chip-labs creator-run-smoke runs/qa-operator-demo
chip-labs creator-run-doctor runs/qa-operator-demo
```

Expected shape:

- Smoke tells you what is present, missing, or blocked.
- Doctor gives the next repair steps.
- Publication/network sharing stays blocked unless review gates pass.

Compatibility links for current agents and CI:

- [docs/creator_system/CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md](docs/creator_system/CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md)
- [docs/creator_system/USER_QUICKSTART_BETA.md](docs/creator_system/USER_QUICKSTART_BETA.md)
- [docs/creator_system/CONTRIBUTING_CREATOR_DOMAINS.md](docs/creator_system/CONTRIBUTING_CREATOR_DOMAINS.md)
- [docs/creator_system/CREATOR_SYSTEM_SWARM_REUSE_END_TO_END_PLAN.md](docs/creator_system/CREATOR_SYSTEM_SWARM_REUSE_END_TO_END_PLAN.md)
- [docs/creator_system/CREATOR_SYSTEM_SPARK_SWARM_ALIGNMENT_AND_LAUNCH_TASKS.md](docs/creator_system/CREATOR_SYSTEM_SPARK_SWARM_ALIGNMENT_AND_LAUNCH_TASKS.md)
- [docs/creator_system/CREATOR_SYSTEM_SPARK_SWARM_PHASED_BUILD_PLAN.md](docs/creator_system/CREATOR_SYSTEM_SPARK_SWARM_PHASED_BUILD_PLAN.md)
- [docs/creator_system/CREATOR_SYSTEM_SWARM_REUSABILITY_TASKS.md](docs/creator_system/CREATOR_SYSTEM_SWARM_REUSABILITY_TASKS.md)
- [docs/creator_system/SWARM_REUSABLE_CREATOR_PATH.md](docs/creator_system/SWARM_REUSABLE_CREATOR_PATH.md)
- [docs/creator_system/RELEASE_READINESS_CHECKLIST_BETA.md](docs/creator_system/RELEASE_READINESS_CHECKLIST_BETA.md)
- [docs/creator_system/PUBLIC_BETA_RELEASE_HANDOFF_2026-05-04.md](docs/creator_system/PUBLIC_BETA_RELEASE_HANDOFF_2026-05-04.md)
- [docs/creator_system/CREATOR_RUN_GOLDEN_PATH_V1.md](docs/creator_system/CREATOR_RUN_GOLDEN_PATH_V1.md)

## What Each Artifact Means

| Artifact | Purpose |
| --- | --- |
| Domain chip | The domain doctrine, examples, traps, hooks, and scoring helpers. |
| Benchmark pack | Cases and rubrics that prove whether the chip actually helps. |
| Specialization path | The improvement lane Spark should follow over multiple runs. |
| Autoloop policy | Mutation limits, stop rules, rollback rules, and evidence gates. |
| Tool integration | Optional adapters that let a chip use product or repo tools safely. |
| Review packet | A local proposal bundle that can be inspected before any network sharing. |

## Where To Start Reading

- [System map](docs/SPARK_SYSTEM_MAP.md)
- [Creator system overview](docs/creator_system/README.md)
- [User quickstart beta](docs/creator_system/USER_QUICKSTART_BETA.md)
- [Agent creator playbook](docs/creator_system/AGENT_CREATOR_PLAYBOOK.md)
- [Golden path](docs/creator_system/CREATOR_RUN_GOLDEN_PATH_V1.md)
- [Benchmark and autoloop protocol](docs/creator_system/BENCHMARK_AND_AUTOLOOP_PROTOCOL.md)
- [Promotion gates and evidence tiers](docs/creator_system/PROMOTION_GATES_AND_EVIDENCE_TIERS.md)
- [Public experiment handoff](docs/PUBLIC_EXPERIMENT_HANDOFF_2026-05-09.md)

## Connected Spark Repos

| Repo | Current role |
| --- | --- |
| `spark-cli` | Public installer and operator CLI for the starter stack. |
| `spark-telegram-bot` | Public Telegram gateway code; live runtime is operator-managed. |
| `spark-intelligence-builder` | Builder runtime and local recursive Builder chip loop owner. |
| `domain-chip-memory` | Starter memory/domain-chip substrate. |
| `spark-character` | Spark voice, persona, overlays, and conversation quality scoring. |
| `spark-personality-chip-labs` | Portable personality chip schemas and experiments. |
| `spark-voice-comms` | Public voice communication chip hooks. |
| `spark-swarm` | Private/upcoming Workspace and collective intelligence runtime. |

Do not confuse `spark-voice-comms` with the older `spark-voice-engine` work. The public voice lab is `spark-voice-comms`.

## CLI Index

| Purpose | Command |
| --- | --- |
| Initialize a creator run | `chip-labs creator-run-init --output-dir runs/<run> --domain "<domain>" --goal "<goal>"` |
| Smoke-check a run | `chip-labs creator-run-smoke runs/<run>` |
| Strict smoke | `chip-labs creator-run-smoke runs/<run> --fail-on-blocked --fail-on-warn` |
| Diagnose repair work | `chip-labs creator-run-doctor runs/<run>` |
| Validate templates | `chip-labs creator-run-template-check --fail-on-blocked` |
| Check beta readiness | `chip-labs creator-system-beta-check --fail-on-blocked` |
| Emit release evidence | `chip-labs creator-system-release-evidence --fail-on-blocked --output /tmp/creator-system-release-evidence.json` |

More commands live in [docs/creator_system/README.md](docs/creator_system/README.md).

## Trust Boundaries

Public and safe to share:

- Source code, schemas, templates, public docs, tests, and example fixtures in this repo.
- Local smoke/doctor results after reviewing them for private paths or source text.
- Review packets that explicitly keep network publication disabled.

Private or review before sharing:

- `.spark-swarm/` folders.
- Generated local runs with private source material.
- Local workspace payloads.
- Provider keys, Telegram tokens, access tokens, refresh tokens, `sscli_...` tokens, cookies, or private key material.
- Benchmark cases copied from private repos or private customer/user content.

Blocked by default:

- `network_absorbable`.
- Automatic Spark Swarm publication.
- Claims that a generated chip/path is official network doctrine.
- Any public claim that skips benchmark proof and review gates.

## Tests

```bash
python -m pytest -q
chip-labs creator-run-template-check --fail-on-blocked
chip-labs creator-system-beta-check --fail-on-blocked
```

## License

AGPL-3.0-only. See [LICENSE](LICENSE).
