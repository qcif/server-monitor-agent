"""Commands related to a server instance."""

import click

from server_monitor_agent.agent import (
    io as agent_io,
    model as agent_model,
)
from server_monitor_agent.server import model as server_model


@click.command(
    name="logged-in-users",
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
def logged_in_users(ctx: click.Context, user_group: str):
    """Send an alert to logged-in users."""
    ctx.obj = server_model.LoggedInUsersArgs(user_group=user_group)
    agent_io.check_send_context(ctx)
    agent_io.execute_context(ctx)


@click.command(
    name="stream-output",
    help="Send an alert to all users logged in to a server instance.",
    short_help="Send an alert to logged-in users.",
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
    type=click.Choice(agent_model.OUT_FORMATS, case_sensitive=False),
    help="Set the output format.",
)
@click.pass_context
def stream_output(ctx: click.Context, target: str, out_format: str):
    ctx.obj = server_model.StreamOutputArgs(target=target, format=out_format)
    agent_io.check_send_context(ctx)
    agent_io.execute_context(ctx)
