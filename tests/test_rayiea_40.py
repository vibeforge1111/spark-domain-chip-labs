"""Regression test for Rayiea compete item #40."""

from __future__ import annotations

import json
from pathlib import Path


def test_rayiea_40_module_imports() -> None:
    """Smoke import for patched module."""
    import importlib

    importlib.import_module("src.chip_labs.lab_hooks.watchtower")
