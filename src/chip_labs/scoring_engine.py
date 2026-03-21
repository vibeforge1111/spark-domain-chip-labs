"""Compatibility alias for the transfer-surface scoring engine."""

from __future__ import annotations

from importlib import import_module
import sys

sys.modules[__name__] = import_module(".transfer_surface.scoring_engine", __package__)
