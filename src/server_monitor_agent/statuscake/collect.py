import click
from click import Context

from server_monitor_agent.agent import io as agent_io, model as agent_model
from server_monitor_agent.alert_manager import send as alert_send
from server_monitor_agent.disk import send as disk_send
from server_monitor_agent.server import send as server_send
from server_monitor_agent.statuscake import model as sc_model, send as sc_send


@click.group(
    name="statuscake",
    epilog="",
    help="Collect information required for the statuscake agent. "
    + agent_model.TEXT_CHOOSE_NOTIFICATION,
    short_help="",
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
collect_commands = [statuscake]
send_commands = [
    server_send.stream_output,
    server_send.logged_in_users,
    disk_send.file_output,
    alert_send.alert_manager,
    sc_send.statuscake,
]
for collect_command in collect_commands:
    for send_command in send_commands:
        collect_command.add_command(send_command)
