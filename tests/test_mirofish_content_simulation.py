from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from chip_labs.mirofish.content_simulation import (
    CLAIM_BOUNDARY,
    format_content_simulation_markdown,
    simulate_content_selection,
)


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
    assert result["claim_boundary"] == CLAIM_BOUNDARY
    assert result["row_count"] == 36
    assert result["top_candidate_id"] in {"specific", "operator"}
    assert result["rankings"][0]["median_composite"] > result["rankings"][-1]["median_composite"]
    assert result["rankings"][0]["weakest_persona"] in result["persona_segments"]


def test_simulate_content_selection_blocks_without_candidates() -> None:
    result = simulate_content_selection({"candidates": []})

    assert result["verdict"] == "blocked"
    assert "candidates_required" in result["blocking_checks"]


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
