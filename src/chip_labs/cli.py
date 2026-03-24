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

from .lab_hooks import (
    generate_packets,
    generate_watchtower_pages,
    run_evaluate,
    run_suggest,
)
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


def _write_text_output(output_path: str | None, content: str) -> None:
    """Write plain-text output to file path or stdout."""
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(content, encoding="utf-8")
    else:
        print(content)


def _get_chip_search_dir() -> str | None:
    """Get the chip search directory from environment or default."""
    return os.environ.get("SPARK_CHIP_SEARCH_DIR", None)


def _write_watchtower_pages(vault_dir: str | Path, pages: list[dict[str, Any]]) -> None:
    """Write generated watchtower pages to the target vault directory."""
    vault_path = Path(vault_dir)
    vault_path.mkdir(parents=True, exist_ok=True)
    for page in pages:
        page_path = vault_path / page["path"]
        page_path.parent.mkdir(parents=True, exist_ok=True)
        page_path.write_text(page["content"], encoding="utf-8")


def _write_discovery_cluster_materialization(
    output_dir: str | Path,
    cluster_bundle: dict[str, Any],
    index_title: str,
) -> dict[str, Any]:
    """Write per-cluster discovery packet files plus an operator-facing index."""
    from .mirofish.discovery import format_discovery_program_markdown

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    cluster_packets = list(cluster_bundle.get("cluster_packets", []))
    written_files: list[str] = []

    readme_path = output_path / "README.md"
    readme_path.write_text(
        format_discovery_program_markdown(cluster_bundle, title=index_title),
        encoding="utf-8",
    )
    written_files.append(str(readme_path))

    for index, cluster_packet in enumerate(cluster_packets, start=1):
        cluster_id = str(cluster_packet.get("cluster_id", f"cluster-{index:02d}"))
        file_path = output_path / f"{index:02d}_{cluster_id}.json"
        file_path.write_text(json.dumps(cluster_packet, indent=2, default=str), encoding="utf-8")
        written_files.append(str(file_path))

    return {
        "output_dir": str(output_path),
        "file_count": len(written_files),
        "files": written_files,
    }


def _summarize_discovery_cluster_directory(directory: str | Path) -> dict[str, Any]:
    """Summarize fill progress for a materialized discovery cluster directory."""
    directory_path = Path(directory)
    cluster_paths = sorted(
        path for path in directory_path.glob("*.json")
        if path.name[:2].isdigit()
    )
    cluster_summaries: list[dict[str, Any]] = []
    total_agents = 0
    filled_agents = 0
    raw_candidates = 0
    for cluster_path in cluster_paths:
        packet = _load_input(str(cluster_path))
        agent_submissions = list(packet.get("agent_submissions", []))
        cluster_total_agents = len(agent_submissions)
        cluster_filled_agents = sum(1 for submission in agent_submissions if submission.get("raw_candidates"))
        cluster_raw_candidates = sum(len(submission.get("raw_candidates", [])) for submission in agent_submissions)
        total_agents += cluster_total_agents
        filled_agents += cluster_filled_agents
        raw_candidates += cluster_raw_candidates
        cluster_summaries.append({
            "cluster_id": packet.get("cluster_id", cluster_path.stem),
            "cluster_label": packet.get("cluster_label", packet.get("cluster_id", cluster_path.stem)),
            "target_agent_count": int(packet.get("target_agent_count", cluster_total_agents)),
            "filled_agent_count": cluster_filled_agents,
            "empty_agent_count": max(cluster_total_agents - cluster_filled_agents, 0),
            "raw_candidate_count": cluster_raw_candidates,
            "file_path": str(cluster_path),
        })

    return {
        "packet_kind": "mirofish_discovery_program_progress",
        "directory": str(directory_path),
        "summary": {
            "cluster_count": len(cluster_summaries),
            "total_agent_count": total_agents,
            "filled_agent_count": filled_agents,
            "empty_agent_count": max(total_agents - filled_agents, 0),
            "raw_candidate_count": raw_candidates,
            "fill_rate": (filled_agents / total_agents) if total_agents else 0.0,
        },
        "clusters": cluster_summaries,
        "next_actions": [
            "Fill empty cluster packets with real candidate submissions.",
            "Re-run progress after each collection tranche to track coverage.",
            "Once collection is complete, recombine the cluster packets into one discovery-program input packet.",
        ],
    }


def _build_discovery_cluster_bundle_from_directory(directory: str | Path) -> dict[str, Any]:
    """Rebuild a combined cluster bundle from a materialized discovery directory."""
    directory_path = Path(directory)
    cluster_paths = sorted(
        path for path in directory_path.glob("*.json")
        if path.name[:2].isdigit()
    )
    cluster_packets = [_load_input(str(path)) for path in cluster_paths]
    if not cluster_packets:
        return {
            "packet_kind": "mirofish_discovery_program_cluster_packets",
            "directory": str(directory_path),
            "cluster_packet_count": 0,
            "summary": {"cluster_count": 0, "agent_count": 0},
            "cluster_plan": [],
            "collection_rules": {},
            "cluster_packets": [],
            "next_actions": [
                "Materialize or populate cluster packet files before rebuilding the bundle.",
            ],
        }

    first_packet = cluster_packets[0]
    collection_rules = first_packet.get("collection_rules", {})
    cluster_plan = []
    agent_count = 0
    for packet in cluster_packets:
        agent_submissions = list(packet.get("agent_submissions", []))
        agent_count += len(agent_submissions)
        cluster_plan.append({
            "cluster_id": packet.get("cluster_id", ""),
            "label": packet.get("cluster_label", packet.get("cluster_id", "")),
            "agent_count": int(packet.get("target_agent_count", len(agent_submissions))),
            "focus": packet.get("focus", ""),
            "seed_domains": list(packet.get("seed_domains", [])),
        })

    return {
        "packet_kind": "mirofish_discovery_program_cluster_packets",
        "directory": str(directory_path),
        "program_id": first_packet.get("program_id", "mirofish-discovery-program"),
        "stage_label": first_packet.get("stage_label", "pilot"),
        "target_agent_count": sum(int(item.get("agent_count", 0)) for item in cluster_plan),
        "cluster_plan": cluster_plan,
        "collection_rules": collection_rules,
        "cluster_packet_count": len(cluster_packets),
        "summary": {
            "cluster_count": len(cluster_packets),
            "agent_count": agent_count,
        },
        "cluster_packets": cluster_packets,
        "next_actions": [
            "Run `mirofish-discovery-program-merge` on this refreshed bundle.",
            "Canonicalize the merged program packet after collection updates.",
            "Rebuild the bundle again after each new collection tranche.",
        ],
    }


