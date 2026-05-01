from __future__ import annotations

from pathlib import Path


README = Path("docs/creator_system/README.md")
RELEASE_NOTES = Path("docs/creator_system/CREATOR_SYSTEM_RELEASE_NOTES_2026-05-01.md")


def test_creator_system_readme_keeps_claim_boundaries_visible() -> None:
    text = README.read_text(encoding="utf-8")

    assert "## Current Claim Levels" in text
    assert "CREATOR_SYSTEM_RELEASE_NOTES_2026-05-01.md" in text
    assert "| Startup YC reference fixture | `transfer_supported` |" in text
    assert "`network_absorbable` is blocked" in text
    assert "| Product surfaces | Deferred |" in text
    assert "| Network absorption | Future gated claim |" in text
    assert "| Retrieval memory domain | Local memory-lane contract |" in text
    assert "does not prove real virality" in text
    assert "does not prove product correctness" in text


def test_creator_system_readme_keeps_command_index_visible() -> None:
    text = README.read_text(encoding="utf-8")

    assert "## Executable Command Index" in text
    for command in (
        "creator-run-init",
        "creator-run-smoke",
        "creator-run-doctor",
        "creator-run-template-check",
        "artifact-quality-score",
        "artifact-quality-benchmark",
        "tool-operation-check",
        "retrieval-memory-check",
        "mirofish-content-simulate",
        "mirofish-content-route",
    ):
        assert command in text


def test_creator_system_release_notes_keep_network_boundary_visible() -> None:
    text = RELEASE_NOTES.read_text(encoding="utf-8")

    assert "Startup YC remains `transfer_supported`, not `network_absorbable`." in text
    assert "Product surfaces remain deferred" in text
    assert "Latest broad suite result before push: `77 passed`." in text
