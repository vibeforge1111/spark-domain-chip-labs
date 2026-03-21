# Research-Grounded: Contract Alignment Findings

## Claim

The lab's core architecture is coherent, but its evaluators and runtime had drifted onto slightly different interpretations of the chip contract.

## Evidence

The repo-level audit showed that `spark-chip.json` declares `schema_version`, `capabilities`, and `commands`, while older scorer logic still looked primarily for `schema` and `hooks`. That produced a false negative in v3 integration maturity even though the live manifest clearly advertised the four canonical hook surfaces. The runtime had a similar mismatch: it could execute subprocess hooks, but it favored stdin payloads even though the lab's CLI hook interface is file-oriented. This is a classic systems-integration failure where each component is locally reasonable but the end-to-end contract becomes inconsistent.

A second grounded finding is that the repo had significant design and mission documentation spread across `docs/`, but the v3 doctrine evaluator only recognized doctrine artifacts in `docs/beliefs`, `docs/doctrines`, `beliefs`, `doctrines`, or `chip_skill.md`. In practice that meant the repo contained doctrine-like content without normalizing it into durable doctrine artifacts. The result was undercounting, not absence of thinking.

## Mechanism

The mechanism behind the false weak score is path mismatch. Structural intelligence only counts when it is stored and emitted through the exact contract that the evaluator understands. Therefore the fix path is not to weaken the rubric, but to keep one compatibility parser for manifest shape and to store doctrine, contradiction, and run artifacts in locations that the rubrics already inspect.

## Boundary

This analysis is grounded in the current repo state as of 2026-03-21. It does not prove that every downstream chip follows the same conventions, so compatibility logic still needs to preserve the legacy `hooks` path for older chips.

## Portfolio Relevance

This grounded finding matters because the lab is not evaluating one isolated codebase. It sits above a portfolio of chips that may be at different ages, with different manifest conventions, and with different levels of runtime maturity. If the lab only reads one manifest dialect, then it stops being a portfolio instrument and becomes a local-style enforcer. That would distort the comparative view that the lab is meant to provide. Therefore backward compatibility is not nostalgia; it is a precondition for valid cross-chip comparison.

The user-facing value of this research is higher trust in the lab's judgments. A chip owner should be able to believe that a low score means their chip is genuinely weak, not that the lab forgot how to read a contract variation that used to be accepted. Likewise, a high score should mean the chip really exposes the right capabilities and runtime surfaces, not that the scorer happened to match one preferred file shape. Because trust in evaluation is upstream of adoption, contract alignment research protects the lab's usefulness to every downstream maintainer and contributor.

The moat implication is that a lab with accurate compatibility discipline accumulates cleaner longitudinal data. If every old chip gets accidentally downgraded by scorer drift, the historical record becomes noisy and transfer learning weakens. If compatibility is maintained deliberately, the lab can compare generations of chips and see which improvements were real. That enables better packet promotion, better graduation decisions, and better evidence about which architectural changes actually compound across the portfolio.

## Open Research Questions

Two grounded questions remain. First, how many manifest variants should the lab continue to support before compatibility becomes counterproductive? Second, what is the smallest sanctioned artifact-path set that preserves evaluator trust without making the contract too permissive? These are still research questions because the answers affect future portfolio coherence, not just this repo's local score.
