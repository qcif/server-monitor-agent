import pathlib

import click
from beartype import typing

from server_monitor_agent.agent import io as agent_io, model as agent_model
from server_monitor_agent.service.consul import model as consul_model


@click.group(
    name="consul-checks",
    epilog="",
    help="Get a summary of the status of all consul checks.",
    short_help="Get a summary of consul check statuses.",
    no_args_is_help=False,
    invoke_without_command=True,
)
@click.option(
    "-a",
    "--http-addr",
    "http_addr",
    type=str,
    required=True,
    help="The consul http api base url.",
)
@click.option(
    "-e",
    "--http-ssl-enabled",
    "http_ssl_enabled",
    type=bool,
    default=True,
    help="Whether the consul http api requires SSL.",
)
@click.option(
    "-v",
    "--http-ssl-verify",
    "http_ssl_verify",
    type=bool,
    default=True,
    help="Whether the consul http api should verify the SSL certificate.",
)
@click.option(
    "-f",
    "--ca-cert-file",
    "ca_cert_file",
    type=click.Path(file_okay=True, dir_okay=False, path_type=pathlib.Path),
    help="Path the CA cert file.",
)
@click.option(
    "-d",
    "--ca-cert-dir",
    "ca_cert_dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=pathlib.Path),
    help="Path the CA cert dir.",
)
@click.option(
    "-c",
    "--client-cert-file",
    "client_cert",
    type=click.Path(file_okay=True, dir_okay=False, path_type=pathlib.Path),
    help="Path the client cert file.",
)
@click.option(
    "-k",
    "--client-key-file",
    "client_key",
    type=click.Path(file_okay=True, dir_okay=False, path_type=pathlib.Path),
    help="Path the client key file.",
)
@click.pass_context
def consul_checks(
    ctx: click.Context,
    http_addr: str,
    http_ssl_enabled: bool,
    http_ssl_verify: bool,
    ca_cert_file: typing.Optional[pathlib.Path],
    ca_cert_dir: typing.Optional[pathlib.Path],
    client_cert: typing.Optional[pathlib.Path],
    client_key: typing.Optional[pathlib.Path],
):
    ctx.obj = consul_model.HealthCheckCollectArgs(
        http_addr=http_addr,
        http_ssl_enabled=http_ssl_enabled,
        http_ssl_verify=http_ssl_verify,
        ca_cert_file=ca_cert_file,
        ca_cert_dir=ca_cert_dir,
        client_cert=client_cert,
        client_key=client_key,
    )
    agent_io.check_collect_context(ctx)


register_commands = [
    agent_model.RegisterCollectCmd(consul_checks),
]
