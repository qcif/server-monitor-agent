"""Commands for collecting details about a server instance."""

import click

from server_monitor_agent.agent import io as agent_io, model as agent_model
from server_monitor_agent.service.server import (
    model as server_model,
)


@click.group(
    name="cpu",
    epilog="Increase the interval for a more accurate measure, "
    "but it will take longer.",
    help="Get the overall CPU usage for this device. "
    + agent_model.TEXT_CHOOSE_NOTIFICATION,
    short_help="Get the overall CPU usage.",
    no_args_is_help=False,
    invoke_without_command=True,
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
    ctx.obj = server_model.CpuCollectArgs(threshold=threshold, interval=interval)
    agent_io.check_collect_context(ctx)


@click.group(
    name="memory",
    epilog="Note the difference between 'free' (unused memory) and "
    "'available' (used but can be re-used if required).",
    help="Get the memory usage for this device. "
    + agent_model.TEXT_CHOOSE_NOTIFICATION,
    short_help="Get the memory usage.",
    no_args_is_help=False,
    invoke_without_command=True,
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
    ctx.obj = server_model.MemoryCollectArgs(threshold=threshold)
    agent_io.check_collect_context(ctx)


@click.group(
    name="stream-input",
    epilog="",
    help="Read input from the given stream. " + agent_model.TEXT_CHOOSE_NOTIFICATION,
    short_help="Read input from a stream.",
    no_args_is_help=False,
    invoke_without_command=True,
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
    type=click.Choice(agent_model.FORMATS_IN, case_sensitive=False),
    help="Set the input format.",
)
@click.pass_context
def stream_input(ctx: click.Context, source: str, in_format: str):
    """Read input from a stream."""
    ctx.obj = server_model.StreamInputCollectArgs(source=source, format=in_format)
    agent_io.check_collect_context(ctx)


# register send commands
register_commands = [
    agent_model.RegisterCollectCmd(cpu),
    agent_model.RegisterCollectCmd(memory),
    agent_model.RegisterCollectCmd(stream_input),
]
