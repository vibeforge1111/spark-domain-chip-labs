# MiroFish Discovery Program Pilot 100 Recombine Note: 2026-03-24

## Scope

Complete the pilot intake loop by recombining cluster packets back into one canonicalization-ready program packet.

Artifact:

- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RECOMBINED_2026-03-24.json`

## What Changed

The repo-local discovery flow is now:

1. build the pilot scaffold
2. split the scaffold into cluster packets
3. collect real discoveries inside those cluster packets
4. recombine them into one merged program packet
5. canonicalize that merged program packet with `mirofish-discovery-program`

The recombined packet now preserves:

- `program_id`
- `stage_label`
- `target_agent_count`
- full `cluster_plan`
- `collection_rules`
- all `agent_submissions`

## Validation Note

The first recombine pass exposed a real metadata-loss issue because the older generated cluster bundle did not yet carry the scaffold metadata. The fix was to preserve that metadata in the split packet and tighten the tests so the round-trip keeps it.

## Next Action

Once the cluster packets are filled with real submissions, run:

```powershell
$env:PYTHONPATH='src'
python -m chip_labs.cli mirofish-discovery-program --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RECOMBINED_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.json
```
