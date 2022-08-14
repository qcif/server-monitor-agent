import click

from server_monitor_agent.agent import io as agent_io, model as agent_model
from server_monitor_agent.service.statuscake import model as sc_model


@click.command(
    name="statuscake",
    epilog="",
    help="Send sample of server instance details to statuscake.",
    short_help="Send server details to statuscake.",
)
@click.pass_context
def statuscake(ctx: click.Context):
    """Send status cake sample."""
    ctx.obj = sc_model.StatusCakeSendArgs()
    agent_io.check_send_context(ctx)
    agent_io.execute_context(ctx)


register_commands = [
    agent_model.RegisterSendCmd(command=statuscake, collect_only=["statuscake"]),
]
