"""Tests for mirofish.curated_frontier round-robin selector + markdown.

The existing test_curated_frontier_profile_listing.py covers only the
profile error message + the default packet build. The _round_robin_select
distribution contract (cross-cluster interleaving), the target-count
clamps (zero / negative / above-source), and the markdown formatter
are unpinned.
"""

from __future__ import annotations

from chip_labs.mirofish.curated_frontier import (
    _round_robin_select,
    build_curated_frontier_packet,
    format_curated_frontier_markdown,
)


# ----- _round_robin_select -----


def test_round_robin_select_interleaves_clusters_until_exhausted() -> None:
    clusters = [
        [{"id": "a1"}, {"id": "a2"}, {"id": "a3"}],
        [{"id": "b1"}, {"id": "b2"}],
        [{"id": "c1"}, {"id": "c2"}, {"id": "c3"}, {"id": "c4"}],
    ]
    out = _round_robin_select(clusters, 100)
    # First round picks one from each cluster in order.
    assert [c["id"] for c in out[:3]] == ["a1", "b1", "c1"]
    # Second round again interleaves; b only has 2 items.
    assert [c["id"] for c in out[3:6]] == ["a2", "b2", "c2"]


def test_round_robin_select_stops_at_target_count() -> None:
    clusters = [
        [{"id": "a1"}, {"id": "a2"}],
        [{"id": "b1"}, {"id": "b2"}],
    ]
    out = _round_robin_select(clusters, 3)
    assert len(out) == 3
    assert [c["id"] for c in out] == ["a1", "b1", "a2"]


def test_round_robin_select_returns_empty_for_zero_or_empty_input() -> None:
    assert _round_robin_select([{"id": "a"}], 0) == []
    assert _round_robin_select([], 5) == []


def test_round_robin_select_does_not_mutate_input_lists() -> None:
    original = [[{"id": "a1"}, {"id": "a2"}]]
    snapshot = [list(items) for items in original]
    _round_robin_select(original, 2)
    # Original outer + inner lists must be untouched.
    assert original == snapshot


# ----- build_curated_frontier_packet target_count clamping -----


def test_build_curated_frontier_packet_clamps_negative_target_to_zero() -> None:
    packet = build_curated_frontier_packet(target_count=-3)
    assert packet["summary"]["accepted_count"] == 0
    assert packet["target_domain_count"] == 0


def test_build_curated_frontier_packet_clamps_target_to_full_source_count() -> None:
    packet = build_curated_frontier_packet(target_count=10_000)
    # The full source has a fixed number of curated ideas; target above
    # that should clamp.
    full = packet["summary"]["unique_idea_count"]
    assert packet["summary"]["accepted_count"] == full
    assert packet["target_domain_count"] == full


def test_build_curated_frontier_packet_exposes_zero_banned_suffixes() -> None:
    packet = build_curated_frontier_packet(target_count=5)
    # The curated source explicitly avoids the banned templated suffixes.
    assert packet["summary"]["banned_suffix_family_count"] == 0


# ----- format_curated_frontier_markdown -----


def test_format_curated_frontier_markdown_uses_title_argument() -> None:
    packet = build_curated_frontier_packet(target_count=5)
    md = format_curated_frontier_markdown(packet, title="My Custom Title")
    assert md.startswith("# My Custom Title")


def test_format_curated_frontier_markdown_contains_cluster_summary_lines() -> None:
    packet = build_curated_frontier_packet(target_count=5)
    md = format_curated_frontier_markdown(packet)
    # Every cluster summary should appear as a backtick-quoted bullet line.
    for cluster in packet["cluster_summary"]:
        assert f"`{cluster['cluster_id']}`" in md


def test_format_curated_frontier_markdown_handles_empty_packet_gracefully() -> None:
    md = format_curated_frontier_markdown({})
    # No crash, includes the next-actions footer.
    assert md.startswith("#")
    assert "Next Actions" in md
