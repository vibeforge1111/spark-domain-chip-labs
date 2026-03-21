"""Internal namespace for the lab hook surface.

This package is the compatibility-preserving home for the lab's public
hook-facing behavior. The underlying implementations still live in their
existing modules until later migration tranches move them behind this surface.
"""

from .api import (
    generate_packets,
    generate_watchtower_pages,
    run_evaluate,
    run_suggest,
)

__all__ = [
    "generate_packets",
    "generate_watchtower_pages",
    "run_evaluate",
    "run_suggest",
]
