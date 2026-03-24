"""Tests for MiroFish frontier readout and export helpers."""

from chip_labs.mirofish.hybrid import (
    build_frontier_viz_packet,
    build_frontier_simulation_tranche,
    build_frontier_readout,
    build_frontier_shortlist,
    format_frontier_readout_markdown,
    format_frontier_shortlist_markdown,
    render_frontier_viz_html,
)


def test_build_frontier_readout_ranks_and_filters() -> None:
    run_packet = {
        "created_at": "2026-03-24T00:00:00+00:00",
        "evidence_lane": "exploratory_frontier",
        "harness": {
            "max_rounds": 12,
            "ensemble_runs": 6,
            "ensemble_count_per_type": 3,
            "flagship_count_per_type": 6,
        },
        "top_line": {
            "top_final_adoption_domain": "alpha",
            "top_final_adoption": 0.03,
        },
        "governance_note": "exploratory_frontier",
        "discovered_domain_ids": ["alpha", "beta", "gamma"],
        "benchmark_domain_ids": ["bench-1", "bench-2"],
        "domain_predictions": [
            {
                "domain_id": "alpha",
                "adoption_probability": 0.03,
                "peak_interest_probability": 0.70,
                "agent_choice_signal": 0.16,
                "consensus_score": 0.50,
            },
            {
                "domain_id": "beta",
                "adoption_probability": 0.01,
                "peak_interest_probability": 0.72,
                "agent_choice_signal": 0.11,
                "consensus_score": 0.40,
            },
            {
                "domain_id": "gamma",
                "adoption_probability": 0.00,
                "peak_interest_probability": 0.40,
                "agent_choice_signal": 0.02,
                "consensus_score": 0.20,
            },
            {
                "domain_id": "bench-1",
                "adoption_probability": 0.02,
                "peak_interest_probability": 0.50,
                "agent_choice_signal": 0.05,
                "consensus_score": 0.30,
            },
            {
                "domain_id": "bench-2",
                "adoption_probability": 0.01,
                "peak_interest_probability": 0.45,
                "agent_choice_signal": 0.04,
                "consensus_score": 0.25,
            },
        ],
        "builder_ensemble_summary": [
            {
                "domain_id": "alpha",
                "mean_adoption": 0.05,
                "mean_trial": 0.06,
                "mean_churn": 0.0,
                "confidence_width": 0.03,
            },
            {
                "domain_id": "beta",
                "mean_adoption": 0.02,
                "mean_trial": 0.04,
                "mean_churn": 0.0,
                "confidence_width": 0.02,
            },
            {
                "domain_id": "gamma",
                "mean_adoption": 0.0,
                "mean_trial": 0.01,
                "mean_churn": 0.0,
                "confidence_width": 0.0,
            },
            {
                "domain_id": "bench-1",
                "mean_adoption": 0.03,
                "mean_trial": 0.04,
                "mean_churn": 0.0,
                "confidence_width": 0.01,
            },
            {
                "domain_id": "bench-2",
                "mean_adoption": 0.01,
                "mean_trial": 0.02,
                "mean_churn": 0.0,
                "confidence_width": 0.01,
            },
        ],
    }

    readout = build_frontier_readout(run_packet, top_n=2, watchlist_n=2, benchmark_n=2)

    assert readout["top_domains_overall"][0]["domain_id"] == "alpha"
    assert readout["top_choice_domains"][0]["domain_id"] == "alpha"
    assert readout["above_benchmark_domains"][0]["domain_id"] == "alpha"
    assert readout["watchlist_domains"][1]["domain_id"] == "beta"
    assert readout["meta"]["benchmark_median_adoption"] == 0.02


