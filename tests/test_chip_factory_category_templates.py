"""Tests for chip_factory.category_templates accelerator helpers.

category_templates.py provides the per-domain mutation axes / evidence
lanes / promotion gates that scaffold.py uses to generate domain-specific
chips faster than generic scaffolding alone. The lookup, fallback, and
detection helpers are pure functions, but ship without direct tests; a
silent shape change to CATEGORY_TEMPLATES or a renamed keyword in
detect_category would degrade chip generation without any CI signal.
"""

from __future__ import annotations

from chip_labs.chip_factory import category_templates as ct


def test_get_template_returns_none_for_unknown_category() -> None:
    assert ct.get_template("not-a-real-category") is None


def test_get_template_returns_full_template_for_known_category() -> None:
    finance = ct.get_template("finance")
    assert finance is not None
    # Every template must expose at least these shape keys for downstream
    # consumers (scaffold.py + apply_template).
    for key in (
        "label",
        "description",
        "default_mutation_axes",
        "default_evidence_lanes",
        "default_primary_metric",
        "promotion_gates",
        "watchtower_pages",
        "example_domains",
    ):
        assert key in finance, f"finance template missing {key}"


def test_list_categories_projects_stable_summary_shape() -> None:
    summary = ct.list_categories()
    assert summary, "should list at least one category"
    template_ids = set(ct.CATEGORY_TEMPLATES.keys())
    summary_ids = {entry["id"] for entry in summary}
    assert summary_ids == template_ids
    for entry in summary:
        for key in ("id", "label", "description", "example_domains"):
            assert key in entry, f"summary entry missing {key}"


def test_apply_template_unknown_category_returns_brief_unchanged() -> None:
    brief = {"category": "not-a-real-category", "mutation_axes": [{"name": "x", "values": ["a"]}]}
    out = ct.apply_template(brief)
    assert out == brief


def test_apply_template_preserves_explicit_brief_values() -> None:
    brief = {
        "category": "finance",
        "mutation_axes": [{"name": "custom_axis", "values": ["a", "b"]}],
        "primary_metric": "custom_metric",
        "evidence_lanes": ["custom_lane"],
    }
    out = ct.apply_template(brief)
    # Caller-supplied values must NOT be overwritten by template defaults.
    assert out["mutation_axes"] == brief["mutation_axes"]
    assert out["primary_metric"] == "custom_metric"
    assert out["evidence_lanes"] == ["custom_lane"]
    # Template metadata still applied for downstream reference.
    assert out["_template_applied"] == "finance"


def test_apply_template_fills_defaults_when_brief_omits_values() -> None:
    out = ct.apply_template({"category": "finance"})
    assert out["primary_metric"] == "risk_adjusted_return"
    assert out["_template_applied"] == "finance"
    assert out["_scoring_template"] == "additive_with_regime_gates"
    # Brief did not provide mutation_axes — template defaults filled in.
    assert out["mutation_axes"] == ct.CATEGORY_TEMPLATES["finance"]["default_mutation_axes"]


def test_detect_category_falls_back_to_technology_on_no_matches() -> None:
    out = ct.detect_category({"domain_id": "", "domain_name": "", "description": ""})
    assert out == "technology"


def test_detect_category_picks_finance_for_trading_brief() -> None:
    out = ct.detect_category({
        "domain_id": "trading-crypto",
        "domain_name": "Crypto Trading",
        "description": "Quant momentum backtest portfolio strategies",
    })
    assert out == "finance"


def test_detect_category_picks_creative_for_design_brief() -> None:
    out = ct.detect_category({
        "domain_id": "web-designer",
        "domain_name": "Web Design",
        "description": "UX visual aesthetic typography brand identity",
    })
    assert out == "creative"
