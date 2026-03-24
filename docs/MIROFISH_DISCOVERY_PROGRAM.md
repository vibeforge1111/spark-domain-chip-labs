# MiroFish Discovery Program

## Purpose

Scale open-ended MiroFish domain discovery without repeating the mistakes from the March 24 rerun cycle.

The rule is:

- discovery scales only after intake quality is proven
- canonicalization stays explicit
- evaluation remains downstream of accepted candidates only
- larger runs need declared pass / fail gates before launch

## What Worked Before

- packet-first discovery intake
- canonicalization with visible accepted / merged / rejected outputs
- hybrid evaluation against benchmark panels instead of treating raw discovery as truth
- explicit stop conditions when runtime or signal quality regressed

## What Did Not Work Before

- broad runs before the surface was trustworthy
- treating thin or zeroed outputs like final truth
- generic boosts instead of narrow hypotheses
- reruns without declared runtime budgets or success criteria

## Staged Scale Plan

### Stage 0: Smoke Pass

Goal:

- prove the multi-agent intake packet shape
- verify duplicate handling, vague rejection, and agent-level rollups

Target:

- `5-10` agents

Pass gate:

- at least `2` clear or proto candidates survive
- duplicate pressure is understandable
- no structural packet problems

### Stage 1: 100-Agent Pilot

Goal:

- test whether the discovery contract holds at meaningful intake volume

Target:

- `100` agents
- `1-3` candidates per agent

Success metrics:

- acceptance rate
- merge rate
- too-vague rate
- persona-only rate
- workflow-only rate
- clear-domain count

Pass gate:

- acceptance rate stays strong enough to justify a bigger pass
- duplicate pressure stays manageable
- at least several clear-domain candidates emerge

### Stage 2: 250-Agent Pilot

Goal:

- test scale effects before the full sweep

Target:

- `250` agents

Success metrics:

- compare all stage-1 metrics against the 100-agent pilot
- check whether cluster diversity improves
- confirm that accepted candidates still survive hybrid evaluation at a useful rate

Pass gate:

- quality does not collapse relative to the 100-agent pilot
- at least one additional high-signal wedge appears

### Stage 3: Full 1,000-Agent Program

Goal:

- generate a large discovery frontier without forcing low-quality acceptance

Target:

- `1,000` agents
- up to `500` canonical candidates after acceptance / merge / rejection

Important constraint:

- the target is not "force 500 accepted chips"
- the target is "run a 1,000-agent intake that yields the best canonical frontier the contract can justify"

## Output Contract

Every program run should emit:

- raw program packet
- canonicalized program packet
- summary metrics
- scale-readiness recommendation
- accepted candidate set for hybrid evaluation

## Repo-Local Commands

Build a `100`-agent pilot scaffold:

```powershell
$env:PYTHONPATH='src'
python -m chip_labs.cli mirofish-discovery-program-scaffold --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SCAFFOLD_2026-03-24.json
```

Split the scaffold into per-cluster collection packets:

```powershell
$env:PYTHONPATH='src'
python -m chip_labs.cli mirofish-discovery-program-split --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_SCAFFOLD_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json
```

Export an operator-facing pilot brief:

```powershell
$env:PYTHONPATH='src'
python -m chip_labs.cli mirofish-discovery-program-brief --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json --title "MiroFish Discovery Pilot 100 Brief" --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_BRIEF_2026-03-24.md
```

Recombine filled cluster packets back into one program packet:

```powershell
$env:PYTHONPATH='src'
python -m chip_labs.cli mirofish-discovery-program-merge --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RECOMBINED_2026-03-24.json
```

Materialize the cluster bundle into per-cluster working files:

```powershell
$env:PYTHONPATH='src'
python -m chip_labs.cli mirofish-discovery-program-materialize --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_PACKETS_2026-03-24.json --output-dir research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24 --index-title "MiroFish Discovery Pilot 100 Clusters" --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_CLUSTER_DIRECTORY_2026-03-24.json
```

Track fill progress on the materialized directory:

```powershell
$env:PYTHONPATH='src'
python -m chip_labs.cli mirofish-discovery-program-progress --input-dir research/meta/mirofish_discovery_pilot_100_clusters_2026-03-24 --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.json --markdown-output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_PROGRESS_2026-03-24.md --title "MiroFish Discovery Pilot 100 Progress"
```

Canonicalize a filled pilot packet:

```powershell
$env:PYTHONPATH='src'
python -m chip_labs.cli mirofish-discovery-program --input research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RECOMBINED_2026-03-24.json --output research/meta/MIROFISH_DISCOVERY_PROGRAM_PILOT_100_RESULT_2026-03-24.json
```

## Governance

- all discovery-program outputs remain `exploratory_frontier`
- no accepted candidate auto-enters the maintained benchmark universe
- scaling decisions must be justified by metrics from the prior stage
