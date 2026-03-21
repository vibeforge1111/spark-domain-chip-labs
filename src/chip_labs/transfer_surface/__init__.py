"""Internal namespace for the transfer and recursive-improvement surface."""

from .api import (
    LoopConfig,
    LoopResult,
    LoopTelemetry,
    RecursiveLoopController,
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
