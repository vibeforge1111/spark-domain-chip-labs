"""Deterministic ordering checks for tied trend opportunities."""

from chip_labs.trend_scanner import rank_opportunities


def test_tied_opportunities_are_ordered_by_domain_id() -> None:
    common = {
        "market_growth": 0.5,
        "research_gap": 0.5,
        "benchmark_availability": 0.5,
        "transfer_potential": 0.5,
    }
    ranked = rank_opportunities([
        {"domain_id": "zeta", **common},
        {"domain_id": "alpha", **common},
    ])
    assert [item["domain_id"] for item in ranked] == ["alpha", "zeta"]
