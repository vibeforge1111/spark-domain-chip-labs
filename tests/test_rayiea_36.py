"""Regression test for Rayiea compete item #36."""

from __future__ import annotations

import json
from pathlib import Path


def test_rayiea_36_module_imports() -> None:
    """Smoke import for patched module."""
    import importlib

    importlib.import_module("src.chip_labs.transfer_surface.loop_controller")
