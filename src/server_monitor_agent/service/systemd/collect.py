import click
from beartype import typing
from click import Context

from server_monitor_agent.agent import io as agent_io, model as agent_model
from server_monitor_agent.service.systemd import model as systemd_model


@click.group(
    name="systemd-unit-status",
    epilog="",
    help="Get the status of a systemd unit. " + agent_model.TEXT_CHOOSE_NOTIFICATION,
    short_help="",
    no_args_is_help=False,
    invoke_without_command=True,
)
@click.option("-n", "--name", "name", required=True, type=str)
@click.option(
    "-a",
    "--attributes",
    "attributes",
    type=(str, str, str),
    multiple=True,
    help="The expected attribute name, comparison, and value.",
)
@click.pass_context
def systemd_unit_status(
    ctx: Context, name: str, attributes: typing.List[typing.Tuple[str, str, str]]
):
    attrs = agent_model.NameValueComparisonsEntry.from_tuple_list(attributes)
    ctx.obj = systemd_model.SystemdUnitStatusCollectArgs(name=name, attributes=attrs)
    agent_io.check_collect_context(ctx)


@click.group(
    name="systemd-unit-logs",
    epilog="",
    help="Get the logs for a systemd unit. " + agent_model.TEXT_CHOOSE_NOTIFICATION,
    short_help="",
    no_args_is_help=False,
    invoke_without_command=True,
)
@click.option("-n", "--name", "name", required=True, type=str)
@click.pass_context
def systemd_unit_logs(ctx: Context, name: str):
    ctx.obj = systemd_model.SystemdUnitLogsCollectArgs(name=name)
    agent_io.check_collect_context(ctx)


# register send commands
register_commands = [
    agent_model.RegisterCollectCmd(systemd_unit_status),
    agent_model.RegisterCollectCmd(systemd_unit_logs),
]
