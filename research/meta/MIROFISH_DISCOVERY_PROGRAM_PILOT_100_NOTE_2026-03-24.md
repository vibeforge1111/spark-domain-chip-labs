# MiroFish Discovery Program Pilot 100 Note: 2026-03-24

## Scope

Create the actual next-stage pilot scaffold after the smoke pass.

This is not a synthetic 100-agent result. It is the structured intake packet for the real `100`-agent pilot.

Artifacts:

- `research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SCAFFOLD_2026-03-24.json`

## What The Scaffold Does

The scaffold allocates `100` agents across the wedges that looked most promising or most decision-relevant after the smoke pass:

1. security / compliance response
2. healthcare revenue cycle
3. HVAC / field maintenance
4. insurance / claims / appeals
5. vendor / procurement ops
6. legal / audit / evidence
7. workplace training / compliance
8. industrial quality / inspection
9. finance / reconciliation / backoffice
10. logistics / last-mile ops

Each agent entry already includes:

- `agent_id`
- `cluster_id`
- cluster-specific focus
- seed domains
- candidate requirements
- empty `raw_candidates` slots for real collection

## Why This Is The Right Next Step

The smoke pass justified moving to the `100`-agent pilot, but not jumping directly to `250` or `1,000`.

That means the next truthful artifact should be:

- a real pilot scaffold ready for collection

not:

- a fake 100-agent result packet filled with invented discoveries

## Next Action

Fill the scaffold with real candidate submissions, then run:

```powershell
$env:PYTHONPATH='src'
python -m chip_labs.cli mirofish-discovery-program --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SCAFFOLD_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.json
```

Only after that should the accepted set go into focused hybrid evaluation.
