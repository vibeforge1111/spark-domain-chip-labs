"""Compatibility alias for the chip factory methodology module."""

from __future__ import annotations

from importlib import import_module
import sys

sys.modules[__name__] = import_module(".chip_factory.methodology", __package__)
