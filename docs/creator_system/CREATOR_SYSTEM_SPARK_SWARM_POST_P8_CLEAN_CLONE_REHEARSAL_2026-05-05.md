# Creator System Spark Swarm Post-P8 Clean-Clone Rehearsal 2026-05-05

This records the clean-clone rehearsal after the Spark Swarm launch hardening
checklist landed.

## Verdict

- Rehearsal status: `pass`
- Verified commit: `ece3c55`
- Clone path:
  `C:\Users\USER\AppData\Local\Temp\spark-swarm-clean-rehearsal-20260505154244`
- Evidence path:
  `C:\Users\USER\AppData\Local\Temp\spark-swarm-clean-rehearsal-evidence-20260505154244`
- Clean before: yes
- Clean after: yes
- Network absorption: `network_absorbable=false`
- Automatic publish: no automatic publish

## Commands Run

```powershell
git clone --no-hardlinks C:\Users\USER\Desktop\spark-domain-chip-labs C:\Users\USER\AppData\Local\Temp\spark-swarm-clean-rehearsal-20260505154244
python -m pytest tests/test_creator_system_docs.py tests/test_creator_swarm_lane_taxonomy.py tests/test_creator_network_proposal_bundle.py tests/test_creator_swarm_collective.py tests/test_swarm_review_bundle_privacy.py -q
python -m chip_labs.cli creator-run-smoke docs/creator_system/examples/startup-yc-creator-run --output C:\Users\USER\AppData\Local\Temp\spark-swarm-clean-rehearsal-evidence-20260505154244\startup-yc-smoke.json --fail-on-blocked
python -m chip_labs.cli creator-run-doctor docs/creator_system/examples/startup-yc-creator-run --output C:\Users\USER\AppData\Local\Temp\spark-swarm-clean-rehearsal-evidence-20260505154244\startup-yc-doctor.json
python -m chip_labs.cli creator-swarm-collective-dry-run docs/creator_system/examples/startup-yc-creator-run --workspace-id workspace-private-clean-clone --agent-id agent-clean-clone --output C:\Users\USER\AppData\Local\Temp\spark-swarm-clean-rehearsal-evidence-20260505154244\startup-yc-collective-dry-run.json
```

## Results

Contract tests:

```text
49 passed
```

Smoke:

```json
{
  "schema_version": "adaptive_creator_loop.smoke_result.v1",
  "verdict": "ready_for_swarm_packet",
  "evidence_tier": "transfer_supported"
}
```

Doctor:

```json
{
  "schema_version": "adaptive_creator_loop.doctor_result.v1",
  "verdict": "ready_for_swarm_packet",
  "evidence_tier": "transfer_supported"
}
```

Collective dry-run:

```json
{
  "workspaceId": "workspace-private-clean-clone",
  "agentId": "agent-clean-clone",
  "runtimeState": "idle",
  "stageKey": "ready_for_swarm_packet",
  "artifactRefs": 6,
  "shareScope": "private",
  "reviewDecision": "defer"
}
```

## Clean-Clone Finding

The first clean-clone attempt failed the network proposal artifact-hash test
because Windows checkout line endings changed raw bytes for text artifacts.
The fix in `ece3c55` changed proposal artifact verification to canonical text hashing
and updated the mission-status artifact hash. This makes proposal
artifact refs reproducible across normal text checkouts.

## What This Proves

- The P1-P8 Spark Swarm contracts reproduce from a clean committed clone.
- Startup YC still reaches `ready_for_swarm_packet` with
  `transfer_supported` evidence.
- The dry-run Collective payload remains private, thin, artifact-reference
  based, and review-deferred.
- Review-bundle privacy gates and proposal-bundle blockers are executable.
- `network_absorbable=false` remains the correct state.

## What Remains Blocked

- no automatic Spark Swarm publish
- no network absorption
- no product runtime creator controls
- no hosted Spark Swarm UI consumption proof yet
- no real verified-repo PR proof placeholder through Spark Swarm launch flow
- no signed publication manifest authority
