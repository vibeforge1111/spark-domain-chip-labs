from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from chip_labs.mirofish.content_simulation import (
    CLAIM_BOUNDARY,
    build_content_simulation_packet,
    extract_content_candidates,
    format_content_simulation_markdown,
    route_content_simulation_request,
    should_invoke_content_simulation,
    simulate_content_multi_seed,
    simulate_content_selection,
)


EXAMPLE_DIR = Path("docs/creator_system/examples/mirofish-content")


def _packet() -> dict[str, object]:
    return {
        "candidates": [
            {
                "id": "specific",
                "text": "7 benchmark mistakes that make AI agent demos look better than they are",
            },
            {
                "id": "generic",
                "text": "The ultimate secret to amazing AI content",
            },
            {
                "id": "operator",
                "text": "How to prove an agent workflow actually improved before you ship it",
            },
        ],
        "persona_segments": [
            "founder-builders",
            "technical-operators",
            "creator-economy-readers",
            "skeptical-experts",
        ],
        "rlm_judges": [
            "spark-local-judge",
            "frontier-reasoning-judge",
            "fast-taste-judge",
        ],
    }


def test_simulate_content_selection_ranks_candidates_with_rows() -> None:
    result = simulate_content_selection(_packet())

    assert result["packet_kind"] == "mirofish_content_simulation_result"
    assert result["verdict"] == "ranked"
    assert result["calibration_verdict"] == "pass"
    assert result["blocking_checks"] == []
    assert result["claim_boundary"] == CLAIM_BOUNDARY
    assert result["row_count"] == 36
    assert result["top_candidate_id"] in {"specific", "operator"}
    assert result["rankings"][0]["median_composite"] > result["rankings"][-1]["median_composite"]
    assert result["rankings"][0]["weakest_persona"] in result["persona_segments"]
    assert {check["check_id"] for check in result["calibration_checks"]} >= {
        "multi_rlm_judge_panel",
        "persona_segment_coverage",
        "row_count_coherence",
        "weak_segment_inspection",
    }


def test_simulate_content_selection_blocks_without_candidates() -> None:
    result = simulate_content_selection({"candidates": []})

    assert result["verdict"] == "blocked"
    assert "candidates_required" in result["blocking_checks"]


def test_simulate_content_selection_marks_single_judge_calibration_blocked() -> None:
    packet = _packet()
    packet["rlm_judges"] = ["spark-local-judge"]

    result = simulate_content_selection(packet)

    assert result["verdict"] == "ranked"
    assert result["calibration_verdict"] == "blocked"
    assert "multi_rlm_judge_panel" in result["blocking_checks"]


def test_simulate_content_selection_blocks_failed_expected_winner() -> None:
    packet = _packet()
    packet["expected_top_candidate_ids"] = ["generic"]

    result = simulate_content_selection(packet)

    assert result["calibration_verdict"] == "blocked"
    assert "expected_top_candidate" in result["blocking_checks"]


def test_simulate_content_multi_seed_requires_stable_top_candidate() -> None:
    result = simulate_content_multi_seed(_packet(), seeds=[1, 2, 3])

    assert result["packet_kind"] == "mirofish_content_multi_seed_result"
    assert result["verdict"] == "candidate_review"
    assert result["calibration_verdict"] == "pass"
    assert result["seed_count"] == 3
    assert result["network_absorbable"] is False
    assert result["blocking_checks"] == []
    assert result["stable_top_candidate_ids"]
    assert sum(result["top_candidate_counts"].values()) == 3


def test_simulate_content_multi_seed_blocks_single_seed() -> None:
    result = simulate_content_multi_seed(_packet(), seeds=[1])

    assert result["verdict"] == "blocked"
    assert result["calibration_verdict"] == "blocked"
    assert "multi_seed_required" in result["blocking_checks"]


def test_should_invoke_content_simulation_for_title_selection_prompt() -> None:
    prompt = """Which title is strongest?

1. 7 benchmark mistakes that make AI demos look better than they are
2. How to prove an agent workflow improved before you ship it
"""

    assert should_invoke_content_simulation(prompt) is True
    assert extract_content_candidates(prompt) == [
        "7 benchmark mistakes that make AI demos look better than they are",
        "How to prove an agent workflow improved before you ship it",
    ]


def test_should_not_invoke_content_simulation_for_unrelated_task() -> None:
    assert should_invoke_content_simulation("Run the unit tests and summarize failures.") is False


def test_build_content_simulation_packet_from_prompt_candidates() -> None:
    prompt = """Pick the best hook:

- Why most agent demos lie by accident
- The checklist I use before trusting agent benchmarks
"""

    packet = build_content_simulation_packet(prompt)

    assert packet["triggered_by"] == "mirofish_content_simulation"
    assert len(packet["candidates"]) == 2
    assert packet["claim_boundary"] == CLAIM_BOUNDARY


def test_route_content_simulation_request_invokes_for_prompt_candidates() -> None:
    prompt = """Which title is strongest?

1. 7 benchmark mistakes that make AI demos look better than they are
2. How to prove an agent workflow improved before you ship it
"""

    route = route_content_simulation_request(prompt)

    assert route["packet_kind"] == "mirofish_content_route"
    assert route["verdict"] == "invoke"
    assert route["route"] == "mirofish-content-simulate"
    assert route["candidate_count"] == 2
    assert route["claim_boundary"] == CLAIM_BOUNDARY
    assert route["simulation_result"]["verdict"] == "ranked"


