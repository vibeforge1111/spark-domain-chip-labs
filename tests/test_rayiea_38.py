"""Regression test for Rayiea compete item #38."""

from __future__ import annotations

import json
from pathlib import Path


def test_rayiea_38_module_imports() -> None:
    """Smoke import for patched module."""
    import importlib

    importlib.import_module("src.chip_labs.transfer_surface.transfer")
