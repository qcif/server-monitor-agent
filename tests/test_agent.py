import inspect

from click.testing import CliRunner

from server_monitor_agent.agent import (
    command as agent_command,
    registry as agent_registry,
)
from tests.data import expected_commands as ex_cmd


def test_main(tmp_path):
    runner = CliRunner(mix_stderr=False)
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(agent_command.cli)

    assert result.exit_code == 1
    assert result.stdout == ""
    assert (
        result.stderr
        == """Usage: server-monitor-agent [OPTIONS] COMMAND [ARGS]...

  Utility to run checks on a server and send notifications. Choose a data
  collection source from the Commands.

Options:
  --debug / --no-debug  Turn on debug logging.  [default: no-debug]
  -c, --config PATH     Provide a config file.
  --version             Show the version and exit.
  --help                Show this message and exit.

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


def test_gather_commands():
    expected_collect = ex_cmd.expected_items["collect"]
    expected_collect_cmds = [i["command"] for i in expected_collect]

    expected_send = ex_cmd.expected_items["send"]
    expected_send_cmds = [i["command"] for i in expected_send]

    reg = agent_registry.CommandRegistry()
    reg.gather()

    collect_commands = reg.collect_commands
    assert len(collect_commands) == len(expected_collect)

    for i in collect_commands:
        assert i.group.name in expected_collect_cmds

    send_commands = reg.send_commands
    assert len(send_commands) == len(expected_send)

    for i in send_commands:
        assert i.command.name in expected_send_cmds


def test_gather_io():
    expected_collect = ex_cmd.expected_items["collect"]
    expected_collect_args = [i["args"] for i in expected_collect]

    expected_send = ex_cmd.expected_items["send"]
    expected_send_args = [i["args"] for i in expected_send]

    reg = agent_registry.SourceTargetIORegistry()
    reg.gather()

    collect_items = reg.collect_inputs
    assert len(collect_items) == len(expected_collect)

    for i in collect_items:
        item_inspect = inspect.signature(i.func)
        item_arg_type = item_inspect.parameters["args"].annotation
        assert item_arg_type.__name__ in expected_collect_args

    send_items = reg.send_outputs
    assert len(send_items) == len(expected_send)

    for i in send_items:
        item_inspect = inspect.signature(i.func)
        item_arg_type = item_inspect.parameters["args"].annotation
        assert item_arg_type.__name__ in expected_send_args


def test_command_links():
    actual = []
    for group_name, group_data in agent_command.cli.commands.items():
        for cmd_name, cmd_data in group_data.commands.items():
            actual.append((group_name, cmd_name))

    expected = ex_cmd.expected_items["pairs"]
    for i in expected:
        assert i in actual

    assert len(actual) == len(expected)
    assert sorted(actual) == sorted(expected)
