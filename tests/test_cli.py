import pathlib

import pytest
from click.testing import CliRunner

import data.expected_commands
from server_monitor_agent.agent.command import cli


@pytest.mark.parametrize(
    "collect_cmd,send_cmd", data.expected_commands.expected_items["pairs"]
)
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
        }
        send_args = [send_cmd, *send_available.get(send_cmd, [])]

        result = runner.invoke(cli, [*collect_args, *send_args], catch_exceptions=False)

    assert result.stdout == ""
    assert result.stderr == ""
    assert result.exit_code == 0
