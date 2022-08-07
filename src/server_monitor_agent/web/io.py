import typing

import requests

from server_monitor_agent.agent import model as agent_model
from server_monitor_agent.server import model as server_model
from server_monitor_agent.web import model as web_model


def collect_web_send_alert_manager(
    collect_args: web_model.WebAppStatusArgs,
    send_args: server_model.StreamOutputArgs,
):
    raise NotImplementedError()


def collect_web_send_file_output(
    collect_args: web_model.WebAppStatusArgs,
    send_args: server_model.StreamOutputArgs,
):
    raise NotImplementedError()


def collect_web_send_logged_in_users(
    collect_args: web_model.WebAppStatusArgs,
    send_args: server_model.StreamOutputArgs,
):
    raise NotImplementedError()


def collect_web_send_stream_output(
    collect_args: web_model.WebAppStatusArgs,
    send_args: server_model.StreamOutputArgs,
):
    raise NotImplementedError()


def request_url(
    method: str,
    url: str,
    headers: typing.Dict[str, typing.Any],
    expected_status: int,
    expected_content: typing.List[agent_model.TextCompareEntry],
    expected_headers: typing.List[web_model.UrlHeadersEntry],
):
    """Request a url."""

    req = requests.request(method, url, headers=headers)
    headers = req.headers
    match_status = req.status_code == expected_status
    response_content = req.text

    match_content = []
    for expected_item in expected_content:
        match_content.append(
            {
                "value": expected_item.value,
                "comparison": expected_item.comparison,
                "outcome": expected_item.compare(response_content),
            }
        )

    match_headers = []
    for expected_header in expected_headers:
        for expected_item in expected_header.comparisons:
            value = headers.get(expected_header.name)
            match_headers.append(
                {
                    "header": expected_header.name,
                    "value": expected_item.value,
                    "comparison": expected_item.comparison,
                    "outcome": expected_item.compare(value),
                }
            )

    return web_model.UrlResponseResult(
        exit_code=req.status_code,
        match_status=match_status,
        match_content=match_content,
        match_headers=match_headers,
    )
