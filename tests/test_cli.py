import io
import json
import os
import pathlib
import re
import subprocess
import sys

import pytest
import requests

from server_monitor_agent.agent import common
from server_monitor_agent.entry import main

expected_version = "0.5.0"

if sys.version_info.minor >= 10:
    help_phrase_options = "options:"
else:
    help_phrase_options = "optional arguments:"


PROG_HELP = (
    "usage: server-monitor-agent [-h] [--version] [--debug] check_command ...\n"
    "\n"
    "Run a check on the local machine.\n"
    "\n"
    f"{help_phrase_options}\n"
    "  -h, --help       show this help message and exit\n"
    "  --version        show program's version number and exit\n"
    "  --debug          Turn on debug mode.\n"
    "\n"
    "Available checks:\n"
    "  Specify the check command to run\n"
    "\n"
    "  check_command\n"
    "    memory         Check the current memory usage.\n"
    "    cpu            Check the current cpu usage.\n"
    "    disk           Check the current free space for a disk.\n"
    "    systemd-service\n"
    "                   Check the current status of a systemd service.\n"
    "    systemd-timer  Check the current status of a systemd timer.\n"
    "    consul-report  Report the current state of all consul checks for this\n"
    "                   datacenter.\n"
)

_collapse_whitespace_re = re.compile(r'\s+')
def _collapse_whitespace(data: str) -> str:
    return _collapse_whitespace_re.sub(' ', data)


def test_cli_no_args(capsys, caplog):
    actual_exit_code = main([])
    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert _collapse_whitespace(stderr) == _collapse_whitespace(PROG_HELP)
    assert caplog.record_tuples == []

    assert actual_exit_code == 1


def test_cli_help(capsys, caplog):
    with pytest.raises(SystemExit, match="0"):
        main(["--help"])

    stdout, stderr = capsys.readouterr()
    assert _collapse_whitespace(stdout) == _collapse_whitespace(PROG_HELP)
    assert stderr == ""
    assert caplog.record_tuples == []


def test_cli_version(capsys, caplog):
    with pytest.raises(SystemExit, match="0"):
        main(["--version"])

    stdout, stderr = capsys.readouterr()
    assert stdout == f"{common.APP_NAME_DASH} {expected_version}\n"
    assert stderr == ""
    assert caplog.record_tuples == []


def test_cli_memory(capsys, caplog):
    actual_exit_code = main(["memory"])

    stdout, stderr = capsys.readouterr()

    assert actual_exit_code in [0, 2]
    if actual_exit_code == 0:
        assert "*PASSING*: `memory` on `" in stdout
        assert stderr == ""
    else:
        assert stdout == ""
        assert "*PROBLEM*: `memory` on `" in stderr

    assert caplog.record_tuples == []


def test_cli_cpu(capsys, caplog):
    actual_exit_code = main(["cpu", "--interval", "0.5"])

    stdout, stderr = capsys.readouterr()

    assert actual_exit_code in [0, 2]
    if actual_exit_code == 0:
        assert "*PASSING*: `cpu` on `" in stdout
        assert stderr == ""
    else:
        assert stdout == ""
        assert "*PROBLEM*: `cpu` on `" in stderr

    assert caplog.record_tuples == []


def test_cli_systemd_service_help(capsys, caplog):
    with pytest.raises(SystemExit, match="0"):
        main(["systemd-service", "--help"])

    stdout, stderr = capsys.readouterr()
    assert "usage: server-monitor-agent systemd-service" in stdout
    assert stderr == ""
    assert caplog.record_tuples == []


def test_cli_systemd_service_ssh_check(capsys, caplog, monkeypatch):

    data = [
        "StatusErrno=0",
        "Result=success",
        "ExecMainStartTimestamp=Mon 2022-10-31 15:30:10 AEST",
        "ExecMainCode=0",
        "ExecMainStatus=0",
        "LoadState=loaded",
        "ActiveState=active",
        "SubState=running",
        "UnitFileState=enabled",
        "UnitFilePreset=enabled",
        "StateChangeTimestamp=Mon 2022-10-31 15:30:10 AEST",
        "InactiveExitTimestamp=Mon 2022-10-31 15:30:10 AEST",
        "ActiveEnterTimestamp=Mon 2022-10-31 15:30:10 AEST",
        "ConditionTimestamp=Mon 2022-10-31 15:30:10 AEST",
        "AssertTimestamp=Mon 2022-10-31 15:30:10 AEST",
    ]

    with monkeypatch.context() as m:

        def execute_process(*args, **kwargs):
            return subprocess.CompletedProcess(
                args=args, returncode=0, stdout="\n".join(data), stderr=""
            )

        m.setattr("server_monitor_agent.agent.common.execute_process", execute_process)
        actual_exit_code = main(["systemd-service", "ssh", "auto-infinite"])

    stdout, stderr = capsys.readouterr()
    assert "*PASSING*: `ssh.service` on `" in stdout
    assert stderr == ""
    assert caplog.record_tuples == []
    assert actual_exit_code == 0