def test_format_frontier_readout_markdown_includes_sections() -> None:
    readout = {
        "created_at": "2026-03-24T00:00:00+00:00",
        "source_run_created_at": "2026-03-24T00:00:00+00:00",
        "meta": {
            "domain_count": 90,
            "rounds": 12,
            "ensemble_runs": 6,
            "benchmark_median_adoption": 0.0252,
        },
        "top_line": {
            "top_final_adoption_domain": "defi_yield_rotation_loop",
            "top_final_adoption": 0.0333,
        },
        "top_domains_overall": [
            {
                "domain_id": "chip_ai_agent_07",
                "mean_adoption": 0.0518,
                "agent_choice_signal": 0.10,
                "peak_interest_probability": 0.73,
                "adoption_probability": 0.0333,
                "benchmark_gap": 0.0266,
                "diagnostic_tags": ["strong_candidate"],
            }
        ],
        "top_choice_domains": [
            {
                "domain_id": "defi_yield_rotation_loop",
                "mean_adoption": 0.0333,
                "agent_choice_signal": 0.1666,
                "peak_interest_probability": 0.70,
                "adoption_probability": 0.0333,
                "benchmark_gap": 0.0081,
                "diagnostic_tags": [],
            }
        ],
        "watchlist_domains": [
            {
                "domain_id": "chip_ai_agent_07",
                "mean_adoption": 0.0518,
                "agent_choice_signal": 0.10,
                "peak_interest_probability": 0.73,
                "adoption_probability": 0.0333,
                "benchmark_gap": 0.0266,
                "diagnostic_tags": ["strong_candidate"],
            }
        ],
        "above_benchmark_domains": [
            {
                "domain_id": "chip_ai_agent_07",
                "mean_adoption": 0.0518,
                "agent_choice_signal": 0.10,
                "peak_interest_probability": 0.73,
                "adoption_probability": 0.0333,
                "benchmark_gap": 0.0266,
                "diagnostic_tags": ["strong_candidate"],
            }
        ],
        "methodology_cautions": [
            "High-interest frontier domains still lose too much between interest and actual agent choice.",
        ],
        "governance_note": "exploratory_frontier",
    }

    markdown = format_frontier_readout_markdown(readout, title="Frontier Deeper Export")

    assert "# Frontier Deeper Export" in markdown
    assert "## Methodology Cautions" in markdown
    assert "## Above Benchmark" in markdown
    assert "`chip_ai_agent_07`" in markdown
    assert "*exploratory_frontier*" in markdown


def test_build_frontier_simulation_tranche_keeps_anchors_and_diversifies() -> None:
    result_packet = {
        "created_at": "2026-03-24T00:00:00+00:00",
        "program_id": "frontier-1000",
        "stage_label": "frontier_1000",
        "evidence_lane": "exploratory_frontier",
        "accepted_candidates": [
            {"domain_id": "alpha", "domain_tags": ["creator"]},
            {"domain_id": "beta", "domain_tags": ["gaming"]},
            {"domain_id": "gamma", "domain_tags": ["crypto"]},
            {"domain_id": "delta", "domain_tags": ["creator"]},
            {"domain_id": "epsilon", "domain_tags": ["gaming"]},
            {"domain_id": "zeta", "domain_tags": ["career"]},
        ],
    }
    anchor_readout = {
        "above_benchmark_domains": [{"domain_id": "beta"}],
        "top_domains_overall": [{"domain_id": "alpha"}],
        "top_choice_domains": [{"domain_id": "gamma"}],
        "watchlist_domains": [{"domain_id": "alpha"}],
    }

    tranche = build_frontier_simulation_tranche(
        result_packet,
        target_count=5,
        anchor_readout=anchor_readout,
    )

    selected_ids = [row["domain_id"] for row in tranche["accepted_candidates"]]
    assert selected_ids[:3] == ["beta", "alpha", "gamma"]
    assert len(selected_ids) == 5
    assert tranche["selection_policy"]["anchor_count_retained"] == 3
    assert set(tranche["selection_policy"]["represented_primary_tags"]) >= {"creator", "gaming", "crypto"}


