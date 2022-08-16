import click

from server_monitor_agent.agent import io as agent_io, model as agent_model
from server_monitor_agent.service.alert_manager import model as alert_model


@click.command(
    name="alert-manager",
    epilog="",
    help="Let Alert Manager know to send out a notification.",
    short_help="Send a notification using Alert manager.",
)
@click.option(
    "-u",
    "--base-url",
    "base_url",
    required=True,
    help="The base url for the alert manager.",
)
@click.pass_context
def alert_manager(ctx: click.Context, base_url: str):
    ctx.obj = alert_model.AlertManagerSendArgs(base_url=base_url)
    agent_io.check_send_context(ctx)
    agent_io.execute_context(ctx)


register_commands = [
    agent_model.RegisterSendCmd(alert_manager),
]
