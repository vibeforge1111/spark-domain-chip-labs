"""Scaffold engine for generating new domain chips.

Generates a complete, functional chip directory from a domain brief,
targeting a quality rubric score of 45-50 out of 100 immediately.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Domain brief schema
# ---------------------------------------------------------------------------

def load_brief(brief_path: str | Path) -> dict[str, Any]:
    """Load a domain brief from YAML-like JSON or dict."""
    brief_path = Path(brief_path)
    if brief_path.suffix in (".yaml", ".yml"):
        # Simple YAML-like parser (no external deps)
        return _parse_simple_yaml(brief_path.read_text(encoding="utf-8"))
    return json.loads(brief_path.read_text(encoding="utf-8"))


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Minimal YAML subset parser - handles flat keys, lists, nested dicts.

    Supports:
    - key: value
    - key:
        - item1
        - item2
    - key:
        nested_key: value
    """
    result: dict[str, Any] = {}
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        indent = len(line) - len(line.lstrip())
        if indent > 0 and ":" in stripped:
            i += 1
            continue

        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if value:
                result[key] = value
            else:
                # Check if next lines are list items or nested dict
                items = []
                nested = {}
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    next_stripped = next_line.strip()
                    next_indent = len(next_line) - len(next_line.lstrip())

                    if not next_stripped or next_stripped.startswith("#"):
                        j += 1
                        continue
                    if next_indent <= indent:
                        break

                    if next_stripped.startswith("- "):
                        item_text = next_stripped[2:].strip().strip('"').strip("'")
                        # Check if it's a dict item (- name: value)
                        if ":" in item_text and not item_text.startswith("http"):
                            item_dict = {}
                            dk, _, dv = item_text.partition(":")
                            item_dict[dk.strip()] = dv.strip().strip('"').strip("'")
                            # Read continuation lines for this dict item
                            k = j + 1
                            while k < len(lines):
                                cont = lines[k]
                                cont_stripped = cont.strip()
                                cont_indent = len(cont) - len(cont.lstrip())
                                if not cont_stripped:
                                    k += 1
                                    continue
                                if cont_indent <= next_indent:
                                    break
                                if ":" in cont_stripped and not cont_stripped.startswith("- "):
                                    ck, _, cv = cont_stripped.partition(":")
                                    cv = cv.strip().strip('"').strip("'")
                                    if cv.startswith("[") and cv.endswith("]"):
                                        cv = [x.strip().strip('"').strip("'") for x in cv[1:-1].split(",")]
                                    item_dict[ck.strip()] = cv
                                k += 1
                            j = k
                            items.append(item_dict)
                            continue
                        items.append(item_text)
                    elif ":" in next_stripped:
                        nk, _, nv = next_stripped.partition(":")
                        nv = nv.strip().strip('"').strip("'")
                        if nv.startswith("[") and nv.endswith("]"):
                            nv = [x.strip().strip('"').strip("'") for x in nv[1:-1].split(",")]
                        nested[nk.strip()] = nv
                    j += 1

                if items:
                    result[key] = items
                elif nested:
                    result[key] = nested
                else:
                    result[key] = ""
                i = j
                continue
        i += 1

    return result


def validate_brief(brief: dict[str, Any]) -> list[str]:
    """Validate a domain brief, returning list of errors (empty = valid)."""
    errors = []
    if not brief.get("domain_id"):
        errors.append("domain_id is required")
    if not brief.get("domain_name"):
        errors.append("domain_name is required")
    if not brief.get("mutation_axes"):
        errors.append("mutation_axes is required (list of {name, values})")
    if not brief.get("primary_metric"):
        errors.append("primary_metric is required")
    return errors


# ---------------------------------------------------------------------------
# File generators
# ---------------------------------------------------------------------------

def _sanitize_module_name(domain_id: str) -> str:
    """Convert domain-id to valid Python module name."""
    return re.sub(r"[^a-z0-9_]", "_", domain_id.lower().replace("-", "_"))


