from __future__ import annotations

import pytest

from chip_labs.mirofish.curated_frontier import build_curated_frontier_packet


def test_curated_frontier_unknown_profile_lists_supported_profile() -> None:
    with pytest.raises(ValueError) as error:
        build_curated_frontier_packet(profile="hotnow")

    message = str(error.value)
    assert "Unsupported curated frontier profile: 'hotnow'" in message
    assert "Supported profiles: hot_now." in message


def test_curated_frontier_default_profile_still_builds_packet() -> None:
    packet = build_curated_frontier_packet(target_count=5)

    assert packet["packet_kind"] == "mirofish_curated_frontier_packet"
    assert packet["summary"]["accepted_count"] == 5


def test_curated_frontier_explicit_supported_profile_still_builds_packet() -> None:
    packet = build_curated_frontier_packet(target_count=5, profile="hot_now")

    assert packet["packet_kind"] == "mirofish_curated_frontier_packet"
    assert packet["summary"]["accepted_count"] == 5
