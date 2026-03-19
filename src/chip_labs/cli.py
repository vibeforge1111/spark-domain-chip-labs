"""CLI entry point for the Spark Domain Chip Labs meta-chip.

Implements the four spark-hook-io.v1 hooks:
  evaluate  -- Score chip quality or lab research progress
  suggest   -- Suggest next research directions
  packets   -- Emit methodology and quality documents
  watchtower -- Generate Obsidian pages for lab observatory
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from .evaluate import evaluate as run_evaluate
from .suggest import suggest as run_suggest
from .packets import generate_packets
from .watchtower import generate_watchtower_pages


def _load_input(input_path: str | None) -> dict[str, Any]:
    """Load input JSON from file path or return empty dict."""
    if not input_path or not Path(input_path).exists():
        return {}
    try:
        return json.loads(Path(input_path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _write_output(output_path: str | None, data: Any) -> None:
    """Write output JSON to file path or stdout."""
    output_json = json.dumps(data, indent=2, default=str)
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(output_json, encoding="utf-8")
    else:
        print(output_json)


def _get_chip_search_dir() -> str | None:
    """Get the chip search directory from environment or default."""
    return os.environ.get("SPARK_CHIP_SEARCH_DIR", None)


# ---------------------------------------------------------------------------
# Hook: evaluate
# ---------------------------------------------------------------------------

def cmd_evaluate(args: argparse.Namespace) -> None:
    """Run the meta-evaluator."""
    input_data = _load_input(args.input)
    mutations = input_data.get("mutations", {})
    chip_search_dir = _get_chip_search_dir()

    result = run_evaluate(mutations, chip_search_dir)

    # Print metrics in spark-researcher ledger format
    print(f"lab_research_quality_score: {result['lab_research_quality_score']}")
    print(f"portfolio_health: {result['portfolio_health']}")
    print(f"methodology_coverage: {result['methodology_coverage']}")
    print(f"chips_evaluated: {result['chips_evaluated']}")
    print(f"graduation_pipeline_count: {result['graduation_pipeline_count']}")

    # Write full result to output file
    _write_output(args.output, result)


# ---------------------------------------------------------------------------
# Hook: suggest
# ---------------------------------------------------------------------------

def cmd_suggest(args: argparse.Namespace) -> None:
    """Suggest next research directions."""
    input_data = _load_input(args.input)
    recent_mutations = input_data.get("recent_mutations", [])
    chip_search_dir = _get_chip_search_dir()

    suggestions = run_suggest(recent_mutations, chip_search_dir)

    # Write suggestions to output
    _write_output(args.output, {"suggestions": suggestions, "count": len(suggestions)})


# ---------------------------------------------------------------------------
# Hook: packets
# ---------------------------------------------------------------------------

def cmd_packets(args: argparse.Namespace) -> None:
    """Generate lab research packets."""
    input_data = _load_input(args.input)
    mutations = input_data.get("mutations", {})
    chip_search_dir = _get_chip_search_dir()

    packets = generate_packets(mutations, chip_search_dir)

    _write_output(args.output, {"packets": packets, "count": len(packets)})


# ---------------------------------------------------------------------------
# Hook: watchtower
# ---------------------------------------------------------------------------

def cmd_watchtower(args: argparse.Namespace) -> None:
    """Generate Obsidian pages for lab observatory."""
    input_data = _load_input(args.input)
    mutations = input_data.get("mutations", {})
    chip_search_dir = _get_chip_search_dir()
    vault_dir = input_data.get("vault_dir", "obsidian-vault")

    pages = generate_watchtower_pages(mutations, chip_search_dir, vault_dir)

    # Write pages to vault directory
    vault_path = Path(vault_dir)
    vault_path.mkdir(parents=True, exist_ok=True)
    for page in pages:
        page_path = vault_path / page["path"]
        page_path.parent.mkdir(parents=True, exist_ok=True)
        page_path.write_text(page["content"], encoding="utf-8")

    _write_output(args.output, {"pages": [p["path"] for p in pages], "count": len(pages)})


# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------

def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="chip-labs",
        description="Spark Domain Chip Labs -- meta-research chip for domain chip R&D.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # evaluate
    p_eval = sub.add_parser("evaluate", help="Score chip quality or lab research progress.")
    p_eval.add_argument("--input", type=str, default=None, help="Input JSON file path.")
    p_eval.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_eval.set_defaults(func=cmd_evaluate)

    # suggest
    p_suggest = sub.add_parser("suggest", help="Suggest next research directions.")
    p_suggest.add_argument("--input", type=str, default=None, help="Input JSON file path.")
    p_suggest.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_suggest.set_defaults(func=cmd_suggest)

    # packets
    p_packets = sub.add_parser("packets", help="Generate lab research packets.")
    p_packets.add_argument("--input", type=str, default=None, help="Input JSON file path.")
    p_packets.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_packets.set_defaults(func=cmd_packets)

    # watchtower
    p_wt = sub.add_parser("watchtower", help="Generate Obsidian pages for lab observatory.")
    p_wt.add_argument("--input", type=str, default=None, help="Input JSON file path.")
    p_wt.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_wt.set_defaults(func=cmd_watchtower)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
