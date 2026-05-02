# Creator System Schemas

These JSON Schemas are compatibility anchors for the creator-run contract.

They are intentionally pragmatic rather than exhaustive. Their job is to keep agents, CLIs, Builder, Telegram, and future product surfaces aligned on required fields while the benchmark and evidence logic continues to live in the smoke validator.

## Schemas

| Schema | Artifact |
| --- | --- |
| [creator-intent.schema.json](creator-intent.schema.json) | `creator-intent.json` |
| [adapter-map.schema.json](adapter-map.schema.json) | `adapter-map.json` |
| [created-artifact-manifest.schema.json](created-artifact-manifest.schema.json) | Shared manifest of generated chip/path/benchmark/loop/packet artifacts |
| [benchmark-pack-manifest.schema.json](benchmark-pack-manifest.schema.json) | Benchmark pack identity, family, lanes, scoring, anti-gaming, and promotion rules |
| [loop-policy-manifest.schema.json](loop-policy-manifest.schema.json) | Autoloop policy, mutation surface, benchmark binding, rollback, and promotion gates |
| [swarm-contribution-packet.schema.json](swarm-contribution-packet.schema.json) | `swarm/contribution_packet.json` |
| [smoke-result.schema.json](smoke-result.schema.json) | `creator-run-smoke` output |
| [doctor-result.schema.json](doctor-result.schema.json) | `creator-run-doctor` output |
| [template-check-result.schema.json](template-check-result.schema.json) | `creator-run-template-check` output |
| [creator-mission-status.schema.json](creator-mission-status.schema.json) | Read-only product surface adapter packet |
| [startup-yc-validation-suite.schema.json](startup-yc-validation-suite.schema.json) | Startup YC validation-suite output |

The smoke validator remains stricter than these schemas where score semantics, promotion gates, transfer boundaries, and publication readiness are concerned.

## Phase 2 Packet Coverage

These schemas cover the shared packet layer called for by the creator master plan:

- creator intent: `creator-intent.schema.json`
- created artifacts: `created-artifact-manifest.schema.json`
- benchmark pack: `benchmark-pack-manifest.schema.json`
- loop policy: `loop-policy-manifest.schema.json`
- Swarm promotion packet: `swarm-contribution-packet.schema.json`

Product surfaces should pass these shapes around, then use `creator-run-smoke`
and `creator-run-doctor` for the stricter evidence verdict. The
`creator-mission-status` packet is the read-only bridge for Builder, Telegram,
Spawner, Canvas, and Kanban; it must not replace the underlying canonical
packets.

The Startup YC validation-suite schema anchors the blocked promotion-gate
workflow. It intentionally requires `network_absorbable=false`; passing the
schema means the packet shape is compatible, not that Startup YC is approved for
network absorption.
