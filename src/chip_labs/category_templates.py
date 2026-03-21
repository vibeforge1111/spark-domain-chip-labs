"""Compatibility alias for the chip factory category templates module."""

from __future__ import annotations

from importlib import import_module
import sys

sys.modules[__name__] = import_module(".chip_factory.category_templates", __package__)
