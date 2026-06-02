"""Regression tests for the curated_frontier profile actionable-error message.

build_curated_frontier_packet rejects any profile that isn't registered.
The error previously named only the bad value; these tests pin the new
message shape (failed value quoted, supported profiles named inline) and
keep the pure-hit path (profile='hot_now') intact.
"""
from __future__ import annotations

import pytest

from chip_labs.mirofish.curated_frontier import build_curated_frontier_packet


def test_unsupported_profile_lists_supported_profiles() -> None:
    with pytest.raises(ValueError) as excinfo:
        build_curated_frontier_packet(target_count=20, profile="bogus_profile")
    message = str(excinfo.value)
    assert "'bogus_profile'" in message
    assert "hot_now" in message


def test_default_profile_pure_hit_path_unchanged() -> None:
    packet = build_curated_frontier_packet(target_count=10)
    assert packet["packet_kind"] == "mirofish_curated_frontier_packet"


def test_explicit_hot_now_profile_pure_hit_path_unchanged() -> None:
    packet = build_curated_frontier_packet(target_count=10, profile="hot_now")
    assert packet["packet_kind"] == "mirofish_curated_frontier_packet"
    assert packet["profile"] == "hot_now"
