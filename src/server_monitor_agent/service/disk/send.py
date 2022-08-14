"""Commands related to disks and files."""

import pathlib

import click
from beartype import typing

from server_monitor_agent.agent import io as agent_io, model as agent_model
from server_monitor_agent.service.disk import model as disk_model


@click.command(
    name="file-output",
    epilog="",
    help="Write the output to a file in the given format.",
    short_help="Write to a file.",
)
@click.option(
    "-p",
    "--path",
    "path",
    required=True,
    type=click.Path(),
    help="Path to the output file.",
)
@click.option(
    "-f",
    "--format",
    "out_format",
    default=agent_model.FORMAT_AGENT,
    type=click.Choice(agent_model.FORMATS_OUT, case_sensitive=False),
    help="Set the output format.",
)
@click.pass_context
def file_output(
    ctx: click.Context, path: typing.Optional[pathlib.Path], out_format: str
):
    """Write to a file."""
    ctx.obj = disk_model.FileOutputSendArgs(path=path, format=out_format)
    agent_io.check_send_context(ctx)
    agent_io.execute_context(ctx)


register_commands = [
    agent_model.RegisterSendCmd(file_output),
]