def _gen_manifest(brief: dict[str, Any]) -> dict[str, Any]:
    """Generate spark-chip.json from brief."""
    module = _sanitize_module_name(brief["domain_id"])
    domain_id = brief["domain_id"]

    # Build allowed_mutations
    allowed_mutations = {}
    for axis in brief.get("mutation_axes", []):
        name = axis["name"] if isinstance(axis, dict) else axis
        values = axis.get("values", []) if isinstance(axis, dict) else []
        allowed_mutations[name] = values

    # Build field_patterns
    field_patterns = {}
    for axis_name in allowed_mutations:
        # Create a regex pattern that matches the allowed values
        values = allowed_mutations[axis_name]
        if values:
            pattern = "^(" + "|".join(re.escape(v) for v in values) + ")$"
            field_patterns[axis_name] = pattern

    return {
        "schema_version": "spark-chip.v1",
        "io_protocol": "spark-hook-io.v1",
        "name": brief.get("domain_name", domain_id),
        "version": "0.0.1",
        "domain": brief.get("category", "general"),
        "description": brief.get("description", f"Domain chip for {brief.get('domain_name', domain_id)}"),
        "capabilities": ["evaluate", "suggest", "packets", "watchtower"],
        "commands": {
            "evaluate": f"python -m {module} evaluate --input {{input}} --output {{output}}",
            "suggest": f"python -m {module} suggest --input {{input}} --output {{output}}",
            "packets": f"python -m {module} packets --input {{input}} --output {{output}}",
            "watchtower": f"python -m {module} watchtower --input {{input}} --output {{output}}",
        },
        "frontier": {
            "enabled": True,
            "web_search": True,
            "model": "generic",
            "allowed_mutations": allowed_mutations,
            "required_fields": list(allowed_mutations.keys())[:3] if allowed_mutations else [],
            "field_patterns": field_patterns,
        },
        "prompt_hints": [
            f"This chip evaluates {brief.get('domain_name', domain_id)} using mutation-based exploration.",
            f"Primary metric: {brief.get('primary_metric', 'domain_score')}",
            "Use evidence lanes: research_grounded, benchmark_grounded, exploratory_frontier, realworld_validated.",
        ],
    }


def _gen_project_json(brief: dict[str, Any]) -> dict[str, Any]:
    """Generate spark-researcher.project.json from brief."""
    domain_id = brief["domain_id"]
    module = _sanitize_module_name(domain_id)
    primary_metric = brief.get("primary_metric", "domain_score")

    # Build candidate trials: baseline + 2 variants
    trials = [
        {
            "id": "global-baseline",
            "label": "Global baseline (no mutations)",
            "mutations": {},
        },
    ]

    axes = brief.get("mutation_axes", [])
    for i, axis in enumerate(axes[:2]):
        name = axis["name"] if isinstance(axis, dict) else axis
        values = axis.get("values", []) if isinstance(axis, dict) else []
        if values:
            trials.append({
                "id": f"variant-{name}-{values[0]}",
                "label": f"Variant: {name}={values[0]}",
                "mutations": {name: values[0]},
            })

    # Ensure at least 3 trials
    while len(trials) < 3:
        trials.append({
            "id": f"variant-{len(trials)}",
            "label": f"Variant {len(trials)}",
            "mutations": {},
        })

    return {
        "project_name": f"domain-chip-{domain_id}",
        "project_root": ".",
        "chip": {
            "path": ".",
            "manifest": "spark-chip.json",
        },
        "eval_metric": primary_metric,
        "eval_goal": "maximize",
        "metrics": {
            primary_metric: {"type": "float", "goal": "maximize"},
            "evidence_quality": {"type": "float", "goal": "maximize"},
            "coverage_breadth": {"type": "float", "goal": "maximize"},
        },
        "commands": {
            "evaluate": {
                "kind": "chip-evaluate",
                "run": f"python -m {module} evaluate --input {{input}} --output {{output}}",
            },
            "suggest": {
                "kind": "chip-suggest",
                "run": f"python -m {module} suggest --input {{input}} --output {{output}}",
            },
        },
        "candidate_trials": trials,
        "mutable_parameters": list({a["name"] if isinstance(a, dict) else a for a in axes}),
        "mutable_targets": [f"src/{module}/evaluate.py", f"src/{module}/suggest.py"],
        "guardrails": {
            "max_loop_iterations": 8,
            "consecutive_discard_limit": 3,
            "blocked_command_fragments": ["rm -rf", "sudo", "DROP TABLE", "format", "> /dev"],
            "require_clean_git": True,
            "require_human_approval_for_self_edit": True,
        },
        "self_edit": {
            "enabled": True,
            "git_mode": "manual",
            "branch_prefix": "self-edit/",
            "auto_push": False,
            "mutable_targets": [f"src/{module}/evaluate.py", f"src/{module}/suggest.py"],
        },
        "memory": {
            "backend": "local",
        },
        "trainers": {},
    }


