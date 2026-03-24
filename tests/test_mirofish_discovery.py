"""Tests for MiroFish discovery batch and program canonicalization."""

from chip_labs.mirofish.discovery import (
    build_discovery_program_scaffold,
    canonicalize_discovery_batch,
    canonicalize_discovery_program,
    format_discovery_program_markdown,
    merge_discovery_cluster_packets,
    split_discovery_program_scaffold,
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
    assert scaffold["target_agent_count"] == 100
    assert len(scaffold["agent_submissions"]) == 100
    assert scaffold["agent_submissions"][0]["agent_id"] == "agent-001"
    assert scaffold["agent_submissions"][-1]["agent_id"] == "agent-100"
    assert scaffold["cluster_plan"][0]["cluster_id"] == "security-compliance-response"


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
    assert "`security-compliance-response`" in result
    assert "Security / Compliance Response" in result


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
