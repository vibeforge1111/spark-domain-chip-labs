"""Internal namespace for the chip factory surface."""

from .api import (
    analyze_gaps,
    apply_template,
    assess_graduation,
    detect_category,
    get_creation_checklist,
    get_patterns_for_area,
    get_proven_patterns,
    improve_chip,
    load_brief,
    scaffold_chip,
    validate_brief,
)

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
