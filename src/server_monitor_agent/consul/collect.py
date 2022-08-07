import click

from server_monitor_agent.agent import io as agent_io
from server_monitor_agent.alert_manager import send as alert_manager_send
from server_monitor_agent.consul import model as consul_model
from server_monitor_agent.disk import send as disk_send
from server_monitor_agent.server import send as server_send


@click.group(name="consul-checks")
@click.pass_context
def consul_checks(ctx: click.Context):
    ctx.obj = consul_model.HealthCheckCollectArg()
    agent_io.check_collect_context(ctx)


# register send commands
collect_commands = [consul_checks]
send_commands = [
    server_send.stream_output,
    server_send.logged_in_users,
    disk_send.file_output,
    alert_manager_send.alert_manager,
]
for collect_command in collect_commands:
    for send_command in send_commands:
        collect_command.add_command(send_command)
