# Startup YC External Recompute Adapters

Date: 2026-05-02

This document defines the external recompute adapter boundary between the
curated Startup YC creator-run fixture and a full fresh rerun of its external
evidence.

## Purpose

The Startup YC fixture currently passes strict saved-evidence smoke as
`ready_for_swarm_packet` with evidence tier `transfer_supported`. That is real
contract evidence, but it is not the same as rerunning Startup Bench,
specialization-path absorption, broad transfer, and Swarm packet generation from
their source repositories.

Full external recompute means Spark can rerun the source evidence, regenerate
the summary artifacts, and prove the regenerated values match the creator-run
fixture within explicit tolerances.

## Current Boundary

Supported today:

- Strict saved-evidence validation for
  `docs/creator_system/examples/startup-yc-creator-run`.
- Recompute for generated creator runs with `creator_generator_v1` provenance.
- Recompute for artifact-quality benchmark reports with `artifact_quality_v1`
  provenance.
- External recompute for Startup YC transfer summaries when the
  `specialization-path-startup-yc` selector report is available next to this
  repo.
- External recompute for Startup YC absorption summaries when the
  `specialization-path-startup-yc` absorption proof report is available next to
  this repo.
- External recompute for Startup YC broad-transfer probes when the
  `specialization-path-startup-yc` selector report is available next to this
  repo.
- Swarm packet comparison checks that compare packet evidence,
  transfer fields, report paths, and network-publication governance against the
  recomputed report bundle.
- `startup_yc_external_v1` report provenance checks for baseline, candidate,
  and absorption reports.
- `startup-yc-external-provenance-packet`, which emits a standalone
  recompute provenance packet with linked smoke status, external source hashes,
  and visible blockers for missing, stale, or unpinned source inputs.

Not supported yet:

- Passing recompute when the sibling external source repo is unavailable or the
  source report hash changed.
- Claiming `network_absorbable`.

## Adapter Matrix

| Adapter | Source Evidence | Required Fresh Output | Fixture Values Checked |
| --- | --- | --- | --- |
| Startup Bench transfer adapter | `specialization-path-startup-yc/reports/startup-yc-fresh-validation-suite-v2/adapter_selector_report.json` | `reports/transfer_summary.json` plus scenario rows | implemented for scenario count, baseline score, transfer score, mean delta, min delta, max delta, and constraints |
| Specialization-path absorption adapter | `specialization-path-startup-yc/reports/absorption-proof-2026-04-30/proof_report.json` | `reports/baseline.json`, `reports/candidate.json`, `reports/absorption_summary.json` | implemented for baseline mean/pass rate/case count, candidate mean/delta/pass rate/case buckets, absorption delta, trap count, and mode integrity |
| Broad transfer adapter | `specialization-path-startup-yc/reports/startup-yc-fresh-validation-suite-v2/adapter_selector_report.json` | `reports/broad_transfer_probe.json` with per-scenario rows | implemented for aggregate scores, scenario buckets, constraints, and row-level scenario results |
| Swarm packet regeneration adapter | Fresh baseline, candidate, absorption, and transfer reports | `swarm/contribution_packet.json` | implemented for packet evidence scores/deltas, transfer fields, report paths, and network-publication blocker |
| Report provenance adapter | SHA-256 hash of `specialization-path-startup-yc/reports/absorption-proof-2026-04-30/proof_report.json` | `reports/baseline.json`, `reports/candidate.json`, `reports/absorption_summary.json` provenance | implemented for `startup_yc_external_v1` source and input hash checks |
| Standalone provenance packet | All external source artifacts named by recompute reports | `startup-yc-external-rerun-provenance.schema.json` packet | implemented for linked smoke status, source hashes, unpinned-source blockers, and `network_absorbable=false` |

## Required Output Contract

Each external rerun adapter must emit a small provenance packet next to the
regenerated report. The repo-local aggregate packet uses
`startup-yc-external-rerun-provenance.schema.json` and is emitted with:

```bash
python -m chip_labs.cli startup-yc-external-provenance-packet docs/creator_system/examples/startup-yc-creator-run --output reports/startup-yc-external-provenance.json
```

Future per-adapter packets should keep the same spirit:

```json
{
  "schema_version": "adaptive_creator_loop.external_recompute.v1",
  "adapter_id": "startup_yc_transfer_v1",
  "source_repo": "specialization-path-startup-yc",
  "source_ref": "git sha or reviewed tag",
  "command": "exact command that reran the source evidence",
  "started_at": "ISO-8601 timestamp",
  "completed_at": "ISO-8601 timestamp",
  "inputs": ["paths or manifest ids"],
  "outputs": ["regenerated report paths"],
  "comparison": {
    "fixture_report": "reports/transfer_summary.json",
    "status": "match",
    "tolerance": 0.0001
  }
}
```

The adapter output must be machine-readable first. Markdown readouts are useful
for operators, but they cannot be the only recompute proof.

## Acceptance Gates

Full external recompute is complete only when:

1. Every adapter in the matrix emits the provenance packet above.
2. `creator-run-smoke --recompute --fail-on-blocked` verifies regenerated
   Startup YC report values against the fixture.
3. `creator-run-doctor --recompute` quarantines any stale external report and
   names the exact adapter to rerun.
4. A changed source report fails recompute before any derived Swarm packet can
   be treated as current.
5. The fixture still reports `transfer_supported`, not `network_absorbable`,
   unless the separate publication gates pass.

## Non-Goals

- Do not copy full external benchmark corpora into this methodology repo.
- Do not run product runtime creation from Builder, Telegram, Spawner, Canvas,
  or Kanban in this layer.
- Do not use external recompute as publication approval.
- Do not upgrade Startup YC beyond `transfer_supported` without multi-seed validation,
  human/operator calibration, privacy review, rollback review, and publication
  approval.

## Implementation Order

1. Add a read-only adapter for the Startup Bench transfer report and compare it
   to `reports/transfer_summary.json`. Done for selector-report comparison in
   `creator-run-smoke --recompute`.
2. Add the absorption adapter and compare it to `reports/baseline.json`,
   `reports/candidate.json`, and `reports/absorption_summary.json`. Done for
   proof-report comparison in `creator-run-smoke --recompute`.
3. Add broad-transfer comparison with row-level checks. Done for selector-report
   comparison in `creator-run-smoke --recompute`.
4. Compare the Swarm contribution packet to fresh reports.
   Done for packet/report comparison in `creator-run-smoke --recompute`.
5. Teach `creator-run-smoke --recompute` to select these adapters only when the
   external repos are explicitly available. Done: absent or stale source reports
   block recompute instead of trusting saved evidence.
6. Add provenance packets for baseline, candidate, and absorption reports.
   Done with `startup_yc_external_v1` source hashes.
7. Add doctor quarantine fixtures for stale external Startup YC evidence.
   Done with `doctor-security/stale_external_startup_yc_candidate_score.json`.
8. Add a standalone aggregate provenance packet for external recompute.
   Done with `startup-yc-external-provenance-packet` and
   `startup-yc-external-rerun-provenance.schema.json`.

Remaining work is per-adapter rerun packets from the external source repos plus
the separate multi-seed, calibration, privacy, rollback, and publication
approval gates. Until those pass, the curated Startup YC fixture remains strict
`transfer_supported` proof with clear claim boundaries.
