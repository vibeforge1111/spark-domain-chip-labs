"""Compatibility alias for the transfer-surface loop controller."""

from __future__ import annotations

from importlib import import_module
import sys

sys.modules[__name__] = import_module(".transfer_surface.loop_controller", __package__)
