"""Tests for MiroFish discovery batch and program canonicalization."""

from argparse import Namespace
import json
from pathlib import Path

from chip_labs.cli import (
    cmd_mirofish_discovery_program_bundle,
    cmd_mirofish_discovery_program_materialize,
    cmd_mirofish_discovery_program_progress,
)
from chip_labs.mirofish.discovery import (
    build_discovery_program_scaffold,
    canonicalize_discovery_batch,
    canonicalize_discovery_program,
    format_discovery_program_markdown,
    merge_discovery_cluster_packets,
    split_discovery_program_scaffold,
)
from chip_labs.mirofish.curated_frontier import (
    build_curated_frontier_packet,
    format_curated_frontier_markdown,
)


def test_canonicalize_discovery_batch_preserves_basic_counts() -> None:
    packet = {
        "batch_id": "discovery-batch-test",
        "existing_domain_ids": ["startup-yc"],
        "raw_candidates": [
            {
                "label": "Dental Insurance Appeals AI",
                "description": "Helps recurring insurance appeal work for dental clinics.",
                "specialization_surface": "dental insurance appeal drafting",
                "mastery_surface": "improving recurring appeal win-rate for clinics",
                "user_value_loop": "gather denial data, draft appeal, learn from payer responses",
                "domain_tags": ["healthcare", "revenue-cycle"],
                "evidence_sources": ["operator-interviews"],
                "evidence_summary": "Clinics repeatedly lose time on appeals with similar structures.",
                "adjacent_domains": ["legal-ops"],
                "duplicate_aliases": [],
                "confidence_read": "medium",
                "promotion_status": "candidate",
                "raw_observation": "Dental offices want a repeated appeals loop.",
            },
            {
                "label": "Founders",
                "description": "A tool for founders.",
                "raw_observation": "Founders need help.",
            },
        ],
    }

    result = canonicalize_discovery_batch(packet)

    assert result["summary"]["raw_count"] == 2
    assert result["summary"]["accepted_count"] == 1
    assert result["summary"]["rejected_count"] == 1


def test_canonicalize_discovery_program_emits_scale_readiness_and_agent_rollup() -> None:
    program = {
        "program_id": "mirofish-discovery-smoke",
        "stage_label": "smoke",
        "target_agent_count": 100,
        "existing_domain_ids": ["startup-yc"],
        "agent_submissions": [
            {
                "agent_id": "agent-001",
                "raw_candidates": [
                    {
                        "label": "Vendor Security Review Copilot",
                        "description": "Helps teams answer recurring vendor security review requests.",
                        "specialization_surface": "security review response drafting",
                        "mastery_surface": "turning repeated vendor review work into a reusable advantage",
                        "user_value_loop": "collect controls, draft answers, reuse winning evidence",
                        "domain_tags": ["security", "compliance"],
                        "evidence_sources": ["operator-interviews"],
                        "evidence_summary": "Teams repeatedly answer the same security review questions.",
                        "adjacent_domains": ["legal-ops"],
                        "duplicate_aliases": [],
                        "confidence_read": "medium",
                        "promotion_status": "candidate",
                        "raw_observation": "Repeated vendor reviews still eat security team time.",
                    }
                ],
            },
            {
                "agent_id": "agent-002",
                "raw_candidates": [
                    {
                        "label": "Vendor Security Questionnaire Copilot",
                        "description": "Handles recurring vendor security questionnaire work.",
                        "specialization_surface": "security questionnaire response packaging",
                        "mastery_surface": "improving repeatable vendor questionnaire throughput",
                        "user_value_loop": "pull prior answers, draft response, update evidence set",
                        "domain_tags": ["security", "compliance"],
                        "evidence_sources": ["operator-interviews"],
                        "evidence_summary": "The work repeats across questionnaires with only small variants.",
                        "adjacent_domains": ["legal-ops"],
                        "duplicate_aliases": ["Vendor Security Review Copilot"],
                        "confidence_read": "medium",
                        "promotion_status": "candidate",
                        "raw_observation": "Questionnaire work repeats across vendors.",
                    }
                ],
            },
            {
                "agent_id": "agent-003",
                "raw_candidates": [
                    {
                        "label": "Dental Insurance Appeals AI",
                        "description": "Helps recurring insurance appeal work for dental clinics.",
                        "specialization_surface": "dental insurance appeal drafting",
                        "mastery_surface": "improving recurring appeal win-rate for clinics",
                        "user_value_loop": "gather denial data, draft appeal, learn from payer responses",
                        "domain_tags": ["healthcare", "revenue-cycle"],
                        "evidence_sources": ["operator-interviews"],
                        "evidence_summary": "Clinics repeatedly lose time on appeals with similar structures.",
                        "adjacent_domains": ["legal-ops"],
                        "duplicate_aliases": [],
                        "confidence_read": "medium",
                        "promotion_status": "candidate",
                        "raw_observation": "Dental offices want a repeated appeals loop.",
                    }
                ],
            },
            {
                "agent_id": "agent-004",
                "raw_candidates": [
                    {
                        "label": "Founders",
                        "description": "A tool for founders.",
                        "raw_observation": "Founders need help.",
                    }
                ],
            },
        ],
    }

    result = canonicalize_discovery_program(program)

    assert result["packet_kind"] == "mirofish_discovery_program"
    assert result["participating_agent_count"] == 4
    assert result["summary"]["raw_count"] == 4
    assert result["summary"]["accepted_count"] == 2
    assert result["summary"]["merged_count"] == 1
    assert result["summary"]["rejected_count"] == 1
    assert result["scale_readiness"]["next_stage"] == "run_100_agent_pilot"
    assert len(result["agent_rollup"]) == 4
    assert result["accepted_candidates"][0]["supporting_agent_count"] >= 1


