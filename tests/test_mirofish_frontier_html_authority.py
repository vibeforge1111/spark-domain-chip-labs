"""Regression coverage for frontier visualization HTML boundaries."""

from __future__ import annotations

import json
import re

import pytest

from chip_labs.mirofish.hybrid import render_frontier_viz_html


_TEMPLATE = (
    "<html><head><title>MiroFish v4 - 500 Domain Knowledge Graph</title></head>"
    "<body><script>"
    "const PERSONA_DATA = { investor: { label: 'Investor' } };"
    "const PERSONA_TYPES = Object.keys(PERSONA_DATA);"
    "async function loadData() { const resp = await fetch('mirofish_500_data.json'); "
    "DATA = await resp.json(); }"
    "</script></body></html>"
)


def _render(data_filename: object, title: object = "Frontier") -> str:
    return render_frontier_viz_html(
        data_filename=data_filename,  # type: ignore[arg-type]
        title=title,  # type: ignore[arg-type]
        template_html=_TEMPLATE,
    )


def _fetch_value(rendered: str) -> str:
    match = re.search(r"fetch\((\"(?:[^\"\\]|\\.)*\")\)", rendered)
    assert match is not None
    return json.loads(match.group(1))


def test_render_frontier_viz_html_preserves_filename_semantics() -> None:
    data_filename = "nested/frontier's\\data set.json?version=2&lane=fast"

    rendered = _render(data_filename)

    assert _fetch_value(rendered) == data_filename


def test_render_frontier_viz_html_escapes_title_for_html_text() -> None:
    title = "</title><script>window.pwned = true</script>"

    rendered = _render("frontier.json", title)

    assert title not in rendered
    assert "&lt;/title&gt;&lt;script&gt;window.pwned = true&lt;/script&gt;" in rendered
    assert rendered.count("<script>") == 1


def test_render_frontier_viz_html_blocks_script_termination_from_filename() -> None:
    data_filename = "</script><script>window.pwned = true</script>.json"

    rendered = _render(data_filename)

    assert data_filename not in rendered
    assert "\\u003c/script\\u003e\\u003cscript\\u003e" in rendered
    assert _fetch_value(rendered) == data_filename
    assert rendered.count("<script>") == 1


@pytest.mark.parametrize(
    "data_filename",
    [None, 7, "", "   ", "frontier\x00.json", "frontier\n.json", "x" * 2049],
)
def test_render_frontier_viz_html_rejects_invalid_filename_without_reflection(
    data_filename: object,
) -> None:
    with pytest.raises(ValueError, match=r"^invalid data filename$") as caught:
        _render(data_filename)

    assert str(data_filename) not in str(caught.value)


@pytest.mark.parametrize("title", [None, 7, "", "   ", "frontier\n", "x" * 513])
def test_render_frontier_viz_html_rejects_invalid_title_without_reflection(title: object) -> None:
    with pytest.raises(ValueError, match=r"^invalid title$") as caught:
        _render("frontier.json", title)

    assert str(title) not in str(caught.value)
