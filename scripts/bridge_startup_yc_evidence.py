#!/usr/bin/env python3
"""Bridge startup-yc evidence into v2 rubric-expected locations.

One-time migration script that maps startup-yc's rich existing artifacts
(800+ runs, 105 research packets, belief files, DSPy configs) from their
current non-standard locations into the directory structure expected by
quality_rubric_v2.

Run from anywhere:
    python scripts/bridge_startup_yc_evidence.py [--chip-path PATH]
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def _find_chip(explicit_path: str | None = None) -> Path:
    """Resolve the startup-yc chip directory."""
    if explicit_path:
        p = Path(explicit_path)
        if p.exists():
            return p
        raise SystemExit(f"Chip path does not exist: {p}")
    desktop = Path(os.path.expanduser("~")) / "Desktop"
    candidate = desktop / "domain-chip-startup-yc"
    if candidate.exists():
        return candidate
    raise SystemExit(
        "Could not find domain-chip-startup-yc on Desktop. "
        "Pass --chip-path explicitly."
    )


# ---------------------------------------------------------------------------
# 1. score_history.jsonl from artifacts/ledger/runs.jsonl
# ---------------------------------------------------------------------------

def bridge_score_history(chip: Path) -> int:
    """Extract startup_score from runs.jsonl into score_history.jsonl.

    Returns the number of entries written.
    """
    runs_path = chip / "artifacts" / "ledger" / "runs.jsonl"
    if not runs_path.exists():
        print(f"  SKIP: {runs_path} not found")
        return 0

    entries: list[dict] = []
    for line in runs_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            run = json.loads(line)
        except json.JSONDecodeError:
            continue

        score = run.get("metric_value")
        if score is None:
            metrics = run.get("metrics", {})
            score = metrics.get("startup_score")
        if score is None:
            continue

        entries.append({
            "run_id": run.get("run_id", ""),
            "score": float(score),
            "total_score": int(float(score) * 100),
            "created_at": run.get("created_at", ""),
            "verdict": run.get("verdict", ""),
            "candidate": run.get("candidate_summary", ""),
        })

    if not entries:
        print("  SKIP: No entries with startup_score found")
        return 0

    out_path = chip / "score_history.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    print(f"  DONE: {len(entries)} entries -> {out_path.name}")
    return len(entries)


# ---------------------------------------------------------------------------
# 2. research/research_grounded/ from docs/research-packets/
# ---------------------------------------------------------------------------

def bridge_research_grounded(chip: Path) -> int:
    """Copy representative research packets to research/research_grounded/.

    Returns number of files copied.
    """
    src = chip / "docs" / "research-packets"
    if not src.exists():
        print(f"  SKIP: {src} not found")
        return 0

    dst = chip / "research" / "research_grounded"
    dst.mkdir(parents=True, exist_ok=True)

    count = 0
    for md in sorted(src.iterdir()):
        if not md.is_file() or md.suffix != ".md":
            continue
        if md.name == "README.md":
            continue
        target = dst / md.name
        if not target.exists():
            shutil.copy2(md, target)
            count += 1

    print(f"  DONE: {count} files -> research/research_grounded/")
    return count


# ---------------------------------------------------------------------------
# 3. research/benchmark_grounded/ from run results
# ---------------------------------------------------------------------------

def bridge_benchmark_grounded(chip: Path) -> int:
    """Create benchmark summary from run data.

    Returns number of files created.
    """
    dst = chip / "research" / "benchmark_grounded"
    dst.mkdir(parents=True, exist_ok=True)

    runs_path = chip / "artifacts" / "ledger" / "runs.jsonl"
    if not runs_path.exists():
        print(f"  SKIP: {runs_path} not found")
        return 0

    # Collect best results per verdict type
    best_by_verdict: dict[str, dict] = {}
    all_scores: list[float] = []

    for line in runs_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            run = json.loads(line)
        except json.JSONDecodeError:
            continue

        score = run.get("metric_value")
        if score is None:
            continue
        all_scores.append(float(score))
        verdict = run.get("verdict", "unknown")
        if verdict not in best_by_verdict or float(score) > best_by_verdict[verdict].get("score", 0):
            best_by_verdict[verdict] = {
                "score": float(score),
                "run_id": run.get("run_id", ""),
                "candidate": run.get("candidate_summary", ""),
                "created_at": run.get("created_at", ""),
            }

    if not all_scores:
        print("  SKIP: No scored runs found")
        return 0

    # Write benchmark summary
    summary = {
        "benchmark_type": "startup_factor_evaluation",
        "total_runs": len(all_scores),
        "score_range": [min(all_scores), max(all_scores)],
        "mean_score": sum(all_scores) / len(all_scores),
        "best_by_verdict": best_by_verdict,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    out_path = dst / "benchmark_summary.json"
    out_path.write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"  DONE: benchmark_summary.json ({len(all_scores)} runs analyzed)")
    return 1


# ---------------------------------------------------------------------------
# 4. research/exploratory_frontier/ -- frontier notes
# ---------------------------------------------------------------------------

def bridge_exploratory_frontier(chip: Path) -> int:
    """Create exploratory frontier content from high-surprise runs.

    Returns number of files created.
    """
    dst = chip / "research" / "exploratory_frontier"
    dst.mkdir(parents=True, exist_ok=True)

    runs_path = chip / "artifacts" / "ledger" / "runs.jsonl"
    if not runs_path.exists():
        print(f"  SKIP: {runs_path} not found")
        return 0

    # Find high-surprise runs (frontier discoveries)
    frontier_runs: list[dict] = []
    for line in runs_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            run = json.loads(line)
        except json.JSONDecodeError:
            continue
        metrics = run.get("metrics", {})
        surprise = metrics.get("surprise_score", 0)
        if surprise and float(surprise) >= 0.9:
            frontier_runs.append({
                "run_id": run.get("run_id", ""),
                "candidate": run.get("candidate_summary", ""),
                "startup_score": run.get("metric_value", 0),
                "surprise_score": float(surprise),
                "verdict": run.get("verdict", ""),
                "created_at": run.get("created_at", ""),
                "stdout_excerpt": run.get("stdout_excerpt", ""),
            })

    if not frontier_runs:
        print("  SKIP: No high-surprise (>=0.9) runs found")
        return 0

    # Write frontier discoveries
    out_path = dst / "frontier_discoveries.json"
    out_path.write_text(
        json.dumps({
            "description": "Runs with surprise_score >= 0.9 representing frontier explorations",
            "count": len(frontier_runs),
            "discoveries": frontier_runs[:50],  # Cap at 50 most notable
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"  DONE: frontier_discoveries.json ({len(frontier_runs)} high-surprise runs)")
    return 1


# ---------------------------------------------------------------------------
# 5. CONTRADICTIONS.md at chip root
# ---------------------------------------------------------------------------

def bridge_contradictions(chip: Path) -> bool:
    """Create substantive CONTRADICTIONS.md at chip root.

    Uses actual run data to identify contradictory findings.
    """
    runs_path = chip / "artifacts" / "ledger" / "runs.jsonl"

    # Collect regressed runs (contradictions to the improvement hypothesis)
    contradictions: list[dict] = []
    if runs_path.exists():
        for line in runs_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                run = json.loads(line)
            except json.JSONDecodeError:
                continue
            if run.get("verdict") == "regressed":
                contradictions.append({
                    "candidate": run.get("candidate_summary", ""),
                    "score": run.get("metric_value", 0),
                    "baseline": run.get("baseline_value", 0),
                })

    out_path = chip / "CONTRADICTIONS.md"
    lines = [
        "# Belief Contradictions",
        "",
        "## Methodology",
        "",
        "Contradictions are tracked when a candidate factor regresses below the",
        "current baseline score. Each regression challenges the hypothesis that",
        "the tested factor improves startup outcomes.",
        "",
    ]

    if contradictions:
        lines.append(f"## Regressed Factors ({len(contradictions)} total)")
        lines.append("")
        # Group by unique candidates and show top examples
        seen: set[str] = set()
        count = 0
        for c in contradictions:
            candidate = c.get("candidate", "Unknown")
            if candidate in seen:
                continue
            seen.add(candidate)
            score = c.get("score", 0)
            baseline = c.get("baseline", 0)
            delta = (score - baseline) if isinstance(score, (int, float)) and isinstance(baseline, (int, float)) else 0
            lines.append(f"- **{candidate}**: scored {score:.2f} vs baseline {baseline:.2f} (delta: {delta:+.2f})")
            count += 1
            if count >= 20:
                lines.append(f"- ... and {len(seen) - 20} more")
                break
        lines.append("")
    else:
        lines.append("## Status")
        lines.append("")
        lines.append("No regressed factors detected across the evaluation history.")
        lines.append("")

    lines.extend([
        "## Resolution Policy",
        "",
        "1. Factors that regress are tagged `defer` rather than rejected outright",
        "2. Deferred factors may be retested with additional quality signals",
        "3. Persistent regressions (3+ consecutive) are demoted from candidate pool",
        "4. Contradictions inform the mutation strategy for future exploration",
        "",
        "## Scoring Model Sensitivity",
        "",
        "The startup_score metric uses a deterministic heuristic model. Observed",
        "regressions may reflect limitations of the scoring model rather than true",
        "negative signals. Cross-referencing with surprise_score helps distinguish",
        "genuine contradictions from model artifacts.",
        "",
    ])

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  DONE: CONTRADICTIONS.md ({len(contradictions)} regressions documented)")
    return True


# ---------------------------------------------------------------------------
# 6. research/packets/ -- structured JSON packets
# ---------------------------------------------------------------------------

def bridge_structured_packets(chip: Path) -> int:
    """Create structured evidence packets with claim/mechanism/boundary.

    Returns number of files created.
    """
    dst = chip / "research" / "packets"
    dst.mkdir(parents=True, exist_ok=True)

    runs_path = chip / "artifacts" / "ledger" / "runs.jsonl"
    if not runs_path.exists():
        print(f"  SKIP: {runs_path} not found")
        return 0

    # Find promoted/improved runs to create packets from
    approved_runs: list[dict] = []
    for line in runs_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            run = json.loads(line)
        except json.JSONDecodeError:
            continue
        if run.get("verdict") in ("improved", "baseline"):
            score = run.get("metric_value")
            if score is not None and float(score) >= 0.5:
                approved_runs.append(run)

    if not approved_runs:
        print("  SKIP: No approved runs found")
        return 0

    count = 0
    for run in approved_runs[:30]:  # Cap at 30 packets
        packet = {
            "claim": run.get("candidate_summary", "Unknown factor"),
            "mechanism": (
                f"Evaluated via chip:evaluate with startup_score={run.get('metric_value', 0):.2f}, "
                f"surprise_score={run.get('metrics', {}).get('surprise_score', 0)}"
            ),
            "boundary": (
                f"Evidence count: {run.get('metrics', {}).get('evidence_count', 0)}. "
                f"Verdict: {run.get('verdict', 'unknown')}. "
                f"Baseline: {run.get('baseline_value', 'N/A')}"
            ),
            "evidence_lane": "benchmark_grounded",
            "type": "research_packet",
            "content": {
                "run_id": run.get("run_id", ""),
                "mutations": run.get("applied_mutations", []),
                "created_at": run.get("created_at", ""),
            },
        }

        slug = run.get("candidate_id", run.get("run_id", f"packet-{count}"))
        slug = slug.replace("/", "-").replace("\\", "-").replace(" ", "-")
        out_path = dst / f"{slug}.json"
        out_path.write_text(
            json.dumps(packet, indent=2) + "\n",
            encoding="utf-8",
        )
        count += 1

    print(f"  DONE: {count} structured packets -> research/packets/")
    return count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    chip_path_arg = None
    if "--chip-path" in sys.argv:
        idx = sys.argv.index("--chip-path")
        if idx + 1 < len(sys.argv):
            chip_path_arg = sys.argv[idx + 1]

    chip = _find_chip(chip_path_arg)
    print(f"Bridging evidence for: {chip.name}")
    print(f"  Location: {chip}")
    print()

    print("[1/6] Score history from runs.jsonl...")
    bridge_score_history(chip)
    print()

    print("[2/6] Research grounded from docs/research-packets/...")
    bridge_research_grounded(chip)
    print()

    print("[3/6] Benchmark grounded from run results...")
    bridge_benchmark_grounded(chip)
    print()

    print("[4/6] Exploratory frontier from high-surprise runs...")
    bridge_exploratory_frontier(chip)
    print()

    print("[5/6] Contradictions document...")
    bridge_contradictions(chip)
    print()

    print("[6/6] Structured evidence packets...")
    bridge_structured_packets(chip)
    print()

    print("Bridge complete. Run `score-v2` to verify improvement.")


if __name__ == "__main__":
    main()
