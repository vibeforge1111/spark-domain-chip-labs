"""Tests for the positive-integer bounds on the mirofish-hybrid-spec CLI.

The mirofish-hybrid-spec command exposes three integer flags
(--flagship-count-per-type, --ensemble-runs, --ensemble-count-per-type)
that drive Monte Carlo simulation harness sizing. argparse was previously
configured with type=int, which let the CLI accept 0, negative values, and
implicit "no ensemble" specs that downstream code would later treat as
"degenerate but valid". This locks those flags to type=_positive_int so
non-positive values are rejected with a clear, actionable error before any
hybrid spec is written to disk.
"""

from __future__ import annotations

import sys

import pytest

from chip_labs import cli


@pytest.mark.parametrize(
    ("flag", "value"),
    [
        ("--flagship-count-per-type", "0"),
        ("--flagship-count-per-type", "-1"),
        ("--ensemble-runs", "0"),
        ("--ensemble-runs", "-10"),
        ("--ensemble-count-per-type", "0"),
        ("--ensemble-count-per-type", "-5"),
    ],
)
def test_mirofish_hybrid_spec_rejects_non_positive_count_flags(
    flag: str, value: str, tmp_path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    input_path = tmp_path / "disc.json"
    input_path.write_text(
        '{"packet_kind":"mirofish_discovery_batch","batch_id":"b1",'
        '"accepted_candidates":[{"domain_id":"d1","label":"d1","tier":"discovered"}]}',
        encoding="utf-8",
    )
    output_path = tmp_path / "spec.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "chip-labs",
            "mirofish-hybrid-spec",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            flag,
            value,
        ],
    )

    with pytest.raises(SystemExit) as error:
        cli.main()

    assert error.value.code == 2
    captured = capsys.readouterr()
    assert flag in captured.err
    assert "expected a positive integer" in captured.err
    assert not output_path.exists(), (
        "spec file must not be written when a count flag is rejected"
    )


def test_mirofish_hybrid_spec_help_describes_positive_integer_constraint(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        sys, "argv", ["chip-labs", "mirofish-hybrid-spec", "--help"]
    )

    with pytest.raises(SystemExit) as error:
        cli.main()

    assert error.value.code == 0
    captured = capsys.readouterr()
    for flag in (
        "--flagship-count-per-type",
        "--ensemble-runs",
        "--ensemble-count-per-type",
    ):
        assert flag in captured.out
        # The help text must mention the positive-integer constraint so
        # that operators discover it before running a real spec build.
        assert "must be a positive integer" in captured.out


def test_mirofish_hybrid_spec_writes_spec_with_default_counts(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path = tmp_path / "disc.json"
    input_path.write_text(
        '{"packet_kind":"mirofish_discovery_batch","batch_id":"b1",'
        '"accepted_candidates":[{"domain_id":"d1","label":"d1","tier":"discovered"}]}',
        encoding="utf-8",
    )
    output_path = tmp_path / "spec.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "chip-labs",
            "mirofish-hybrid-spec",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ],
    )

    cli.main()

    import json

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    harness = payload["harness"]
    # Defaults unchanged by the new bounds: 30 / 15 / 15.
    assert harness["flagship_count_per_type"] == 30
    assert harness["ensemble_runs"] == 15
    assert harness["ensemble_count_per_type"] == 15
