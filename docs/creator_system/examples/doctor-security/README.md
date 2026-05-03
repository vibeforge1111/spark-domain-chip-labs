# Doctor Security Fixtures

These fixtures are executable adversarial inputs for `creator-run-doctor`.

- `stale_candidate_report_score.json` mutates a saved candidate report so
  `creator-run-doctor --recompute` must quarantine stale evidence.
- `stale_external_startup_yc_candidate_score.json` mutates a Startup YC report
  backed by an external proof source so the doctor must quarantine stale
  external recompute evidence.
- `malicious_network_absorption_packet.json` mutates a contribution packet so
  candidate-review evidence tries to masquerade as `network_absorbable`.
- `adversarial_schema_sweep.json` runs isolated mutations across adapter-map,
  candidate-report, absorption-summary, Swarm-packet, and evidence-ladder
  schema families. Each row must make `creator-run-doctor` block with the
  expected checks and calibrated repair coverage.

Run the sweep:

```bash
python -m chip_labs.cli creator-run-doctor-adversarial-sweep <run_dir> \
  --manifest docs/creator_system/examples/doctor-security/adversarial_schema_sweep.json \
  --fail-on-blocked
```

They do not grant publication or network absorption. They exist to prove that
doctor repair advice stays tied to fresh smoke/recompute evidence.
