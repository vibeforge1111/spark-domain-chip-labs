# Retrieval Memory Fixtures

These packets are local proof fixtures for the future retrieval/memory layer.
They do not wire Spark's production memory system.

- `correct_prior_decision.json` is a local workspace memory entry with source
  refs, provenance, and no network claim.
- `stale_memory.json` blocks stale context that has not been revalidated.
- `contradicted_memory.json` blocks recalled context contradicted by newer
  creator-system artifacts.
- `residue_contamination.json` blocks conversational residue from becoming
  durable memory truth.
- `network_without_review.json` blocks network-shareable memory without
  explicit review approval.

Run:

```bash
python -m chip_labs.cli retrieval-memory-check \
  --input docs/creator_system/examples/retrieval-memory/correct_prior_decision.json
```

The claim boundary is local: these fixtures prove the creator-system memory
contract shape, not production recall quality or network absorption.
