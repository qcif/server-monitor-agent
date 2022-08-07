"""Commands for collecting information about docker."""

import click

from server_monitor_agent.agent import io as agent_io
from server_monitor_agent.alert_manager import send as alert_manager_send
from server_monitor_agent.disk import send as disk_send
from server_monitor_agent.docker import model as docker_model
from server_monitor_agent.server import send as server_send


@click.group(
    name="docker-container",
    epilog="",
    help="Get the status for a docker container.",
    short_help="Get docker container status.",
)
@click.option("-n", "--name", "name", required=True, type=str)
@click.option(
    "-s",
    "--state",
    "state",
    default="running",
    type=click.Choice(["running", "stopped"]),
)
@click.option(
    "-h",
    "--health",
    "health",
    default="healthy",
    type=click.Choice(["healthy", "unhealthy", "ignore"]),
)
@click.pass_context
def docker_container_status(ctx: click.Context, name: str, state: str, health: str):
    """Get docker container status."""
    ctx.obj = docker_model.DockerContainerStatusArgs(
        name=name,
        state=state,
        health=health,
    )
    agent_io.check_collect_context(ctx)


# register send commands
collect_commands = [docker_container_status]
send_commands = [
    server_send.stream_output,
    server_send.logged_in_users,
    disk_send.file_output,
    alert_manager_send.alert_manager,
]
for collect_command in collect_commands:
    for send_command in send_commands:
        collect_command.add_command(send_command)
