"""Factory-surface compatibility API."""

from __future__ import annotations

from ..category_templates import apply_template, detect_category
from ..gap_analyzer import analyze_gaps, improve_chip
from ..scaffold import load_brief, scaffold_chip, validate_brief

__all__ = [
    "analyze_gaps",
    "apply_template",
    "detect_category",
    "improve_chip",
    "load_brief",
    "scaffold_chip",
    "validate_brief",
]
