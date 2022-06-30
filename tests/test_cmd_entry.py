import pytest

from server_monitor_agent.cmd.cli import Cli
from server_monitor_agent.cmd.entry import main


@pytest.mark.parametrize("option", (["-h"], ["--help"]))
def test_main(capsys, option):
    with pytest.raises(SystemExit) as error:
        main(option)

    out, err = capsys.readouterr()

    assert out.startswith("usage: server-monitor-agent")
    assert Cli.description in out
    assert "{sub_command}" in out
    assert " check " in out
    assert " notify " in out

    assert err == ""

    assert error.value.code == 0


@pytest.mark.parametrize("option", (["check", "-h"], ["check", "--help"]))
def test_check(capsys, option):
    with pytest.raises(SystemExit) as error:
        main(option)

    out, err = capsys.readouterr()

    assert out.startswith("usage: server-monitor-agent check")
    assert err == ""

    assert error.value.code == 0


@pytest.mark.parametrize("option", (["notify", "-h"], ["notify", "--help"]))
def test_notify(capsys, option):
    with pytest.raises(SystemExit) as error:
        main(option)

    out, err = capsys.readouterr()

    assert out.startswith("usage: server-monitor-agent notify")
    assert err == ""

    assert error.value.code == 0
