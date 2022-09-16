"""Input (parsing) and output (formatting) functions
for general use within the agent."""

import logging

import beartype
import click

from server_monitor_agent.agent import (
    model as agent_model,
    operation as agent_op,
    registry as agent_reg,
)


@beartype.beartype
def check_collect_context(ctx: click.Context) -> None:
    cub_cmd = ctx.invoked_subcommand
    if cub_cmd is None:
        click.echo(ctx.get_help(), err=True)
        ctx.exit(1)

    agent_op.log_msg(
        logging.DEBUG, f"Running collect {ctx.command.name} with {cub_cmd}"
    )
    agent_op.log_msg(logging.DEBUG, f"   Obj {ctx.obj}")


@beartype.beartype
def check_send_context(ctx: click.Context) -> None:
    agent_op.log_msg(logging.DEBUG, f"Running send {ctx.command.name}")
    agent_op.log_msg(logging.DEBUG, f"   Obj {ctx.obj}")


@beartype.beartype
def execute_context(send_ctx: click.Context) -> None:
    send_args = send_ctx.obj
    collect_ctx = send_ctx.parent
    collect_args = collect_ctx.obj
    execute_args(collect_args, send_args)


@beartype.beartype
def execute_args(
    collect_args: agent_model.CollectArgs, send_args: agent_model.SendArgs
) -> None:
    io_reg = agent_reg.SourceTargetIORegistry()
    io_reg.gather()
    io_reg.run(collect_args, send_args)
