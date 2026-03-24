"""Tests for the repo-local 515-domain MiroFish wrapper."""

from chip_labs.mirofish.portfolio import (
    build_portfolio_readout,
    format_portfolio_readout_markdown,
    load_full_domain_universe,
)


def test_load_full_domain_universe_has_expected_counts() -> None:
    universe = load_full_domain_universe()
    assert len(universe["all_domains"]) == 515
    assert len(universe["v3_domains"]) == 250
    assert len(universe["v4_domains"]) == 265


def test_load_full_domain_universe_has_unique_ids() -> None:
    universe = load_full_domain_universe()
    domain_ids = [item["domain_id"] for item in universe["all_domains"]]
    assert len(domain_ids) == len(set(domain_ids))


def test_build_portfolio_readout_filters_sections() -> None:
    run_packet = {
        "created_at": "2026-03-24T00:00:00+00:00",
        "meta": {"domain_count": 515},
        "governance_note": "exploratory_frontier",
        "ranked_domains": [
            {
                "domain_id": "startup-yc",
                "label": "Startup YC",
                "generation": "v3",
                "domain_tags": ["roi"],
                "ensemble_mean_adoption": 0.04,
                "agent_choice_signal": 0.14,
                "final_adoption_rate": 0.02,
                "diagnostic_tags": [],
            },
            {
                "domain_id": "ai-security-questionnaire-copilot",
                "label": "Questionnaire",
                "generation": "v4",
                "domain_tags": ["compliance", "enterprise-sales"],
                "ensemble_mean_adoption": 0.02,
                "agent_choice_signal": 0.13,
                "final_adoption_rate": 0.01,
                "diagnostic_tags": ["interest_to_choice_friction"],
            },
        ],
    }
    readout = build_portfolio_readout(run_packet, top_n=2, enterprise_n=2, newly_discovered_n=2)
    assert len(readout["top_domains_overall"]) == 2
    assert readout["top_enterprise_domains"][0]["domain_id"] == "ai-security-questionnaire-copilot"
    assert readout["top_newly_discovered_domains"][0]["domain_id"] == "ai-security-questionnaire-copilot"


def test_format_portfolio_readout_markdown_includes_sections() -> None:
    readout = {
        "created_at": "2026-03-24T00:00:00+00:00",
        "source_run_created_at": "2026-03-24T00:00:00+00:00",
        "meta": {
            "domain_count": 515,
            "rounds": 6,
            "ensemble_runs": 4,
            "bootstrap_resamples": 10,
        },
        "top_domains_overall": [
            {
                "domain_id": "defi-architect",
                "ensemble_mean_adoption": 0.0083,
                "agent_choice_signal": 0.0167,
                "peak_interest_probability": 0.7667,
                "final_adoption_rate": 0.0,
                "diagnostic_tags": ["interest_to_choice_friction"],
            }
        ],
        "top_enterprise_domains": [
            {
                "domain_id": "chronic-disease-mgr",
                "ensemble_mean_adoption": 0.0,
                "agent_choice_signal": 0.0333,
                "peak_interest_probability": 0.45,
                "final_adoption_rate": 0.0,
                "diagnostic_tags": [],
            }
        ],
        "top_newly_discovered_domains": [
            {
                "domain_id": "last-mile-delivery-ai",
                "ensemble_mean_adoption": 0.0083,
                "agent_choice_signal": 0.0,
                "peak_interest_probability": 0.55,
                "final_adoption_rate": 0.0,
                "diagnostic_tags": ["interest_to_choice_friction"],
            }
        ],
        "methodology_cautions": [
            "Top ensemble adoption remains modest, so rank order is more trustworthy than absolute demand magnitude.",
        ],
        "governance_note": "exploratory_frontier",
    }

    markdown = format_portfolio_readout_markdown(readout, title="Medium Checkpoint Export")

    assert "# Medium Checkpoint Export" in markdown
    assert "## Methodology Cautions" in markdown
    assert "`defi-architect`" in markdown
    assert "## Top Enterprise" in markdown
    assert "*exploratory_frontier*" in markdown
