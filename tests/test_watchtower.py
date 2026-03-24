"""Tests for the watchtower page generation module."""

from pathlib import Path

import pytest

import chip_labs.watchtower as watchtower_module
from chip_labs.watchtower import generate_watchtower_pages


class TestPageGeneration:
    """Test that the watchtower generates the expected set of pages."""

    def test_generates_at_least_four_pages(self, tmp_path: Path) -> None:
        pages = generate_watchtower_pages(
            mutations={},
            chip_search_dir=tmp_path,
        )
        assert len(pages) >= 6

    def test_expected_page_names(self, tmp_path: Path) -> None:
        pages = generate_watchtower_pages(
            mutations={},
            chip_search_dir=tmp_path,
        )
        paths = [p["path"] for p in pages]
        assert "Lab Home.md" in paths
        assert "Portfolio Dashboard.md" in paths
        assert "MiroFish Portfolio.md" in paths
        assert "MiroFish Frontier.md" in paths
        assert "Agent Team Status.md" in paths
        assert "Graduation Pipeline.md" in paths


class TestPageStructure:
    """Test that generated pages have the required fields."""

    def test_pages_have_path_and_content(self, tmp_path: Path) -> None:
        pages = generate_watchtower_pages(
            mutations={},
            chip_search_dir=tmp_path,
        )
        for page in pages:
            assert "path" in page, f"Page missing 'path' field: {page}"
            assert "content" in page, f"Page missing 'content' field: {page}"
            assert isinstance(page["path"], str)
            assert isinstance(page["content"], str)
            assert len(page["content"]) > 0


class TestLabHomePage:
    """Test specific content of the Lab Home page."""

    def test_lab_home_contains_mission_heading(self, tmp_path: Path) -> None:
        pages = generate_watchtower_pages(
            mutations={},
            chip_search_dir=tmp_path,
        )
        lab_home = next(p for p in pages if p["path"] == "Lab Home.md")
        assert "## Mission" in lab_home["content"]

    def test_lab_home_contains_portfolio_overview(self, tmp_path: Path) -> None:
        pages = generate_watchtower_pages(
            mutations={},
            chip_search_dir=tmp_path,
        )
        lab_home = next(p for p in pages if p["path"] == "Lab Home.md")
        assert "Portfolio Overview" in lab_home["content"]

    def test_lab_home_contains_agent_list(self, tmp_path: Path) -> None:
        pages = generate_watchtower_pages(
            mutations={},
            chip_search_dir=tmp_path,
        )
        lab_home = next(p for p in pages if p["path"] == "Lab Home.md")
        assert "Frontier Scout" in lab_home["content"]
        assert "Methodology Researcher" in lab_home["content"]


class TestMiroFishPortfolioPage:
    """Test MiroFish portfolio watchtower page generation."""

    def test_mirofish_page_contains_heading(self, tmp_path: Path) -> None:
        pages = generate_watchtower_pages(
            mutations={},
            chip_search_dir=tmp_path,
        )
        mirofish_page = next(p for p in pages if p["path"] == "MiroFish Portfolio.md")
        assert "# MiroFish Portfolio" in mirofish_page["content"]

    def test_mirofish_page_links_back_to_dashboard(self, tmp_path: Path) -> None:
        pages = generate_watchtower_pages(
            mutations={},
            chip_search_dir=tmp_path,
        )
        mirofish_page = next(p for p in pages if p["path"] == "MiroFish Portfolio.md")
        assert "[[Portfolio Dashboard]]" in mirofish_page["content"]


class TestMiroFishFrontierPage:
    """Test MiroFish frontier watchtower page generation."""

    def test_mirofish_frontier_page_contains_heading(self, tmp_path: Path) -> None:
        pages = generate_watchtower_pages(
            mutations={},
            chip_search_dir=tmp_path,
        )
        frontier_page = next(p for p in pages if p["path"] == "MiroFish Frontier.md")
        assert "# MiroFish Frontier" in frontier_page["content"]

    def test_mirofish_frontier_page_links_to_portfolio(self, tmp_path: Path) -> None:
        pages = generate_watchtower_pages(
            mutations={},
            chip_search_dir=tmp_path,
        )
        frontier_page = next(p for p in pages if p["path"] == "MiroFish Frontier.md")
        assert "[[MiroFish Portfolio]]" in frontier_page["content"]

    def test_mirofish_frontier_page_prefers_shortlist_when_available(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        research_meta = tmp_path / "research" / "meta"
        research_meta.mkdir(parents=True)
        shortlist = research_meta / "MIROFISH_FRONTIER_SHORTLIST_180_DEEPER_2026-03-25.md"
        shortlist_note = research_meta / "MIROFISH_FRONTIER_SHORTLIST_180_DEEPER_NOTE_2026-03-25.md"
        export = research_meta / "MIROFISH_FRONTIER_EXPORT_TRANCHE_180_DEEPER_2026-03-25.md"
        compare = research_meta / "MIROFISH_FRONTIER_CHECKPOINTS_2026-03-25.html"

        shortlist.write_text("# Shortlist Body\n\nTop winners here.", encoding="utf-8")
        shortlist_note.write_text("# Shortlist Note\n\nMetadata only.", encoding="utf-8")
        export.write_text("# Full Export Body\n\nFull ranked export here.", encoding="utf-8")
        compare.write_text("<html></html>", encoding="utf-8")

        def fake_latest_meta_file(pattern: str) -> Path | None:
            mapping = {
                "MIROFISH_FRONTIER_SHORTLIST_*.md": shortlist_note,
                "MIROFISH_FRONTIER_EXPORT_*.md": export,
                "MIROFISH_FRONTIER_READOUT_*.json": None,
                "MIROFISH_FRONTIER_CHECKPOINTS_*.html": compare,
                "MIROFISH_PORTFOLIO_EXPORT_*.md": None,
                "MIROFISH_PORTFOLIO_READOUT_*.json": None,
            }
            return mapping.get(pattern)

        monkeypatch.setattr(watchtower_module, "_latest_meta_file", fake_latest_meta_file)
        monkeypatch.setattr(watchtower_module, "_repo_root", lambda: tmp_path)

        pages = generate_watchtower_pages(
            mutations={},
            chip_search_dir=tmp_path,
        )
        frontier_page = next(p for p in pages if p["path"] == "MiroFish Frontier.md")
        assert "## Current Frontier Shortlist" in frontier_page["content"]
        assert "# Shortlist Body" in frontier_page["content"]
        assert "## Full Frontier Checkpoint" in frontier_page["content"]
        assert "# Full Export Body" in frontier_page["content"]
