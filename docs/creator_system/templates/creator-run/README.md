# Creator Run Templates

These templates instantiate the Adaptive Creator Loop Standard. Copy this folder into a new creator run workspace, fill the fields, and keep the generated reports with the repo or mission that produced them.

Minimum order:

1. Fill `creator-intent.template.json`.
2. Fill `adapter-map.template.json`.
3. Generate or link the domain chip, specialization path, benchmark, and autoloop artifacts.
4. Run baseline, candidate, weak-case, and absorption checks.
5. Fill `creator-run-summary.template.md`.
6. Fill `swarm-contribution-packet.template.json` only if the run has a valid evidence tier.
7. Use `standard-change-proposal.template.md` only when the creator standard itself needs to change.

Do not claim `network_absorbable` unless provenance, rollback, trap status, and review state are filled.

Supporting templates:

| Template | Use |
| --- | --- |
| `evidence-ladder.template.md` | Record the weakest supported evidence tier, gate status, safe claim, unsafe claim, and remaining gaps. |
| `benchmark-pack.template.md` | Design a benchmark pack with case lanes, scoring dimensions, calibration, anti-gaming checks, and promotion rules. |
| `specialization-path-contract.template.md` | Define the path artifacts, mastery ladder, runtime use, benchmark binding, mutation boundary, and Swarm boundary. |
| `autoloop-policy.template.json` | Draft the autoloop policy before converting it into the run's `autoloop/policy.json`. |

Use `PROMOTION_GATES_AND_EVIDENCE_TIERS.md` as the source of truth when deciding what the run is allowed to claim.