def _format_discovery_progress_markdown(progress: dict[str, Any], title: str) -> str:
    """Render a materialized discovery directory progress report as markdown."""
    summary = progress.get("summary", {})
    lines = [
        f"# {title}",
        "",
        f"- Directory: `{progress.get('directory', 'unknown')}`",
        f"- Clusters: `{summary.get('cluster_count', 0)}`",
        f"- Filled agents: `{summary.get('filled_agent_count', 0)}` / `{summary.get('total_agent_count', 0)}`",
        f"- Raw candidates: `{summary.get('raw_candidate_count', 0)}`",
        f"- Fill rate: `{summary.get('fill_rate', 0.0):.2%}`",
        "",
        "## Cluster Progress",
        "",
    ]
    for cluster in progress.get("clusters", []):
        lines.append(
            f"- `{cluster['cluster_id']}`: {cluster['filled_agent_count']} / "
            f"{cluster['target_agent_count']} agents filled, {cluster['raw_candidate_count']} raw candidates"
        )
    lines.extend([
        "",
        "## Next Actions",
        "",
    ])
    for action in progress.get("next_actions", []):
        lines.append(f"- {action}")
    return "\n".join(lines).rstrip() + "\n"


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
    _write_watchtower_pages(vault_dir, pages)

    _write_output(args.output, {"pages": [p["path"] for p in pages], "count": len(pages)})


def cmd_mirofish_watchtower_snapshot(args: argparse.Namespace) -> None:
    """Generate a repo-local watchtower snapshot for the current MiroFish checkpoint."""
    mutations = {
        "research_focus": args.research_focus,
        "agent_workstream": args.agent_workstream,
    }
    chip_search_dir = args.chip_search_dir or "."
    pages = generate_watchtower_pages(
        mutations,
        chip_search_dir=chip_search_dir,
        vault_dir=args.vault_dir,
    )
    _write_watchtower_pages(args.vault_dir, pages)
    _write_output(
        args.output,
        {
            "pages": [p["path"] for p in pages],
            "count": len(pages),
            "vault_dir": args.vault_dir,
            "chip_search_dir": chip_search_dir,
            "mutations": mutations,
        },
    )


# ---------------------------------------------------------------------------
# Command: scaffold
# ---------------------------------------------------------------------------

def cmd_scaffold(args: argparse.Namespace) -> None:
    """Scaffold a new domain chip from a brief."""
    from .chip_factory import (
        apply_template,
        detect_category,
        load_brief,
        scaffold_chip,
        validate_brief,
    )

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
    from .chip_factory import improve_chip

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
    from .transfer_surface import RecursiveLoopController, LoopConfig

    config = LoopConfig(
        target_score=args.target_score,
        max_iterations=args.max_iterations,
    )
    controller = RecursiveLoopController(config)

    if args.brief:
        from .chip_factory import load_brief
        from .chip_factory import apply_template, detect_category

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
    from .transfer_surface import (
        apply_pattern,
        extract_portfolio_patterns,
        find_applicable_patterns,
        transfer_intelligence,
    )

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
# Command: score-v2
# ---------------------------------------------------------------------------

def cmd_score_v2(args: argparse.Namespace) -> None:
    """Score a chip against the hardened v2 quality rubric."""
    from .quality_rubric_v2 import score_chip_v2

    chip_path = Path(args.chip_path)
    result = score_chip_v2(chip_path)

    print(f"Chip: {chip_path.name}")
    print(f"Score: {result['total_score']}/100 (v2 rubric)")
    print(f"Verdict: {result['verdict']}")
    print()

    for dim in result.get("dimensions", []):
        print(f"  {dim['label']}: {dim['score']}/{dim['max_points']}")
        for check in dim.get("checks", []):
            status = "PASS" if check["passed"] else "FAIL"
            print(f"    [{status}] {check['description']} ({check['points']} pts)")

    _write_output(args.output, result)


# ---------------------------------------------------------------------------
# Command: score-v3
# ---------------------------------------------------------------------------

def cmd_score_v3(args: argparse.Namespace) -> None:
    """Score a chip with the V3 deep evaluation rubric."""
    from .deep_eval import score_chip_v3

    chip_path = Path(args.chip_path)
    result = score_chip_v3(chip_path)
    d = result.as_dict()

    print(f"Chip: {chip_path.name}")
    print(f"Score: {d['total_score']}/100 (v3 deep eval)")
    print(f"Verdict: {d['verdict']}")
    print()

    for dim in d["dimensions"]:
        depth = dim["depth_level"]
        print(f"  {dim['label']}: {dim['score']}/{dim['max_points']} [{depth}]")

    if args.verbose:
        if d["strengths"]:
            print("\nStrengths:")
            for s in d["strengths"]:
                print(f"  + {s}")
        if d["gaps"]:
            print("\nGaps:")
            for g in d["gaps"]:
                print(f"  - {g}")
        if d["recommendations"]:
            print("\nRecommendations:")
            for r in d["recommendations"]:
                print(f"  > {r}")
        if d["anti_gaming_flags"]:
            print("\nAnti-gaming flags:")
            for f in d["anti_gaming_flags"]:
                print(f"  ! {f}")

    _write_output(args.output, d)


