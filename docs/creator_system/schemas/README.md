# Creator System Schemas

These JSON Schemas are compatibility anchors for the creator-run contract.

They are intentionally pragmatic rather than exhaustive. Their job is to keep agents, CLIs, Builder, Telegram, and future product surfaces aligned on required fields while the benchmark and evidence logic continues to live in the smoke validator.

## Schemas

| Schema | Artifact |
| --- | --- |
| [creator-intent.schema.json](creator-intent.schema.json) | `creator-intent.json` |
| [adapter-map.schema.json](adapter-map.schema.json) | `adapter-map.json` |
| [created-artifact-manifest.schema.json](created-artifact-manifest.schema.json) | Shared manifest of generated chip/path/benchmark/loop/packet artifacts |
| [domain-chip-manifest.schema.json](domain-chip-manifest.schema.json) | `domain-chip/chip.manifest.json` |
| [scoring-hooks.schema.json](scoring-hooks.schema.json) | `domain-chip/scoring_hooks.json` |
| [hook-smoke-result.schema.json](hook-smoke-result.schema.json) | Generated domain-chip hook smoke output |
| [benchmark-pack-manifest.schema.json](benchmark-pack-manifest.schema.json) | Benchmark pack identity, family, lanes, scoring, anti-gaming, and promotion rules |
| [benchmark-case.schema.json](benchmark-case.schema.json) | Generated benchmark JSONL case rows |
| [benchmark-report.schema.json](benchmark-report.schema.json) | Generated and source-linked baseline/candidate benchmark reports |
| [absorption-summary.schema.json](absorption-summary.schema.json) | Generated and source-linked absorption summary reports |
| [specialization-path-manifest.schema.json](specialization-path-manifest.schema.json) | `specialization-path/path.manifest.json` |
| [autoloop-simulation-result.schema.json](autoloop-simulation-result.schema.json) | Generated keep/revert autoloop simulation output |
| [artifact-quality-report.schema.json](artifact-quality-report.schema.json) | Local artifact-quality score report |
| [artifact-quality-benchmark-manifest.schema.json](artifact-quality-benchmark-manifest.schema.json) | Artifact-quality benchmark manifest |
| [artifact-quality-benchmark-result.schema.json](artifact-quality-benchmark-result.schema.json) | Artifact-quality benchmark result bundle |
| [mirofish-content-route.schema.json](mirofish-content-route.schema.json) | Local MiroFish content route packet |
| [mirofish-content-simulation-result.schema.json](mirofish-content-simulation-result.schema.json) | Local MiroFish content simulation result |
| [mirofish-content-multi-seed-result.schema.json](mirofish-content-multi-seed-result.schema.json) | Local MiroFish content multi-seed result |
| [mirofish-provider-adapter-manifest.schema.json](mirofish-provider-adapter-manifest.schema.json) | Local MiroFish provider-adapter manifest |
| [mirofish-provider-adapter-check.schema.json](mirofish-provider-adapter-check.schema.json) | Local MiroFish provider-adapter check output |
| [mirofish-outcome-calibration-evidence.schema.json](mirofish-outcome-calibration-evidence.schema.json) | Local MiroFish real outcome calibration evidence |
| [mirofish-outcome-calibration-check.schema.json](mirofish-outcome-calibration-check.schema.json) | Local MiroFish outcome calibration check output |
| [loop-policy-manifest.schema.json](loop-policy-manifest.schema.json) | Autoloop policy, mutation surface, benchmark binding, rollback, and promotion gates |
| [swarm-contribution-packet.schema.json](swarm-contribution-packet.schema.json) | `swarm/contribution_packet.json` |
| [smoke-result.schema.json](smoke-result.schema.json) | `creator-run-smoke` output |
| [doctor-result.schema.json](doctor-result.schema.json) | `creator-run-doctor` output |
| [doctor-adversarial-sweep-manifest.schema.json](doctor-adversarial-sweep-manifest.schema.json) | `creator-run-doctor-adversarial-sweep` mutation manifest |
| [doctor-adversarial-sweep-result.schema.json](doctor-adversarial-sweep-result.schema.json) | `creator-run-doctor-adversarial-sweep` output |
| [template-check-result.schema.json](template-check-result.schema.json) | `creator-run-template-check` output |
| [creator-mission-status.schema.json](creator-mission-status.schema.json) | Read-only product surface adapter packet |
| [creator-release-gate.schema.json](creator-release-gate.schema.json) | Stronger-release gate aggregate for multi-seed, Startup YC review, and product runtime review evidence |
| [creator-system-beta-check.schema.json](creator-system-beta-check.schema.json) | Local creator-system beta readiness aggregate |
| [creator-system-release-evidence.schema.json](creator-system-release-evidence.schema.json) | Machine-readable technical beta release evidence packet |
| [operator-review-packet.schema.json](operator-review-packet.schema.json) | Generic generated-domain human/operator review packet |
| [operator-review-check.schema.json](operator-review-check.schema.json) | Generic generated-domain human/operator review check output |
| [product-runtime-review-packet.schema.json](product-runtime-review-packet.schema.json) | Product runtime review packet for Builder, Telegram, Spawner, Canvas, and Kanban |
| [product-runtime-review-check.schema.json](product-runtime-review-check.schema.json) | Product runtime review check output |
| [retrieval-memory-packet.schema.json](retrieval-memory-packet.schema.json) | Local retrieval-memory packet input |
| [retrieval-memory-check.schema.json](retrieval-memory-check.schema.json) | Local retrieval-memory check output |
| [tool-operation-manifest.schema.json](tool-operation-manifest.schema.json) | Local safe tool-operation manifest |
| [tool-operation-packet.schema.json](tool-operation-packet.schema.json) | Local tool-operation packet input |
| [tool-operation-check.schema.json](tool-operation-check.schema.json) | Local tool-operation safety check output |
| [startup-yc-validation-plan.schema.json](startup-yc-validation-plan.schema.json) | Startup YC validation plan and network-absorption gate list |
| [startup-yc-validation-evidence.schema.json](startup-yc-validation-evidence.schema.json) | Startup YC raw validation evidence inputs and promotion bundles |
| [startup-yc-validation-evidence-check-result.schema.json](startup-yc-validation-evidence-check-result.schema.json) | Startup YC raw validation-evidence shape-check output |
| [startup-yc-gate-check-result.schema.json](startup-yc-gate-check-result.schema.json) | Startup YC individual gate-check outputs |
| [startup-yc-validation-suite.schema.json](startup-yc-validation-suite.schema.json) | Startup YC validation-suite output |
| [startup-yc-external-rerun-provenance.schema.json](startup-yc-external-rerun-provenance.schema.json) | Startup YC external recompute provenance packet |
| [startup-yc-network-absorption-review.schema.json](startup-yc-network-absorption-review.schema.json) | Startup YC network-absorption review packet |
| [startup-yc-production-gate-workbench.schema.json](startup-yc-production-gate-workbench.schema.json) | Startup YC production-gate rehearsal summary |
| [generated-multi-seed-summary.schema.json](generated-multi-seed-summary.schema.json) | Generated multi-domain multi-seed summary output |
| [generated-multi-seed-summary-check.schema.json](generated-multi-seed-summary-check.schema.json) | Recomputed generated multi-seed summary check output |

