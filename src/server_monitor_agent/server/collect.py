"""Commands for collecting details about a server instance."""

import click

from server_monitor_agent.agent import io as agent_io, model as agent_model
from server_monitor_agent.alert_manager import send as alert_manager_send
from server_monitor_agent.disk import send as disk_send
from server_monitor_agent.server import model as server_model, send as server_send


@click.group(
    name="cpu",
    epilog="Increase the interval for a more accurate measure, "
    "but it will take longer.",
    help="Get the overall CPU usage for this device.",
    short_help="Get the overall CPU usage.",
)
@click.option(
    "-t",
    "--threshold",
    "threshold",
    default=80,
    type=int,
    help="Usage over this threshold in percent is critical.",
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
def cpu(ctx: click.Context, threshold: int, interval: float):
    """Get the overall CPU usage."""
    ctx.obj = server_model.CpuArgs(threshold=threshold, interval=interval)
    agent_io.check_collect_context(ctx)


@click.group(
    name="memory",
    epilog="Note the difference between 'free' (unused memory) and "
    "'available' (used but can be re-used if required).",
    help="Get the memory usage for this device.",
    short_help="Get the memory usage.",
)
@click.option(
    "-t",
    "--threshold",
    "threshold",
    default=80,
    type=int,
    help="Usage over this threshold in percent is critical.",
)
@click.pass_context
def memory(ctx: click.Context, threshold: int):
    """Get the memory usage."""
    ctx.obj = server_model.MemoryArgs(threshold=threshold)
    agent_io.check_collect_context(ctx)


@click.group(
    name="stream-input",
    epilog="",
    help="Read input from the given stream.",
    short_help="Read input from a stream.",
)
@click.option(
    "-s",
    "--source",
    "source",
    default=agent_model.STREAM_STDIN,
    type=click.Choice(agent_model.STREAM_SOURCES),
    help="Set the input source.",
)
@click.option(
    "-f",
    "--format",
    "in_format",
    default=agent_model.FORMAT_AGENT,
    type=click.Choice(agent_model.IN_FORMATS, case_sensitive=False),
    help="Set the input format.",
)
@click.pass_context
def stream_input(ctx: click.Context, source: str, in_format: str):
    """Read input from a stream."""
    ctx.obj = server_model.StreamInputArgs(source=source, format=in_format)
    agent_io.check_collect_context(ctx)


# register send commands
collect_commands = [cpu, memory, stream_input]
send_commands = [
    server_send.stream_output,
    server_send.logged_in_users,
    disk_send.file_output,
    alert_manager_send.alert_manager,
]
for collect_command in collect_commands:
    for send_command in send_commands:
        collect_command.add_command(send_command)
