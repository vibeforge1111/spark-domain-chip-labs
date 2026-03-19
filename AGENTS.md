# AGENTS.md -- Self-Edit Agent Contract

## Scope

External agents working on this repo must follow these rules.

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
