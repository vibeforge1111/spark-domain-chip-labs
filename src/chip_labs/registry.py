"""Chip portfolio registry -- discovers and tracks domain chips."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


DEFAULT_SEARCH_DIR = Path(os.path.expanduser("~")) / "Desktop"

KNOWN_CHIP_PREFIXES = ("domain-chip-",)


def discover_chips(search_dir: str | Path | None = None) -> list[dict[str, Any]]:
    """Discover domain chips in the search directory.

    Returns a list of chip descriptors with name, path, version, and manifest status.
    """
    search_dir = Path(search_dir) if search_dir else DEFAULT_SEARCH_DIR
    chips: list[dict[str, Any]] = []

    if not search_dir.exists():
        return chips

    for entry in sorted(search_dir.iterdir()):
        if not entry.is_dir():
            continue
        if not any(entry.name.startswith(prefix) for prefix in KNOWN_CHIP_PREFIXES):
            continue

        chip_info: dict[str, Any] = {
            "name": entry.name,
            "path": str(entry),
            "has_manifest": False,
            "has_project": False,
            "version": None,
            "domain": None,
            "capabilities": [],
        }

        manifest_path = entry / "spark-chip.json"
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                chip_info["has_manifest"] = True
                chip_info["version"] = manifest.get("version")
                chip_info["domain"] = manifest.get("domain")
                chip_info["capabilities"] = manifest.get("capabilities", [])
            except (json.JSONDecodeError, OSError):
                pass

        project_path = entry / "spark-researcher.project.json"
        if project_path.exists():
            chip_info["has_project"] = True

        # Count artifacts and vault docs
        artifacts_dir = entry / "artifacts"
        vault_dir = entry / "obsidian-vault"
        chip_info["artifact_count"] = sum(1 for _ in artifacts_dir.rglob("*") if _.is_file()) if artifacts_dir.exists() else 0
        chip_info["vault_doc_count"] = sum(1 for _ in vault_dir.rglob("*.md")) if vault_dir.exists() else 0

        chips.append(chip_info)

    return chips


def get_portfolio_summary(search_dir: str | Path | None = None) -> dict[str, Any]:
    """Get a summary of the chip portfolio."""
    chips = discover_chips(search_dir)

    maturity_counts: dict[str, int] = {"production": 0, "beta": 0, "alpha": 0, "scaffold": 0}
    total_artifacts = 0
    total_vault_docs = 0

    for chip in chips:
        total_artifacts += chip.get("artifact_count", 0)
        total_vault_docs += chip.get("vault_doc_count", 0)

        version = chip.get("version", "")
        if version and version.startswith("0.3"):
            maturity_counts["production"] += 1
        elif version and version.startswith("0.2"):
            maturity_counts["beta"] += 1
        elif version and version.startswith("0.1"):
            maturity_counts["alpha"] += 1
        else:
            maturity_counts["scaffold"] += 1

    return {
        "total_chips": len(chips),
        "maturity_distribution": maturity_counts,
        "total_artifacts": total_artifacts,
        "total_vault_docs": total_vault_docs,
        "chips": chips,
    }
