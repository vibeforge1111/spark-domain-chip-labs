from __future__ import annotations

import sys

import pytest

from chip_labs import cli


def test_parse_seed_list_returns_tuple_of_ints_for_clean_input() -> None:
    assert cli._parse_seed_list("1,2,3") == (1, 2, 3)


def test_parse_seed_list_strips_whitespace_and_skips_empty_tokens() -> None:
    assert cli._parse_seed_list(" 1 , , 2,3, ") == (1, 2, 3)


def test_parse_seed_list_returns_empty_tuple_for_empty_input() -> None:
    assert cli._parse_seed_list("") == ()


def test_parse_seed_list_rejects_non_numeric_token_with_actionable_message() -> None:
    with pytest.raises(SystemExit) as error:
        cli._parse_seed_list("1,foo,3")

    message = str(error.value)
    assert "--seeds" in message
    assert "'foo'" in message
    assert "comma-separated list of integer seeds" in message


def test_parse_seed_list_collects_all_invalid_tokens_in_single_message() -> None:
    with pytest.raises(SystemExit) as error:
        cli._parse_seed_list("1,foo,2,bar")

    message = str(error.value)
    assert "'foo'" in message
    assert "'bar'" in message


def test_parse_seed_list_honors_custom_flag_label_in_error_message() -> None:
    with pytest.raises(SystemExit) as error:
        cli._parse_seed_list("x", flag="--custom-seeds")

    assert "--custom-seeds" in str(error.value)


def test_cli_version_flag_prints_package_version(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", ["chip-labs", "--version"])

    with pytest.raises(SystemExit) as error:
        cli.main()

    assert error.value.code == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == f"chip-labs {cli.__version__}"
    assert captured.err == ""
