"""Focused race-boundary tests for the Startup YC evidence bridge script."""

from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "bridge_startup_yc_evidence.py"
SPEC = importlib.util.spec_from_file_location("bridge_startup_yc_evidence", SCRIPT)
assert SPEC and SPEC.loader
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)


def test_missing_rotated_run_ledger_is_a_documented_skip(tmp_path: Path) -> None:
    assert bridge.bridge_score_history(tmp_path) == 0
    assert bridge.bridge_benchmark_grounded(tmp_path) == 0


def test_missing_rotated_research_directory_is_a_documented_skip(tmp_path: Path) -> None:
    assert bridge.bridge_research_grounded(tmp_path) == 0
