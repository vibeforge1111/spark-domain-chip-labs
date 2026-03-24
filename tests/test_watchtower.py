"""Tests for the watchtower page generation module."""

from pathlib import Path

import pytest

from chip_labs.watchtower import generate_watchtower_pages


class TestPageGeneration:
    """Test that the watchtower generates the expected set of pages."""

    def test_generates_at_least_four_pages(self, tmp_path: Path) -> None:
        pages = generate_watchtower_pages(
            mutations={},
            chip_search_dir=tmp_path,
        )
        assert len(pages) >= 5

    def test_expected_page_names(self, tmp_path: Path) -> None:
        pages = generate_watchtower_pages(
            mutations={},
            chip_search_dir=tmp_path,
        )
        paths = [p["path"] for p in pages]
        assert "Lab Home.md" in paths
        assert "Portfolio Dashboard.md" in paths
        assert "MiroFish Portfolio.md" in paths
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
