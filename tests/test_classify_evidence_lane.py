import pytest
from unittest.mock import MagicMock


def _make_engine(default_lane: str):
    from chip_labs.transfer_surface.scoring_engine import ScoringEngine
    cfg = MagicMock()
    cfg.default_evidence_lane = default_lane
    engine = object.__new__(ScoringEngine)
    engine._config = cfg
    return engine


def test_default_lane_used_on_empty_mutations():
    engine = _make_engine("exploratory_frontier")
    result = engine._classify_evidence_lane({"mutations": {}})
    assert result == "exploratory_frontier"


def test_default_lane_used_on_unknown_mutations():
    engine = _make_engine("exploratory_frontier")
    result = engine._classify_evidence_lane({"mutations": {"unknown_key": 1}})
    assert result == "exploratory_frontier"


def test_custom_default_lane_respected():
    engine = _make_engine("benchmark_grounded")
    result = engine._classify_evidence_lane({"mutations": {}})
    assert result == "benchmark_grounded"


def test_not_hardcoded_to_exploratory_frontier():
    engine = _make_engine("my_custom_lane")
    result = engine._classify_evidence_lane({"mutations": {}})
    assert result == "my_custom_lane"
    assert result != "exploratory_frontier"


def test_config_default_lane_is_authoritative():
    for lane in ("benchmark_grounded", "exploratory_frontier", "custom"):
        engine = _make_engine(lane)
        result = engine._classify_evidence_lane({"mutations": {}})
        assert result == lane