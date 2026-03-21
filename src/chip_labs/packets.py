"""Compatibility alias for the lab hook packets module."""

from __future__ import annotations

from importlib import import_module
import sys

sys.modules[__name__] = import_module(".lab_hooks.packets", __package__)
