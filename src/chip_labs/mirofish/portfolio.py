"""Portfolio-scale MiroFish runner for the legacy 515-domain universe.

Bridges the old `scripts/predict_500_domains.py` dataset into the repo-local
CLI and emits reviewable artifacts under `research/meta/`.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
import sys
from typing import Any

from .graph import DomainGraph, build_graph_from_opportunities
from .macro import MARCH_2026, MARCH_2026_EVENTS
from .report import generate_prediction_report
from .signals import create_shock, signals_from_graph, signals_from_opportunities
from .simulation import run_ensemble, run_simulation


def load_full_domain_universe() -> dict[str, Any]:
    """Load the legacy 515-domain MiroFish universe from the script dataset."""
    _ensure_legacy_scripts_importable()
    predict_100 = import_module("predict_100_domains")
    predict_250 = import_module("predict_250_domains")
    domains_v4 = import_module("domains_v4")

    first_100 = (
        list(predict_100.EXISTING_CHIPS)
        + list(predict_100.NEW_CANDIDATES)
        + list(predict_100.VIRAL_DOMAINS)
        + list(predict_100.NEW_48_DOMAINS)
    )
    v3_domains = [deepcopy(item) for item in first_100 + list(predict_250.NEW_150_DOMAINS)]
    v4_domains = [deepcopy(item) for item in list(domains_v4.NEW_250_V4_DOMAINS)]
    v3_relationships = list(predict_100.RELATIONSHIPS) + list(predict_250.NEW_RELATIONSHIPS)
    all_domains = [_enrich_v3_domain(item) for item in v3_domains] + v4_domains
    all_relationships = v3_relationships + list(domains_v4.NEW_V4_RELATIONSHIPS)

    domain_ids = [item["domain_id"] for item in all_domains]
    if len(set(domain_ids)) != len(domain_ids):
        raise ValueError("Duplicate domain_ids detected in the 515-domain universe.")

    return {
        "all_domains": all_domains,
        "all_relationships": all_relationships,
        "v3_domains": v3_domains,
        "v4_domains": v4_domains,
        "v3_relationships": v3_relationships,
        "shocks": _v4_shocks(),
        "macro": MARCH_2026,
        "macro_events": MARCH_2026_EVENTS,
    }


def run_full_portfolio_evaluation(
    seed: int = 42,
    max_rounds: int = 20,
    flagship_count_per_type: int = 50,
    ensemble_runs: int = 30,
    ensemble_count_per_type: int = 15,
    convergence_threshold: float = 0.005,
    min_runs: int = 15,
    bootstrap_resamples: int = 1000,
) -> dict[str, Any]:
    """Run the current MiroFish engine against the full legacy portfolio."""
    universe = load_full_domain_universe()
    domains = universe["all_domains"]
    relationships = universe["all_relationships"]
    shocks = universe["shocks"]
    macro = universe["macro"]
    macro_events = universe["macro_events"]

    graph = build_full_portfolio_graph(domains, relationships)
    domain_ids = [item["domain_id"] for item in domains]
    all_signals = signals_from_opportunities(domains) + signals_from_graph(graph)

    result = _run_flagship(
        graph,
        domain_ids,
        all_signals,
        shocks,
        max_rounds=max_rounds,
        seed=seed,
        macro=macro,
        macro_events=macro_events,
        count_per_type=flagship_count_per_type,
    )

    report = generate_prediction_report(result, static_rankings=domains)
    ensemble = run_ensemble(
        graph,
        domain_ids=domain_ids,
        signals=all_signals,
        shocks=shocks,
        max_rounds=max_rounds,
        n_runs=ensemble_runs,
        base_seed=seed,
        context="builder_community",
        count_per_type=ensemble_count_per_type,
        macro=macro,
        macro_events=macro_events,
        convergence_threshold=convergence_threshold,
        min_runs=min_runs,
        bootstrap_resamples=bootstrap_resamples,
    )
    ranked_domains = _ranked_portfolio_rows(domains, result, report, ensemble)
    top_choice_row = max(
        ranked_domains,
        key=lambda row: row["agent_choice_signal"],
        default={"domain_id": None, "agent_choice_signal": 0.0},
    )
    top_retained_row = max(
        ranked_domains,
        key=lambda row: row["final_adoption_rate"],
        default={"domain_id": None, "final_adoption_rate": 0.0},
    )

    return {
        "packet_kind": "mirofish_portfolio_run",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "meta": {
            "title": "MiroFish Portfolio Run",
            "domain_count": len(domains),
            "v3_domain_count": len(universe["v3_domains"]),
            "v4_domain_count": len(universe["v4_domains"]),
            "graph_nodes": graph.node_count,
            "graph_edges": graph.edge_count,
            "signal_count": len(all_signals),
            "shock_count": len(shocks),
            "rounds": max_rounds,
            "flagship_count_per_type": flagship_count_per_type,
            "ensemble_runs": ensemble.get("n_runs", ensemble_runs),
            "ensemble_count_per_type": ensemble_count_per_type,
            "bootstrap_resamples": bootstrap_resamples,
            "macro_context": "march_2026",
        },
        "top_line": {
            "top_ensemble_domain": ranked_domains[0]["domain_id"] if ranked_domains else None,
            "top_ensemble_mean_adoption": ranked_domains[0]["ensemble_mean_adoption"] if ranked_domains else 0.0,
            "top_choice_domain": top_choice_row.get("domain_id"),
            "top_choice_signal": top_choice_row.get("agent_choice_signal", 0.0),
            "top_retained_domain": top_retained_row.get("domain_id"),
            "top_retained_adoption": top_retained_row.get("final_adoption_rate", 0.0),
        },
        "ranked_domains": ranked_domains,
        "domain_predictions": report.get("domain_predictions", []),
        "cross_domain": report.get("cross_domain", {}),
        "ensemble": ensemble,
        "governance_note": (
            "Portfolio runs are exploratory_frontier methodology artifacts. "
            "Use them to compare domains and inspect mechanism changes, not to auto-promote doctrine."
        ),
    }


def build_portfolio_readout(
    run_packet: dict[str, Any],
    top_n: int = 30,
    enterprise_n: int = 15,
    newly_discovered_n: int = 15,
) -> dict[str, Any]:
    """Build a concise ranked readout from a saved portfolio run."""
    rows = list(run_packet.get("ranked_domains", []))
    top_domains = rows[:top_n]
    enterprise_rows = [
        row for row in rows
        if {"compliance", "audit", "enterprise-sales", "enterprise-ops", "risk_management"} & set(row.get("domain_tags", []))
    ][:enterprise_n]
    newly_discovered_rows = [row for row in rows if row.get("generation") == "v4"][:newly_discovered_n]

    cautions: list[str] = []
    if top_domains and top_domains[0].get("ensemble_mean_adoption", 0.0) < 0.05:
        cautions.append("Top ensemble adoption remains modest, so rank order is more trustworthy than absolute demand magnitude.")
    if any("interest_to_choice_friction" in row.get("diagnostic_tags", []) for row in enterprise_rows):
        cautions.append("Enterprise-response domains still show visible interest-to-choice friction even after the latest methodology tranches.")
    if any(row.get("final_adoption_rate", 0.0) < row.get("agent_choice_signal", 0.0) * 0.4 for row in enterprise_rows):
        cautions.append("Several enterprise domains still lose too much between in-run choice and retained adoption.")

    return {
        "packet_kind": "mirofish_portfolio_readout",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_run_created_at": run_packet.get("created_at"),
        "meta": run_packet.get("meta", {}),
        "top_domains_overall": top_domains,
        "top_enterprise_domains": enterprise_rows,
        "top_newly_discovered_domains": newly_discovered_rows,
        "methodology_cautions": cautions,
        "governance_note": run_packet.get("governance_note", ""),
    }


def format_portfolio_readout_markdown(
    readout_packet: dict[str, Any],
    title: str = "MiroFish Portfolio Export",
) -> str:
    """Format a portfolio readout packet as operator-facing markdown."""
    meta = readout_packet.get("meta", {})
    overall_rows = list(readout_packet.get("top_domains_overall", []))
    enterprise_rows = list(readout_packet.get("top_enterprise_domains", []))
    newly_discovered_rows = list(readout_packet.get("top_newly_discovered_domains", []))
    cautions = list(readout_packet.get("methodology_cautions", []))

    def _leader_line(label: str, rows: list[dict[str, Any]]) -> str:
        if not rows:
            return f"- {label}: none"
        row = rows[0]
        return (
            f"- {label}: `{row.get('domain_id', 'unknown')}` "
            f"(ensemble {row.get('ensemble_mean_adoption', 0.0):.2%}, "
            f"choice {row.get('agent_choice_signal', 0.0):.2%})"
        )

    def _table_lines(rows: list[dict[str, Any]]) -> list[str]:
        lines = [
            "| Rank | Domain | Ensemble | Choice | Peak Interest | Final Adoption | Notes |",
            "|------|--------|----------|--------|---------------|----------------|-------|",
        ]
        for idx, row in enumerate(rows, start=1):
            notes = ", ".join(row.get("diagnostic_tags", [])) or "-"
            lines.append(
                f"| {idx} | `{row.get('domain_id', 'unknown')}` | "
                f"{row.get('ensemble_mean_adoption', 0.0):.2%} | "
                f"{row.get('agent_choice_signal', 0.0):.2%} | "
                f"{row.get('peak_interest_probability', 0.0):.2%} | "
                f"{row.get('final_adoption_rate', 0.0):.2%} | {notes} |"
            )
        if len(lines) == 2:
            lines.append("| - | none | - | - | - | - | - |")
        return lines

    lines = [
        f"# {title}",
        "",
        f"> Generated: {readout_packet.get('created_at', 'unknown')}",
        f"> Source run: {readout_packet.get('source_run_created_at', 'unknown')}",
        f"> Domains: {meta.get('domain_count', 'unknown')}",
        f"> Rounds: {meta.get('rounds', 'unknown')}",
        f"> Ensemble runs: {meta.get('ensemble_runs', 'unknown')}",
        f"> Bootstrap resamples: {meta.get('bootstrap_resamples', 'unknown')}",
        "",
        "## Top Line",
        "",
        _leader_line("Overall leader", overall_rows),
        _leader_line("Enterprise leader", enterprise_rows),
        _leader_line("Newly discovered `v4` leader", newly_discovered_rows),
    ]

    if cautions:
        lines.extend(["", "## Methodology Cautions", ""])
        for caution in cautions:
            lines.append(f"- {caution}")

    lines.extend(["", "## Top Overall", ""])
    lines.extend(_table_lines(overall_rows))

    lines.extend(["", "## Top Enterprise", ""])
    lines.extend(_table_lines(enterprise_rows))

    lines.extend(["", "## Top Newly Discovered `v4`", ""])
    lines.extend(_table_lines(newly_discovered_rows))

    governance_note = readout_packet.get("governance_note", "")
    if governance_note:
        lines.extend(["", "---", "", f"*{governance_note}*"])

    return "\n".join(lines)


def build_full_portfolio_graph(
    domains: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
) -> DomainGraph:
    """Build the portfolio graph while preserving explicit legacy priors."""
    graph = DomainGraph()
    for domain in domains:
        props = {
            "description": domain.get("description", ""),
            "composite_score": domain.get("composite_score", 0.0),
            "scores": domain.get("scores", {}),
            "rationale": domain.get("rationale", ""),
            "domain_tags": list(domain.get("domain_tags", [])),
            "retention_score": domain.get("retention_score", 0.5),
            "urgency_score": domain.get("urgency_score", 0.5),
            "status": domain.get("status", "candidate"),
        }
        graph.add_node(domain["domain_id"], "domain", domain.get("label", domain["domain_id"]), props)

    tech_nodes = {
        "ai-tools", "blockchain", "web-platform", "social-media", "saas-infra",
        "healthcare-tech", "govtech", "enterprise-infra", "fintech-platform",
        "edtech-platform",
    }
    for node_id in tech_nodes:
        graph.add_node(node_id, "technology", node_id)

    source_tech_map = {
        "github": "ai-tools",
        "x_twitter": "social-media",
        "producthunt": "saas-infra",
    }
    for domain in domains:
        for source in domain.get("evidence_sources", []):
            tech = source_tech_map.get(source)
            if tech:
                graph.add_edge(tech, domain["domain_id"], "ENABLES", 0.4)

    inferred_graph = build_graph_from_opportunities(domains)
    for node_id, node_data in inferred_graph.nodes.items():
        if node_id not in graph.nodes:
            graph.add_node(node_id, node_data["type"], node_data["label"], node_data.get("properties", {}))
            continue
        merged = dict(node_data.get("properties", {}))
        merged.update(graph.nodes[node_id].get("properties", {}))
        graph.nodes[node_id]["properties"] = merged

    for edge in inferred_graph.edges:
        graph.add_edge(edge["source"], edge["target"], edge["relationship"], edge.get("weight", 0.5))

    for relation in relationships:
        if relation["source"] in graph.nodes and relation["target"] in graph.nodes:
            graph.add_edge(
                relation["source"],
                relation["target"],
                relation["relationship"],
                relation.get("weight", 0.5),
            )
    return graph


def _run_flagship(
    graph: DomainGraph,
    domain_ids: list[str],
    signals: list[dict[str, Any]],
    shocks: list[dict[str, Any]],
    *,
    max_rounds: int,
    seed: int,
    macro: Any,
    macro_events: list[dict[str, Any]],
    count_per_type: int,
) -> dict[str, Any]:
    from .personas import generate_personas

    personas = generate_personas(graph, domain_ids=domain_ids, count_per_type=count_per_type, seed=seed)
    return run_simulation(
        graph,
        domain_ids,
        personas=personas,
        signals=signals,
        shocks=shocks,
        max_rounds=max_rounds,
        seed=seed,
        macro=macro,
        macro_events=macro_events,
        context="builder_community",
    )


def _ranked_portfolio_rows(
    domains: list[dict[str, Any]],
    flagship: dict[str, Any],
    report: dict[str, Any],
    ensemble: dict[str, Any],
) -> list[dict[str, Any]]:
    prediction_map = {
        row["domain_id"]: row
        for row in report.get("domain_predictions", [])
        if row.get("domain_id")
    }
    rows: list[dict[str, Any]] = []
    v3_ids = {item["domain_id"] for item in domains[:250]}

    for domain in domains:
        domain_id = domain["domain_id"]
        sim_data = flagship.get("domains", {}).get(domain_id, {})
        ens_data = ensemble.get("domains", {}).get(domain_id, {})
        prediction = prediction_map.get(domain_id, {})
        rows.append({
            "domain_id": domain_id,
            "label": domain.get("label", domain_id),
            "generation": "v3" if domain_id in v3_ids else "v4",
            "status": domain.get("status", "candidate"),
            "domain_tags": list(domain.get("domain_tags", [])),
            "static_score": round(domain.get("composite_score", 0.0), 4),
            "retention_score": round(domain.get("retention_score", 0.5), 4),
            "urgency_score": round(domain.get("urgency_score", 0.5), 4),
            "ensemble_mean_adoption": round(ens_data.get("mean_adoption", 0.0), 4),
            "ensemble_ci_lower": round(ens_data.get("bootstrap_ci_lower", 0.0), 4),
            "ensemble_ci_upper": round(ens_data.get("bootstrap_ci_upper", 0.0), 4),
            "ensemble_mean_trial": round(ens_data.get("mean_trial", 0.0), 4),
            "ensemble_mean_churn": round(ens_data.get("mean_churn", 0.0), 4),
            "confidence_width": round(ens_data.get("confidence_width", 0.0), 4),
            "agent_choice_signal": round(prediction.get("agent_choice_signal", 0.0), 4),
            "peak_interest_probability": round(prediction.get("peak_interest_probability", 0.0), 4),
            "final_adoption_rate": round(sim_data.get("final_adoption_rate", 0.0), 4),
            "final_trial_rate": round(sim_data.get("final_trial_rate", 0.0), 4),
            "final_retention_rate": round(sim_data.get("final_retention_rate", 0.0), 4),
            "final_churn_rate": round(sim_data.get("final_churn_rate", 0.0), 4),
            "final_committed_rate": round(sim_data.get("final_committed_rate", 0.0), 4),
            "diagnostic_tags": _diagnostic_tags(prediction, ens_data),
        })

    rows.sort(
        key=lambda row: (
            row["ensemble_mean_adoption"],
            row["agent_choice_signal"],
            row["final_adoption_rate"],
        ),
        reverse=True,
    )
    return rows


def _diagnostic_tags(prediction: dict[str, Any], ensemble_row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    choice = prediction.get("agent_choice_signal", 0.0)
    interest = prediction.get("peak_interest_probability", 0.0)
    mean_adoption = ensemble_row.get("mean_adoption", 0.0)
    mean_trial = ensemble_row.get("mean_trial", 0.0)
    mean_churn = ensemble_row.get("mean_churn", 0.0)
    if interest - choice >= 0.45:
        tags.append("interest_to_choice_friction")
    if choice - mean_adoption >= 0.12:
        tags.append("attention_retention_drop")
    if mean_trial > 0.02 and mean_adoption < mean_trial * 0.4:
        tags.append("trial_to_adoption_loss")
    if mean_churn >= 0.03:
        tags.append("elevated_churn")
    return tags


def _ensure_legacy_scripts_importable() -> None:
    scripts_dir = _repo_root() / "scripts"
    scripts_str = str(scripts_dir)
    if scripts_str not in sys.path:
        sys.path.insert(0, scripts_str)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _enrich_v3_domain(domain: dict[str, Any]) -> dict[str, Any]:
    enriched = deepcopy(domain)
    tags = set(enriched.get("domain_tags", []))
    if "retention_score" not in enriched:
        if tags & {"productivity", "workflow", "dx"}:
            enriched["retention_score"] = 0.7
        elif tags & {"trading", "defi", "alpha"}:
            enriched["retention_score"] = 0.5
        elif tags & {"content_quality", "creative"}:
            enriched["retention_score"] = 0.6
        else:
            enriched["retention_score"] = 0.5
    if "urgency_score" not in enriched:
        if tags & {"career", "reskill", "easy_start"}:
            enriched["urgency_score"] = 0.8
        elif tags & {"compliance", "risk_management"}:
            enriched["urgency_score"] = 0.7
        elif tags & {"alpha", "first_mover", "edge"}:
            enriched["urgency_score"] = 0.6
        else:
            enriched["urgency_score"] = 0.5
    return enriched


def _v4_shocks() -> list[dict[str, Any]]:
    return [
        create_shock(
            "mass_layoff",
            [
                "resume-ai", "career-pivot-ai", "upskill-path-ai",
                "ai-proof-career", "coding-bootcamp-ai",
                "prompt-job-skills", "interview-prep-ai",
            ],
            inject_at_round=3,
        ),
        create_shock(
            "open_source_release",
            [
                "ai-agent-builder", "cursor-copilot", "fine-tuning-lab",
                "rag-pipeline", "multi-modal-ai", "prompt-engineer",
            ],
            inject_at_round=5,
        ),
        create_shock(
            "government_subsidy",
            [
                "coding-bootcamp-ai", "upskill-path-ai", "corporate-training-ai",
                "ai-literacy-coach", "digital-skills-ai", "employee-onboarding-ai",
            ],
            inject_at_round=8,
        ),
        create_shock(
            "security_breach",
            [
                "cybersecurity-ai", "ai-compliance-checker", "hipaa-compliance-ai",
                "fraud-detection-ai", "data-privacy-ai", "enterprise-search-ai",
            ],
            inject_at_round=10,
        ),
        create_shock(
            "platform_ban",
            [
                "content", "faceless-youtube", "tiktok-shop",
                "ai-ghostwriter", "ai-music-producer", "social-media-manager",
            ],
            inject_at_round=12,
        ),
    ]
