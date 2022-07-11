import pytest

from server_monitor_agent.core.cli import Cli
from server_monitor_agent.entry import main


@pytest.mark.parametrize("option", (["-h"], ["--help"]))
def test_main(capsys, option):
    with pytest.raises(SystemExit) as error:
        main(option)

    out, err = capsys.readouterr()

    assert out.startswith("usage: server-monitor-agent")
    assert Cli.description in out
    assert " --help " in out
    assert " --version " in out
    assert " --log-level " in out
    assert "{sub_command}" in out
    assert " check " in out
    assert " notify " in out
    assert " list " in out

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


@pytest.mark.parametrize("option", (["list", "-h"], ["list", "--help"]))
def test_notify(capsys, option):
    with pytest.raises(SystemExit) as error:
        main(option)

    out, err = capsys.readouterr()

    assert out.startswith("usage: server-monitor-agent list")
    assert err == ""

    assert error.value.code == 0


@pytest.mark.parametrize("option", (["check", "name"],))
def test_check_io_required(capsys, option):
    with pytest.raises(SystemExit) as error:
        main(option)

    out, err = capsys.readouterr()

    assert out == ""
    assert (
        "\nserver-monitor-agent check: error: "
        "one of the arguments --std-out --std-err --write-file is required\n" in err
    )

    assert error.value.code == 2
