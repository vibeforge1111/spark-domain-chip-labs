# Spark System Map

This is the public map for where Spark's creator and recursive specialization
systems live. It is written for humans and Spark agents that need to know which
repo owns which part of the system.

## Public Launch Boundary

The public system that people can use today is `spark-domain-chip-labs`.

Do not tell public users to install or download these systems yet:

- `spark-swarm`
- `spawner-ui`
- Spark Telegram runtime control
- private Spark Workspace/runtime services
- unreleased generated specialization-path repos

Those systems are part of the broader Spark architecture, but they are not the
public release path yet. They should be described as connected, private, local,
or upcoming until their own public launch docs are live.

This boundary should not block anyone from using Spark Domain Chip Labs. The
creator-system beta works locally with this repo, Python, and the `chip-labs`
commands.

## Ownership Map

| System area | Primary owner | Public status | What it owns |
| --- | --- | --- | --- |
| Creator standards | `spark-domain-chip-labs` | Public now | Domain chip, benchmark pack, specialization path, autoloop, evidence, and review-packet standards |
| Creator local CLI | `spark-domain-chip-labs` | Public now | `chip-labs` commands for scaffolding, smoke checks, doctor checks, beta checks, and release evidence |
| Domain chip examples | `domain-chip-*` repos | Mixed/local | Actual specialist chips and generated chip workspaces |
| Specialization paths | `specialization-path-*` repos | Mixed/local | Path manifests, path-owned benchmarks, templates, and path guidance |
| Recursive runtime and Workspace | `spark-swarm` | Private for now | Workspace, recursion state, specialization path execution, collective sync, network review boundary |
| Telegram control | `spark-telegram-bot` | Public code, private runtime | Natural-language control, slash commands, recursive reports, creator mission messages |
| Mission execution UI | `spawner-ui` | Private for now | Mission Control, Canvas, Kanban, creator mission planning and execution panels |
| Character and voice | `spark-character` | Public | Spark persona, voice consistency, behavior checks, provider overlays |
| Skill graph standards | `spark-skill-graphs` | Public/workspace dependent | Reusable skill definitions and skill authoring conventions |
| Memory substrate | `domain-chip-memory` | Spark module | Memory quality, recall, source-aware memory lanes, memory contracts |
| Research loop substrate | `spark-researcher` | Spark module | Evidence collection, packets, bounded loops, research-led improvement |

## Creator System Mental Model

`spark-domain-chip-labs` is the "how to create properly" repo. It defines the
shape of good creator output:

- creator intent
- adapter map
- domain chip
- benchmark pack
- specialization path
- autoloop policy
- evidence ladder
- local Spark Swarm review packet
- release evidence

The repo can be used publicly for local experiments. Generated work stays
private by default until review gates pass and a human/operator chooses to share
it.

## Runtime Mental Model

`spark-swarm` is not the public creator standard. It is the upcoming runtime and
Workspace layer that can run and display recursive loops in Spark environments
where it is installed.

Do not route public users to Spark Swarm as a required install path yet. Use
Domain Chip Labs local commands first:

```bash
chip-labs creator-run-template-check --fail-on-blocked
chip-labs creator-system-beta-check --fail-on-blocked
```

When Spark Swarm is available in an operator environment, it can own:

- starting specialization path loops
- recording recursion reports
- syncing local/private evidence into Workspace
- separating private runs from official network paths
- preparing review packets for possible contribution

Do not claim Spark Swarm network publication unless review gates pass and an
authorized operator approves the contribution.

## Telegram Mental Model

Telegram should be the natural-language control layer for installed Spark
environments. It is not required for public Domain Chip Labs usage today.

Good future user phrases:

- "create a QA Operator specialization path"
- "run QA Operator for one round"
- "show the Startup YC recursion report"
- "prepare Crypto Trading for review in Spark Swarm"
- "what blocks sharing this path?"

Public users should still be able to experiment without Telegram by using
`chip-labs` commands in this repo.

## Self-Awareness Rule

When Spark is asked "where is what?" it should answer from this map with source
boundaries:

- public standard available now: `spark-domain-chip-labs`
- private/upcoming runtime layer: `spark-swarm`
- public code but private runtime control: `spark-telegram-bot`
- private/upcoming execution UI: `spawner-ui`
- actual created systems: `domain-chip-*` and `specialization-path-*` repos

Spark should say when a repo is public, private, mixed, local-only, or not
released yet. It should not imply a private runtime repo is downloadable or
required just because the standards repo is public.

## Current Public Entry Point

For outside users and fresh agents, start with:

```bash
git clone https://github.com/vibeforge1111/spark-domain-chip-labs.git
cd spark-domain-chip-labs
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .
chip-labs creator-system-beta-check --fail-on-blocked
```

Then read:

- `docs/creator_system/USER_QUICKSTART_BETA.md`
- `docs/creator_system/CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md`
- `docs/creator_system/PUBLIC_EXPERIMENT_TASKS_2026-05-09.md`
