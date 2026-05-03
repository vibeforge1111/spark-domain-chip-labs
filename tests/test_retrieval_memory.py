from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from chip_labs.retrieval_memory import (
    check_retrieval_memory_packet,
    load_retrieval_memory_packet,
)


FIXTURE_DIR = Path("docs/creator_system/examples/retrieval-memory")


def test_retrieval_memory_accepts_correct_prior_decision() -> None:
    result = check_retrieval_memory_packet(
        load_retrieval_memory_packet(FIXTURE_DIR / "correct_prior_decision.json")
    )

    assert result["verdict"] == "pass"
    assert result["calibration_verdict"] == "pass"
    assert result["promotion"]["allowed"] is True
    assert result["promotion"]["network_absorbable"] is False
    assert result["blocking_checks"] == []


def test_saved_correct_prior_decision_check_matches_current_checker() -> None:
    saved = json.loads(
        (FIXTURE_DIR / "correct_prior_decision.check.json").read_text(encoding="utf-8")
    )
    regenerated = check_retrieval_memory_packet(
        load_retrieval_memory_packet(FIXTURE_DIR / "correct_prior_decision.json")
    )

    assert regenerated == saved
    assert saved["promotion"]["allowed"] is True
    assert saved["promotion"]["network_absorbable"] is False
    assert saved["calibration_verdict"] == "pass"


def test_retrieval_memory_blocks_antipattern_fixtures() -> None:
    expected_blockers = {
        "stale_memory.json": {"entry:0:freshness"},
        "contradicted_memory.json": {"entry:0:contradiction"},
        "residue_contamination.json": {"entry:0:residue_boundary"},
        "network_without_review.json": {"entry:0:network_review"},
    }

    for fixture_name, blockers in expected_blockers.items():
        result = check_retrieval_memory_packet(
            load_retrieval_memory_packet(FIXTURE_DIR / fixture_name)
        )

        assert result["verdict"] == "blocked"
        assert result["calibration_verdict"] == "blocked"
        assert blockers.issubset(set(result["blocking_checks"]))
        assert result["promotion"]["allowed"] is False


def test_retrieval_memory_blocks_provenance_not_in_source_refs() -> None:
    packet = load_retrieval_memory_packet(FIXTURE_DIR / "correct_prior_decision.json")
    packet["entries"][0]["provenance"]["source_path"] = "docs/creator_system/README.md"

    result = check_retrieval_memory_packet(packet)

    assert result["verdict"] == "blocked"
    assert "entry:0:provenance_source_ref" in result["blocking_checks"]


def test_cli_retrieval_memory_check_blocks_bad_fixture() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "chip_labs.cli",
            "retrieval-memory-check",
            "--input",
            str(FIXTURE_DIR / "residue_contamination.json"),
            "--fail-on-blocked",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "entry:0:residue_boundary" in result.stdout
