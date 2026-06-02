"""Regression tests for the shared ``_parse_seed_list`` CLI helper.

The CLI subcommands ``generated-multi-seed-run`` and
``creator-system-production-readiness`` accept a comma-separated
``--seeds`` argument.  Previously each subcommand coerced every token
to ``int`` with a bare ``int(item.strip())`` inside a generator
expression.  A single non-numeric token (e.g. ``"1,foo,3"``) raised
``ValueError`` and crashed the entire subcommand before any friendly
hint could be emitted.  ``_parse_seed_list`` collects the offending
tokens and raises a single ``SystemExit`` listing them so the operator
can correct the typo without parsing a Python traceback.
"""

from __future__ import annotations

import pytest

from chip_labs.cli import _parse_seed_list


def test_parse_seed_list_returns_tuple_of_ints_for_clean_input() -> None:
    assert _parse_seed_list("1,2,3") == (1, 2, 3)


def test_parse_seed_list_strips_whitespace_and_skips_empty_tokens() -> None:
    # Trailing comma, internal whitespace, and an empty token must all be
    # tolerated without raising; the previous generator-expression form
    # already skipped empty tokens via ``if item.strip()``.
    assert _parse_seed_list(" 1 , 2 ,, 3 , ") == (1, 2, 3)


def test_parse_seed_list_accepts_a_single_seed() -> None:
    assert _parse_seed_list("42") == (42,)


def test_parse_seed_list_returns_empty_tuple_for_empty_input() -> None:
    # The CLI subcommand callers re-check the result and emit their own
    # ``--seeds must include at least one integer seed`` message; the
    # helper itself simply returns ``()`` for empty input so the
    # downstream check stays as the single source of truth.
    assert _parse_seed_list("") == ()
    assert _parse_seed_list(None) == ()
    assert _parse_seed_list("   ") == ()


def test_parse_seed_list_rejects_non_numeric_token_with_actionable_message() -> None:
    # Before the fix this raised ``ValueError: invalid literal for int()
    # with base 10: 'foo'`` from inside a generator expression, which
    # surfaced as an uncaught traceback at the CLI boundary.
    with pytest.raises(SystemExit) as exc:
        _parse_seed_list("1,foo,3")
    message = str(exc.value)
    assert "--seeds" in message
    assert "'foo'" in message
    assert "non-numeric token" in message


def test_parse_seed_list_collects_all_invalid_tokens_in_single_message() -> None:
    # Listing every bad token at once avoids the slow drip of repeated
    # ValueError surfaces when the operator fat-fingers more than one
    # entry.
    with pytest.raises(SystemExit) as exc:
        _parse_seed_list("1,foo,2,bar")
    message = str(exc.value)
    assert "'foo'" in message
    assert "'bar'" in message


def test_parse_seed_list_honors_custom_flag_label_in_error_message() -> None:
    with pytest.raises(SystemExit) as exc:
        _parse_seed_list("nope", flag="--my-flag")
    assert "--my-flag" in str(exc.value)
