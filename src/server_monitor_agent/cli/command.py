import logging
from pathlib import Path
from typing import Optional

import click

from server_monitor_agent.agent import (
    io as agent_io,
    model as agent_model,
    operation as agent_op,
)
from server_monitor_agent.cli import model as cli_model
from server_monitor_agent.consul import collect as consul_collect
from server_monitor_agent.disk import collect as disk_collect
from server_monitor_agent.docker import collect as docker_collect
from server_monitor_agent.server import collect as server_collect
from server_monitor_agent.statuscake import collect as sc_collect
from server_monitor_agent.systemd import collect as systemd_collect
from server_monitor_agent.web import collect as web_collect

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
    "-l",
    "--log-level",
    "log_level",
    default=cli_model.LOG_LEVEL_INFO,
    type=click.Choice(cli_model.LOG_LEVELS, case_sensitive=False),
    help="Set the log level.",
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
    log_level: str,
    config_file: Optional[Path] = None,
):
    ctx.obj = cli_model.CliArgs(
        log_level=log_level,
        config_file=config_file,
    )

    # set the logger level from the cli parameter
    logger.setLevel(cli_model.LOG_ITEMS[ctx.obj.log_level])

    agent_io.check_collect_context(ctx)

    # load the config file and set as the defaults
    if ctx.obj.config_file:
        config = agent_op.read_config(ctx.obj.config_file)
        ctx.default_map = {**ctx.default_map, **config}


# register collect commands
collect_commands = [
    consul_collect.consul_checks,
    disk_collect.disk,
    disk_collect.file_status,
    disk_collect.file_input,
    docker_collect.docker_container_status,
    server_collect.cpu,
    server_collect.memory,
    server_collect.stream_input,
    sc_collect.statuscake,
    systemd_collect.systemd_unit_status,
    systemd_collect.systemd_unit_logs,
    web_collect.web_app_status,
]
for collect_command in collect_commands:
    cli.add_command(collect_command)