# ---------------------------------------------------------------------------
# Command: portfolio-v3
# ---------------------------------------------------------------------------

def cmd_portfolio_v3(args: argparse.Namespace) -> None:
    """Score all discovered chips with the V3 deep evaluation rubric."""
    from .deep_eval import score_portfolio_v3

    search_dir = args.search_dir if args.search_dir else None
    report = score_portfolio_v3(search_dir)

    if "error" in report:
        print(f"Error: {report['error']}", file=sys.stderr)
        sys.exit(1)

    summary = report.get("summary", {})
    print(f"Portfolio V3 Deep Eval Report")
    print(f"Chips: {summary.get('chip_count', 0)}")
    print(f"Average: {summary.get('average_score', 0)}/100")
    print(f"Verdicts: {summary.get('verdicts', {})}")
    print()

    ranking = summary.get("ranking", [])
    print("Ranking:")
    for i, (name, score) in enumerate(ranking, 1):
        chip_data = report["chips"].get(name, {})
        verdict = chip_data.get("verdict", "?")
        flags = chip_data.get("anti_gaming_flags", [])
        flag_str = f" [!{','.join(flags)}]" if flags else ""
        print(f"  {i:2d}. {name}: {score}/100 ({verdict}){flag_str}")

    _write_output(args.output, report)


# ---------------------------------------------------------------------------
# Command: build-skill
# ---------------------------------------------------------------------------

def cmd_build_skill(args: argparse.Namespace) -> None:
    """Build intelligence delivery artifacts for a chip."""
    from .intelligence_serving import refresh_skill

    chip_path = Path(args.chip_path)
    if not chip_path.exists():
        print(f"Chip path not found: {chip_path}", file=sys.stderr)
        sys.exit(1)

    result = refresh_skill(chip_path)

    print(f"Chip: {chip_path.name}")
    print(f"Skill file: {result['skill_path']}")
    print(f"Context file: {result['context_path']}")
    print(f"Digest file: {result['digest_path']}")
    print(f"Doctrines: {result.get('doctrine_count', 0)}")
    print(f"Evidence files: {result.get('evidence_files', 0)}")
    print(f"Quality score: {result.get('current_score', 0)}/100")


# ---------------------------------------------------------------------------
# Command: serve
# ---------------------------------------------------------------------------

def cmd_serve(args: argparse.Namespace) -> None:
    """Serve context from a chip for a query."""
    from .intelligence_serving import serve_context

    chip_path = Path(args.chip_path)
    if not chip_path.exists():
        print(f"Chip path not found: {chip_path}", file=sys.stderr)
        sys.exit(1)

    result = serve_context(chip_path, args.query)
    _write_output(args.output, result)


# ---------------------------------------------------------------------------
# Command: serve-intelligence
# ---------------------------------------------------------------------------

def cmd_serve_intelligence(args: argparse.Namespace) -> None:
    """Inject chip intelligence context for a task description."""
    from .intelligence_serving import inject_context_for_task

    result = inject_context_for_task(
        args.task,
        max_chips=args.max_chips,
        style=args.style,
    )
    if args.output:
        _write_output(args.output, {"context": result})
    else:
        print(result)


# ---------------------------------------------------------------------------
# Command: advise
# ---------------------------------------------------------------------------

def cmd_advise(args: argparse.Namespace) -> None:
    """Get pre-action advisory from chip doctrines."""
    from .intelligence_serving import AdvisoryRequest, advise_pre_action

    request = AdvisoryRequest(
        action_description=args.action,
        domain_hint=args.domain,
    )
    response = advise_pre_action(request)

    output = {
        "verdict": response.verdict,
        "guidance": [
            {
                "claim": g.claim,
                "confidence": g.confidence,
                "relevance": round(g.relevance, 3),
                "guidance_type": g.guidance_type,
                "source_chip": g.source_chip,
            }
            for g in response.guidance
        ],
        "contradictions": response.contradictions,
        "uncertainty_areas": response.uncertainty_areas,
        "trajectory_context": response.trajectory_context,
        "chips_consulted": response.chips_consulted,
    }
    _write_output(args.output, output)


# ---------------------------------------------------------------------------
# Command: mirofish-discovery-batch
# ---------------------------------------------------------------------------

def cmd_mirofish_discovery_batch(args: argparse.Namespace) -> None:
    """Canonicalize a raw MiroFish discovery batch into a packet."""
    from .mirofish.discovery import canonicalize_discovery_batch

    input_data = _load_input(args.input)
    result = canonicalize_discovery_batch(input_data)
    _write_output(args.output, result)


def cmd_mirofish_discovery_program(args: argparse.Namespace) -> None:
    """Canonicalize a staged multi-agent MiroFish discovery program into a packet."""
    from .mirofish.discovery import canonicalize_discovery_program

    input_data = _load_input(args.input)
    result = canonicalize_discovery_program(input_data)
    _write_output(args.output, result)


