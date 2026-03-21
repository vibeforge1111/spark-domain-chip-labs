"""Compatibility alias for the intelligence-serving runtime."""

from __future__ import annotations

from importlib import import_module
import sys

sys.modules[__name__] = import_module(".intelligence_serving.chip_runtime", __package__)