def _gen_pyproject(brief: dict[str, Any]) -> str:
    """Generate pyproject.toml."""
    domain_id = brief["domain_id"]
    module = _sanitize_module_name(domain_id)
    name = brief.get("domain_name", domain_id)

    return f'''[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "domain-chip-{domain_id}"
version = "0.0.1"
description = "Domain chip for {name}"
requires-python = ">= 3.10"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-dir]
"" = "src"

[project.scripts]
{domain_id} = "{module}.cli:main"
'''


def _gen_readme(brief: dict[str, Any]) -> str:
    """Generate README.md."""
    domain_id = brief["domain_id"]
    name = brief.get("domain_name", domain_id)
    desc = brief.get("description", f"Domain intelligence chip for {name}")
    primary_metric = brief.get("primary_metric", "domain_score")

    axes_text = ""
    for axis in brief.get("mutation_axes", []):
        aname = axis["name"] if isinstance(axis, dict) else axis
        values = axis.get("values", []) if isinstance(axis, dict) else []
        axes_text += f"- **{aname}**: {', '.join(values[:5])}\n"

    return f'''# domain-chip-{domain_id}

> {desc}

## Mission

What this is: A domain chip following the `spark-chip.v1` contract for {name}.

This chip uses mutation-based exploration to build domain intelligence through
recursive evaluation loops.

## Quick Start

```bash
# Evaluate with default mutations
python -m {_sanitize_module_name(domain_id)} evaluate --input input.json --output output.json

# Get suggestions for next research directions
python -m {_sanitize_module_name(domain_id)} suggest --input input.json --output output.json

# Generate evidence packets
python -m {_sanitize_module_name(domain_id)} packets --input input.json --output output.json

# Update Obsidian watchtower
python -m {_sanitize_module_name(domain_id)} watchtower --input input.json --output output.json
```

## Primary Metric

**{primary_metric}** — The main evaluation metric for this domain.

## Mutation Axes

{axes_text}

## Evidence Lanes

- **research_grounded**: Knowledge from primary sources and literature
- **benchmark_grounded**: Validated against reproducible benchmarks
- **exploratory_frontier**: Novel hypotheses and untested ideas
- **realworld_validated**: Confirmed by real-world outcomes

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the one-loop specification.

## Contract

- Schema: `spark-chip.v1`
- Protocol: `spark-hook-io.v1`
- Hooks: evaluate, suggest, packets, watchtower
- Dependencies: Zero external dependencies
'''


