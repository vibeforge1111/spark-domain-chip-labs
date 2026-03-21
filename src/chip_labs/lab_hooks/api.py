"""Hook-surface compatibility API.

Internal callers should depend on this namespace instead of importing
individual top-level hook modules directly. That keeps the future module move
behind one stable internal surface.
"""

from __future__ import annotations

from .evaluate import evaluate as run_evaluate
from .packets import generate_packets
from .suggest import suggest as run_suggest
from .watchtower import generate_watchtower_pages

__all__ = [
    "generate_packets",
    "generate_watchtower_pages",
    "run_evaluate",
    "run_suggest",
]
