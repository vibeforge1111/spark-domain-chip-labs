# Benchmark-Grounded: Stabilization Pass Results

## Benchmarks Run

The stabilization pass cleared the repo-local failing tests that previously pointed to real contract or scorer defects. The high-signal checks were:

- `tests/test_hooks.py::TestSessionDomain::test_pre_tool_use_enriches_with_session_domain`
- `tests/test_quality_rubric_v2.py`
- `tests/test_domain_chip_integration.py -k "test_no_chip_below_scaffold or test_no_regression_from_baseline"`
- `tests/test_chip_runtime.py`
- `tests/test_chip_mcp_server.py`
- `tests/test_deep_eval.py`

## Outcome

The earlier full-suite state included four failures, three of which were directly attributable to repo-local contract drift and one of which reflected a scorer interpretation problem that penalized legitimate bounded chips. After the stabilization patches, the targeted regressions passed, the full suite before the deep-eval pass reached `1693 passed, 186 xfailed`, and the v3 evaluator tests passed at `71 passed`. The repo's own `score-v3` moved from `23.0/100` to `28.0/100` once the evaluator recognized the current manifest contract, which confirms the drift diagnosis rather than merely restating it.

## Interpretation

This benchmark evidence supports two conclusions. First, the repo's low self-score was partly caused by missing artifacts and partly caused by evaluator mismatch, so both code and documentation needed work. Second, the stabilization effort improved correctness without weakening the fixed benchmarks: the same tests still ran, and the result improved because the implementation now matches the declared contract more closely.

## Boundary

These benchmarks establish local correctness for the audited paths. They do not yet prove that the lab has a long-running flywheel with durable operational history; that still depends on continued run logging and artifact production.

## Benchmark Interpretation For Operators

The important operator lesson is that benchmark movement only became meaningful after the contract and artifact-path drift was removed. Before that alignment, a score delta could mean either a real regression or a scorer mismatch. After the stabilization pass, the same benchmark surfaces started reflecting a cleaner distinction: runtime errors looked like runtime errors, rubric gaps looked like rubric gaps, and missing artifacts looked like missing artifacts rather than invisible sanctioned artifacts. That shift improves operational decision-making because maintainers can spend effort on the right bottleneck.

This benchmark evidence also clarifies where the lab is still early. The repo can now pass its scorer checks and explain its contract coherently, but it still lacks long-horizon empirical volume relative to a mature recursive system. The measured state therefore supports a more disciplined narrative: the lab is structurally ready, benchmark-clean on the audited paths, and beginning to accumulate its own flywheel history, but it is not yet a decades-deep memory system. That distinction matters because benchmark honesty is part of the product. Users trust a lab that can name both its strengths and its unfinished dimensions.

From a product standpoint, these benchmarks show immediate usefulness. Runtime compatibility improvements reduce false breakage for hook execution. Rubric compatibility improvements reduce false positives and false negatives in portfolio health monitoring. Artifact-path compatibility improves self-edit traceability. Each of those outcomes is operational rather than cosmetic, because they change what happens when the lab actually evaluates, advises, or governs future chips.

## Next Benchmark Targets

The next high-signal benchmark targets should be multi-chip transfer validation, packet retrieval precision, and longer-run trajectory quality. Those areas would test whether the lab can move beyond local repo stabilization into portfolio-level compounding.