def test_build_frontier_shortlist_splits_winners_breakouts_and_speculative() -> None:
    readout = {
        "created_at": "2026-03-25T00:00:00+00:00",
        "evidence_lane": "exploratory_frontier",
        "meta": {
            "domain_count": 180,
            "benchmark_median_adoption": 0.0163,
        },
        "top_line": {
            "top_ensemble_domain": "alpha",
            "top_ensemble_mean_adoption": 0.05,
            "top_final_adoption_domain": "beta",
            "top_final_adoption": 0.06,
            "top_choice_signal_domain": "gamma",
            "top_choice_signal": 0.2,
        },
        "top_domains_overall": [
            {
                "domain_id": "alpha",
                "mean_adoption": 0.05,
                "agent_choice_signal": 0.10,
                "peak_interest_probability": 0.80,
                "diagnostic_tags": [],
            },
            {
                "domain_id": "beta",
                "mean_adoption": 0.03,
                "agent_choice_signal": 0.08,
                "peak_interest_probability": 0.70,
                "diagnostic_tags": ["trial_to_retention_collapse"],
            },
            {
                "domain_id": "gamma",
                "mean_adoption": 0.01,
                "agent_choice_signal": 0.20,
                "peak_interest_probability": 0.75,
                "diagnostic_tags": ["strong_candidate"],
            },
            {
                "domain_id": "delta",
                "mean_adoption": 0.015,
                "agent_choice_signal": 0.09,
                "peak_interest_probability": 0.65,
                "diagnostic_tags": [],
            },
        ],
        "top_choice_domains": [
            {
                "domain_id": "gamma",
                "mean_adoption": 0.01,
                "agent_choice_signal": 0.20,
                "peak_interest_probability": 0.75,
                "diagnostic_tags": ["strong_candidate"],
            }
        ],
        "watchlist_domains": [
            {
                "domain_id": "delta",
                "mean_adoption": 0.015,
                "agent_choice_signal": 0.09,
                "peak_interest_probability": 0.65,
                "diagnostic_tags": [],
            }
        ],
        "above_benchmark_domains": [
            {
                "domain_id": "alpha",
                "mean_adoption": 0.05,
                "agent_choice_signal": 0.10,
                "peak_interest_probability": 0.80,
                "diagnostic_tags": [],
            },
            {
                "domain_id": "beta",
                "mean_adoption": 0.03,
                "agent_choice_signal": 0.08,
                "peak_interest_probability": 0.70,
                "diagnostic_tags": ["trial_to_retention_collapse"],
            },
        ],
    }

    shortlist = build_frontier_shortlist(readout, winner_n=2, breakout_n=2, speculative_n=2)

    assert shortlist["winner_domains"][0]["domain_id"] == "alpha"
    assert shortlist["winner_domains"][0]["shortlist_stage"] == "winner"
    assert shortlist["breakout_domains"][0]["domain_id"] == "gamma"
    assert shortlist["breakout_domains"][0]["shortlist_stage"] == "breakout"
    assert shortlist["speculative_domains"][0]["domain_id"] == "delta"
    assert shortlist["meta"]["winner_count"] == 2


def test_format_frontier_shortlist_markdown_includes_sections() -> None:
    shortlist = {
        "created_at": "2026-03-25T00:00:00+00:00",
        "source_readout_created_at": "2026-03-25T00:00:00+00:00",
        "meta": {
            "domain_count": 180,
            "benchmark_median_adoption": 0.0163,
        },
        "top_line": {
            "top_ensemble_domain": "chip_ai_agent_07",
            "top_ensemble_mean_adoption": 0.0533,
            "top_final_adoption_domain": "governance-vote-brief-loop",
            "top_final_adoption": 0.0667,
            "top_choice_signal_domain": "governance-vote-brief-loop",
            "top_choice_signal": 0.2,
        },
        "winner_domains": [
            {
                "domain_id": "chip_ai_agent_07",
                "mean_adoption": 0.0533,
                "agent_choice_signal": 0.10,
                "peak_interest_probability": 0.83,
                "shortlist_reason": "Clears the current benchmark median on retained ensemble adoption.",
            }
        ],
        "breakout_domains": [
            {
                "domain_id": "governance-vote-brief-loop",
                "mean_adoption": 0.0385,
                "agent_choice_signal": 0.20,
                "peak_interest_probability": 0.76,
                "shortlist_reason": "Choice signal is strong enough to justify closer review even with retained-adoption friction.",
            }
        ],
        "speculative_domains": [
            {
                "domain_id": "pricing-review-copilot",
                "mean_adoption": 0.0311,
                "agent_choice_signal": 0.0667,
                "peak_interest_probability": 0.73,
                "shortlist_reason": "Still interesting enough for monitoring, but weaker than the current winner and breakout set.",
            }
        ],
        "governance_note": "exploratory_frontier",
    }

    markdown = format_frontier_shortlist_markdown(shortlist, title="Frontier Shortlist")

    assert "# Frontier Shortlist" in markdown
    assert "## Winners" in markdown
    assert "## Breakouts" in markdown
    assert "## Speculative" in markdown
    assert "`chip_ai_agent_07`" in markdown
    assert "*exploratory_frontier*" in markdown