def _gen_cli(brief: dict[str, Any]) -> str:
    """Generate cli.py (100% boilerplate hook routing)."""
    module = _sanitize_module_name(brief["domain_id"])

    return f'''"""CLI entry point for domain-chip-{brief["domain_id"]}.

Implements the four spark-hook-io.v1 hooks:
  evaluate   -- Score domain candidates
  suggest    -- Suggest next research directions
  packets    -- Emit evidence packets
  watchtower -- Generate Obsidian pages
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .lab_hooks import (
    generate_packets,
    generate_watchtower_pages,
    run_evaluate,
    run_suggest,
)


def _load_input(input_path: str | None) -> dict[str, Any]:
    """Load input JSON from file path or return empty dict."""
    if not input_path or not Path(input_path).exists():
        return {{}}
    try:
        return json.loads(Path(input_path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {{}}


def _write_output(output_path: str | None, data: Any) -> None:
    """Write output JSON to file path or stdout."""
    output_json = json.dumps(data, indent=2, default=str)
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(output_json, encoding="utf-8")
    else:
        print(output_json)


def cmd_evaluate(args: argparse.Namespace) -> None:
    input_data = _load_input(args.input)
    mutations = input_data.get("mutations", {{}})
    result = run_evaluate(mutations)
    metric = result.get("metrics", {{}}).get("{brief.get("primary_metric", "domain_score")}", 0)
    print(f"{brief.get("primary_metric", "domain_score")}: {{metric}}")
    _write_output(args.output, result)


def cmd_suggest(args: argparse.Namespace) -> None:
    input_data = _load_input(args.input)
    recent = input_data.get("recent_mutations", [])
    suggestions = run_suggest(recent)
    _write_output(args.output, {{"suggestions": suggestions, "count": len(suggestions)}})


def cmd_packets(args: argparse.Namespace) -> None:
    input_data = _load_input(args.input)
    mutations = input_data.get("mutations", {{}})
    packets = generate_packets(mutations)
    _write_output(args.output, {{"packets": packets, "count": len(packets)}})


def cmd_watchtower(args: argparse.Namespace) -> None:
    input_data = _load_input(args.input)
    mutations = input_data.get("mutations", {{}})
    vault_dir = input_data.get("vault_dir", "obsidian-vault")
    pages = generate_watchtower_pages(mutations, vault_dir)
    vault_path = Path(vault_dir)
    vault_path.mkdir(parents=True, exist_ok=True)
    for page in pages:
        page_path = vault_path / page["path"]
        page_path.parent.mkdir(parents=True, exist_ok=True)
        page_path.write_text(page["content"], encoding="utf-8")
    _write_output(args.output, {{"pages": [p["path"] for p in pages], "count": len(pages)}})


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="{brief["domain_id"]}",
        description="Domain chip for {brief.get("domain_name", brief["domain_id"])}.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for name, func in [("evaluate", cmd_evaluate), ("suggest", cmd_suggest),
                       ("packets", cmd_packets), ("watchtower", cmd_watchtower)]:
        p = sub.add_parser(name)
        p.add_argument("--input", type=str, default=None)
        p.add_argument("--output", type=str, default=None)
        p.set_defaults(func=func)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
'''


def _gen_evaluate(brief: dict[str, Any]) -> str:
    """Generate evaluate.py with additive mutation scoring."""
    primary_metric = brief.get("primary_metric", "domain_score")
    axes = brief.get("mutation_axes", [])

    # Build dimension scoring dicts
    dim_lines = []
    for axis in axes:
        name = axis["name"] if isinstance(axis, dict) else axis
        values = axis.get("values", []) if isinstance(axis, dict) else []
        entries = ", ".join(f'"{v}": {(i + 1) * 2}' for i, v in enumerate(values[:5]))
        dim_lines.append(f'    "{name}": {{{entries}}},')

    dims_str = "\n".join(dim_lines) if dim_lines else '    # Add dimension scoring here'

    return f'''"""Evaluate hook for domain-chip-{brief["domain_id"]}.

Implements a deterministic additive mutation scoring model.
Evidence lanes: research_grounded, benchmark_grounded, exploratory_frontier, realworld_validated.
"""

from __future__ import annotations

from typing import Any


BASE_SCORE = 50

# Dimension scoring: mutation value -> score delta
DIMENSIONS: dict[str, dict[str, int]] = {{
{dims_str}
}}

# Pair bonuses: ((dim_a, val_a), (dim_b, val_b)) -> bonus
PAIR_BONUSES: dict[tuple, int] = {{
    # Add pair synergies as domain knowledge grows
}}


def _classify_evidence_lane(mutations: dict[str, Any]) -> str:
    """Classify the evidence lane based on mutation context."""
    if not mutations:
        return "benchmark_grounded"
    return "exploratory_frontier"


def score_candidate(mutations: dict[str, Any]) -> dict[str, Any]:
    """Score a mutation combination using the additive model.

    Returns scoring breakdown with evidence lane classification.
    """
    score = BASE_SCORE
    breakdown = {{}}

    for dim_name, dim_values in DIMENSIONS.items():
        val = mutations.get(dim_name)
        if val and val in dim_values:
            delta = dim_values[val]
            score += delta
            breakdown[dim_name] = {{"value": val, "delta": delta}}

    for (key, bonus) in PAIR_BONUSES.items():
        # Pair bonus format to be defined per domain
        pass

    score = max(0, min(100, score))

    return {{
        "score": score,
        "breakdown": breakdown,
        "evidence_lane": _classify_evidence_lane(mutations),
    }}


def evaluate(mutations: dict[str, Any]) -> dict[str, Any]:
    """Main evaluate hook entry point."""
    result = score_candidate(mutations)

    verdict = "approve" if result["score"] >= 70 else "defer" if result["score"] >= 40 else "reject"

    return {{
        "returncode": 0,
        "stdout": "",
        "stderr": "",
        "metrics": {{
            "{primary_metric}": result["score"],
            "evidence_quality": 0.5,
            "coverage_breadth": 0.3,
        }},
        "result": {{
            "claim": f"Candidate scored {{result['score']}}/100",
            "verdict": verdict,
            "mechanism": "additive_mutation_scoring",
            "boundary": "Score range 0-100, approve >= 70, defer >= 40",
            "recommended_next_step": "Run benchmark validation" if verdict == "approve" else "Explore alternative mutations",
            "evidence_lane": result["evidence_lane"],
        }},
    }}
'''


