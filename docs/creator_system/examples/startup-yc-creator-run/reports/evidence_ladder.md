# Evidence Ladder

Run ID: creator-run-2026-05-01-startup-yc
Domain: Startup YC
Target capability: Startup operating judgment for early-stage agents
Claim being tested: Startup YC packets improve fresh-agent startup advice and Startup YC adapters transfer across the fresh validation suite.

## Tier Claimed

Claimed tier: transfer_supported

Weakest supported tier: transfer_supported

Reason: The run has candidate-review evidence from the 20-case fresh-agent absorption suite, a positive 12-scenario Startup Bench fresh-validation transfer suite, and a positive broad fresh-transfer probe. It still does not claim network absorption because publication, privacy, and human/operator review are not approved.

## Gate Checklist

| Gate | Status | Evidence path | Notes |
| --- | --- | --- | --- |
| Prototype scaffold | pass | `creator-intent.json`, `adapter-map.json` | Run intent and adapters are present. |
| Baseline benchmark | pass | `reports/baseline.json` | No-pack fresh-agent mean score is `0.6803`. |
| Candidate benchmark | pass | `reports/candidate.json` | Validated-pack mean score is `0.7003`, delta `+0.0200`. |
| Held-out or weak-case replay | pass | `reports/absorption_summary.json` | Full 20-case absorption suite includes basic, intermediate, advanced, and trap bands. |
| Fresh-agent absorption | pass | `reports/absorption_summary.json` | All modes are present/scored with positive validated-pack delta. |
| Trap/adversarial coverage | pass | `reports/absorption_summary.json` | Trap-band coverage is present and packet reports zero trap regressions. |
| Transfer probe | pass | `reports/transfer_summary.json` | Startup YC adapters won `12/12` fresh scenarios with mean delta `+0.0560`. |
| Broad transfer probe | pass | `reports/broad_transfer_probe.json` | Broad fresh transfer is positive across all six tracks, with min delta `+0.0144`. |
| Swarm packet consistency | pass | `swarm/contribution_packet.json` | Packet tier and deltas match reports. |
| Privacy/provenance/rollback | pass | `swarm/contribution_packet.json` | Workspace-only publication boundary, source commit, and rollback rule are present. |

## Score Summary

| Surface | Baseline | Candidate | Delta | Min Delta | Constraints | Verdict |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Main absorption benchmark | 0.6803 | 0.7003 | +0.0200 |  | pass | pass |
| Fresh validation transfer | 0.7139 | 0.7699 | +0.0560 | +0.0144 | pass | pass |
| Broad fresh transfer | 0.7139 | 0.7699 | +0.0560 | +0.0144 | pass | pass |

## Failure Lineage

- Weakness found: The earlier broad compatible-suite probe was negative because one generic 0-to-1 script was being reused too broadly.
- Benchmark or trace that exposed it: The older `reports/broad_transfer_probe.json` with delta `-0.0151`.
- Patch or packet mechanism: Use track-specific Startup YC adapters and a 12-scenario fresh validation suite covering GTM, Finance, Product, People, Board, and Scale.
- Counterfactual if unchanged: Startup YC would stay stuck at one-scenario transfer evidence and could not support broader fresh-suite claims.

## Safe Claim

```text
Startup YC has transfer-supported evidence: the validated pack improved the 20-case fresh-agent absorption suite by +0.0200, and current Startup YC adapters won 12/12 fresh-validation scenarios across six tracks with mean scenario delta +0.0560 and min delta +0.0144.
```

## Unsafe Claim

```text
Startup YC is network-absorbable or fully mastered without human/operator review, multi-seed fresh validation, and publication approval.
```

## Remaining Gaps

- Fresh validation currently ran seed 0 only.
- Human/operator review and calibration are still needed for score validity.
- Network absorption remains disabled until privacy, review, and publication gates approve it.