def test_cli_consul_report_aws(capsys, caplog, monkeypatch, tmp_path):

    os.environ["CONSUL_HTTP_ADDR"] = "https://localhost:8501"
    os.environ["CONSUL_HTTP_SSL"] = "true"
    os.environ["CONSUL_HTTP_SSL_VERIFY"] = "true"
    os.environ["CONSUL_CACERT"] = str(tmp_path / "ca_cert")
    os.environ["CONSUL_CAPATH"] = str(tmp_path / "ca_path")
    os.environ["CONSUL_CLIENT_CERT"] = str(tmp_path / "client_cert")
    os.environ["CONSUL_CLIENT_KEY"] = str(tmp_path / "client_key")
    os.environ["SLACK_WEBHOOK_URL_CONSUL"] = "slack_webhook_url"

    for i in [
        "CONSUL_CACERT",
        "CONSUL_CAPATH",
        "CONSUL_CLIENT_CERT",
        "CONSUL_CLIENT_KEY",
    ]:
        pathlib.Path(os.environ[i]).touch()

    with monkeypatch.context() as m:

        def request_url(*args, **kwargs):
            if (
                kwargs["method"] == "get"
                and kwargs["url"] == "https://localhost:8501/v1/health/state/any"
            ):
                resp = requests.Response()
                resp.url = kwargs["url"]
                resp.status_code = 200
                resp.encoding = "utf-8"

                resp.raw = io.BytesIO()
                resp.raw.write(
                    json.dumps(
                        [
                            {
                                "Node": "test.example.com",
                                "Name": "Check name",
                                "Status": "critical",
                                "ServiceName": "Service name",
                            }
                        ]
                    ).encode(resp.encoding)
                )
                resp.raw.seek(0)

                return resp

            if (
                kwargs["method"] == "get"
                and kwargs["url"] == "https://localhost:8501/v1/status/leader"
            ):
                resp = requests.Response()
                resp.url = kwargs["url"]
                resp.status_code = 200
                resp.encoding = "utf-8"

                resp.raw = io.BytesIO()
                resp.raw.write('"127.0.0.1:8300"'.encode(resp.encoding))
                resp.raw.seek(0)
                return resp
            if (
                kwargs["method"] == "put"
                and kwargs["url"]
                == "http://169.254.169.254/latest/api/token"
            ):
                resp = requests.Response()
                resp.url = kwargs["url"]
                resp.status_code = 200
                resp.encoding = "utf-8"

                resp.raw = io.BytesIO()
                resp.raw.write("aws-ec2-instance-metadata-token".encode(resp.encoding))
                resp.raw.seek(0)
                return resp
            if (
                kwargs["method"] == "get"
                and kwargs["url"]
                == "http://169.254.169.254/latest/meta-data/local-ipv4"
            ):
                resp = requests.Response()
                resp.url = kwargs["url"]
                resp.status_code = 200
                resp.encoding = "utf-8"

                resp.raw = io.BytesIO()
                resp.raw.write("127.0.0.1".encode(resp.encoding))
                resp.raw.seek(0)
                return resp
            if kwargs["method"] == "post" and kwargs["url"] == "slack_webhook_url":
                resp = requests.Response()
                resp.url = kwargs["url"]
                resp.status_code = 200
                resp.encoding = "utf-8"

                resp.raw = io.BytesIO()
                resp.raw.seek(0)
                return resp

            raise ValueError()

        m.setattr("requests.sessions.Session.request", request_url)

        actual_exit_code = main(["--debug", "consul-report", "aws"])

    stdout, stderr = capsys.readouterr()
    assert "*PASSING*: `consul-report` on `" in stdout
    assert "This instance is the consul leader. Sending report to Slack." in stdout
    assert stderr == ""
    assert caplog.record_tuples == []
    assert actual_exit_code == 0
