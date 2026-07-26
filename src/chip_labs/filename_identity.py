"""Portable, collision-resistant identities for filenames derived from data."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import Any


_PORTABLE_COMPONENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")
_WINDOWS_RESERVED = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def derived_filename_component(value: Any, *, fallback: str) -> str:
    """Return a bounded component while keeping the original value in its packet."""
    if (
        isinstance(value, str)
        and _PORTABLE_COMPONENT.fullmatch(value)
        and value.upper() not in _WINDOWS_RESERVED
    ):
        return value

    canonical = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=repr,
    )
    normalized = unicodedata.normalize("NFKC", value if isinstance(value, str) else str(value))
    slug = re.sub(r"[^A-Za-z0-9_-]+", "-", normalized).strip("-_")[:40]
    if not slug or slug.upper() in _WINDOWS_RESERVED:
        slug = fallback
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
    return f"{slug}-{digest}"
