"""Compatibility alias for the intelligence-serving context injector."""

from __future__ import annotations

from importlib import import_module
import sys

sys.modules[__name__] = import_module(".intelligence_serving.chip_context_injector", __package__)
