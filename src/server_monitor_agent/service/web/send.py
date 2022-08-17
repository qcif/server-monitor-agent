import click
from beartype import typing

from server_monitor_agent.agent import io as agent_io, model as agent_model
from server_monitor_agent.service.web import model as web_model


@click.command(
    name="email-message",
    epilog="",
    help="Send an email.",
    short_help="Send an email.",
)
@click.option(
    "-h",
    "--host",
    "host",
    required=True,
    help="The email server host.",
)
@click.option(
    "-p",
    "--port",
    "port",
    type=int,
    required=True,
    help="The email server port.",
)
@click.option(
    "-u",
    "--user",
    "username",
    required=True,
    help="The email username.",
)
@click.option(
    "-w",
    "--password",
    "password",
    required=True,
    help="The email password.",
)
@click.option(
    "-f",
    "--from",
    "from_address",
    required=True,
    help="The email address that sent the message.",
)
@click.option(
    "-t",
    "--to",
    "to_addresses",
    type=str,
    required=True,
    multiple=True,
    help="The email addresses that will receive the message.",
)
@click.pass_context
def email_message(
    ctx: click.Context,
    host: str,
    port: int,
    username: str,
    password: str,
    from_address: str,
    to_addresses: typing.Sequence[str],
):
    ctx.obj = web_model.EmailMessageSendArgs(
        host=host,
        port=port,
        username=username,
        password=password,
        from_address=from_address,
        to_addresses=to_addresses,
    )
    agent_io.check_send_context(ctx)
    agent_io.execute_context(ctx)


@click.command(
    name="slack-message",
    epilog="",
    help="Send a slack message.",
    short_help="Send a slack message.",
)
@click.option("-w", "--webhook", "webhook", required=True, help="The webhook url.")
@click.pass_context
def slack_message(ctx: click.Context, webhook: str):
    ctx.obj = web_model.SlackMessageSendArgs(webhook=webhook)
    agent_io.check_send_context(ctx)
    agent_io.execute_context(ctx)


register_commands = [
    agent_model.RegisterSendCmd(email_message),
    agent_model.RegisterSendCmd(slack_message),
]
