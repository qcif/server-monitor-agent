import logging

import click

from server_monitor_agent.agent import io as agent_io, model as agent_model
from server_monitor_agent.statuscake import model as sc_model

logger = logging.getLogger(f"{agent_model.APP_NAME_UNDER}.statuscake.send")


@click.command(name="statuscake", help="", short_help="")
@click.pass_context
def statuscake(ctx: click.Context):
    """Send status cake sample."""
    ctx.obj = sc_model.StatusCakeSendArgs()
    agent_io.check_send_context(ctx)
    agent_io.execute_context(ctx)
