"""Compatibility alias for the chip factory scaffold module."""

from __future__ import annotations

from importlib import import_module
import sys

sys.modules[__name__] = import_module(".chip_factory.scaffold", __package__)
