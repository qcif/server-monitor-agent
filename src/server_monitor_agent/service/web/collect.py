import click
from beartype import typing
from click import Context

from server_monitor_agent.agent import io as agent_io, model as agent_model
from server_monitor_agent.service.web import model as web_model


@click.group(
    name="web-app",
    epilog="",
    help="Check the response to a url request. " + agent_model.TEXT_CHOOSE_NOTIFICATION,
    short_help="",
    no_args_is_help=False,
    invoke_without_command=True,
)
@click.option(
    "-u",
    "--url",
    "url",
    type=str,
    required=True,
    help="The url to request.",
)
@click.option(
    "-m",
    "--method",
    "method",
    type=str,
    default="GET",
    help="The url request method.",
)
@click.option(
    "-h",
    "--headers",
    "headers",
    type=(str, str),
    multiple=True,
    help="The headers to include with the url request.",
)
@click.option(
    "-s",
    "--status",
    "status_code",
    type=int,
    default=200,
    help="The expected response status code.",
)
@click.option(
    "-r",
    "--response-headers",
    "response_headers",
    type=(str, str, str),
    multiple=True,
    help="The expected response header and comparison and value.",
)
@click.option(
    "-c",
    "--response-content",
    "response_content",
    type=(str, str),
    multiple=True,
    help="The expected response content comparison and value.",
)
@click.pass_context
def web_app_status(
    ctx: Context,
    url: str,
    method: str,
    headers: typing.Sequence[typing.Tuple[str, str]],
    status_code: int,
    response_headers: typing.Sequence[typing.Tuple[str, str, str]],
    response_content: typing.Sequence[typing.Tuple[str, str]],
):
    request = web_model.UrlRequestEntry(url=url, method=method, headers=dict(headers))

    resp_headers = agent_model.NameValueComparisonsEntry.from_tuple_list(
        response_headers
    )
    resp_content = agent_model.TextCompareEntry.from_tuple_list(response_content)

    response = web_model.UrlResponseEntry(
        status_code=status_code, headers=resp_headers, content=resp_content
    )

    ctx.obj = web_model.RequestUrlCollectArgs(request=request, response=response)
    agent_io.check_collect_context(ctx)


# register send commands
register_commands = [
    agent_model.RegisterCollectCmd(web_app_status),
]
