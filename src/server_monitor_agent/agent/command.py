import logging
from pathlib import Path

import click
from beartype.typing import Optional

import server_monitor_agent.agent.model
from server_monitor_agent.agent import (
    io as agent_io,
    model as agent_model,
    operation as agent_op,
    registry as agent_registry,
)

logger = logging.getLogger(agent_model.APP_NAME_UNDER)


@click.group(
    name=agent_model.APP_NAME_DASH,
    epilog="The config file provides defaults in a file that can be templated.",
    help="Utility to run checks on a server and send notifications. "
    "Choose a data collection source from the Commands.",
    context_settings={"show_default": True},
    # these settings allow for printing help and exiting with 1 if no subcommand
    no_args_is_help=False,
    invoke_without_command=True,
)
@click.option(
    "--debug/--no-debug",
    "debug",
    default=False,
    type=bool,
    help="Turn on debug logging.",
)
@click.option(
    "-c",
    "--config",
    "config_file",
    type=click.Path(),
    help="Provide a config file.",
)
@click.version_option(version=agent_op.get_version())
@click.pass_context
def cli(
    ctx: click.Context,
    debug: bool,
    config_file: Optional[Path] = None,
):
    ctx.obj = server_monitor_agent.agent.model.CliArgs(
        debug=debug, config_file=config_file
    )

    # set the logger level from the cli parameter
    if debug:
        logger.setLevel(logging.DEBUG)

    agent_io.check_collect_context(ctx)

    # load the config file and set as the defaults
    if ctx.obj.config_file:
        config = agent_op.read_config(ctx.obj.config_file)
        ctx.default_map = {**ctx.default_map, **config}


# gather and register cli commands
cmd_reg = agent_registry.CommandRegistry()
cmd_reg.gather()
cmd_reg.run(cli)
