"""Tests for MiroFish frontier readout and export helpers."""

from chip_labs.mirofish.hybrid import (
    build_frontier_readout,
    format_frontier_readout_markdown,
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
