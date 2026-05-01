# Evidence Ladder

Run ID: creator-run-2026-05-01-startup-yc
Domain: Startup YC
Target capability: Startup operating judgment for early-stage agents
Claim being tested: Startup YC packets improve fresh-agent startup advice and transfer to one Startup Bench scenario.

## Tier Claimed

Claimed tier: transfer_supported

Weakest supported tier: transfer_supported

Reason: The run has candidate-review evidence from the 20-case fresh-agent absorption suite and one positive Startup Bench transfer probe. It does not claim network absorption because the broad transfer probe is negative.

## Gate Checklist

| Gate | Status | Evidence path | Notes |
| --- | --- | --- | --- |
| Prototype scaffold | pass | `creator-intent.json`, `adapter-map.json` | Run intent and adapters are present. |
| Baseline benchmark | pass | `reports/baseline.json` | No-pack fresh-agent mean score is `0.6803`. |
| Candidate benchmark | pass | `reports/candidate.json` | Validated-pack mean score is `0.7003`, delta `+0.0200`. |
| Held-out or weak-case replay | pass | `reports/absorption_summary.json` | Full 20-case absorption suite includes basic, intermediate, advanced, and trap bands. |
| Fresh-agent absorption | pass | `reports/absorption_summary.json` | All modes are present/scored with positive validated-pack delta. |
| Trap/adversarial coverage | pass | `reports/absorption_summary.json` | Trap-band coverage is present and packet reports zero trap regressions. |
| Transfer probe | pass | `reports/transfer_summary.json` | One fresh Startup Bench activation scenario transfers positively by `+0.0169`. |
| Broad transfer probe | warn | `reports/broad_transfer_probe.json` | Compatible 10-scenario probe is negative at `-0.0151`; broad mastery is not supported. |
| Swarm packet consistency | pass | `swarm/contribution_packet.json` | Packet tier and delta match reports. |
| Privacy/provenance/rollback | pass | `swarm/contribution_packet.json` | Workspace-only publication boundary, source commit, and rollback rule are present. |

## Score Summary

| Surface | Baseline | Candidate | Delta | Min Delta | Constraints | Verdict |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Main absorption benchmark | 0.6803 | 0.7003 | +0.0200 |  | pass | pass |
| Transfer | 0.6195 | 0.6364 | +0.0169 | +0.0169 | pass | pass |
| Broad transfer | 0.6885 | 0.6734 | -0.0151 | -0.0526 | pass | warn |

## Failure Lineage

- Weakness found: The first broad transfer probe underperformed on most compatible Startup Bench scenarios.
- Benchmark or trace that exposed it: `reports/broad_transfer_probe.json`.
- Patch or packet mechanism: Keep this fixture at `transfer_supported`, use track-specific adapters before claiming broad transfer.
- Counterfactual if unchanged: Startup YC could be overclaimed as general startup mastery from focused evidence.

## Safe Claim

```text
Startup YC has transfer-supported evidence: the validated pack improved the 20-case fresh-agent absorption suite by +0.0200 and transferred positively to one fresh Startup Bench activation scenario by +0.0169, while broad transfer remains unproven.
```

## Unsafe Claim

```text
Startup YC is broadly mastered and should be absorbed by all agents without additional track-specific validation.
```

## Remaining Gaps

- Broad Startup Bench transfer is still negative.
- Current transfer evidence covers one fresh Startup Bench scenario.
- Network absorption requires broad transfer repair, privacy review, and publication review.
