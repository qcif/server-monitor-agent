import click

from server_monitor_agent.agent import io as agent_io
from server_monitor_agent.alert_manager import model as alert_model


@click.command(
    name="alert-manager",
    epilog="",
    help="Let Alert Manager know to send out a notification.",
    short_help="Send a notification using Alert manager.",
)
@click.pass_context
def alert_manager(ctx: click.Context):
    ctx.obj = alert_model.AlertManagerArgs()
    agent_io.check_send_context(ctx)
    agent_io.execute_context(ctx)