def test_route_content_simulation_request_skips_unrelated_prompt() -> None:
    route = route_content_simulation_request("Run the unit tests and summarize failures.")

    assert route["verdict"] == "skip"
    assert route["route"] is None
    assert route["candidate_count"] == 0
    assert "needs at least two content candidates" in route["reason"]
    assert "simulation_result" not in route


def test_route_content_simulation_request_skips_selection_without_candidates() -> None:
    route = route_content_simulation_request("Pick the best title.")

    assert route["verdict"] == "skip"
    assert route["candidate_count"] == 0
    assert "needs at least two content candidates" in route["reason"]


def test_route_content_simulation_request_invokes_for_explicit_candidates() -> None:
    route = route_content_simulation_request(
        "Pick the best option.",
        candidates=[
            "Why most agent demos lie by accident",
            "The ultimate secret to amazing AI content",
        ],
        include_simulation=False,
    )

    assert route["verdict"] == "invoke"
    assert route["candidate_count"] == 2
    assert route["candidate_ids"] == ["candidate-1", "candidate-2"]
    assert "simulation_packet" in route
    assert "simulation_result" not in route


def test_format_content_simulation_markdown_includes_ranking() -> None:
    result = simulate_content_selection(_packet())

    markdown = format_content_simulation_markdown(result)

    assert "# MiroFish Content Simulation" in markdown
    assert "Claim boundary" in markdown
    assert result["top_candidate_id"] in markdown


def test_cli_mirofish_content_simulate_outputs_json_and_markdown(tmp_path: Path) -> None:
    input_path = tmp_path / "content_candidates.json"
    output_path = tmp_path / "result.json"
    markdown_path = tmp_path / "result.md"
    input_path.write_text(json.dumps(_packet()), encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "mirofish-content-simulate",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--markdown-output",
            str(markdown_path),
        ],
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["verdict"] == "ranked"
    assert markdown_path.read_text(encoding="utf-8").startswith(
        "# MiroFish Content Simulation"
    )


def test_cli_mirofish_content_simulate_accepts_direct_candidates(tmp_path: Path) -> None:
    output_path = tmp_path / "result.json"
    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "mirofish-content-simulate",
            "--task",
            "Pick the best post title.",
            "--candidate",
            "7 benchmark mistakes that make AI demos look better than they are",
            "--candidate",
            "The ultimate secret to amazing AI content",
            "--output",
            str(output_path),
        ],
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["verdict"] == "ranked"
    assert payload["candidate_count"] == 2


def test_cli_mirofish_content_multi_seed_outputs_json(tmp_path: Path) -> None:
    output_path = tmp_path / "multi_seed.json"
    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "mirofish-content-multi-seed",
            "--task",
            "Pick the best post title.",
            "--candidate",
            "7 benchmark mistakes that make AI demos look better than they are",
            "--candidate",
            "The ultimate secret to amazing AI content",
            "--candidate",
            "How to prove an agent workflow actually improved before you ship it",
            "--seed",
            "1",
            "--seed",
            "2",
            "--seed",
            "3",
            "--output",
            str(output_path),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["verdict"] == "candidate_review"
    assert payload["seed_count"] == 3
    assert payload["network_absorbable"] is False


def test_cli_mirofish_content_route_outputs_route_packet(tmp_path: Path) -> None:
    output_path = tmp_path / "route.json"
    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "mirofish-content-route",
            "--task",
            "Pick the best title.",
            "--candidate",
            "7 benchmark mistakes that make AI demos look better than they are",
            "--candidate",
            "The ultimate secret to amazing AI content",
            "--no-simulation",
            "--output",
            str(output_path),
        ],
        cwd=Path.cwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["packet_kind"] == "mirofish_content_route"
    assert payload["verdict"] == "invoke"
    assert payload["route"] == "mirofish-content-simulate"
    assert "simulation_result" not in payload


def test_saved_mirofish_content_examples_preserve_claim_boundary() -> None:
    route = json.loads((EXAMPLE_DIR / "route-invoke.json").read_text(encoding="utf-8"))
    simulation = json.loads((EXAMPLE_DIR / "simulation-result.json").read_text(encoding="utf-8"))
    markdown = (EXAMPLE_DIR / "simulation-result.md").read_text(encoding="utf-8")

    assert route["packet_kind"] == "mirofish_content_route"
    assert route["verdict"] == "invoke"
    assert route["claim_boundary"] == CLAIM_BOUNDARY
    assert route["simulation_packet"]["claim_boundary"] == CLAIM_BOUNDARY
    assert simulation["packet_kind"] == "mirofish_content_simulation_result"
    assert simulation["verdict"] == "ranked"
    assert simulation["calibration_verdict"] == "pass"
    assert simulation["blocking_checks"] == []
    assert simulation["claim_boundary"] == CLAIM_BOUNDARY
    assert simulation["row_count"] == (
        simulation["candidate_count"]
        * len(simulation["persona_segments"])
        * len(simulation["rlm_judges"])
    )
    assert any(
        check["check_id"] == "multi_rlm_judge_panel"
        for check in simulation["calibration_checks"]
    )
    assert "candidate_review local simulator protocol only" in markdown
