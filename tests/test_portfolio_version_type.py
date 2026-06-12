"""Regression tests for non-string manifest versions in portfolio summary.

A JSON manifest with an unquoted numeric version (e.g. ``{"version": 0.3}`` --
a common authoring slip) must not crash ``get_portfolio_summary``: a single
malformed co-located chip should not take down the whole portfolio evaluation.
"""

from __future__ import annotations

import json
from pathlib import Path

from chip_labs.registry import get_portfolio_summary


def _write_chip(search_dir: Path, name: str, version: object) -> None:
    chip_dir = search_dir / name
    chip_dir.mkdir(parents=True)
    (chip_dir / "spark-chip.json").write_text(
        json.dumps({"version": version, "domain": "test"}),
        encoding="utf-8",
    )


def test_numeric_version_does_not_crash_portfolio_summary(tmp_path: Path) -> None:
    # An unquoted numeric version is a truthy float; without coercion it would
    # crash on ``version.startswith`` and abort the entire portfolio scan.
    _write_chip(tmp_path, "domain-chip-numeric", 0.3)

    summary = get_portfolio_summary(tmp_path)

    assert summary["total_chips"] == 1
    # str(0.3) == "0.3" -> detection intent preserved, classified as production.
    assert summary["maturity_distribution"]["production"] == 1


def test_string_version_still_classifies_correctly(tmp_path: Path) -> None:
    _write_chip(tmp_path, "domain-chip-alpha", "0.1.0")
    _write_chip(tmp_path, "domain-chip-beta", "0.2.5")
    _write_chip(tmp_path, "domain-chip-prod", "0.3.1")

    summary = get_portfolio_summary(tmp_path)

    assert summary["total_chips"] == 3
    assert summary["maturity_distribution"]["alpha"] == 1
    assert summary["maturity_distribution"]["beta"] == 1
    assert summary["maturity_distribution"]["production"] == 1