def cmd_mirofish_discovery_program_scaffold(args: argparse.Namespace) -> None:
    """Build a structured multi-agent discovery pilot scaffold."""
    from .mirofish.discovery import build_discovery_program_scaffold

    result = build_discovery_program_scaffold(
        program_id=args.program_id,
        target_agent_count=args.target_agent_count,
        stage_label=args.stage_label,
        profile=args.profile,
    )
    _write_output(args.output, result)


def cmd_mirofish_discovery_program_split(args: argparse.Namespace) -> None:
    """Split a discovery scaffold into operator-facing per-cluster packets."""
    from .mirofish.discovery import split_discovery_program_scaffold

    input_data = _load_input(args.input)
    result = split_discovery_program_scaffold(input_data)
    _write_output(args.output, result)


def cmd_mirofish_discovery_program_merge(args: argparse.Namespace) -> None:
    """Recombine filled cluster packets into one discovery-program input packet."""
    from .mirofish.discovery import merge_discovery_cluster_packets

    input_data = _load_input(args.input)
    result = merge_discovery_cluster_packets(input_data)
    _write_output(args.output, result)


def cmd_mirofish_discovery_program_brief(args: argparse.Namespace) -> None:
    """Export a discovery scaffold, cluster bundle, or result packet as markdown."""
    from .mirofish.discovery import format_discovery_program_markdown

    input_data = _load_input(args.input)
    result = format_discovery_program_markdown(
        input_data,
        title=args.title,
    )
    _write_text_output(args.output, result)


def cmd_mirofish_discovery_program_materialize(args: argparse.Namespace) -> None:
    """Write cluster packets into a working directory with an operator-facing index."""
    input_data = _load_input(args.input)
    result = _write_discovery_cluster_materialization(
        args.output_dir,
        input_data,
        index_title=args.index_title,
    )
    _write_output(args.output, result)


def cmd_mirofish_discovery_program_progress(args: argparse.Namespace) -> None:
    """Summarize fill progress for a materialized discovery cluster directory."""
    result = _summarize_discovery_cluster_directory(args.input_dir)
    _write_output(args.output, result)
    if args.markdown_output:
        _write_text_output(
            args.markdown_output,
            _format_discovery_progress_markdown(result, title=args.title),
        )


def cmd_mirofish_discovery_program_bundle(args: argparse.Namespace) -> None:
    """Rebuild a combined cluster bundle from a materialized discovery directory."""
    result = _build_discovery_cluster_bundle_from_directory(args.input_dir)
    _write_output(args.output, result)


# ---------------------------------------------------------------------------
# Command: mirofish-hybrid-spec
# ---------------------------------------------------------------------------

def cmd_mirofish_hybrid_spec(args: argparse.Namespace) -> None:
    """Build a hybrid evaluation spec from a canonical discovery packet."""
    from .mirofish.hybrid import build_hybrid_evaluation_spec

    input_data = _load_input(args.input)
    benchmark_ids = [item.strip() for item in (args.benchmarks or "").split(",") if item.strip()]
    promoted_domain_ids = [item.strip() for item in (args.promote_domains or "").split(",") if item.strip()]
    proposed_benchmark_domain_ids = [item.strip() for item in (args.proposed_benchmarks or "").split(",") if item.strip()]
    result = build_hybrid_evaluation_spec(
        input_data,
        benchmark_ids=benchmark_ids or None,
        promoted_domain_ids=promoted_domain_ids or None,
        proposed_benchmark_domain_ids=proposed_benchmark_domain_ids or None,
        max_rounds=args.rounds,
        flagship_count_per_type=args.flagship_count_per_type,
        ensemble_runs=args.ensemble_runs,
        ensemble_count_per_type=args.ensemble_count_per_type,
        scenario_label=args.scenario_label,
    )
    _write_output(args.output, result)


# ---------------------------------------------------------------------------
# Command: mirofish-hybrid-run
# ---------------------------------------------------------------------------

def cmd_mirofish_hybrid_run(args: argparse.Namespace) -> None:
    """Run a saved hybrid evaluation spec through MiroFish."""
    from .mirofish.hybrid import run_hybrid_evaluation

    input_data = _load_input(args.input)
    result = run_hybrid_evaluation(input_data, seed=args.seed)
    _write_output(args.output, result)


# ---------------------------------------------------------------------------
# Command: mirofish-promotion-brief
# ---------------------------------------------------------------------------

def cmd_mirofish_promotion_brief(args: argparse.Namespace) -> None:
    """Build a promotion-review brief from a saved hybrid run packet."""
    from .mirofish.hybrid import build_promotion_brief

    input_data = _load_input(args.input)
    domain_ids = [item.strip() for item in (args.domains or "").split(",") if item.strip()]
    result = build_promotion_brief(input_data, candidate_ids=domain_ids or None)
    _write_output(args.output, result)


# ---------------------------------------------------------------------------
# Command: mirofish-run-diagnostic
# ---------------------------------------------------------------------------

def cmd_mirofish_run_diagnostic(args: argparse.Namespace) -> None:
    """Build a bottleneck-focused diagnostic brief from a saved hybrid run packet."""
    from .mirofish.hybrid import build_run_diagnostic_brief

    input_data = _load_input(args.input)
    domain_ids = [item.strip() for item in (args.domains or "").split(",") if item.strip()]
    result = build_run_diagnostic_brief(input_data, focus_domain_ids=domain_ids or None)
    _write_output(args.output, result)


# ---------------------------------------------------------------------------
# Command: mirofish-portfolio-run
# ---------------------------------------------------------------------------