def test_build_discovery_program_scaffold_creates_100_agent_plan() -> None:
    scaffold = build_discovery_program_scaffold()

    assert scaffold["packet_kind"] == "mirofish_discovery_program_scaffold"
    assert scaffold["profile"] == "viral"
    assert scaffold["target_agent_count"] == 100
    assert len(scaffold["agent_submissions"]) == 100
    assert scaffold["agent_submissions"][0]["agent_id"] == "agent-001"
    assert scaffold["agent_submissions"][-1]["agent_id"] == "agent-100"
    assert scaffold["cluster_plan"][0]["cluster_id"] == "creator-growth-systems"


def test_build_discovery_program_scaffold_scales_diverse_frontier_to_1000() -> None:
    scaffold = build_discovery_program_scaffold(
        program_id="mirofish-discovery-program-frontier-1000-diverse",
        target_agent_count=1000,
        stage_label="frontier_1000_diverse",
        profile="diverse_frontier",
    )

    assert scaffold["profile"] == "diverse_frontier"
    assert scaffold["target_agent_count"] == 1000
    assert len(scaffold["agent_submissions"]) == 1000
    assert len(scaffold["cluster_plan"]) == 18
    assert sum(cluster["agent_count"] for cluster in scaffold["cluster_plan"]) == 1000
    assert scaffold["cluster_plan"][0]["cluster_id"] == "creator-growth-systems"


def test_split_discovery_program_scaffold_emits_cluster_packets() -> None:
    scaffold = build_discovery_program_scaffold()

    result = split_discovery_program_scaffold(scaffold)

    assert result["packet_kind"] == "mirofish_discovery_program_cluster_packets"
    assert result["cluster_packet_count"] == 10
    assert result["summary"]["agent_count"] == 100
    assert len(result["cluster_plan"]) == 10
    assert result["collection_rules"]["max_candidates_per_agent"] == 3
    assert result["cluster_packets"][0]["packet_kind"] == "mirofish_discovery_cluster_packet"
    assert result["cluster_packets"][0]["target_agent_count"] == 16
    assert len(result["cluster_packets"][0]["agent_submissions"]) == 16


def test_format_discovery_program_markdown_renders_scaffold_summary() -> None:
    scaffold = build_discovery_program_scaffold()

    result = format_discovery_program_markdown(scaffold, title="Pilot Brief")

    assert "# Pilot Brief" in result
    assert "## Cluster Allocation" in result
    assert "`creator-growth-systems`" in result
    assert "Creator Growth Systems" in result


def test_merge_discovery_cluster_packets_round_trips_agent_submissions() -> None:
    scaffold = build_discovery_program_scaffold()
    cluster_bundle = split_discovery_program_scaffold(scaffold)

    result = merge_discovery_cluster_packets(cluster_bundle)

    assert result["packet_kind"] == "mirofish_discovery_program_input"
    assert result["program_id"] == scaffold["program_id"]
    assert result["target_agent_count"] == 100
    assert len(result["cluster_plan"]) == 10
    assert result["collection_rules"]["min_candidates_per_agent"] == 1
    assert len(result["agent_submissions"]) == 100
    assert result["agent_submissions"][0]["agent_id"] == "agent-001"