def _gen_suggest(brief: dict[str, Any]) -> str:
    """Generate suggest.py with gap-driven suggestion engine."""
    axes = brief.get("mutation_axes", [])

    axis_lines = []
    for a in axes:
        name = a["name"] if isinstance(a, dict) else a
        values = a.get("values", []) if isinstance(a, dict) else []
        axis_lines.append(f'    "{name}": {json.dumps(values)},')
    axis_block = "\n".join(axis_lines)

    return f'''"""Suggest hook for domain-chip-{brief["domain_id"]}.

Generates mutation candidates based on coverage gaps and frontier exploration.
"""

from __future__ import annotations

from typing import Any


# Mutation axes and their values (from domain brief)
MUTATION_SPACE: dict[str, list[str]] = {{
{axis_block}
}}


def _find_coverage_gaps(recent_mutations: list[dict]) -> list[dict[str, Any]]:
    """Identify underexplored regions of the mutation space."""
    explored = set()
    for m in recent_mutations:
        muts = m.get("mutations", {{}})
        for k, v in muts.items():
            explored.add((k, v))

    gaps = []
    for axis, values in MUTATION_SPACE.items():
        for val in values:
            if (axis, val) not in explored:
                gaps.append({{"axis": axis, "value": val}})
    return gaps


def suggest(recent_mutations: list[dict]) -> list[dict[str, Any]]:
    """Generate suggestion candidates.

    Strategy:
    1. Find coverage gaps in the mutation space
    2. Prioritize underexplored axes
    3. Return top candidates with rationale
    """
    suggestions = []
    gaps = _find_coverage_gaps(recent_mutations)

    # Group gaps by axis for prioritization
    axis_gaps: dict[str, list] = {{}}
    for g in gaps:
        axis_gaps.setdefault(g["axis"], []).append(g["value"])

    # Generate candidates from most-gapped axes first
    for axis, values in sorted(axis_gaps.items(), key=lambda x: -len(x[1])):
        for val in values[:2]:  # Top 2 per axis
            suggestions.append({{
                "mutations": {{axis: val}},
                "rationale": f"Underexplored: {{axis}}={{val}} ({{len(values)}} gaps in this axis)",
                "priority": "high" if len(values) > 3 else "medium",
                "evidence_lane": "exploratory_frontier",
            }})

    return suggestions[:10]  # Cap at 10 suggestions
'''


