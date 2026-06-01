from __future__ import annotations

import sys

import pytest

from chip_labs import cli


@pytest.mark.parametrize(
    ("argv", "flag"),
    [
        (["chip-labs", "doctor", "chip", "--max-iterations", "0"], "--max-iterations"),
        (["chip-labs", "autoloop", "--max-iterations", "-1"], "--max-iterations"),
        (["chip-labs", "serve-intelligence", "task", "--max-chips", "0"], "--max-chips"),
        (["chip-labs", "mirofish-hybrid-spec", "--input", "in.json", "--rounds", "0"], "--rounds"),
        (["chip-labs", "mirofish-portfolio-run", "--rounds", "0"], "--rounds"),
        (["chip-labs", "mirofish-portfolio-run", "--flagship-count-per-type", "0"], "--flagship-count-per-type"),
        (["chip-labs", "mirofish-portfolio-run", "--ensemble-runs", "0"], "--ensemble-runs"),
        (["chip-labs", "mirofish-portfolio-run", "--ensemble-count-per-type", "0"], "--ensemble-count-per-type"),
        (["chip-labs", "mirofish-portfolio-run", "--min-runs", "0"], "--min-runs"),
        (["chip-labs", "mirofish-portfolio-run", "--bootstrap-resamples", "0"], "--bootstrap-resamples"),
        (["chip-labs", "mirofish-portfolio-readout", "--input", "in.json", "--top-n", "0"], "--top-n"),
        (["chip-labs", "mirofish-portfolio-readout", "--input", "in.json", "--enterprise-n", "0"], "--enterprise-n"),
        (
            ["chip-labs", "mirofish-portfolio-readout", "--input", "in.json", "--newly-discovered-n", "0"],
            "--newly-discovered-n",
        ),
        (["chip-labs", "mirofish-frontier-readout", "--input", "in.json", "--top-n", "0"], "--top-n"),
        (["chip-labs", "mirofish-frontier-readout", "--input", "in.json", "--watchlist-n", "0"], "--watchlist-n"),
        (["chip-labs", "mirofish-frontier-readout", "--input", "in.json", "--benchmark-n", "0"], "--benchmark-n"),
        (["chip-labs", "mirofish-frontier-shortlist", "--input", "in.json", "--winner-n", "0"], "--winner-n"),
        (["chip-labs", "mirofish-frontier-shortlist", "--input", "in.json", "--breakout-n", "0"], "--breakout-n"),
        (["chip-labs", "mirofish-frontier-shortlist", "--input", "in.json", "--speculative-n", "0"], "--speculative-n"),
    ],
)
def test_cli_rejects_non_positive_count_flags(argv: list[str], flag: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "argv", argv)

    with pytest.raises(SystemExit) as error:
        cli.main()

    assert error.value.code == 2
    captured = capsys.readouterr()
    assert flag in captured.err
    assert "expected a positive integer" in captured.err
