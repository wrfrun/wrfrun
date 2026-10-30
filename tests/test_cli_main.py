import sys

import pytest

from wrfrun.cli.main import main_entry


def test_version_option_reads_installed_distribution_version(monkeypatch, capsys):
    monkeypatch.setattr("wrfrun.cli.main.version", lambda _: "9.9.9")
    monkeypatch.setattr(sys, "argv", ["wrfrun", "--version"])

    with pytest.raises(SystemExit, match="0"):
        main_entry()

    assert capsys.readouterr().out == "wrfrun 9.9.9\n"