def _gen_packets(brief: dict[str, Any]) -> str:
    """Generate packets.py with evidence-lane-tagged emitter."""
    return f'''"""Packets hook for domain-chip-{brief["domain_id"]}.

Emits evidence packets tagged with evidence lanes.
Packet types: research_grounded, benchmark_grounded, exploratory_frontier, realworld_validated.
"""

from __future__ import annotations

import datetime
from typing import Any


def _make_packet(
    packet_type: str,
    title: str,
    content: str,
    evidence_lane: str,
    metadata: dict | None = None,
) -> dict[str, Any]:
    """Create a standardized evidence packet."""
    return {{
        "type": packet_type,
        "title": title,
        "content": content,
        "evidence_lane": evidence_lane,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "metadata": metadata or {{}},
    }}


def generate_packets(mutations: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate evidence packets for current state.

    Packet categories:
    - Domain methodology documents (research_grounded)
    - Benchmark results and comparisons (benchmark_grounded)
    - Frontier exploration notes (exploratory_frontier)
    - Real-world validation reports (realworld_validated)
    """
    packets = []

    # Methodology packet
    packets.append(_make_packet(
        packet_type="methodology",
        title="Domain Evaluation Methodology",
        content="Additive mutation scoring with dimension deltas and pair bonuses.",
        evidence_lane="research_grounded",
    ))

    # Benchmark packet stub
    packets.append(_make_packet(
        packet_type="benchmark",
        title="Baseline Benchmark",
        content="Baseline scoring with empty mutations establishes the floor.",
        evidence_lane="benchmark_grounded",
    ))

    # Frontier packet
    if mutations:
        packets.append(_make_packet(
            packet_type="frontier",
            title=f"Frontier Exploration: {{list(mutations.keys())}}",
            content=f"Exploring mutations: {{mutations}}",
            evidence_lane="exploratory_frontier",
        ))

    return packets
'''


def _gen_watchtower(brief: dict[str, Any]) -> str:
    """Generate watchtower.py with Obsidian page templates."""
    name = brief.get("domain_name", brief["domain_id"])

    return f'''"""Watchtower hook for domain-chip-{brief["domain_id"]}.

Generates Obsidian pages for domain observatory.
"""

from __future__ import annotations

from typing import Any


def generate_watchtower_pages(
    mutations: dict[str, Any],
    vault_dir: str = "obsidian-vault",
) -> list[dict[str, Any]]:
    """Generate Obsidian markdown pages for the domain observatory."""
    pages = []

    # Home page
    pages.append({{
        "path": "Home.md",
        "content": """# {name} Observatory

## Overview
Domain intelligence chip for {name}.

## Evidence Lanes
- **research_grounded**: Primary source research
- **benchmark_grounded**: Reproducible benchmarks
- **exploratory_frontier**: Novel hypotheses
- **realworld_validated**: Real-world outcomes

## Navigation
- [[Leaderboard]] - Top scoring candidates
- [[Research Log]] - Evidence gathering history
- [[Frontier Status]] - Exploration progress
""",
    }})

    # Leaderboard page
    pages.append({{
        "path": "Leaderboard.md",
        "content": """# Leaderboard

## Top Candidates

| Rank | Candidate | Score | Evidence Lane | Verdict |
|------|-----------|-------|---------------|---------|
| 1 | Baseline | 50 | benchmark_grounded | defer |

## Scoring History
_Updated by watchtower hook on each evaluation cycle._
""",
    }})

    # Research Log
    pages.append({{
        "path": "Research Log.md",
        "content": """# Research Log

## Recent Research
_Populated by packets hook as evidence is gathered._

## Source Registry
See [docs/SOURCE_REGISTRY.md](../docs/SOURCE_REGISTRY.md) for primary sources.
""",
    }})

    return pages
'''


