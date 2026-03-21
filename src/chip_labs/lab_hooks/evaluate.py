"""Meta-evaluator -- scores chip quality and lab research progress."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..deep_eval import score_chip_v3
from ..quality_rubric import score_chip, score_portfolio
from ..registry import discover_chips, get_portfolio_summary
from ..trend_scanner import SEED_OPPORTUNITIES, rank_opportunities


def _resolve_repo_root(chip_search_dir: str | Path | None = None) -> Path:
    """Resolve the lab repo root for artifact-grounded research scoring."""
    candidates: list[Path] = []
    if chip_search_dir:
        candidate = Path(chip_search_dir)
        if candidate.exists():
            candidates.append(candidate)
    candidates.extend([Path.cwd(), Path(__file__).resolve().parent, Path(__file__).resolve().parents[3]])

    seen: set[Path] = set()
    for candidate in candidates:
        for root in [candidate, *candidate.parents]:
            if root in seen:
                continue
            seen.add(root)
            if (root / "spark-chip.json").exists() and (root / "research").exists():
                return root
    return Path(__file__).resolve().parents[3]


def _read_text(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _word_count(paths: list[Path]) -> int:
    total = 0
    for path in paths:
        total += len(_read_text(path).split())
    return total


def _packet_files(repo_root: Path) -> list[Path]:
    packets_dir = repo_root / "research" / "packets"
    return sorted(packets_dir.glob("*.json")) if packets_dir.exists() else []


def _load_runs(repo_root: Path) -> list[dict[str, Any]]:
    """Load deterministic run history from sanctioned paths."""
    runs: list[dict[str, Any]] = []
    for candidate in [
        repo_root / "research" / "meta" / "runs.jsonl",
        repo_root / "artifacts" / "ledger" / "runs.jsonl",
        repo_root / "score_history.jsonl",
    ]:
        if not candidate.exists():
            continue
        for line in _read_text(candidate).splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                runs.append(payload)
    return runs


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _focus_run_stats(runs: list[dict[str, Any]], focus: str) -> dict[str, float | int]:
    scores: list[float] = []
    for run in runs:
        if run.get("focus") != focus:
            continue
        value = run.get("score", run.get("metric_value", 0.0))
        try:
            scores.append(float(value))
        except (TypeError, ValueError):
            continue
    return {
        "count": len(scores),
        "mean": round(_mean(scores), 4),
        "best": round(max(scores), 4) if scores else 0.0,
    }


def _dimension_fraction(v3_dimensions: dict[str, float], name: str) -> float:
    return v3_dimensions.get(name, 0.0)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


@lru_cache(maxsize=8)
def _cached_lab_state(repo_root_str: str, chip_search_dir_str: str) -> dict[str, Any]:
    repo_root = Path(repo_root_str)
    chip_search_dir: str | Path | None = chip_search_dir_str or None
    v3 = score_chip_v3(repo_root)
    v3_dimensions = {
        dim.name: (dim.score / dim.max_points) if dim.max_points else 0.0
        for dim in v3.dimensions
    }
    runs = _load_runs(repo_root)
    packets = _packet_files(repo_root)
    return {
        "repo_root": repo_root,
        "v3_dimensions": v3_dimensions,
        "runs": runs,
        "packets": packets,
        "portfolio_summary": get_portfolio_summary(chip_search_dir),
    }


def _lab_state(repo_root: Path, chip_search_dir: str | Path | None = None) -> dict[str, Any]:
    return _cached_lab_state(str(repo_root.resolve()), str(chip_search_dir or ""))


_METHODOLOGY_AREA_CONFIG: dict[str, dict[str, Any]] = {
    "evaluation_frameworks": {
        "files": [
            "docs/EVALUATION_METHODOLOGY.md",
            "docs/HARDENED_RUBRIC_V2.md",
            "docs/doctrines/evaluator_trust.md",
        ],
        "packet_keywords": ["rubric", "benchmark", "evaluator", "score"],
        "dimensions": ["doctrine_quality", "integration_maturity"],
    },
    "evidence_lanes": {
        "files": [
            "docs/beliefs/evidence_lanes.md",
            "docs/LAB_RESEARCH_PACKET.md",
        ],
        "packet_keywords": ["lane", "sanctioned_memory", "packet_retrieval"],
        "dimensions": ["evidence_integrity", "contradiction_rigor"],
    },
    "scoring_systems": {
        "files": [
            "docs/EVALUATION_METHODOLOGY.md",
            "docs/HARDENED_RUBRIC_V2.md",
            "research/benchmark_grounded/2026-03-21_stabilization_benchmarks.md",
        ],
        "packet_keywords": ["score", "benchmark", "rubric"],
        "dimensions": ["manifest_structure", "integration_maturity"],
    },
    "graduation_criteria": {
        "files": [
            "docs/LAB_GRADUATION_CRITERIA.md",
            "docs/VALIDATION_PORTFOLIO_LIVE_RUN.md",
        ],
        "packet_keywords": ["benchmark_to_product", "portfolio_baselines", "finished_product_shape"],
        "dimensions": ["flywheel_health", "integration_maturity"],
    },
    "frontier_design": {
        "files": [
            "docs/LAB_ONE_LOOP_SPEC.md",
            "docs/LAB_SAFETY_POLICY.md",
            "docs/doctrines/loop_governance.md",
        ],
        "packet_keywords": ["bounded_loop", "governance", "path_compatibility"],
        "dimensions": ["manifest_structure", "doctrine_quality"],
    },
    "source_registry": {
        "files": [
            "docs/LAB_SOURCE_MAP.md",
            "docs/LAB_TREND_METHODOLOGY.md",
        ],
        "packet_keywords": ["research_to_doctrine", "operator_trust", "packet_retrieval"],
        "dimensions": ["evidence_integrity", "watchtower_depth"],
    },
    "packet_quality": {
        "files": [
            "docs/LAB_RESEARCH_PACKET.md",
            "docs/beliefs/evidence_lanes.md",
        ],
        "packet_keywords": ["packet", "retrieval", "memory", "evidence"],
        "dimensions": ["evidence_integrity", "doctrine_quality"],
    },
}


def _score_methodology_area(state: dict[str, Any], methodology_area: str) -> dict[str, Any]:
    repo_root = state["repo_root"]
    config = _METHODOLOGY_AREA_CONFIG.get(methodology_area, _METHODOLOGY_AREA_CONFIG["evaluation_frameworks"])
    files = [repo_root / rel_path for rel_path in config["files"]]
    artifact_words = _word_count(files)
    packet_count = sum(
        1
        for packet_path in state["packets"]
        if any(keyword in packet_path.stem for keyword in config["packet_keywords"])
    )
    dimension_fraction = _mean([
        _dimension_fraction(state["v3_dimensions"], name)
        for name in config["dimensions"]
    ])
    run_stats = _focus_run_stats(state["runs"], "methodology")

    coverage = _clamp01(
        0.35 * min(1.0, artifact_words / 1400.0) +
        0.20 * min(1.0, packet_count / 4.0) +
        0.25 * dimension_fraction +
        0.20 * float(run_stats["mean"])
    )

    return {
        "score": round(coverage, 4),
        "details": {
            "artifact_word_count": artifact_words,
            "matching_packet_count": packet_count,
            "dimension_fraction": round(dimension_fraction, 4),
            "run_count": run_stats["count"],
            "run_mean": run_stats["mean"],
        },
    }


def _score_domain_discovery(state: dict[str, Any], trend_source: str) -> dict[str, Any]:
    repo_root = state["repo_root"]
    opportunities = [
        opp for opp in rank_opportunities(SEED_OPPORTUNITIES)
        if trend_source in opp.get("evidence_sources", [])
    ]
    opportunity_mean = _mean([float(opp["composite_score"]) for opp in opportunities])
    exploratory_words = _word_count(
        [repo_root / "docs" / "LAB_TREND_METHODOLOGY.md"] +
        list((repo_root / "research" / "exploratory_frontier").glob("*.md"))
    )
    run_stats = _focus_run_stats(state["runs"], "domain_discovery")
    source_coverage = len(opportunities) / max(1, len(SEED_OPPORTUNITIES))

    score = _clamp01(
        0.50 * opportunity_mean +
        0.20 * min(1.0, exploratory_words / 900.0) +
        0.15 * float(run_stats["mean"]) +
        0.15 * source_coverage
    )

    return {
        "score": round(score, 4),
        "details": {
            "opportunity_count": len(opportunities),
            "opportunity_mean": round(opportunity_mean, 4),
            "exploratory_word_count": exploratory_words,
            "run_count": run_stats["count"],
            "run_mean": run_stats["mean"],
            "candidate_domains": [
                {
                    "domain_id": opp["domain_id"],
                    "composite_score": opp["composite_score"],
                    "related_chips": opp.get("related_chips", []),
                }
                for opp in opportunities[:3]
            ],
        },
    }


def _score_transfer_patterns(state: dict[str, Any]) -> dict[str, Any]:
    repo_root = state["repo_root"]
    transfer_words = _word_count([
        repo_root / "docs" / "doctrines" / "transfer_promotion.md",
        repo_root / "docs" / "beliefs" / "CONTRADICTIONS.md",
        repo_root / "research" / "research_grounded" / "2026-03-21_lab_contract_alignment.md",
    ])
    transfer_packets = sum(1 for packet_path in state["packets"] if "transfer" in packet_path.stem)
    run_stats = _focus_run_stats(state["runs"], "transfer_patterns")
    maturity = state["portfolio_summary"].get("maturity_distribution", {})
    mature_count = int(maturity.get("production", 0)) + int(maturity.get("beta", 0))
    maturity_fraction = min(1.0, mature_count / 4.0)

    score = _clamp01(
        0.35 * min(1.0, transfer_words / 900.0) +
        0.20 * min(1.0, transfer_packets / 4.0) +
        0.20 * float(run_stats["mean"]) +
        0.25 * maturity_fraction
    )

    return {
        "score": round(score, 4),
        "details": {
            "transfer_word_count": transfer_words,
            "transfer_packet_count": transfer_packets,
            "run_count": run_stats["count"],
            "run_mean": run_stats["mean"],
            "mature_chip_count": mature_count,
            "portfolio_size": state["portfolio_summary"].get("total_chips", 0),
        },
    }


def _score_agi_theory(state: dict[str, Any]) -> dict[str, Any]:
    repo_root = state["repo_root"]
    agi_words = _word_count([
        repo_root / "docs" / "LAB_AGI_RESEARCH.md",
        repo_root / "docs" / "LAB_MISSION.md",
    ])
    run_stats = _focus_run_stats(state["runs"], "agi_theory")
    empirical_fraction = min(1.0, len(state["runs"]) / 50.0)
    doctrine_fraction = _dimension_fraction(state["v3_dimensions"], "doctrine_quality")

    score = min(
        0.49,
        _clamp01(
            0.35 * min(1.0, agi_words / 1800.0) +
            0.30 * float(run_stats["mean"]) +
            0.20 * empirical_fraction +
            0.15 * doctrine_fraction
        ),
    )

    return {
        "score": round(score, 4),
        "details": {
            "agi_word_count": agi_words,
            "run_count": run_stats["count"],
            "run_mean": run_stats["mean"],
            "empirical_fraction": round(empirical_fraction, 4),
            "doctrine_fraction": round(doctrine_fraction, 4),
        },
    }


def evaluate(mutations: dict[str, str], chip_search_dir: str | Path | None = None) -> dict[str, Any]:
    """Run the lab's evaluate hook.

    Depending on research_focus mutation:
    - quality_audit: Score chip(s) against the quality rubric
    - portfolio_health: Score entire portfolio
    - methodology / domain_discovery / transfer_patterns / agi_theory:
      Return methodology coverage and research progress metrics

    Returns metrics dict with lab_research_quality_score as primary.
    """
    research_focus = mutations.get("research_focus", "quality_audit")
    portfolio_target = mutations.get("portfolio_target")

    if research_focus == "quality_audit" and portfolio_target:
        # Score a specific chip
        chips = discover_chips(chip_search_dir)
        target_chip = None
        for chip in chips:
            if portfolio_target in chip["name"]:
                target_chip = chip
                break

        if target_chip:
            result = score_chip(target_chip["path"])
            return {
                "lab_research_quality_score": round(result["total_score"] / 100.0, 4),
                "portfolio_health": round(result["total_score"] / 100.0, 4),
                "methodology_coverage": 0.0,
                "chips_evaluated": 1,
                "graduation_pipeline_count": 0,
                "chip_result": result,
                "comparison_class": "benchmark_grounded",
            }
        else:
            return {
                "lab_research_quality_score": 0.0,
                "portfolio_health": 0.0,
                "methodology_coverage": 0.0,
                "chips_evaluated": 0,
                "graduation_pipeline_count": 0,
                "error": f"Chip not found: {portfolio_target}",
                "comparison_class": "benchmark_grounded",
            }

    elif research_focus in ("quality_audit", "portfolio_health"):
        # Score entire portfolio
        chips = discover_chips(chip_search_dir)
        chip_paths = [Path(c["path"]) for c in chips if c["has_manifest"]]
        portfolio_result = score_portfolio(chip_paths)

        return {
            "lab_research_quality_score": round(portfolio_result["average_score"] / 100.0, 4),
            "portfolio_health": round(portfolio_result["average_score"] / 100.0, 4),
            "methodology_coverage": 0.0,
            "chips_evaluated": portfolio_result["portfolio_size"],
            "graduation_pipeline_count": 0,
            "portfolio_result": portfolio_result,
            "comparison_class": "benchmark_grounded",
        }

    elif research_focus == "methodology":
        methodology_area = mutations.get("methodology_area", "evaluation_frameworks")
        state = _lab_state(_resolve_repo_root(chip_search_dir), chip_search_dir)
        methodology = _score_methodology_area(state, methodology_area)
        coverage = methodology["score"]
        return {
            "lab_research_quality_score": round(coverage, 4),
            "portfolio_health": 0.0,
            "methodology_coverage": round(coverage, 4),
            "chips_evaluated": 0,
            "graduation_pipeline_count": 0,
            "methodology_area": methodology_area,
            "comparison_class": "exploratory_frontier",
            "artifact_basis": methodology["details"],
        }

    elif research_focus == "domain_discovery":
        trend_source = mutations.get("trend_source", "github")
        state = _lab_state(_resolve_repo_root(chip_search_dir), chip_search_dir)
        discovery = _score_domain_discovery(state, trend_source)
        coverage = discovery["score"]
        return {
            "lab_research_quality_score": round(coverage, 4),
            "portfolio_health": 0.0,
            "methodology_coverage": 0.0,
            "chips_evaluated": 0,
            "graduation_pipeline_count": 0,
            "trend_source": trend_source,
            "comparison_class": "exploratory_frontier",
            "artifact_basis": discovery["details"],
        }

    elif research_focus == "transfer_patterns":
        state = _lab_state(_resolve_repo_root(chip_search_dir), chip_search_dir)
        transfer = _score_transfer_patterns(state)
        return {
            "lab_research_quality_score": transfer["score"],
            "portfolio_health": 0.0,
            "methodology_coverage": 0.0,
            "chips_evaluated": 0,
            "graduation_pipeline_count": 0,
            "comparison_class": "exploratory_frontier",
            "artifact_basis": transfer["details"],
            "note": "Transfer pattern scoring now reflects actual doctrine, packet, run-history, and portfolio-maturity state.",
        }

    elif research_focus == "trend_simulation":
        # Run MiroFish trend simulation and return prediction quality metrics
        from .trend_scanner import simulate_opportunities, SEED_OPPORTUNITIES
        sim = simulate_opportunities(SEED_OPPORTUNITIES, seed=42)
        report = sim.get("simulation_report", {})
        cal = sim.get("calibration", {})
        hist = cal.get("historical_calibration", {})
        agg_brier = hist.get("aggregate_brier", 1.0)
        # Prediction quality = inverse of Brier score (lower Brier = better)
        prediction_score = round(1.0 - agg_brier, 4)
        return {
            "lab_research_quality_score": prediction_score,
            "portfolio_health": 0.0,
            "methodology_coverage": 0.0,
            "chips_evaluated": 0,
            "graduation_pipeline_count": 0,
            "trend_prediction_score": prediction_score,
            "simulation_calibration": agg_brier,
            "domain_predictions_count": len(report.get("domain_predictions", [])),
            "comparison_class": "exploratory_frontier",
            "note": "Simulation predictions are exploratory_frontier. Calibration via Brier scoring.",
        }

    elif research_focus == "agi_theory":
        state = _lab_state(_resolve_repo_root(chip_search_dir), chip_search_dir)
        agi = _score_agi_theory(state)
        return {
            "lab_research_quality_score": agi["score"],
            "portfolio_health": 0.0,
            "methodology_coverage": 0.0,
            "chips_evaluated": 0,
            "graduation_pipeline_count": 0,
            "comparison_class": "exploratory_frontier",
            "artifact_basis": agi["details"],
            "note": "AGI theory remains capped below production confidence until the lab has more repeated portfolio evidence.",
        }

    else:
        return {
            "lab_research_quality_score": 0.0,
            "portfolio_health": 0.0,
            "methodology_coverage": 0.0,
            "chips_evaluated": 0,
            "graduation_pipeline_count": 0,
            "comparison_class": "exploratory_frontier",
            "error": f"Unknown research_focus: {research_focus}",
        }
