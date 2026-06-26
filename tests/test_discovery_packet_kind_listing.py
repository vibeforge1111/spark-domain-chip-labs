from __future__ import annotations

import pytest

from chip_labs.mirofish.discovery import (
    build_discovery_program_scaffold,
    canonicalize_discovery_program,
    format_discovery_program_markdown,
    merge_discovery_cluster_packets,
    split_discovery_program_scaffold,
)


def _valid_program_result() -> dict[str, object]:
    return canonicalize_discovery_program(
        {
            "program_id": "mirofish-discovery-smoke",
            "stage_label": "smoke",
            "target_agent_count": 1,
            "existing_domain_ids": [],
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
                            "evidence_summary": "Teams repeatedly answer similar security review questions.",
                            "adjacent_domains": ["legal-ops"],
                            "duplicate_aliases": [],
                            "confidence_read": "medium",
                            "promotion_status": "candidate",
                            "raw_observation": "Repeated vendor reviews still eat security team time.",
                        }
                    ],
                }
            ],
        }
    )


def test_discovery_markdown_unknown_packet_kind_lists_supported_values() -> None:
    with pytest.raises(ValueError) as error:
        format_discovery_program_markdown({"packet_kind": "mirofish_discovery_program_bogus"})

    message = str(error.value)
    assert "mirofish_discovery_program_bogus" in message
    for packet_kind in (
        "mirofish_discovery_program_scaffold",
        "mirofish_discovery_program_input",
        "mirofish_discovery_program_cluster_packets",
        "mirofish_discovery_program",
    ):
        assert packet_kind in message


def test_discovery_markdown_supported_packet_kinds_still_render() -> None:
    scaffold = build_discovery_program_scaffold()
    cluster_bundle = split_discovery_program_scaffold(scaffold)
    program_input = merge_discovery_cluster_packets(cluster_bundle)

    for packet in (scaffold, program_input, cluster_bundle, _valid_program_result()):
        markdown = format_discovery_program_markdown(packet)
        assert markdown.startswith("# ")
        assert len(markdown) > 50