def _gen_tests(brief: dict[str, Any]) -> dict[str, str]:
    """Generate test files for all 4 hooks."""
    module = _sanitize_module_name(brief["domain_id"])

    tests = {}

    tests["test_evaluate.py"] = f'''"""Smoke tests for evaluate hook."""

import json
from {module}.evaluate import evaluate, score_candidate


def test_evaluate_empty_mutations():
    result = evaluate({{}})
    assert result["returncode"] == 0
    assert "{brief.get("primary_metric", "domain_score")}" in result["metrics"]
    assert result["result"]["verdict"] in ("approve", "defer", "reject")
    assert result["result"]["evidence_lane"] in (
        "research_grounded", "benchmark_grounded",
        "exploratory_frontier", "realworld_validated",
    )


def test_score_candidate_baseline():
    result = score_candidate({{}})
    assert result["score"] == 50  # BASE_SCORE
    assert result["evidence_lane"] == "benchmark_grounded"


def test_evaluate_returns_valid_json():
    result = evaluate({{}})
    # Ensure JSON-serializable
    json.dumps(result)
'''

    tests["test_suggest.py"] = f'''"""Smoke tests for suggest hook."""

from {module}.suggest import suggest


def test_suggest_with_no_history():
    suggestions = suggest([])
    assert isinstance(suggestions, list)
    for s in suggestions:
        assert "mutations" in s
        assert "rationale" in s
        assert "evidence_lane" in s


def test_suggest_respects_cap():
    suggestions = suggest([])
    assert len(suggestions) <= 10
'''

    tests["test_packets.py"] = f'''"""Smoke tests for packets hook."""

from {module}.packets import generate_packets


def test_packets_baseline():
    packets = generate_packets({{}})
    assert isinstance(packets, list)
    assert len(packets) >= 1
    for p in packets:
        assert "type" in p
        assert "evidence_lane" in p
        assert p["evidence_lane"] in (
            "research_grounded", "benchmark_grounded",
            "exploratory_frontier", "realworld_validated",
        )


def test_packets_with_mutations():
    packets = generate_packets({{"test": "value"}})
    lanes = {{p["evidence_lane"] for p in packets}}
    assert "exploratory_frontier" in lanes
'''

    tests["test_watchtower.py"] = f'''"""Smoke tests for watchtower hook."""

from {module}.watchtower import generate_watchtower_pages


def test_watchtower_generates_pages():
    pages = generate_watchtower_pages({{}})
    assert isinstance(pages, list)
    assert len(pages) >= 1
    for p in pages:
        assert "path" in p
        assert "content" in p
        assert p["path"].endswith(".md")
'''

    return tests


def _gen_docs(brief: dict[str, Any]) -> dict[str, str]:
    """Generate docs/ directory content."""
    name = brief.get("domain_name", brief["domain_id"])
    primary_metric = brief.get("primary_metric", "domain_score")

    docs = {}

    docs["MISSION.md"] = f'''# Mission: {name}

## Intent
Build domain intelligence for {name} through recursive mutation-based exploration.

## Success Criteria
- Quality rubric score >= 80 (production_ready)
- Evidence across all 4 lanes
- Benchmark validation passing
- Real-world validation initiated

## Primary Metric
**{primary_metric}** — measured by the evaluate hook scoring model.
'''

    docs["ARCHITECTURE.md"] = f'''# Architecture: {name}

## One-Loop Specification

### Always-On Stages
1. **Evaluate**: Score current mutations using additive model
2. **Quality Gate**: Check score against thresholds
3. **Memory Update**: Persist results to local memory
4. **Watchtower Update**: Refresh Obsidian observatory pages

### Conditional Stages
- **Research Frontier**: When coverage gaps detected
- **Benchmark Validation**: When candidates score above promote threshold
- **Real-World Check**: When benchmark-validated candidates exist

### Loop Constraints
- Max 8 iterations per pass
- Consecutive discard limit: 3
- Require clean git for self-edits

## Evidence Lanes
- research_grounded -> benchmark_grounded -> realworld_validated
- exploratory_frontier feeds into research_grounded when validated
'''

    docs["SOURCE_REGISTRY.md"] = f'''# Source Registry: {name}

## Primary Sources
_Add authoritative sources for this domain here._

| Source | Type | Reliability | Notes |
|--------|------|-------------|-------|
| | | | |

## Research Seed URLs
_Add URLs for initial research here._

## Benchmark Data
_Add benchmark datasets or references here._
'''

    return docs


