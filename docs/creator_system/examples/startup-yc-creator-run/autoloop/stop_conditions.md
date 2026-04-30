# Startup YC Autoloop Stop Conditions

Stop the loop when:

- The run produces zero keeps and weak-case diagnosis has not been performed.
- Trap cases regress.
- Benchmark artifacts fail schema or integrity checks.
- The mutation attempts to alter scoring semantics.
- A no-gain streak suggests the mutation surface is saturated.

