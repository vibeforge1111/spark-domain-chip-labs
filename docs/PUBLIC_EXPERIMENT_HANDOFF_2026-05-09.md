# Spark Domain Chip Labs Public Experiment Handoff - 2026-05-09

## Status

Spark Domain Chip Labs can be treated as a public local-experiment repo for
creator-system work.

This handoff opens the repo for people and agents to experiment with:

- domain chip standards
- benchmark pack standards
- specialization path manifests
- autoloop policies
- local Spark Swarm review packets
- creator-system smoke and doctor gates

It does not open automatic network publication. Generated systems remain private
until review gates pass and a human/operator explicitly approves a contribution.

## Public Boundary

Safe to expose:

- `README.md`
- `LICENSE`
- `pyproject.toml`
- `src/chip_labs/**`
- `tests/**`
- `docs/creator_system/**`
- `docs/CHIP_INTELLIGENCE_QUICKSTART.md`
- `docs/LAB_*.md`
- template and schema examples under `docs/creator_system/`

Keep private or review before sharing:

- generated local runs
- `.spark-swarm/` folders
- local operator notes that include customer, repo, token, or provider details
- any output file produced from a live private workspace
- any benchmark evidence containing private source text

## Secret Scan

The public-facing repo surfaces were scanned on 2026-05-09 for common secret
patterns:

- OpenAI-style API tokens
- Spark Swarm CLI tokens
- GitHub personal access tokens
- AWS access keys
- private key headers
- obvious bearer/access/refresh token strings

No raw credential was found in the intended public source, docs, tests, README,
PROJECT, pyproject, or LICENSE surfaces. Some docs mention access-token flows as
historical product friction; those are conceptual references, not secrets.

## Fresh Clone Commands

```bash
git clone https://github.com/vibeforge1111/spark-domain-chip-labs.git
cd spark-domain-chip-labs
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .
chip-labs creator-run-template-check --fail-on-blocked
chip-labs creator-system-beta-check --fail-on-blocked
```

Expected result:

- template check passes
- beta check passes
- `network_absorbable` remains false
- network/publication claims remain blocked unless explicit review gates pass

## What People Can Try Tomorrow

Start with a local creator run:

```bash
chip-labs creator-run-init \
  --output-dir runs/qa-operator-demo \
  --domain "QA Operator" \
  --goal "Create a Spark QA specialist that tests Telegram, Workspace sync, creator missions, and readable reports" \
  --source-channel local

chip-labs creator-run-smoke runs/qa-operator-demo
chip-labs creator-run-doctor runs/qa-operator-demo
```

Then compare the generated artifacts with:

- `docs/creator_system/USER_QUICKSTART_BETA.md`
- `docs/creator_system/CREATOR_RUN_GOLDEN_PATH_V1.md`
- `docs/creator_system/BENCHMARK_AND_AUTOLOOP_PROTOCOL.md`
- `docs/creator_system/PROMOTION_GATES_AND_EVIDENCE_TIERS.md`

## Tomorrow Priorities

1. Run a fresh clone beta check from a clean machine or temp directory.
2. Create one public-safe demo creator run, preferably `Spark QA Operator`.
3. Confirm generated output stays local/private by default.
4. Connect the generated benchmark pack to Spark Swarm only after the local
   smoke/doctor gates pass.
5. Keep Telegram phrasing natural: "create a QA Operator specialization path"
   should be the golden user flow, not a long slash-command flow.

## Rollback

If public publication feels unsafe, revert the README license boundary and keep
the repo internal until the fresh clone, secret scan, and generated-run privacy
checks pass again.
