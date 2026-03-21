"""Factory-surface compatibility API."""

from __future__ import annotations

from .category_templates import apply_template, detect_category
from .graduation import assess_graduation
from .gap_analyzer import analyze_gaps, improve_chip
from .methodology import (
    get_creation_checklist,
    get_patterns_for_area,
    get_proven_patterns,
)
from .scaffold import load_brief, scaffold_chip, validate_brief

__all__ = [
    "analyze_gaps",
    "apply_template",
    "assess_graduation",
    "detect_category",
    "get_creation_checklist",
    "get_patterns_for_area",
    "get_proven_patterns",
    "improve_chip",
    "load_brief",
    "scaffold_chip",
    "validate_brief",
]
