# Creator System Schemas

These JSON Schemas are compatibility anchors for the creator-run contract.

They are intentionally pragmatic rather than exhaustive. Their job is to keep agents, CLIs, Builder, Telegram, and future product surfaces aligned on required fields while the benchmark and evidence logic continues to live in the smoke validator.

## Schemas

| Schema | Artifact |
| --- | --- |
| [creator-intent.schema.json](creator-intent.schema.json) | `creator-intent.json` |
| [adapter-map.schema.json](adapter-map.schema.json) | `adapter-map.json` |
| [swarm-contribution-packet.schema.json](swarm-contribution-packet.schema.json) | `swarm/contribution_packet.json` |
| [smoke-result.schema.json](smoke-result.schema.json) | `creator-run-smoke` output |
| [doctor-result.schema.json](doctor-result.schema.json) | `creator-run-doctor` output |
| [template-check-result.schema.json](template-check-result.schema.json) | `creator-run-template-check` output |

The smoke validator remains stricter than these schemas where score semantics, promotion gates, transfer boundaries, and publication readiness are concerned.

