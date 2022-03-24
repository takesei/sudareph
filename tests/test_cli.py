from click.testing import CliRunner

from sudareph.cli import main


def test_main():
    runner = CliRunner()
    res = runner.invoke(main)

    assert res.exit_code == 0
