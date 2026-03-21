# Doctrine: Bounded Loops Beat Clever Loops

The lab should prefer bounded recursive improvement over open-ended autonomy because the real failure mode is not "too little exploration" but silent contract drift. A loop that can mutate everything will often produce superficially novel output, yet it becomes hard to explain which change caused an improvement, which boundary was crossed, and why a later regression appeared. Therefore the lab treats fixed evaluators, explicit mutation fields, and human review gates as first-class control surfaces rather than bureaucratic overhead.

This doctrine applies most strongly when the lab is editing itself or proposing cross-domain methodology changes. In those cases, the blast radius is larger than in a single domain chip, so guardrails must tighten rather than loosen. The loop should record what hypothesis was tested, what artifact changed, what score moved, and whether the result was promoted, deferred, or rejected. When a mutation cannot be described in that form, it is usually too broad to ship safely.

The boundary condition is that bounded loops can become performative if the allowed mutations are too narrow. If the lab only allows cosmetic edits, then the loop preserves safety but fails to improve the underlying system. For that reason, mutation spaces should stay closed but meaningful: research focus, methodology area, benchmark profile, and transfer targets can vary, while cross-repo contract changes still require deliberate approval. At most eight autonomous iterations should occur before a human reviews the evidence, because after that point lineage gets harder to audit and the probability of accidental narrative drift rises.

The useful consequence is operational clarity. A bounded loop can be benchmarked, contradicted, and improved. An unbounded loop can usually only be narrated.

## Operational Mechanism

Bounded loops improve the lab because they force every iteration to expose a mechanism rather than hide inside a vague story of progress. When a run names the mutation surface, the expected effect, and the measured delta, the evaluator can verify whether the claimed improvement actually occurred. That traceability enables contradiction review, prevents accidental over-promotion, and causes later maintainers to inherit a legible lineage instead of a pile of unexplained edits.

The doctrine also prevents a common recursive-systems failure mode: complexity rises faster than understanding. If a loop can alter prompts, memory policy, runtime behavior, and rubric logic in one step, then a regression rarely has one clear source. Because the search space explodes, diagnosis slows down, and therefore the lab learns less from each failure. Keeping mutation spaces closed reduces branching factor, which improves attribution quality and enables faster rollback or refinement when a run degrades outcomes.

This mechanism only holds when the boundaries remain honest. If operators start labeling broad conceptual rewrites as narrow mutations, the loop regains all the ambiguity it was meant to remove. Therefore the lab should validate mutation descriptions against the actual files changed and should reject runs whose claimed scope does not match their diff.
