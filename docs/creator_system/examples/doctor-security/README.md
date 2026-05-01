# Doctor Security Fixtures

These fixtures are executable adversarial inputs for `creator-run-doctor`.

- `stale_candidate_report_score.json` mutates a saved candidate report so
  `creator-run-doctor --recompute` must quarantine stale evidence.
- `malicious_network_absorption_packet.json` mutates a contribution packet so
  candidate-review evidence tries to masquerade as `network_absorbable`.

They do not grant publication or network absorption. They exist to prove that
doctor repair advice stays tied to fresh smoke/recompute evidence.
