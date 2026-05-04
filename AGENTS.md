# AGENTS.md -- Self-Edit Agent Contract

## Scope

External agents working on this repo must follow these rules.

## Creator-System Fresh Agent Path

When working on Spark creator systems, domain chips, benchmark packs,
specialization paths, autoloop policies, creator-run reports, local Swarm
packets, mission status, or release evidence, start here:

1. Read `docs/creator_system/CREATOR_SYSTEM_USER_AND_AGENT_ONBOARDING.md`.
2. Read `docs/creator_system/AGENT_CREATOR_PLAYBOOK.md`.
3. Read `docs/creator_system/USER_QUICKSTART_BETA.md`.
4. Run `git status --short` before edits.
5. Verify the local creator-system contract before stronger claims:

   ```bash
   python -m chip_labs.cli creator-run-template-check --fail-on-blocked
   python -m chip_labs.cli creator-system-beta-check --fail-on-blocked
   python -m chip_labs.cli creator-system-production-readiness --fail-on-blocked
   ```

Treat `ready_for_swarm_packet` as local artifact readiness only.
Do not claim `network_absorbable`, publish to Spark Swarm, or wire Builder,
Telegram, Spawner, Canvas, or Kanban runtime creator controls from this repo
unless the separate promotion bundle and product-runtime reviews explicitly
approve that stronger release.

## Allowed Actions

1. Edit files only within `mutable_targets` defined in `spark-researcher.project.json`:
   - `src/chip_labs/`
   - `docs/`
   - `research/`
   - `README.md`
   - `spark-chip.json`

2. Work only in the copied workspace provided by spark-researcher's self-edit flow.

3. Leave transparent artifacts: every edit must produce a diff + log + request packet.

## Prohibited Actions

1. **Never** silently modify production code outside the workspace copy.
2. **Never** modify spark-researcher core or spark-swarm contracts.
3. **Never** modify other domain chip repos without explicit owner consent.
4. **Never** auto-graduate a chip prototype without human review.
5. **Never** suppress contradictions or override evidence lane separation.
6. **Never** run destructive commands (shutdown, format, rm -rf, del /f).

## Agent Workstream Roles

Agents operating within the lab may work on any of these research workstreams:

| Workstream | Focus | Constraint |
|------------|-------|-----------|
| Frontier Scout | New domain discovery | Must provide evidence links |
| Methodology Researcher | Chip-building methodology | Changes must be benchmark-tested |
| Chip Architect | New chip manifest design | Must follow spark-chip.v1 contract |
| Benchmark Engineer | Quality benchmarks | Must use fixed evaluator pattern |
| Integration Specialist | spark-researcher/swarm compat | Must validate against contracts |
| Growth Analyst | Ecosystem adoption | Must ground claims in data |
| AGI Theorist | Recursive self-improvement | Must cite sources, no speculation without evidence |

## Self-Edit Flow

1. Agent receives workspace copy from spark-researcher
2. Agent edits only files in mutable_targets within the copy
3. Agent saves diff + logs + request packet
4. Human reviews the proposal
5. If approved, changes are copied back to the repo
6. If rejected, the workspace copy is discarded

## Guardrails

- `max_loop_iterations`: 8
- `consecutive_discard_limit`: 3
- `require_human_approval_for_self_edit`: true
- `require_clean_git_for_self_edit`: true
