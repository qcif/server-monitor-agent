import pathlib

import pytest
from click.testing import CliRunner

from server_monitor_agent.cli.command import cli


@pytest.mark.parametrize("collect_arg", ["disk", "file-status", "file-input"])
@pytest.mark.parametrize(
    "send_arg", ["alert-manager", "file-output", "logged-in-users", "stream-output"]
)
def test_disk_module(
    tmp_path,
    collect_arg,
    send_arg,
    monkeypatch,
    execute_process_setup,
    execute_process_unknown,
    execute_process_timedatectl_show,
):
    runner = CliRunner(mix_stderr=False)

    execute_process_setup(
        [
            execute_process_timedatectl_show,
            execute_process_unknown,
        ]
    )

    with runner.isolated_filesystem(temp_dir=tmp_path) as d:
        temp_dir = pathlib.Path(d)
        collect_available = {
            "disk": ["--label", "test"],
            "file-status": ["--path", temp_dir / "test-file-status.txt"],
            "file-input": ["--path", temp_dir / "test-file-input.txt"],
        }
        collect_args = [collect_arg, *collect_available[collect_arg]]

        send_available = {
            "alert-manager": [],
            "file-output": ["-p", temp_dir / "test-file-output.txt"],
            "logged-in-users": ["-g", "testers"],
            "stream-output": [],
        }
        send_args = [send_arg, *send_available[send_arg]]

        with pytest.raises(NotImplementedError):
            result = runner.invoke(
                cli, [*collect_args, *send_args], catch_exceptions=False
            )

    # assert result.stdout == ""
    # assert result.stderr == ""
    # assert result.exit_code == 0