# ---------------------------------------------------------------------------
# Main scaffold function
# ---------------------------------------------------------------------------

def scaffold_chip(
    brief: dict[str, Any],
    output_dir: str | Path | None = None,
) -> Path:
    """Generate a complete domain chip directory from a brief.

    Args:
        brief: Domain brief dict with domain_id, domain_name, mutation_axes, etc.
        output_dir: Where to create the chip directory. Defaults to current dir.

    Returns:
        Path to the generated chip directory.
    """
    errors = validate_brief(brief)
    if errors:
        raise ValueError(f"Invalid brief: {'; '.join(errors)}")

    domain_id = brief["domain_id"]
    module = _sanitize_module_name(domain_id)

    if output_dir is None:
        output_dir = Path.cwd()
    output_dir = Path(output_dir)

    chip_dir = output_dir / f"domain-chip-{domain_id}"
    chip_dir.mkdir(parents=True, exist_ok=True)

    # 1. spark-chip.json (manifest)
    manifest = _gen_manifest(brief)
    (chip_dir / "spark-chip.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    # 2. spark-researcher.project.json
    project = _gen_project_json(brief)
    (chip_dir / "spark-researcher.project.json").write_text(
        json.dumps(project, indent=2), encoding="utf-8"
    )

    # 3. pyproject.toml
    (chip_dir / "pyproject.toml").write_text(
        _gen_pyproject(brief), encoding="utf-8"
    )

    # 4. README.md
    (chip_dir / "README.md").write_text(
        _gen_readme(brief), encoding="utf-8"
    )

    # 5. src/{module}/ with all hooks
    src_dir = chip_dir / "src" / module
    src_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "__init__.py").write_text(
        f'"""Domain chip: {brief.get("domain_name", domain_id)}."""\n',
        encoding="utf-8",
    )
    (src_dir / "cli.py").write_text(_gen_cli(brief), encoding="utf-8")
    (src_dir / "evaluate.py").write_text(_gen_evaluate(brief), encoding="utf-8")
    (src_dir / "suggest.py").write_text(_gen_suggest(brief), encoding="utf-8")
    (src_dir / "packets.py").write_text(_gen_packets(brief), encoding="utf-8")
    (src_dir / "watchtower.py").write_text(_gen_watchtower(brief), encoding="utf-8")

    # 6. Tests
    test_dir = chip_dir / "tests"
    test_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / "__init__.py").write_text("", encoding="utf-8")
    for test_name, test_content in _gen_tests(brief).items():
        (test_dir / test_name).write_text(test_content, encoding="utf-8")

    # 7. Docs
    docs_dir = chip_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    for doc_name, doc_content in _gen_docs(brief).items():
        (docs_dir / doc_name).write_text(doc_content, encoding="utf-8")

    # 8. Obsidian vault with initial content
    vault_dir = chip_dir / "obsidian-vault"
    vault_dir.mkdir(parents=True, exist_ok=True)
    (vault_dir / "README.md").write_text(
        f"# {brief.get('domain_name', domain_id)} Observatory\n\nGenerated by chip scaffold.\n",
        encoding="utf-8",
    )

    # 9. Data directory
    data_dir = chip_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "README.md").write_text(
        "# Data\n\nDomain-specific data assets go here.\n",
        encoding="utf-8",
    )

    # 10. Research directory
    research_dir = chip_dir / "research"
    research_dir.mkdir(parents=True, exist_ok=True)
    (research_dir / "packets").mkdir(parents=True, exist_ok=True)
    (research_dir / "sources").mkdir(parents=True, exist_ok=True)

    # 11. Optional DSPy slot generation
    if brief.get("dspy_enabled", False):
        from .dspy_slot import scaffold_dspy_slot

        slot_type = brief.get("dspy_slot_type", "packet_extractor")
        try:
            scaffold_dspy_slot(chip_dir, slot_type)
        except Exception:
            pass  # Non-fatal: DSPy slot is optional enhancement

    return chip_dir