def test_materialize_discovery_program_writes_cluster_files(tmp_path: Path) -> None:
    scaffold = build_discovery_program_scaffold()
    cluster_bundle = split_discovery_program_scaffold(scaffold)
    input_path = tmp_path / "cluster_bundle.json"
    output_manifest = tmp_path / "manifest.json"
    output_dir = tmp_path / "materialized"
    input_path.write_text(json.dumps(cluster_bundle, indent=2), encoding="utf-8")

    cmd_mirofish_discovery_program_materialize(
        Namespace(
            input=str(input_path),
            output_dir=str(output_dir),
            index_title="Pilot Cluster Directory",
            output=str(output_manifest),
        )
    )

    manifest = json.loads(output_manifest.read_text(encoding="utf-8"))
    assert manifest["file_count"] == 11
    assert (output_dir / "README.md").exists()
    assert (output_dir / "01_creator-growth-systems.json").exists()
    assert "Pilot Cluster Directory" in (output_dir / "README.md").read_text(encoding="utf-8")


def test_discovery_program_progress_reports_empty_materialized_directory(tmp_path: Path) -> None:
    scaffold = build_discovery_program_scaffold()
    cluster_bundle = split_discovery_program_scaffold(scaffold)
    input_path = tmp_path / "cluster_bundle.json"
    manifest_path = tmp_path / "manifest.json"
    progress_path = tmp_path / "progress.json"
    progress_md_path = tmp_path / "progress.md"
    output_dir = tmp_path / "materialized"
    input_path.write_text(json.dumps(cluster_bundle, indent=2), encoding="utf-8")

    cmd_mirofish_discovery_program_materialize(
        Namespace(
            input=str(input_path),
            output_dir=str(output_dir),
            index_title="Pilot Cluster Directory",
            output=str(manifest_path),
        )
    )
    cmd_mirofish_discovery_program_progress(
        Namespace(
            input_dir=str(output_dir),
            output=str(progress_path),
            markdown_output=str(progress_md_path),
            title="Pilot Progress",
        )
    )

    progress = json.loads(progress_path.read_text(encoding="utf-8"))
    assert progress["packet_kind"] == "mirofish_discovery_program_progress"
    assert progress["summary"]["cluster_count"] == 10
    assert progress["summary"]["filled_agent_count"] == 0
    assert progress["summary"]["total_agent_count"] == 100
    assert "Pilot Progress" in progress_md_path.read_text(encoding="utf-8")


def test_discovery_program_bundle_rebuilds_from_materialized_directory(tmp_path: Path) -> None:
    scaffold = build_discovery_program_scaffold()
    cluster_bundle = split_discovery_program_scaffold(scaffold)
    input_path = tmp_path / "cluster_bundle.json"
    manifest_path = tmp_path / "manifest.json"
    rebuilt_path = tmp_path / "rebuilt_bundle.json"
    output_dir = tmp_path / "materialized"
    input_path.write_text(json.dumps(cluster_bundle, indent=2), encoding="utf-8")

    cmd_mirofish_discovery_program_materialize(
        Namespace(
            input=str(input_path),
            output_dir=str(output_dir),
            index_title="Pilot Cluster Directory",
            output=str(manifest_path),
        )
    )
    cmd_mirofish_discovery_program_bundle(
        Namespace(
            input_dir=str(output_dir),
            output=str(rebuilt_path),
        )
    )

    rebuilt = json.loads(rebuilt_path.read_text(encoding="utf-8"))
    assert rebuilt["packet_kind"] == "mirofish_discovery_program_cluster_packets"
    assert rebuilt["cluster_packet_count"] == 10
    assert rebuilt["summary"]["agent_count"] == 100
    assert rebuilt["cluster_packets"][0]["cluster_id"] == "creator-growth-systems"


def test_build_curated_frontier_packet_emits_500_unique_domains() -> None:
    packet = build_curated_frontier_packet()

    accepted = packet["accepted_candidates"]
    cluster_counts = {row["cluster_id"]: row["count"] for row in packet["cluster_summary"]}
    domain_ids = {row["domain_id"] for row in accepted}

    assert packet["packet_kind"] == "mirofish_curated_frontier_packet"
    assert packet["summary"]["accepted_count"] == 500
    assert packet["summary"]["unique_idea_count"] == 500
    assert len(accepted) == 500
    assert len(domain_ids) == 500
    assert cluster_counts["creator-growth-systems"] == 50
    assert cluster_counts["crypto-defi-trading"] == 50
    assert not any(
        domain_id.endswith(("-copilot", "-engine", "-loop", "-lab", "-os"))
        for domain_id in domain_ids
    )


def test_format_curated_frontier_markdown_renders_cluster_breakdown() -> None:
    packet = build_curated_frontier_packet(target_count=20)

    markdown = format_curated_frontier_markdown(packet, title="Curated Frontier")

    assert "# Curated Frontier" in markdown
    assert "## Cluster Breakdown" in markdown
    assert "`creator-growth-systems`" in markdown
    assert "Accepted domains" in markdown