def cmd_mirofish_portfolio_run(args: argparse.Namespace) -> None:
    """Run the repo-local 515-domain MiroFish portfolio harness."""
    from .mirofish.portfolio import run_full_portfolio_evaluation

    result = run_full_portfolio_evaluation(
        seed=args.seed,
        max_rounds=args.rounds,
        flagship_count_per_type=args.flagship_count_per_type,
        ensemble_runs=args.ensemble_runs,
        ensemble_count_per_type=args.ensemble_count_per_type,
        convergence_threshold=args.convergence_threshold,
        min_runs=args.min_runs,
        bootstrap_resamples=args.bootstrap_resamples,
    )
    _write_output(args.output, result)


# ---------------------------------------------------------------------------
# Command: mirofish-portfolio-readout
# ---------------------------------------------------------------------------

def cmd_mirofish_portfolio_readout(args: argparse.Namespace) -> None:
    """Build a ranked readout from a saved 515-domain MiroFish portfolio run."""
    from .mirofish.portfolio import build_portfolio_readout

    input_data = _load_input(args.input)
    result = build_portfolio_readout(
        input_data,
        top_n=args.top_n,
        enterprise_n=args.enterprise_n,
        newly_discovered_n=args.newly_discovered_n,
    )
    _write_output(args.output, result)


def cmd_mirofish_portfolio_export(args: argparse.Namespace) -> None:
    """Export a saved portfolio readout as operator-facing markdown."""
    from .mirofish.portfolio import format_portfolio_readout_markdown

    input_data = _load_input(args.input)
    result = format_portfolio_readout_markdown(
        input_data,
        title=args.title,
    )
    _write_text_output(args.output, result)


def cmd_mirofish_frontier_readout(args: argparse.Namespace) -> None:
    """Build a ranked readout from a saved frontier hybrid run."""
    from .mirofish.hybrid import build_frontier_readout

    input_data = _load_input(args.input)
    result = build_frontier_readout(
        input_data,
        top_n=args.top_n,
        watchlist_n=args.watchlist_n,
        benchmark_n=args.benchmark_n,
    )
    _write_output(args.output, result)


def cmd_mirofish_frontier_export(args: argparse.Namespace) -> None:
    """Export a saved frontier readout as operator-facing markdown."""
    from .mirofish.hybrid import format_frontier_readout_markdown

    input_data = _load_input(args.input)
    result = format_frontier_readout_markdown(
        input_data,
        title=args.title,
    )
    _write_text_output(args.output, result)


def cmd_mirofish_frontier_tranche(args: argparse.Namespace) -> None:
    """Build a tractable frontier simulation tranche from the full canonical frontier."""
    from .mirofish.hybrid import build_frontier_simulation_tranche

    input_data = _load_input(args.input)
    anchor_data = _load_input(args.anchor_readout) if args.anchor_readout else None
    result = build_frontier_simulation_tranche(
        input_data,
        target_count=args.target_count,
        anchor_readout=anchor_data,
    )
    _write_output(args.output, result)


# ---------------------------------------------------------------------------
# Command: run-mcp-server
# ---------------------------------------------------------------------------

