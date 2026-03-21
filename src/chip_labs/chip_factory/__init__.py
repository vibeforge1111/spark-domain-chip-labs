"""Internal namespace for the chip factory surface."""

from .api import (
    analyze_gaps,
    apply_template,
    detect_category,
    improve_chip,
    load_brief,
    scaffold_chip,
    validate_brief,
)

__all__ = [
    "analyze_gaps",
    "apply_template",
    "detect_category",
    "improve_chip",
    "load_brief",
    "scaffold_chip",
    "validate_brief",
]
