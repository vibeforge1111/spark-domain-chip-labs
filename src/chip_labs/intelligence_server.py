"""Compatibility wrapper for the intelligence-serving implementation."""

from __future__ import annotations

from .intelligence_serving.intelligence_server import *  # noqa: F401,F403
from .intelligence_serving.intelligence_server import _score_relevance  # noqa: F401
