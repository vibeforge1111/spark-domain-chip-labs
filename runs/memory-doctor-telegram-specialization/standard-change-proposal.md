# Creator Standard Change Proposal

Proposal ID: creator-standard-memory-context-movement-map-v1
Date: 2026-05-09
Proposer: Codex
Affected standard version: adaptive_creator_loop.v1

## Proposed Change

Creator-system diagnostic artifacts should include a movement map and proactive diagnostic brain for stateful systems: ingress, routing, memory reads/writes, lifecycle/policy gates, context capsule/source ledger, SDK/wiki/dashboard senses, dashboard/watchtower state, detected gaps, unknowns, coverage score, and next probes.

## Causal Anchor

- Concrete loop failure: Memory Doctor could verify active memory and delete integrity but still miss close-turn blankness caused by `recent_conversation=0` in provider capsules.
- Counterfactual if unchanged: doctors would keep saying memory is healthy while context handoffs silently drop recent Telegram turns.
- Why this is not only wording/style improvement: the Builder implementation now detects the real gateway-to-context-capsule lineage gap from item-level traces, repairs the covered recent-conversation assembly path with tests, and reports whether the doctor had enough diagnostic senses to trust or deepen the diagnosis.

## Lineage

1. Maya was historically present in memory traces and sometimes overtook active profile behavior.
2. A multi-delete Telegram turn initially deleted only one of several requested fields.
3. Spark later went blank because provider context capsules omitted recent same-session conversation despite gateway traces having earlier messages.

## Complexity Delta

- New fields: movement map stages, gaps, unknowns, gateway trace audit, brain coverage score, diagnostic senses, proactive improvements, SDK runtime visibility, wiki packet metadata, LLM wiki health, and dashboard movement export status.
- New branches: one diagnostic branch for gateway-to-capsule lineage gaps and one context assembly fallback when Builder event transcript is absent.
- New tools: no new external tools; uses existing Builder observability, gateway trace, memory inspection, and watchtower surfaces.
- Removed complexity: reduces manual DB/log spelunking during memory incidents.
- Why the tradeoff is worth it: it prevents false health claims by separating active state, trace history, and context movement failures.

## Transfer Check

- Source domain: Spark Telegram memory/context incident diagnosis.
- Target domain: creator-system diagnostics for any stateful domain chip or specialization path.
- Label mapping: `source_ledger` -> movement source, `gateway trace` -> ingress evidence, `watchtower` -> dashboard evidence, `gaps` -> repair candidates.
- Shadow test or low-risk test: local-only Memory Doctor tests, context capsule fallback tests, and live local repair probe.
- Result: targeted tests pass; the first live probe reported the gateway-to-capsule gap directly, and the fresh live probe shows `recent_conversation=6` with movement gaps=0.

## Guardrail Status

| Gate | Status | Evidence |
| --- | --- | --- |
| Schema | pass | Existing creator-run smoke still passes. |
| Lineage | pass | Three failure lineage anchors listed above. |
| Complexity | pass | Diagnostic-only, no storage semantics or repair authority changed. |
| Transfer | warn | Pattern is transferable, and the covered repair path plus doctor-brain senses are verified locally; only one live domain has been exercised. |
| Memory hygiene | pass | Historical trace remains non-authoritative and no purge is suggested. |
| Autonomy | pass | Diagnosis-only; repair remains gated. |

## Rollback

- Rollback condition: movement-map diagnostics produce false failure claims in focused tests or live probes.
- Evaluation window: next memory/context incident and next benchmark pack pass.
- Owner: Builder Memory Doctor specialization.

## Decision

Decision: approve locally

Reason: the change is trace-grounded, local-only, reversible, and directly addresses the close-turn blankness class without granting repair authority.
