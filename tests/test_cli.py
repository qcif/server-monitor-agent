from click.testing import CliRunner

from server_monitor_agent.agent.command import cli


def test_cli(tmp_path):
    runner = CliRunner(mix_stderr=False)
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli)

    assert result.exit_code == 1
    assert result.stdout == ""
    assert (
        result.stderr
        == """Usage: server-monitor-agent [OPTIONS] COMMAND [ARGS]...

  Utility to run checks on a server and send notifications. Choose a data
  collection source from the Commands.

Options:
  -l, --log-level [critical|error|warning|info|debug]
                                  Set the log level.  [default: info]
  -c, --config PATH               Provide a config file.
  --version                       Show the version and exit.
  --help                          Show this message and exit.

Commands:
  consul-checks        Get a summary of consul check statuses.
  cpu                  Get the overall CPU usage.
  disk                 Get disk usage.
  docker-container     Get docker container status.
  file-input           Load input from a file.
  file-status          Get information about a file.
  memory               Get the memory usage.
  statuscake           Collect information required for the statuscake agent.
  stream-input         Read input from a stream.
  systemd-unit-logs    Get the logs for a systemd unit.
  systemd-unit-status  Get the status of a systemd unit.
  web-app              Check the response to a url request.

  The config file provides defaults in a file that can be templated.
"""
    )
