"""Commands related to a server instance."""

import click

from server_monitor_agent.agent import (
    io as agent_io,
    model as agent_model,
)
from server_monitor_agent.service.server import model as server_model


@click.command(
    name="logged-in-users",
    epilog="",
    help="Send an alert to all users logged in to a server instance.",
    short_help="Send an alert to logged-in users.",
)
@click.option(
    "-g",
    "--user-group",
    "user_group",
    required=True,
    type=str,
)
@click.pass_context
def users_message_output(ctx: click.Context, user_group: str):
    """Send an alert to logged-in users."""
    ctx.obj = server_model.LoggedInUsersSendArgs(user_group=user_group)
    agent_io.check_send_context(ctx)
    agent_io.execute_context(ctx)


@click.command(
    name="stream-output",
    epilog="",
    help="Print a notification to an output stream.",
    short_help="Print to an output stream.",
)
@click.option(
    "-t",
    "--target",
    "target",
    default=agent_model.STREAM_STDOUT,
    type=click.Choice(agent_model.STREAM_TARGETS),
    help="Set the output target.",
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
def stream_output(ctx: click.Context, target: str, out_format: str):
    ctx.obj = server_model.StreamOutputSendArgs(target=target, format=out_format)
    agent_io.check_send_context(ctx)
    agent_io.execute_context(ctx)


register_commands = [
    agent_model.RegisterSendCmd(users_message_output),
    agent_model.RegisterSendCmd(stream_output),
]
