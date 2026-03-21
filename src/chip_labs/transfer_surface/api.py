"""Transfer-surface compatibility API."""

from __future__ import annotations

from .loop_controller import LoopConfig, LoopResult, LoopTelemetry, RecursiveLoopController
from .transfer import (
    apply_pattern,
    extract_portfolio_patterns,
    find_applicable_patterns,
    portfolio_transfer,
    transfer_intelligence,
)

__all__ = [
    "LoopConfig",
    "LoopResult",
    "LoopTelemetry",
    "RecursiveLoopController",
    "apply_pattern",
    "extract_portfolio_patterns",
    "find_applicable_patterns",
    "portfolio_transfer",
    "transfer_intelligence",
]
