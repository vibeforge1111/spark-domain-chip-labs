"""Shared fixtures for domain chip testing.

Discovers real domain chips on Desktop and provides parametrized fixtures
for running tests across the entire portfolio.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Chip discovery
# ---------------------------------------------------------------------------

def _discover_desktop_chips() -> list[Path]:
    """Find all domain-chip-* directories on the Desktop."""
    desktop = Path(os.path.expanduser("~")) / "Desktop"
    if not desktop.exists():
        return []
    chips = sorted(
        p
        for p in desktop.iterdir()
        if p.is_dir()
        and p.name.startswith("domain-chip-")
        and (p / "spark-chip.json").exists()
    )
    return chips


_DESKTOP_CHIPS = _discover_desktop_chips()


# ---------------------------------------------------------------------------
# Markers
# ---------------------------------------------------------------------------

def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "flywheel: marks tests that check flywheel intelligence production",
    )
    config.addinivalue_line(
        "markers",
        "real_chips: marks tests that require real chips on Desktop",
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def desktop_chips() -> list[Path]:
    """All discovered domain chip directories on Desktop."""
    return list(_DESKTOP_CHIPS)


@pytest.fixture(
    scope="session",
    params=_DESKTOP_CHIPS,
    ids=lambda p: p.name,
)
def chip_path(request: pytest.FixtureRequest) -> Path:
    """Parametrized fixture: one test run per discovered chip."""
    return request.param


@pytest.fixture(scope="session")
def startup_yc_path() -> Path:
    """Direct access to the startup-yc chip (flagship)."""
    for chip in _DESKTOP_CHIPS:
        if chip.name == "domain-chip-startup-yc":
            return chip
    pytest.skip("domain-chip-startup-yc not found on Desktop")


def _skip_if_no_chips() -> None:
    """Skip helper for environments without real chips."""
    if not _DESKTOP_CHIPS:
        pytest.skip("No real domain chips found on Desktop")


@pytest.fixture(autouse=False)
def require_real_chips() -> None:
    """Use this fixture to skip tests when no real chips are available."""
    _skip_if_no_chips()


# ---------------------------------------------------------------------------
# Baseline snapshot path
# ---------------------------------------------------------------------------

BASELINE_PATH = Path(__file__).parent / "baseline_v2_scores.json"
