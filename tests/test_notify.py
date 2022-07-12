import io
import logging
from datetime import datetime
from importlib.resources import files, as_file
from subprocess import CompletedProcess
from tempfile import NamedTemporaryFile

from server_monitor_agent.common import ProgramMixin
from server_monitor_agent.entry import main
from server_monitor_agent.service.agent import AgentItem
from tests.helpers import check_logs, log_debug_msgs


def test_notify_user_message_file(caplog, capsys, monkeypatch):
    caplog.set_level(logging.DEBUG)
    source = files("tests.resources").joinpath("config-pass.yml")
    with as_file(source) as p:
        config_file = str(p)

    item = AgentItem(
        service_name="service_name",
        host_name="host_name",
        source_name="source_name",
        status_code="status_code",
        status_name="status_name",
        title="title",
        description="description",
        check_name="check_name",
        check_type="check_type",
        date=datetime.now(),
        tags={"tag1key": "tag1value", "tag2key": "tag2value"},
    )

    def run_cmd(self, args):
        if args[0:5] == ["wall", "--timeout", "30", "--group", "vagrant"]:
            return CompletedProcess(args=args, returncode=0, stdout="", stderr="")
        else:
            raise ValueError()

    monkeypatch.setattr(ProgramMixin, "_run_cmd", run_cmd)

    with NamedTemporaryFile(mode="wt") as fp:
        fp.write(item.to_json())
        fp.seek(0)

        cmd = "test_user_message"
        main_result = main(
            [
                "notify",
                cmd,
                "--read-file",
                fp.name,
                "--config",
                config_file,
                "--log-level",
                "debug",
            ]
        )

    assert main_result == 0
    msgs = log_debug_msgs("notify", cmd, config_file, "file")
    check_logs(caplog.record_tuples, msgs)

    out, err = capsys.readouterr()
    assert err == ""
    assert out == ""


def test_notify_user_message_stdin(caplog, capsys, monkeypatch):
    caplog.set_level(logging.DEBUG)
    source = files("tests.resources").joinpath("config-pass.yml")
    with as_file(source) as p:
        config_file = str(p)

    item = AgentItem(
        service_name="service_name",
        host_name="host_name",
        source_name="source_name",
        status_code="status_code",
        status_name="status_name",
        title="title",
        description="description",
        check_name="check_name",
        check_type="check_type",
        date=datetime.now(),
        tags={"tag1key": "tag1value", "tag2key": "tag2value"},
    )
    monkeypatch.setattr("sys.stdin", io.StringIO(item.to_json()))

    def run_cmd(self, args):
        if args[0:5] == ["wall", "--timeout", "30", "--group", "vagrant"]:
            return CompletedProcess(args=args, returncode=0, stdout="", stderr="")
        else:
            raise ValueError()

    monkeypatch.setattr(ProgramMixin, "_run_cmd", run_cmd)

    cmd = "test_user_message"
    main_result = main(
        [
            "notify",
            cmd,
            "--std-in",
            "--config",
            config_file,
            "--log-level",
            "debug",
        ]
    )

    assert main_result == 0
    msgs = log_debug_msgs("notify", cmd, config_file, "stdin")
    check_logs(caplog.record_tuples, msgs)

    out, err = capsys.readouterr()
    assert err == ""
    assert out == ""


def test_notify_email(caplog, capsys, monkeypatch):
    caplog.set_level(logging.DEBUG)
    source = files("tests.resources").joinpath("config-pass.yml")
    with as_file(source) as p:
        config_file = str(p)

    item = AgentItem(
        service_name="service_name",
        host_name="host_name",
        source_name="source_name",
        status_code="status_code",
        status_name="status_name",
        title="title",
        description="description",
        check_name="check_name",
        check_type="check_type",
        date=datetime.now(),
        tags={"tag1key": "tag1value", "tag2key": "tag2value"},
    )

    with NamedTemporaryFile(mode="wt") as fp:
        fp.write(item.to_json())
        fp.seek(0)

        cmd = "test_email"
        main_result = main(
            [
                "notify",
                cmd,
                "--read-file",
                fp.name,
                "--config",
                config_file,
                "--log-level",
                "debug",
            ]
        )

    assert main_result == 0
    msgs = log_debug_msgs("notify", cmd, config_file, "file")
    check_logs(caplog.record_tuples, msgs)

    out, err = capsys.readouterr()
    assert err == ""
    assert out == ""


def test_notify_status_cake(caplog, capsys, monkeypatch):
    caplog.set_level(logging.DEBUG)
    source = files("tests.resources").joinpath("config-pass.yml")
    with as_file(source) as p:
        config_file = str(p)

    with NamedTemporaryFile(mode="wt") as fp:
        fp.write("")
        fp.seek(0)

        cmd = "statuscake_agent"
        main_result = main(
            [
                "notify",
                cmd,
                "--read-file",
                fp.name,
                "--config",
                config_file,
                "--log-level",
                "debug",
            ]
        )

    assert main_result == 0
    msgs = log_debug_msgs("notify", cmd, config_file, "file")
    check_logs(caplog.record_tuples, msgs)

    out, err = capsys.readouterr()
    assert err == ""
    assert out == ""


def test_notify_slack(caplog, capsys, monkeypatch):
    caplog.set_level(logging.DEBUG)
    source = files("tests.resources").joinpath("config-pass.yml")
    with as_file(source) as p:
        config_file = str(p)

    item = AgentItem(
        service_name="service_name",
        host_name="host_name",
        source_name="source_name",
        status_code="status_code",
        status_name="status_name",
        title="title",
        description="description",
        check_name="check_name",
        check_type="check_type",
        date=datetime.now(),
        tags={"tag1key": "tag1value", "tag2key": "tag2value"},
    )

    with NamedTemporaryFile(mode="wt") as fp:
        fp.write(item.to_json())
        fp.seek(0)

        cmd = "testing_slack"
        main_result = main(
            [
                "notify",
                cmd,
                "--read-file",
                fp.name,
                "--config",
                config_file,
                "--log-level",
                "debug",
                "--format",
                "consul-watch",
            ]
        )

    assert main_result == 0
    msgs = log_debug_msgs("notify", cmd, config_file, "file")
    check_logs(caplog.record_tuples, msgs)

    out, err = capsys.readouterr()
    assert err == ""
    assert out == ""
