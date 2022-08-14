"""Commands for collecting information about docker."""

import click

from server_monitor_agent.agent import io as agent_io, model as agent_model
from server_monitor_agent.service.docker import model as docker_model


@click.group(
    name="docker-container",
    epilog="",
    help="Get the status for a docker container."
    + agent_model.TEXT_CHOOSE_NOTIFICATION,
    short_help="Get docker container status.",
    no_args_is_help=False,
    invoke_without_command=True,
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
    ctx.obj = docker_model.ContainerStatusCollectArgs(
        name=name,
        state=state,
        health=health,
    )
    agent_io.check_collect_context(ctx)


# register send commands
register_commands = [
    agent_model.RegisterCollectCmd(docker_container_status),
]
