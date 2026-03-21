# Doctrine: Evaluator Trust Requires Path Trust

A fixed evaluator only stays trustworthy when the artifact paths it inspects match the places the system is actually allowed to write. If the rubric demands root-only files while the self-edit contract allows durable artifacts mainly under `docs/` and `research/`, then the evaluator will report false weakness even when the lab is behaving correctly. That mismatch causes avoidable regressions, distorts prioritization, and teaches agents to optimize for path compliance instead of truth.

The mechanism is straightforward. Scorers, runtime contracts, and self-edit rules form one operational surface, so a change in one layer propagates into the others. When those layers share path expectations, run history remains visible, contradictions remain inspectable, and doctrine remains promotable. When they drift apart, the same repo can look mature to one subsystem and incomplete to another, which degrades operator trust because score deltas stop meaning what they claim to measure.

This doctrine matters because the lab is upstream of the portfolio. A path mismatch inside the lab does not remain local; it spreads into how downstream chips are judged, scaffolded, and improved. Therefore compatibility work is not paperwork. It is a reliability mechanism that prevents the benchmark layer from punishing the governance layer for following its own rules.

The boundary is that path trust should not become path permissiveness. The solution is not to accept artifacts from everywhere. The solution is to define a small sanctioned set of locations, keep those locations stable, and validate them consistently across runtime, rubric, and self-edit flows.

## Causal Consequences

Evaluator trust improves because path alignment causes scores to track actual product state instead of storage accidents. When sanctioned paths remain stable, operators can verify why a score moved, compare one run to the next, and promote lessons with less ambiguity. That causal chain matters because trust in evaluation enables better planning, and better planning prevents wasted work on false regressions.

Path trust also prevents a subtler failure mode: invisible maturity. If the lab stores real doctrine, contradictions, and run history in sanctioned locations that the scorer ignores, the system degrades its own best work and teaches maintainers the wrong lesson about where intelligence should live. Therefore path trust is not only about passing checks. It is a mechanism that protects memory quality, benchmark honesty, and downstream advisory usefulness at the same time.

Because sanctioned paths keep evidence visible, later operators can test the same surface under the same rules and therefore compare runs more honestly. This only works when the allowed path set stays small and stable; otherwise path trust degrades into path sprawl and the score loses meaning again.