def cmd_run_mcp_server(args: argparse.Namespace) -> None:
    """Start the MCP server for domain chip intelligence."""
    from .intelligence_serving import ChipMCPServer

    server = ChipMCPServer()
    print("Starting domain chip MCP server on stdio...", file=sys.stderr)
    server.run()


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

    # mirofish-watchtower-snapshot
    p_mirofish_watchtower_snapshot = sub.add_parser(
        "mirofish-watchtower-snapshot",
        help="Generate a repo-local watchtower snapshot for the current MiroFish checkpoint.",
    )
    p_mirofish_watchtower_snapshot.add_argument(
        "--vault-dir",
        type=str,
        default="research/meta/watchtower_latest",
        help="Directory to write the generated watchtower pages into.",
    )
    p_mirofish_watchtower_snapshot.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON file path for the generated page list.",
    )
    p_mirofish_watchtower_snapshot.add_argument(
        "--chip-search-dir",
        type=str,
        default=".",
        help="Chip search directory for the watchtower pass.",
    )
    p_mirofish_watchtower_snapshot.add_argument(
        "--research-focus",
        type=str,
        default="mirofish_portfolio_surface",
        help="Research focus to display in the generated watchtower pages.",
    )
    p_mirofish_watchtower_snapshot.add_argument(
        "--agent-workstream",
        type=str,
        default="methodology_researcher",
        help="Agent workstream to display in the generated watchtower pages.",
    )
    p_mirofish_watchtower_snapshot.set_defaults(func=cmd_mirofish_watchtower_snapshot)

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

    # score-v2
    p_score_v2 = sub.add_parser("score-v2", help="Score a chip against the hardened v2 rubric.")
    p_score_v2.add_argument("chip_path", type=str, help="Path to chip directory.")
    p_score_v2.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_score_v2.set_defaults(func=cmd_score_v2)

    # score-v3
    p_score_v3 = sub.add_parser("score-v3", help="Score a chip with the V3 deep evaluation rubric.")
    p_score_v3.add_argument("chip_path", type=str, help="Path to chip directory.")
    p_score_v3.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_score_v3.add_argument("--verbose", action="store_true", help="Show gaps, strengths, and anti-gaming flags.")
    p_score_v3.set_defaults(func=cmd_score_v3)

    # portfolio-v3
    p_portfolio_v3 = sub.add_parser("portfolio-v3", help="Score all discovered chips with V3 deep eval.")
    p_portfolio_v3.add_argument("--search-dir", type=str, default=None, help="Directory to scan for chips.")
    p_portfolio_v3.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_portfolio_v3.set_defaults(func=cmd_portfolio_v3)

    # build-skill
    p_skill = sub.add_parser("build-skill", help="Build intelligence delivery artifacts.")
    p_skill.add_argument("chip_path", type=str, help="Path to chip directory.")
    p_skill.set_defaults(func=cmd_build_skill)

    # serve
    p_serve = sub.add_parser("serve", help="Serve context from a chip for a query.")
    p_serve.add_argument("chip_path", type=str, help="Path to chip directory.")
    p_serve.add_argument("query", type=str, help="Query to match against chip intelligence.")
    p_serve.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_serve.set_defaults(func=cmd_serve)

    # serve-intelligence
    p_si = sub.add_parser("serve-intelligence", help="Inject chip intelligence context for a task.")
    p_si.add_argument("task", type=str, help="Task description to match against chips.")
    p_si.add_argument("--style", choices=["concise", "detailed", "guardrails_only"], default="concise")
    p_si.add_argument("--max-chips", type=int, default=2)
    p_si.add_argument("--output", type=str, default=None)
    p_si.set_defaults(func=cmd_serve_intelligence)

    # advise
    p_advise = sub.add_parser("advise", help="Get pre-action advisory from chip doctrines.")
    p_advise.add_argument("action", type=str, help="Action description to advise on.")
    p_advise.add_argument("--domain", type=str, default=None, help="Domain hint.")
    p_advise.add_argument("--output", type=str, default=None)
    p_advise.set_defaults(func=cmd_advise)

    # mirofish-discovery-batch
    p_mirofish_discovery = sub.add_parser(
        "mirofish-discovery-batch",
        help="Canonicalize a raw discovery batch into a MiroFish candidate packet.",
    )
    p_mirofish_discovery.add_argument("--input", type=str, required=True, help="Input JSON file path.")
    p_mirofish_discovery.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_mirofish_discovery.set_defaults(func=cmd_mirofish_discovery_batch)

    # mirofish-discovery-program
    p_mirofish_discovery_program = sub.add_parser(
        "mirofish-discovery-program",
        help="Canonicalize a staged multi-agent discovery program into a MiroFish candidate packet.",
    )
    p_mirofish_discovery_program.add_argument("--input", type=str, required=True, help="Input JSON file path.")
    p_mirofish_discovery_program.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_mirofish_discovery_program.set_defaults(func=cmd_mirofish_discovery_program)

    # mirofish-discovery-program-scaffold
    p_mirofish_discovery_program_scaffold = sub.add_parser(
        "mirofish-discovery-program-scaffold",
        help="Build a staged multi-agent discovery pilot scaffold.",
    )
    p_mirofish_discovery_program_scaffold.add_argument(
        "--program-id",
        type=str,
        default="mirofish-discovery-program-pilot-100",
        help="Program ID for the scaffold packet.",
    )
    p_mirofish_discovery_program_scaffold.add_argument(
        "--target-agent-count",
        type=int,
        default=100,
        help="Target agent count for the scaffold packet.",
    )
    p_mirofish_discovery_program_scaffold.add_argument(
        "--stage-label",
        type=str,
        default="pilot_100",
        help="Stage label for the scaffold packet.",
    )
    p_mirofish_discovery_program_scaffold.add_argument(
        "--profile",
        type=str,
        choices=["viral", "diverse_frontier"],
        default="viral",
        help="Cluster profile to use for the scaffold packet.",
    )
    p_mirofish_discovery_program_scaffold.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_mirofish_discovery_program_scaffold.set_defaults(func=cmd_mirofish_discovery_program_scaffold)

    # mirofish-discovery-program-split
    p_mirofish_discovery_program_split = sub.add_parser(
        "mirofish-discovery-program-split",
        help="Split a discovery scaffold into operator-facing per-cluster packets.",
    )
    p_mirofish_discovery_program_split.add_argument("--input", type=str, required=True, help="Input scaffold JSON file path.")
    p_mirofish_discovery_program_split.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_mirofish_discovery_program_split.set_defaults(func=cmd_mirofish_discovery_program_split)

    # mirofish-discovery-program-merge
    p_mirofish_discovery_program_merge = sub.add_parser(
        "mirofish-discovery-program-merge",
        help="Recombine filled cluster packets into one discovery-program input packet.",
    )
    p_mirofish_discovery_program_merge.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input cluster-packets JSON file path.",
    )
    p_mirofish_discovery_program_merge.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_mirofish_discovery_program_merge.set_defaults(func=cmd_mirofish_discovery_program_merge)

    # mirofish-discovery-program-brief
    p_mirofish_discovery_program_brief = sub.add_parser(
        "mirofish-discovery-program-brief",
        help="Export a discovery scaffold, cluster bundle, or result packet as markdown.",
    )
    p_mirofish_discovery_program_brief.add_argument("--input", type=str, required=True, help="Input JSON file path.")
    p_mirofish_discovery_program_brief.add_argument(
        "--title",
        type=str,
        default="MiroFish Discovery Program",
        help="Markdown heading for the exported brief.",
    )
    p_mirofish_discovery_program_brief.add_argument("--output", type=str, default=None, help="Output markdown file path.")
    p_mirofish_discovery_program_brief.set_defaults(func=cmd_mirofish_discovery_program_brief)

    # mirofish-discovery-program-materialize
    p_mirofish_discovery_program_materialize = sub.add_parser(
        "mirofish-discovery-program-materialize",
        help="Write cluster packets into a working directory with an operator-facing index.",
    )
    p_mirofish_discovery_program_materialize.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input cluster-packets JSON file path.",
    )
    p_mirofish_discovery_program_materialize.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Directory to write the cluster packet files and README into.",
    )
    p_mirofish_discovery_program_materialize.add_argument(
        "--index-title",
        type=str,
        default="MiroFish Discovery Program Clusters",
        help="Markdown heading for the generated README.",
    )
    p_mirofish_discovery_program_materialize.add_argument("--output", type=str, default=None, help="Output JSON manifest path.")
    p_mirofish_discovery_program_materialize.set_defaults(func=cmd_mirofish_discovery_program_materialize)

    # mirofish-discovery-program-progress
    p_mirofish_discovery_program_progress = sub.add_parser(
        "mirofish-discovery-program-progress",
        help="Summarize fill progress for a materialized discovery cluster directory.",
    )
    p_mirofish_discovery_program_progress.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="Materialized cluster directory path.",
    )
    p_mirofish_discovery_program_progress.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_mirofish_discovery_program_progress.add_argument(
        "--markdown-output",
        type=str,
        default=None,
        help="Optional markdown progress report path.",
    )
    p_mirofish_discovery_program_progress.add_argument(
        "--title",
        type=str,
        default="MiroFish Discovery Pilot Progress",
        help="Markdown heading for the progress report.",
    )
    p_mirofish_discovery_program_progress.set_defaults(func=cmd_mirofish_discovery_program_progress)

    # mirofish-discovery-program-bundle
    p_mirofish_discovery_program_bundle = sub.add_parser(
        "mirofish-discovery-program-bundle",
        help="Rebuild a combined cluster bundle from a materialized discovery directory.",
    )
    p_mirofish_discovery_program_bundle.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="Materialized cluster directory path.",
    )
    p_mirofish_discovery_program_bundle.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_mirofish_discovery_program_bundle.set_defaults(func=cmd_mirofish_discovery_program_bundle)

    # mirofish-hybrid-spec
    p_mirofish_hybrid = sub.add_parser(
        "mirofish-hybrid-spec",
        help="Build a hybrid MiroFish evaluation spec from a discovery packet.",
    )
    p_mirofish_hybrid.add_argument("--input", type=str, required=True, help="Input discovery packet path.")
    p_mirofish_hybrid.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_mirofish_hybrid.add_argument(
        "--benchmarks",
        type=str,
        default=None,
        help="Comma-separated benchmark domain_ids to include. Defaults to the standard panel.",
    )
    p_mirofish_hybrid.add_argument(
        "--promote-domains",
        type=str,
        default=None,
        help="Comma-separated discovered domain_ids to move into the benchmark-review lane.",
    )
    p_mirofish_hybrid.add_argument(
        "--proposed-benchmarks",
        type=str,
        default=None,
        help="Comma-separated discovered domain_ids to treat as provisional benchmark members in the spec.",
    )
    p_mirofish_hybrid.add_argument("--rounds", type=int, default=20, help="Simulation rounds for the hybrid harness.")
    p_mirofish_hybrid.add_argument(
        "--flagship-count-per-type",
        type=int,
        default=30,
        help="Personas per type for the flagship hybrid harness.",
    )
    p_mirofish_hybrid.add_argument(
        "--ensemble-runs",
        type=int,
        default=15,
        help="Monte Carlo runs for the hybrid harness.",
    )
    p_mirofish_hybrid.add_argument(
        "--ensemble-count-per-type",
        type=int,
        default=15,
        help="Personas per type per ensemble run.",
    )
    p_mirofish_hybrid.add_argument(
        "--scenario-label",
        type=str,
        default="mirofish-hybrid-discovery",
        help="Scenario label for generated shocks.",
    )
    p_mirofish_hybrid.set_defaults(func=cmd_mirofish_hybrid_spec)

    # mirofish-hybrid-run
    p_mirofish_hybrid_run = sub.add_parser(
        "mirofish-hybrid-run",
        help="Run a saved hybrid MiroFish evaluation spec.",
    )
    p_mirofish_hybrid_run.add_argument("--input", type=str, required=True, help="Input hybrid spec path.")
    p_mirofish_hybrid_run.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_mirofish_hybrid_run.add_argument("--seed", type=int, default=42, help="Base seed for the run.")
    p_mirofish_hybrid_run.set_defaults(func=cmd_mirofish_hybrid_run)

    # mirofish-promotion-brief
    p_mirofish_promotion = sub.add_parser(
        "mirofish-promotion-brief",
        help="Build a promotion-review brief from a hybrid MiroFish run.",
    )
    p_mirofish_promotion.add_argument("--input", type=str, required=True, help="Input hybrid run path.")
    p_mirofish_promotion.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_mirofish_promotion.add_argument(
        "--domains",
        type=str,
        default=None,
        help="Optional comma-separated discovered domain_ids to include. Defaults to all discovered candidates.",
    )
    p_mirofish_promotion.set_defaults(func=cmd_mirofish_promotion_brief)

    # mirofish-run-diagnostic
    p_mirofish_diagnostic = sub.add_parser(
        "mirofish-run-diagnostic",
        help="Build a diagnostic brief from a saved hybrid MiroFish run.",
    )
    p_mirofish_diagnostic.add_argument("--input", type=str, required=True, help="Input hybrid run path.")
    p_mirofish_diagnostic.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_mirofish_diagnostic.add_argument(
        "--domains",
        type=str,
        default=None,
        help="Optional comma-separated domain_ids to focus on. Defaults to review candidates or discovered domains.",
    )
    p_mirofish_diagnostic.set_defaults(func=cmd_mirofish_run_diagnostic)

    # mirofish-portfolio-run
    p_mirofish_portfolio_run = sub.add_parser(
        "mirofish-portfolio-run",
        help="Run the repo-local 515-domain MiroFish portfolio harness.",
    )
    p_mirofish_portfolio_run.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_mirofish_portfolio_run.add_argument("--seed", type=int, default=42, help="Base seed for the run.")
    p_mirofish_portfolio_run.add_argument("--rounds", type=int, default=20, help="Simulation rounds.")
    p_mirofish_portfolio_run.add_argument(
        "--flagship-count-per-type",
        type=int,
        default=50,
        help="Personas per type for the flagship run.",
    )
    p_mirofish_portfolio_run.add_argument(
        "--ensemble-runs",
        type=int,
        default=30,
        help="Monte Carlo runs for the ensemble.",
    )
    p_mirofish_portfolio_run.add_argument(
        "--ensemble-count-per-type",
        type=int,
        default=15,
        help="Personas per type per ensemble run.",
    )
    p_mirofish_portfolio_run.add_argument(
        "--convergence-threshold",
        type=float,
        default=0.005,
        help="Early-stop threshold for ensemble mean stabilization.",
    )
    p_mirofish_portfolio_run.add_argument(
        "--min-runs",
        type=int,
        default=15,
        help="Minimum ensemble runs before convergence checks.",
    )
    p_mirofish_portfolio_run.add_argument(
        "--bootstrap-resamples",
        type=int,
        default=1000,
        help="Bootstrap resamples for ensemble confidence intervals.",
    )
    p_mirofish_portfolio_run.set_defaults(func=cmd_mirofish_portfolio_run)

    # mirofish-portfolio-readout
    p_mirofish_portfolio_readout = sub.add_parser(
        "mirofish-portfolio-readout",
        help="Build a ranked readout from a saved 515-domain MiroFish portfolio run.",
    )
    p_mirofish_portfolio_readout.add_argument("--input", type=str, required=True, help="Input portfolio run path.")
    p_mirofish_portfolio_readout.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_mirofish_portfolio_readout.add_argument("--top-n", type=int, default=30, help="Number of overall domains to include.")
    p_mirofish_portfolio_readout.add_argument("--enterprise-n", type=int, default=15, help="Number of enterprise domains to include.")
    p_mirofish_portfolio_readout.add_argument(
        "--newly-discovered-n",
        type=int,
        default=15,
        help="Number of v4 / newly added domains to include.",
    )
    p_mirofish_portfolio_readout.set_defaults(func=cmd_mirofish_portfolio_readout)

    # mirofish-portfolio-export
    p_mirofish_portfolio_export = sub.add_parser(
        "mirofish-portfolio-export",
        help="Export a saved MiroFish portfolio readout as operator-facing markdown.",
    )
    p_mirofish_portfolio_export.add_argument("--input", type=str, required=True, help="Input portfolio readout path.")
    p_mirofish_portfolio_export.add_argument("--output", type=str, default=None, help="Output markdown file path.")
    p_mirofish_portfolio_export.add_argument(
        "--title",
        type=str,
        default="MiroFish Portfolio Export",
        help="Document title for the markdown export.",
    )
    p_mirofish_portfolio_export.set_defaults(func=cmd_mirofish_portfolio_export)

    # mirofish-frontier-readout
    p_mirofish_frontier_readout = sub.add_parser(
        "mirofish-frontier-readout",
        help="Build a ranked readout from a saved MiroFish frontier hybrid run.",
    )
    p_mirofish_frontier_readout.add_argument("--input", type=str, required=True, help="Input frontier run path.")
    p_mirofish_frontier_readout.add_argument("--output", type=str, default=None, help="Output JSON file path.")
    p_mirofish_frontier_readout.add_argument("--top-n", type=int, default=25, help="Number of overall domains to include.")
    p_mirofish_frontier_readout.add_argument(
        "--watchlist-n",
        type=int,
        default=15,
        help="Number of watchlist domains to include.",
    )
    p_mirofish_frontier_readout.add_argument(
        "--benchmark-n",
        type=int,
        default=5,
        help="Number of above-benchmark domains to include.",
    )
    p_mirofish_frontier_readout.set_defaults(func=cmd_mirofish_frontier_readout)

    # mirofish-frontier-export
    p_mirofish_frontier_export = sub.add_parser(
        "mirofish-frontier-export",
        help="Export a saved MiroFish frontier readout as operator-facing markdown.",
    )
    p_mirofish_frontier_export.add_argument("--input", type=str, required=True, help="Input frontier readout path.")
    p_mirofish_frontier_export.add_argument("--output", type=str, default=None, help="Output markdown file path.")
    p_mirofish_frontier_export.add_argument(
        "--title",
        type=str,
        default="MiroFish Frontier Export",
        help="Document title for the markdown export.",
    )
    p_mirofish_frontier_export.set_defaults(func=cmd_mirofish_frontier_export)

    # mirofish-frontier-tranche
    p_mirofish_frontier_tranche = sub.add_parser(
        "mirofish-frontier-tranche",
        help="Build a tractable frontier simulation tranche from the canonical frontier result.",
    )
    p_mirofish_frontier_tranche.add_argument("--input", type=str, required=True, help="Input canonical frontier result path.")
    p_mirofish_frontier_tranche.add_argument("--output", type=str, default=None, help="Output tranche path.")
    p_mirofish_frontier_tranche.add_argument(
        "--anchor-readout",
        type=str,
        default=None,
        help="Optional frontier readout path to anchor tranche selection.",
    )
    p_mirofish_frontier_tranche.add_argument(
        "--target-count",
        type=int,
        default=180,
        help="Target number of accepted frontier domains to keep in the tranche.",
    )
    p_mirofish_frontier_tranche.set_defaults(func=cmd_mirofish_frontier_tranche)

    # run-mcp-server
    p_mcp = sub.add_parser("run-mcp-server", help="Start MCP server for chip intelligence.")
    p_mcp.set_defaults(func=cmd_run_mcp_server)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