The smoke validator remains stricter than these schemas where score semantics, promotion gates, transfer boundaries, and publication readiness are concerned.

## Phase 2 Packet Coverage

These schemas cover the shared packet layer called for by the creator master plan:

- creator intent: `creator-intent.schema.json`
- created artifacts: `created-artifact-manifest.schema.json`
- domain chip: `domain-chip-manifest.schema.json`
- scoring hooks: `scoring-hooks.schema.json`
- generated hook smoke: `hook-smoke-result.schema.json`
- benchmark pack: `benchmark-pack-manifest.schema.json`
- benchmark cases: `benchmark-case.schema.json`
- benchmark reports: `benchmark-report.schema.json`
- absorption summary: `absorption-summary.schema.json`
- specialization path: `specialization-path-manifest.schema.json`
- loop policy: `loop-policy-manifest.schema.json`
- autoloop simulation: `autoloop-simulation-result.schema.json`
- Swarm promotion packet: `swarm-contribution-packet.schema.json`

Product surfaces should pass these shapes around, then use `creator-run-smoke`
and `creator-run-doctor` for the stricter evidence verdict. The
`creator-mission-status` packet is the read-only bridge for Builder, Telegram,
Spawner, Canvas, and Kanban; it must not replace the underlying canonical
packets.

The Startup YC validation-plan, validation-evidence, validation-evidence-check,
gate-check, and validation-suite schemas anchor the blocked promotion workflow.
The validation-plan schema keeps the current `transfer_supported` claim, the
required human/review gates, the multi-seed floor, and the publication boundary
machine-checkable. Raw validation evidence is shape-checked before it becomes a
gate output. Shape-check and individual gate-check outputs include raw-evidence
provenance hashes so saved evidence can be compared with fresh inputs and
promotion bundles can reject stale saved evidence. The shape-check result schema
requires hashes when evidence is present, missing-input records when it is
absent, and verdicts that match the blocker state. These schemas intentionally
require `network_absorbable=false` when that field is present; passing the
schema means the packet shape is compatible, not that Startup YC is approved for
network absorption. The validation-suite schema references the gate-check schema
for every subcheck, so a saved suite cannot hide malformed gate evidence inside
a generic object field. Creator-system CI validates both freshly generated suite
output and the saved blocked suite fixture against that referenced schema pair.
The external rerun provenance schema anchors a standalone packet for Startup YC
recompute runs. It requires recomputed smoke linkage, source input paths,
source hashes, `network_absorbable=false`, and visible blockers when any
external source is missing, stale, or present without a hash.
The network-absorption review schema combines the validation-suite state,
required approval gates, and optional external provenance packet into a single
review artifact. It still requires `network_absorbable=false`; a
`review_ready` packet only means blockers are absent for human review, not that
Spark may publish or network-absorb Startup YC.
The production-gate workbench schema anchors the end-to-end rehearsal command
that writes the individual Startup YC gate outputs, promotion bundle,
validation suite, and network-absorption review into a clean workspace. Its
summary records whether the workspace was clean before outputs were written,
is intentionally a rehearsal packet, and keeps `network_absorbable=false` even
when supplied gate evidence lets subchecks pass.

