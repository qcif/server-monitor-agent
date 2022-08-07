import click
from click import Context

from server_monitor_agent.agent import io as agent_io
from server_monitor_agent.alert_manager import send as alert_send
from server_monitor_agent.disk import send as disk_send
from server_monitor_agent.server import send as server_send
from server_monitor_agent.web import model as web_model


@click.group(name="web-app")
@click.pass_context
def web_app_status(ctx: Context):
    ctx.obj = web_model.WebAppStatusArgs(request=None, response=None)
    agent_io.check_collect_context(ctx)


# register send commands
collect_commands = [web_app_status]
send_commands = [
    server_send.stream_output,
    server_send.logged_in_users,
    disk_send.file_output,
    alert_send.alert_manager,
]
for collect_command in collect_commands:
    for send_command in send_commands:
        collect_command.add_command(send_command)