def test_build_frontier_viz_packet_builds_legacy_graph_shape() -> None:
    result_packet = {
        "created_at": "2026-03-25T00:00:00+00:00",
        "program_id": "frontier-1000",
        "stage_label": "frontier_1000",
        "evidence_lane": "exploratory_frontier",
        "accepted_candidates": [
            {
                "domain_id": "alpha",
                "label": "Alpha",
                "description": "Creator alpha loop.",
                "domain_tags": ["creator-growth-systems"],
                "adjacent_domains": ["beta"],
                "evidence_sources": ["x_twitter"],
                "promotion_status": "candidate",
                "specialization_surface": "creator hooks",
                "mastery_surface": "packaging",
                "user_value_loop": "publish and learn",
            },
            {
                "domain_id": "beta",
                "label": "Beta",
                "description": "Crypto beta loop.",
                "domain_tags": ["crypto-defi-trading"],
                "adjacent_domains": ["alpha"],
                "evidence_sources": ["community"],
                "promotion_status": "candidate",
                "specialization_surface": "onchain signals",
                "mastery_surface": "rotation timing",
                "user_value_loop": "track and rotate",
            },
        ],
    }
    anchor_readout = {
        "top_domains_overall": [{"domain_id": "alpha"}],
        "top_choice_domains": [{"domain_id": "beta"}],
        "watchlist_domains": [],
        "above_benchmark_domains": [],
    }
    run_packet = {
        "domain_predictions": [
            {
                "domain_id": "alpha",
                "adoption_probability": 0.04,
                "peak_interest_probability": 0.75,
                "agent_choice_signal": 0.12,
                "consensus_score": 0.61,
            }
        ],
        "builder_ensemble_summary": [
            {
                "domain_id": "alpha",
                "mean_adoption": 0.05,
                "mean_trial": 0.07,
                "mean_churn": 0.01,
                "confidence_width": 0.02,
            }
        ],
    }

    packet = build_frontier_viz_packet(
        result_packet,
        target_count=2,
        anchor_readout=anchor_readout,
        run_packet=run_packet,
        rounds=12,
    )

    assert packet["meta"]["domain_count"] == 2
    assert "graph_nodes" in packet
    assert "graph_edges" in packet
    assert "domains" in packet
    assert "persona_types" in packet
    assert "shocks" in packet
    assert packet["domains"][0]["domain_id"] == "alpha"
    assert packet["domains"][0]["builder_curve"][0]["round"] == 0
    assert "adoption_by_persona_type" in packet["domains"][0]


def test_render_frontier_viz_html_rewrites_template_fetch_and_title() -> None:
    template = (
        "<html><head><title>MiroFish v4 - 500 Domain Knowledge Graph</title></head>"
        "<body><script>fetch('mirofish_500_data.json')</script></body></html>"
    )

    html = render_frontier_viz_html(
        data_filename="MIROFISH_FRONTIER_VIZ_500_2026-03-25.json",
        title="MiroFish Frontier 500 Graph",
        template_html=template,
    )

    assert "<title>MiroFish Frontier 500 Graph</title>" in html
    assert "fetch('MIROFISH_FRONTIER_VIZ_500_2026-03-25.json')" in html
