from __future__ import annotations

import json
import re
from pathlib import Path

from chip_labs.creator_run import validate_creator_run


def test_startup_yc_creator_run_fixture_is_swarm_ready() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    fixture_dir = repo_root / "docs" / "creator_system" / "examples" / "startup-yc-creator-run"

    result = validate_creator_run(fixture_dir)

    assert result.verdict == "ready_for_swarm_packet"
    assert result.evidence_tier == "transfer_supported"
    assert result.missing_paths == ()


def test_startup_yc_transfer_summary_pins_external_source_hashes() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    fixture_dir = repo_root / "docs" / "creator_system" / "examples" / "startup-yc-creator-run"
    transfer = json.loads(
        (fixture_dir / "reports" / "transfer_summary.json").read_text(
            encoding="utf-8"
        )
    )

    source_artifacts = set(transfer["source_artifacts"].values())
    source_hashes = transfer["source_artifact_hashes"]

    assert source_artifacts == set(source_hashes)
    assert all(
        re.fullmatch(r"[0-9a-f]{64}", digest)
        for digest in source_hashes.values()
    )
