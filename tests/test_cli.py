import io
import pathlib

import pytest
from click.testing import CliRunner

from server_monitor_agent.agent.command import cli
from tests.data import expected_commands as ex_cmd


@pytest.mark.parametrize("collect_cmd,send_cmd", ex_cmd.expected_items["pairs"])
def test_cli_commands(
    tmp_path, collect_cmd, send_cmd, monkeypatch, execute_process_setup
):
    runner = CliRunner(mix_stderr=False)

    with runner.isolated_filesystem(temp_dir=tmp_path) as d:
        temp_dir = pathlib.Path(d)

        collect_available = {
            "file-input": ["-p", temp_dir / "file-input.txt"],
            "file-status": ["-p", temp_dir / "file-status.txt"],
            "consul-checks": ["-a", "http://localhost:8500", "-e" "false"],
            "docker-container": ["--name", "consul"],
            "systemd-unit-status": ["--name", "docker.service"],
            "systemd-unit-logs": ["--name", "docker.service"],
            "web-app": ["-u", "http://localhost:8080/web-app"],
        }
        collect_args = [collect_cmd, *collect_available.get(collect_cmd, [])]

        send_available = {
            "alert-manager": ["-u", "http://localhost:8080/alert-manager"],
            "file-output": ["-p", temp_dir / "test-file-output.txt"],
            "logged-in-users": ["-g", "testers"],
            "slack-message": ["-w", "http://localhost:8080/slack-webhook"],
            "email-message": [
                "-h",
                "localhost",
                "-p",
                587,
                "-u",
                "user",
                "-w",
                "pass",
                "-f",
                "sender@example.com",
                "-t",
                "to1@example.com",
                "-t",
                "to2@example.com",
            ],
        }
        send_args = [send_cmd, *send_available.get(send_cmd, [])]

        # mocking
        if collect_cmd == "stream-input":
            monkeypatch.setattr("sys.stdin", io.StringIO("{}"))

        result = runner.invoke(cli, [*collect_args, *send_args], catch_exceptions=False)

    assert result.stdout == ""
    assert result.stderr == ""
    assert result.exit_code == 0


# for smtp:
# https://stackoverflow.com/questions/63754359/correct-way-to-mock-patch-smtplib-smtp
# import unittest.mock
# with unittest.mock.patch('smtplib.SMTP', autospec=True) as mock:
#     import smtplib
#     smtp = smtplib.SMTP('localhost')
#     smtp.sendmail('me', 'you', 'hello world\n')
#
#     # Validate sendmail() was called
#     name, args, kwargs = smtpmock.method_calls.pop(0)
#     self.assertEqual(name, '().sendmail')
#     self.assertEqual({}, kwargs)
#
#     # Validate the sendmail() parameters
#     from_, to_, body_ = args
#     self.assertEqual('me', from_)
#     self.assertEqual(['you'], to_)
#     self.assertIn('hello world', body_)
