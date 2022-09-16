import click
from click import Context

from server_monitor_agent.agent import io as agent_io, model as agent_model
from server_monitor_agent.service.statuscake import model as sc_model


@click.group(
    name="statuscake",
    epilog="",
    help="Collect information required for the statuscake agent. "
    + agent_model.TEXT_CHOOSE_NOTIFICATION,
    short_help="Collect data for the statuscake agent.",
    no_args_is_help=False,
    invoke_without_command=True,
)
@click.option(
    "-i",
    "--interval",
    "interval",
    default=2.0,
    type=float,
    help="Sample the CPU usage over this time in seconds.",
)
@click.pass_context
def statuscake(ctx: Context, interval: float):
    ctx.obj = sc_model.StatusCakeCollectArgs(interval=interval)
    agent_io.check_collect_context(ctx)


# register send commands
register_commands = [
    agent_model.RegisterCollectCmd(statuscake),
]
