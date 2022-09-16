import json
import pathlib
from unittest.mock import call

import pytest
from click.testing import CliRunner

from conftest import svmem
from tests.data import expected_commands as ex_cmd
from tests.helpers import execute_process_side_effect


@pytest.mark.parametrize("collect_cmd,send_cmd", ex_cmd.expected_items["pairs"])
def test_cli_commands(tmp_path, collect_cmd, send_cmd, capsys, mocker, requests_mock):
    execute_process_mock = mocker.patch(
        "server_monitor_agent.agent.operation.execute_process", spec=True
    )
    execute_process_mock.side_effect = execute_process_side_effect

    smtp_mock = mocker.patch("smtplib.SMTP_SSL", autospec=True)

    socket_fqdn_mock = mocker.patch("socket.getfqdn", spec=True)
    socket_fqdn_mock.return_value = "test-instance.example.com"

    platform_node_mock = mocker.patch("platform.node", spec=True)

    pu_cpu_percent_mock = mocker.patch("psutil.cpu_percent", spec=True)
    pu_disk_partitions_mock = mocker.patch("psutil.disk_partitions", spec=True)
    pu_disk_usage_mock = mocker.patch("psutil.disk_usage", spec=True)
    pu_process_iter_mock = mocker.patch("psutil.process_iter", spec=True)
    pu_boot_time_mock = mocker.patch("psutil.boot_time", spec=True)

    pu_virtual_memory_mock = mocker.patch("psutil.virtual_memory", spec=True)

    def pu_virtual_memory_mock_side_effect(*args, **kwargs):
        return svmem(
            total=10367352832,
            available=6472179712,
            percent=37.6,
            used=8186245120,
            free=2181107712,
            active=4748992512,
            inactive=2758115328,
            buffers=790724608,
            cached=3500347392,
            shared=787554304,
            slab=199348224,
        )

    pu_virtual_memory_mock.side_effect = pu_virtual_memory_mock_side_effect

    pu_net_io_counters_mock = mocker.patch("psutil.net_io_counters", spec=True)

    mocks = {
        "execute_process": {
            "mock": execute_process_mock,
            "expected": [call(["timedatectl", "show"])],
        },
        "smtp": {"mock": smtp_mock, "expected": []},
        "socket_fqdn": {"mock": socket_fqdn_mock, "expected": [call()]},
        "platform_node": {"mock": platform_node_mock, "expected": []},
        "pu_cpu_percent": {"mock": pu_cpu_percent_mock, "expected": []},
        "pu_disk_partitions": {"mock": pu_disk_partitions_mock, "expected": []},
        "pu_disk_usage": {"mock": pu_disk_usage_mock, "expected": []},
        "pu_process_iter": {"mock": pu_process_iter_mock, "expected": []},
        "pu_boot_time": {"mock": pu_boot_time_mock, "expected": []},
        "pu_virtual_memory": {"mock": pu_virtual_memory_mock, "expected": []},
        "pu_net_io_counters": {"mock": pu_net_io_counters_mock, "expected": []},
    }

    from server_monitor_agent.agent import command as agent_command

    runner = CliRunner(mix_stderr=False)

    with runner.isolated_filesystem(temp_dir=tmp_path) as d:
        temp_dir = pathlib.Path(d)
        file_input_path = temp_dir / "file-input.txt"
        file_status_path = temp_dir / "file-status.txt"
        file_output_path = temp_dir / "file-output.txt"

        collect_available = {
            "file-input": ["-p", file_input_path],
            "file-status": ["-p", file_status_path],
            "consul-checks": ["-a", "http://localhost:8500", "-e" "false"],
            "docker-container": ["--name", "consul"],
            "systemd-unit-status": ["--name", "docker.service"],
            "systemd-unit-logs": ["--name", "docker.service"],
            "web-app": ["-u", "http://localhost:8080/web-app"],
        }
        collect_args = [collect_cmd, *collect_available.get(collect_cmd, [])]

        send_available = {
            "alert-manager": ["-u", "http://localhost:8080/alert-manager"],
            "file-output": ["-p", file_output_path],
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

        # mocking - collect
        if collect_cmd == "stream-input":
            # monkeypatch.setattr("sys.stdin", io.StringIO("{}"))
            pass

        if collect_cmd == "file-input":
            (temp_dir / "file-input.txt").touch(exist_ok=True)

        if collect_cmd == "web-app":
            requests_mock.get("http://localhost:8080/web-app")

        if collect_cmd == "consul-checks":
            requests_mock.get("http://localhost:8500/v1/health/state/any")

        # mocking - send
        if send_cmd == "slack-message":
            requests_mock.post("http://localhost:8080/slack-webhook")

        if send_cmd == "logged-in-users":
            mocks["execute_process"]["expected"].append(
                call(["wall", "--timeout", "30", "--group", "testers", "__MATCH_ANY__"])
            )

        result = runner.invoke(
            agent_command.cli, [*collect_args, *send_args], catch_exceptions=False
        )

        # check mocks
        for name, data in mocks.items():
            m = data["mock"]
            expected = data["expected"]

            if len(expected) < 1:
                m.assert_not_called()
            else:
                assert m.call_count == len(expected)

            m.assert_has_calls(expected)

        if collect_cmd == "file-status" and send_cmd == "stream-output":
            actual = json.loads(result.stdout)
            expected = {
                "summary": "Unexpected file " + str(file_status_path) + " state",
                "description": "Unexpected file " + str(file_status_path) + " state. "
                "Could not find file in expected path.  "
                "Check instance for excessive log files or increased application storage use.",
                "host_name": "test-instance.example.com",
                "source_name": "server",
                "check_name": "file",
                "status_name": "critical",
                "service_name": str(file_status_path),
                "extra_data": {"exists": False, "expected_state": "present"},
            }
            assert actual.get("date")
            del actual["date"]
            assert actual == expected

        else:
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
