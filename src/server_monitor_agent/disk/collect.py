"""Commands for collecting information about disks and files."""

import pathlib
import typing
import uuid

import click

from server_monitor_agent.agent import io as agent_io, model as agent_model
from server_monitor_agent.alert_manager import send as alert_manager_send
from server_monitor_agent.disk import model as disk_model, send as disk_send
from server_monitor_agent.server import send as server_send


@click.group(
    name="disk",
    epilog="",
    help="Get information about disk usage.",
    short_help="Get disk usage.",
    no_args_is_help=False,
    invoke_without_command=True,
)
@click.option(
    "-t",
    "--threshold",
    "threshold",
    default=80,
    type=int,
    help="Usage over this threshold in percent is critical.",
)
@click.option("-p", "--path", "path", type=click.Path())
@click.option("-d", "--device", "device", type=click.Path())
@click.option("-u", "--uuid", "disk_uuid", type=click.UUID)
@click.option("-l", "--label", "label", type=str)
@click.pass_context
def disk(
    ctx: click.Context,
    threshold: int,
    path: typing.Optional[pathlib.Path],
    device: typing.Optional[pathlib.Path],
    disk_uuid: typing.Optional[uuid.UUID],
    label: typing.Optional[str],
):
    """Get the memory usage for this device."""

    ctx.obj = disk_model.DiskCollectArgs(
        threshold=threshold, path=path, device=device, disk_uuid=disk_uuid, label=label
    )
    agent_io.check_collect_context(ctx)


@click.group(
    name="file-status",
    epilog="",
    help="Get information about disk usage.",
    short_help="Get disk usage.",
    no_args_is_help=False,
    invoke_without_command=True,
)
@click.option(
    "-p",
    "--path",
    "path",
    required=True,
    type=click.Path(),
    help="Path to the file to check.",
)
@click.option(
    "-s",
    "--state",
    "state",
    default="present",
    type=click.Choice(["present", "absent"]),
)
@click.option("-c", "--compare", "compare", multiple=True, type=(str, str))
@click.pass_context
def file_status(
    ctx: click.Context,
    path: typing.Optional[pathlib.Path],
    state: str,
    compare: typing.List[typing.Tuple[str, str]],
):
    """Write the current status of a file to the given output."""

    content = [
        agent_model.TextCompareEntry(comparison=c, value=v) for c, v in (compare or [])
    ]
    ctx.obj = disk_model.FileStatusArgs(path=path, state=state, content=content)
    agent_io.check_collect_context(ctx)


@click.group(
    name="file-input",
    epilog="",
    help="Get information about disk usage.",
    short_help="Get disk usage.",
    no_args_is_help=False,
    invoke_without_command=True,
)
@click.option(
    "-p",
    "--path",
    "path",
    required=True,
    type=click.Path(),
    help="Path to the input file.",
)
@click.option(
    "-f",
    "--format",
    "file_format",
    default=agent_model.FORMAT_AGENT,
    type=click.Choice(agent_model.IN_FORMATS, case_sensitive=False),
    help="Set the input format.",
)
@click.pass_context
def file_input(
    ctx: click.Context, path: typing.Optional[pathlib.Path], file_format: str
):
    ctx.obj = disk_model.FileInputArgs(path=path, format=file_format)
    agent_io.check_collect_context(ctx)


# register send commands
collect_commands = [disk, file_status, file_input]
send_commands = [
    server_send.stream_output,
    server_send.logged_in_users,
    disk_send.file_output,
    alert_manager_send.alert_manager,
]
for collect_command in collect_commands:
    for send_command in send_commands:
        collect_command.add_command(send_command)
