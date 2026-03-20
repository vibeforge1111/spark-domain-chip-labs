# Intelligence Delivery System

**Date**: 2026-03-20
**Module**: `src/chip_labs/intelligence_server.py`

---

## The Problem

A mature domain chip accumulates doctrines, evidence, beliefs, benchmarks, and contradictions through the autoloop flywheel. But this intelligence was **inert** -- stored in files but never delivered to users or systems that need it.

Compare with:
- **Claude Code skills**: Load context into conversation via CLAUDE.md
- **Codex skills**: Inject domain knowledge at inference time
- **Spawner skills**: Provide structured patterns and anti-patterns

Domain chips had none of this. The intelligence_server closes this gap.

---

## What Gets Delivered

### `chip_skill.md` (Primary Artifact)

A living skill file following the Claude Code CLAUDE.md convention. Auto-generated from the chip's accumulated intelligence.

Structure:
```markdown
# {chip_name} Domain Intelligence
> Quality: {score}/100 ({verdict}) | Doctrines: {count}

## Domain Identity
{mission and description}

## Core Doctrines (sorted by confidence)
1. [grounded_doctrine] Doctrine title
   Mechanism: how it works
   Boundary: when it doesn't apply

## Active Contradictions
- Contradiction description (source: ...)

## Mutation Axes
- axis_name: value1 | value2 | value3

## Evidence Summary
- research_grounded: N files
- benchmark_grounded: N files
- ...

## Key Benchmarks
- benchmark_id: description (score: N)

## Quality Trajectory
50 -> 65 -> 73 -> 80
```

### `chip_context.json` (Machine-Readable)

Structured JSON for LLM injection or API consumption:
```json
{
  "chip_name": "domain-chip-startup-yc",
  "mission": "...",
  "doctrines": [...],
  "contradictions": [...],
  "mutation_axes": [...],
  "evidence_summary": {...},
  "score": 73,
  "verdict": "beta"
}
```

### `chip_doctrine_digest.md` (Human Summary)

Concise markdown digest of all doctrines, grouped by confidence tier.

---

## API Reference

### `extract_intelligence(chip_path) -> ChipIntelligence`

Reads a chip directory and extracts all intelligence into a structured dataclass:

```python
@dataclass
class ChipIntelligence:
    chip_name: str
    mission: str
    doctrines: list[dict]        # Sorted by confidence
    contradictions: list[dict]
    mutation_axes: list[dict]
    evidence_summary: dict       # Lane -> file count
    benchmarks: list[dict]
    score_trajectory: list[int]
    current_score: int
    verdict: str
    has_dspy: bool
    packet_count: int
```

### `build_skill(chip_path) -> Path`

Generates `chip_skill.md` from extracted intelligence. Returns the path to the generated file.

### `build_context(chip_path) -> Path`

Generates `chip_context.json`. Returns the path.

### `build_doctrine_digest(chip_path) -> Path`

Generates `chip_doctrine_digest.md`. Returns the path.

### `serve_context(chip_path, query) -> dict`

Query-based context retrieval. Uses Jaccard similarity to find the most relevant doctrines for a given query.

Returns:
```json
{
  "query": "distribution velocity retention",
  "chip_name": "domain-chip-startup-yc",
  "relevant_doctrines": [...],  // Top 5 most relevant
  "total_doctrines": 40,
  "evidence_summary": {...}
}
```

### `refresh_skill(chip_path) -> dict`

Regenerates all three artifacts and returns metadata:
```json
{
  "skill_path": "...",
  "context_path": "...",
  "digest_path": "...",
  "chip_name": "domain-chip-startup-yc",
  "doctrine_count": 40,
  "evidence_files": 28,
  "current_score": 73,
  "verdict": "beta",
  "packet_count": 12,
  "last_updated": "2026-03-20T..."
}
```

---

## CLI Commands

```bash
# Build all intelligence artifacts for a chip
chip-labs build-skill <chip-path>

# Query a chip's intelligence
chip-labs serve <chip-path> "distribution velocity retention"
```

---

## DSPy Integration Framework

**Module**: `src/chip_labs/dspy_slot.py`

Provides a zero-dependency framework for generating DSPy scripts. Does NOT import dspy -- it generates complete runnable Python files.

### Pre-built Slot Types

| Slot Type | Purpose |
|-----------|---------|
| `packet_extractor` | Extract structured evidence packets from raw text |
| `doctrine_evaluator` | Evaluate doctrine quality and consistency |
| `contradiction_detector` | Detect contradictions between doctrines |

### Usage

```python
from chip_labs.dspy_slot import scaffold_dspy_slot

# Add a DSPy slot to an existing chip
scaffold_dspy_slot(chip_path, "packet_extractor")

# Or enable during scaffold
brief = {
    "domain_id": "my-domain",
    "dspy_enabled": True,
    "dspy_slot_type": "doctrine_evaluator",  # optional, defaults to packet_extractor
    ...
}
scaffold_chip(brief, output_dir)
```

### What Gets Created

- `src/{module}/dspy_slot_{type}.py` -- Complete runnable DSPy script
- `data/dspy_training_{type}.jsonl` -- Placeholder training data
- `dspy_config.json` -- Slot configuration

### Detection

The v2 rubric's `has_dspy_integration` check detects:
- Files matching `*dspy*` in the chip
- `dspy_config.json`
- Import statements or references to dspy in Python files

---

## Loop Controller Integration

The `RecursiveLoopController` now includes **Phase 5: Skill Regeneration** after the main improvement loop:

```
Brief -> Scaffold -> Score -> [Loop: Fix -> Research -> Evaluate -> Suggest -> Evidence] -> Skill Regeneration -> Mature Chip
```

Phase 5 calls `refresh_skill()` to rebuild all intelligence delivery artifacts from the latest accumulated evidence. This ensures the skill file always reflects the chip's current state.

---

## How It All Connects

```
                    ┌─────────────────────┐
                    │   Domain Chip Dir   │
                    │                     │
                    │  research/          │ Evidence accumulation
                    │  docs/              │ Doctrines, contradictions
                    │  score_history.jsonl│ Run history
                    │  dspy_config.json   │ DSPy integration
                    └────────┬────────────┘
                             │
                    ┌────────▼────────────┐
                    │  extract_intelligence│ Reads everything
                    └────────┬────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───┐  ┌──────▼──────┐ ┌─────▼──────┐
     │chip_skill.md│  │chip_context │ │  doctrine  │
     │ (for humans │  │  .json      │ │  digest.md │
     │  and Claude)│  │(for systems)│ │(for review)│
     └─────────────┘  └─────────────┘ └────────────┘
              │
     ┌────────▼────────┐
     │  serve_context() │ Query-based retrieval
     │  "What do I know │
     │  about X?"       │
     └──────────────────┘
```

---

## Production Readiness Criteria (V2)

A domain chip is production-ready (score >= 80) when:

1. **Manifest is valid** (15/15) -- spark-chip.v1 schema, all hooks, frontier config
2. **Evidence is real** (15/15) -- Files exist in research subdirectories per lane
3. **Evaluation is deep** (15/15) -- Real scoring logic with numeric returns, URL-backed sources
4. **Memory is active** (10/10) -- Source registry, Obsidian vault with pages, memory backend
5. **Integration is healthy** (10/10) -- Project JSON, guardrails, self-edit config
6. **Documentation has substance** (10/10) -- README >200 chars, mission/arch >150 chars each
7. **Flywheel is producing** (>= 5/25 minimum, ideally 15+/25) -- Run history, belief promotion, DSPy, skill file
