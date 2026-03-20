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
from .quality_rubric import score_chip


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
# Command: scaffold
# ---------------------------------------------------------------------------

def cmd_scaffold(args: argparse.Namespace) -> None:
    """Scaffold a new domain chip from a brief."""
    from .scaffold import load_brief, scaffold_chip, validate_brief
    from .category_templates import apply_template, detect_category

    brief = load_brief(args.brief)

    # Auto-detect and apply category template if not set
    if not brief.get("category"):
        brief["category"] = detect_category(brief)
    brief = apply_template(brief)

    errors = validate_brief(brief)
    if errors:
        print(f"Brief validation errors: {'; '.join(errors)}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
    chip_dir = scaffold_chip(brief, output_dir)

    # Score the scaffolded chip
    result = score_chip(chip_dir)
    print(f"Scaffolded: {chip_dir}")
    print(f"Score: {result['total_score']}/100 ({result['verdict']})")
    print(f"Passed: {len(result['passed_checks'])}/30 checks")


# ---------------------------------------------------------------------------
# Command: doctor
# ---------------------------------------------------------------------------

def cmd_doctor(args: argparse.Namespace) -> None:
    """Run gap analysis and auto-fix on a chip."""
    from .gap_analyzer import analyze_gaps, improve_chip

    chip_path = Path(args.chip_path)
    if not chip_path.exists():
        print(f"Chip path not found: {chip_path}", file=sys.stderr)
        sys.exit(1)

    # Initial score
    initial = score_chip(chip_path)
    print(f"Initial score: {initial['total_score']}/100 ({initial['verdict']})")
    print(f"Failed checks: {len(initial['failed_checks'])}")

    # Run improvement
    target = args.target_score or 60
    report = improve_chip(chip_path, target_score=target, max_iterations=args.max_iterations or 20)

    final_result = report.get("final_result", {})
    final_verdict = final_result.get("verdict", "unknown")
    fixes_count = len(report.get("fixes_applied", []))

    print(f"\nAfter improvement:")
    print(f"Score: {report['final_score']}/100 ({final_verdict})")
    print(f"Iterations: {report.get('iterations', 0)}")
    print(f"Fixes applied: {fixes_count}")

    remaining = [c for c in final_result.get("failed_checks", [])]
    if remaining:
        print(f"\nRemaining failed checks: {len(remaining)}")
        for check_id in remaining[:5]:
            print(f"  - {check_id}")


# ---------------------------------------------------------------------------
# Command: score
# ---------------------------------------------------------------------------

def cmd_score(args: argparse.Namespace) -> None:
    """Score a chip against the quality rubric."""
    chip_path = Path(args.chip_path)
    result = score_chip(chip_path)

    print(f"Chip: {chip_path.name}")
    print(f"Score: {result['total_score']}/100")
    print(f"Verdict: {result['verdict']}")
    print()

    for dim in result.get("dimensions", []):
        print(f"  {dim['label']}: {dim['score']}/{dim['max_points']}")
        for check in dim.get("checks", []):
            status = "PASS" if check["passed"] else "FAIL"
            print(f"    [{status}] {check['description']} ({check['points']} pts)")

    _write_output(args.output, result)


# ---------------------------------------------------------------------------
# Command: autoloop
# ---------------------------------------------------------------------------

def cmd_autoloop(args: argparse.Namespace) -> None:
    """Run recursive improvement loop on a chip."""
    from .loop_controller import RecursiveLoopController, LoopConfig

    config = LoopConfig(
        target_score=args.target_score,
        max_iterations=args.max_iterations,
    )
    controller = RecursiveLoopController(config)

    if args.brief:
        from .scaffold import load_brief
        from .category_templates import apply_template, detect_category

        brief = load_brief(args.brief)
        if not brief.get("category"):
            brief["category"] = detect_category(brief)
        brief = apply_template(brief)

        output_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
        result = controller.run_from_brief(brief, output_dir)
    elif args.chip_path:
        result = controller.run_on_chip(Path(args.chip_path))
    else:
        print("Either --brief or chip_path is required.", file=sys.stderr)
        sys.exit(1)

    print(f"Chip: {result.chip_path}")
    print(f"Score: {result.initial_score} -> {result.final_score} ({result.verdict})")
    print(f"Iterations: {result.iterations}")
    print(f"Improvements: {len(result.improvements)}")
    for imp in result.improvements:
        print(f"  + {imp}")
    if result.remaining_gaps:
        print(f"Remaining gaps: {len(result.remaining_gaps)}")
        for gap in result.remaining_gaps[:5]:
            print(f"  - {gap}")


# ---------------------------------------------------------------------------
# Command: transfer
# ---------------------------------------------------------------------------

def cmd_transfer(args: argparse.Namespace) -> None:
    """Transfer intelligence between chips."""
    from .transfer import transfer_intelligence, extract_portfolio_patterns, find_applicable_patterns

    target_path = Path(args.target_chip)
    if not target_path.exists():
        print(f"Target chip not found: {target_path}", file=sys.stderr)
        sys.exit(1)

    if args.source:
        source_path = Path(args.source)
        result = transfer_intelligence(source_path, target_path)
    elif args.search_dir:
        registry = extract_portfolio_patterns(Path(args.search_dir))
        patterns = find_applicable_patterns(target_path, registry)
        from .transfer import apply_pattern
        score_before = score_chip(target_path)["total_score"]
        applied = []
        for p in patterns[:10]:
            if apply_pattern(target_path, p):
                applied.append(p.pattern_id)
        score_after = score_chip(target_path)["total_score"]
        print(f"Patterns applied: {len(applied)}")
        print(f"Score: {score_before} -> {score_after} (+{score_after - score_before})")
        return
    else:
        print("Either --source or --search-dir is required.", file=sys.stderr)
        sys.exit(1)

    print(f"Transfer: {len(result.patterns_applied)} patterns applied")
    print(f"Score: {result.score_before} -> {result.score_after} (+{result.score_delta})")
    if result.successful_transfers:
        print(f"Successful: {len(result.successful_transfers)}")
    if result.failed_transfers:
        print(f"Failed: {len(result.failed_transfers)}")


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

    # scaffold
    p_scaffold = sub.add_parser("scaffold", help="Scaffold a new domain chip from a brief.")
    p_scaffold.add_argument("--brief", type=str, required=True, help="Path to domain brief (JSON or YAML).")
    p_scaffold.add_argument("--output-dir", type=str, default=None, help="Directory to create chip in.")
    p_scaffold.set_defaults(func=cmd_scaffold)

    # doctor
    p_doctor = sub.add_parser("doctor", help="Run gap analysis and auto-fix on a chip.")
    p_doctor.add_argument("chip_path", type=str, help="Path to chip directory.")
    p_doctor.add_argument("--target-score", type=int, default=60, help="Target quality score.")
    p_doctor.add_argument("--max-iterations", type=int, default=20, help="Max fix iterations.")
    p_doctor.set_defaults(func=cmd_doctor)

    # score
    p_score = sub.add_parser("score", help="Score a chip against the quality rubric.")
    p_score.add_argument("chip_path", type=str, help="Path to chip directory.")
    p_score.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_score.set_defaults(func=cmd_score)

    # autoloop
    p_loop = sub.add_parser("autoloop", help="Run recursive improvement loop on a chip.")
    p_loop.add_argument("chip_path", type=str, nargs="?", default=None, help="Path to chip directory.")
    p_loop.add_argument("--brief", type=str, default=None, help="Domain brief to scaffold from.")
    p_loop.add_argument("--output-dir", type=str, default=None, help="Output dir for scaffold.")
    p_loop.add_argument("--target-score", type=int, default=80, help="Target quality score.")
    p_loop.add_argument("--max-iterations", type=int, default=50, help="Max loop iterations.")
    p_loop.set_defaults(func=cmd_autoloop)

    # transfer
    p_transfer = sub.add_parser("transfer", help="Transfer intelligence between chips.")
    p_transfer.add_argument("target_chip", type=str, help="Target chip path.")
    p_transfer.add_argument("--source", type=str, default=None, help="Source chip path (auto-selects best if omitted).")
    p_transfer.add_argument("--search-dir", type=str, default=None, help="Directory to scan for source chips.")
    p_transfer.set_defaults(func=cmd_transfer)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
