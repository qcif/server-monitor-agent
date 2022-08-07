from click.testing import CliRunner

from server_monitor_agent.cli.command import cli


def test_cli(tmp_path):
    runner = CliRunner(mix_stderr=False)
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli)

    assert result.exit_code == 1
    assert result.stdout == ""
    assert (
        result.stderr
        == """Usage: server-monitor-agent [OPTIONS] COMMAND [ARGS]...

  Utility to run checks on a server and send notifications.

Options:
  -l, --log-level [critical|error|warning|info|debug]
                                  Set the log level.  [default: info]
  -c, --config PATH               Provide a config file.
  --version                       Show the version and exit.
  --help                          Show this message and exit.

Commands:
  consul-checks
  cpu                  Get the overall CPU usage.
  disk                 Get disk usage.
  docker-container     Get docker container status.
  file-input
  file-status          Write the current status of a file to the given output.
  memory               Get the memory usage.
  statuscake
  stream-input         Read input from a stream.
  systemd-unit-logs
  systemd-unit-status
  web-app

  The config file provides defaults in a file that can be templated.
"""
    )
