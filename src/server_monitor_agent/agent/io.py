"""Input (parsing) and output (formatting) functions
for general use within the agent."""

import importlib
import logging

import beartype
import click

from server_monitor_agent.agent import model as agent_model, operation as agent_op


@beartype.beartype
def check_collect_context(ctx: click.Context):
    cub_cmd = ctx.invoked_subcommand
    if cub_cmd is None:
        click.echo(ctx.get_help(), err=True)
        ctx.exit(1)

    agent_op.log_msg(
        logging.DEBUG, f"Running collect {ctx.command.name} with {cub_cmd}"
    )
    agent_op.log_msg(logging.DEBUG, f"   Obj {ctx.obj}")


@beartype.beartype
def check_send_context(ctx: click.Context):
    agent_op.log_msg(logging.DEBUG, f"Running send {ctx.command.name}")
    agent_op.log_msg(logging.DEBUG, f"   Obj {ctx.obj}")
    pass


@beartype.beartype
def execute_context(send_ctx: click.Context):
    send_args = send_ctx.obj

    collect_ctx = send_ctx.parent
    collect_args = collect_ctx.obj

    cli_ctx = collect_ctx.parent
    cli_args = cli_ctx.obj

    execute_args(collect_args, send_args)


@beartype.beartype
def execute_args(
    collect_args: agent_model.CollectArgs, send_args: agent_model.SendArgs
):
    app = agent_model.APP_NAME_UNDER
    # e.g.
    # 1) mod: consul.io prefix: check_status suffix: stream
    #    full: consul.io.collect_check_status_send_stream
    # 2) mod: server.io prefix: stream suffix: alert_manager
    #    full: server.io.collect_stream_send_alert_manager
    mod_name = f"{app}.{collect_args.io_module}.io"
    mod_inst = importlib.import_module(mod_name)

    func_name = f"collect_{collect_args.io_func_prefix}_send_{send_args.io_func_suffix}"
    func_inst = getattr(mod_inst, func_name)

    return func_inst(collect_args, send_args)
