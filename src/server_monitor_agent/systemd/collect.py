import click
from click import Context

from server_monitor_agent.agent import io as agent_io
from server_monitor_agent.alert_manager import send as alert_manager_send
from server_monitor_agent.disk import send as disk_send
from server_monitor_agent.server import send as server_send
from server_monitor_agent.systemd import model as systemd_model


@click.group(name="systemd-unit-status")
@click.option("-n", "--name", "name", required=True, type=str)
@click.pass_context
def systemd_unit_status(ctx: Context, name: str):
    ctx.obj = systemd_model.SystemdUnitStatusArgs(name=name)
    agent_io.check_collect_context(ctx)


@click.group(name="systemd-unit-logs")
@click.option("-n", "--name", "name", required=True, type=str)
@click.pass_context
def systemd_unit_logs(ctx: Context, name: str):
    ctx.obj = systemd_model.SystemdUnitLogsArgs(name=name)
    agent_io.check_collect_context(ctx)


# register send commands
collect_commands = [systemd_unit_status, systemd_unit_logs]
send_commands = [
    server_send.stream_output,
    server_send.logged_in_users,
    disk_send.file_output,
    alert_manager_send.alert_manager,
]
for collect_command in collect_commands:
    for send_command in send_commands:
        collect_command.add_command(send_command)
