import pathlib

import pytest
from click.testing import CliRunner

from server_monitor_agent.agent.command import cli


@pytest.mark.parametrize("collect_arg", ["statuscake"])
@pytest.mark.parametrize(
    "send_arg",
    ["alert-manager", "file-output", "logged-in-users", "stream-output", "statuscake"],
)
def test_status_cake_module(tmp_path, collect_arg, send_arg):
    runner = CliRunner(mix_stderr=False)

    with runner.isolated_filesystem(temp_dir=tmp_path) as d:
        temp_dir = pathlib.Path(d)
        collect_available = {
            "statuscake": [],
        }
        collect_args = [collect_arg, *collect_available[collect_arg]]

        send_available = {
            "alert-manager": [],
            "file-output": ["-p", temp_dir / "test-file-output.txt"],
            "logged-in-users": ["-g", "testers"],
            "stream-output": [],
            "statuscake": [],
        }
        send_args = [send_arg, *send_available[send_arg]]

        result = runner.invoke(cli, [*collect_args, *send_args], catch_exceptions=False)

    assert result.stdout == ""
    assert result.stderr == ""
    assert result.exit_code == 0