The creator-release-gate schema aggregates stronger-release evidence without
turning it into publication approval. It requires visible phase rows for the
generated multi-seed matrix, Startup YC network-absorption review, and product
runtime integration review. It also records source hashes for supplied inputs
and keeps `network_absorbable=false` even when a future packet reaches
`review_ready`.
The creator-system beta check schema is the user/operator-facing aggregate for
this technical beta. It proves templates, strict Startup YC smoke, raw evidence
shape, network-absorption blockers, the fresh Startup YC production-gate
workbench rehearsal, and stronger-release blockers in one packet while still
keeping `network_absorbable=false`.
The creator-system release-evidence schema wraps that beta check with repo
branch, commit, remote, clean-worktree status, required rerun commands, release
docs, and the explicit promotion boundary. A passing packet requires a clean
checkout and a passing beta check; dirty release evidence blocks without
changing `network_absorbable=false`.
The product-runtime review schemas define the evidence packet that can satisfy
the release gate's product phase. They require Builder, Telegram, Spawner,
Canvas, and Kanban to preserve read-only adapters, blocked-state visibility,
`evidence_mode`, reviewer evidence, rollback references, and disabled creator
controls in this methodology repo. In short: disabled creator controls remain
part of the product review evidence until product repos pass separate runtime
reviews.

The generated multi-seed summary schemas anchor the generic domain-generator
matrix separately from the Startup YC promotion gate. They require recomputed
evidence mode, `network_absorbable=false`, visible failed seed ids, no hidden aggregate failures, and a check packet that blocks tampered summary rows or
stale underlying run reports.

The doctor adversarial sweep schemas anchor the local schema-family mutation
suite. The manifest requires explicit unsafe claims, safe boundaries, expected
blocking checks, and expected quarantine reasons for adapter-map,
candidate-report, absorption-summary, Swarm-packet, and evidence-ladder
mutations. The result schema requires visible row outcomes and
`network_absorbable=false`; a passing result cannot hide failed case ids.

The generic operator-review schemas anchor Phase 5 for generated domains. They
require explicit human/operator calibration, privacy review, rollback review,
publication approval, known limits, forbidden claims, and
`network_absorbable=false`. Their evidence tier remains bounded to
`candidate_review` or `transfer_supported`; `network_absorbable` may be the
requested claim under review, but never the packet's own evidence tier. A
passing operator-review check is review evidence only; it does not replace
multi-seed validation or the full promotion bundle.

The retrieval-memory schemas anchor the local memory-lane contract while the
production memory runtime remains deferred. Packet inputs require explicit
lanes, source refs, freshness, provenance, contradiction fields, and review
metadata. Check outputs require `network_absorbable=false`, visible blockers for
blocked packets, and calibration verdicts that match the blocker state.

The tool-operation schemas anchor the local mission-control safety boundary.
They describe the supported command manifest, the parsed operation packet shape,
and the check output that product or mission traces may read. Passing checks
must have `allowed=true` and no blockers; blocked checks must have
`allowed=false`, visible blockers, and rollback-state protection.

The artifact-quality schemas anchor the local design-doc and PR evidence reviewer.
They keep artifact reports tied to the local review-only claim boundary, require
unsafe claims to say the score does not prove product correctness or replace
human review, and keep benchmark pass results aligned with reviewer calibration,
trap regression, and keep/revert decisions.

The MiroFish content schemas anchor the local content-routing and simulator
contract. Route packets must preserve the candidate-review claim boundary,
simulation results must expose calibration blockers, and multi-seed packets
must keep `network_absorbable=false` until real outcome calibration, review,
privacy, rollback, and publication gates exist.
The provider-adapter schemas add future RLM judge slots without wiring live
provider calls. Manifests must keep network calls and live credentials disabled,
require per-judge/per-persona rows plus prompt hashes, and forbid real virality,
calibrated reliability, and network absorption claims until outcome evidence
exists.
The outcome-calibration schemas require real content outcome rows to include
denominators, downstream-aware signals, qualitative review, explicit forbidden
claims, and `network_absorbable=false`. The saved insufficient fixture is
supposed to validate as evidence shape while its check remains `inconclusive`;
that is the honest state before real calibration data exists.
