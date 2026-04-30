from __future__ import annotations

from pathlib import Path

from chip_labs.creator_run import validate_creator_run


def test_startup_yc_creator_run_fixture_is_swarm_ready() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    fixture_dir = repo_root / "docs" / "creator_system" / "examples" / "startup-yc-creator-run"

    result = validate_creator_run(fixture_dir)

    assert result.verdict == "ready_for_swarm_packet"
    assert result.evidence_tier == "candidate_review"
    assert result.missing_paths == ()

