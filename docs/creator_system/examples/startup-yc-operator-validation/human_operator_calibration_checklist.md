# Startup YC Human Operator Calibration Checklist

Current claim: `transfer_supported`

Do not approve `network_absorbable` until all checklist rows are complete.

| Gate | Required Evidence | Pass Condition | Current State |
| --- | --- | --- | --- |
| Multi-seed validation | At least 5 seeds across GTM, Finance, Product, People, Board, and Scale | Positive min delta and no negative scenario rows | open |
| Held-out founder advice | Held-out cases in `held_out_founder_advice_cases.jsonl` | Spark rejects vanity traction and gives a narrow next action | open |
| Operator calibration | Human startup operator review notes | Advice is useful, specific, and not overconfident | open |
| Privacy review | Review of founder/customer details and publication lane | No private founder or customer data leaves workspace by default | open |
| Rollback review | Deprecation condition for failed repeats or trap regressions | Packet can be rolled back without confusing future agents | open |
| Publication approval | Named human approval for public/network sharing | Approval is explicit, dated, and scoped | open |

Calibration questions:

1. Does the advice identify the binding constraint rather than restating generic startup doctrine?
2. Does it ask for evidence that would actually change the plan?
3. Does it reject vanity metrics as traction when buyer pull, usage, retention, or payment is absent?
4. Does it choose a narrow next operating move with an owner and a dated follow-up?
5. Does it preserve privacy boundaries and avoid publishing founder/customer details without approval?
