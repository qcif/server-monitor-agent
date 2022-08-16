import beartype
import requests

from server_monitor_agent.agent import model as agent_model
from server_monitor_agent.service.web import model as web_model, operation as web_op


@beartype.beartype
def email_message_output(
    args: web_model.EmailMessageSendArgs, item: agent_model.AgentItem
) -> None:
    subject = item.summary
    body_text = item.description
    body_html = item.description
    web_op.submit_email(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        subject=subject,
        from_address=args.from_address,
        to_addresses=args.to_addresses,
        body_text=body_text,
        body_html=body_html,
    )


@beartype.beartype
def slack_message_output(
    args: web_model.SlackMessageSendArgs, item: agent_model.AgentItem
) -> None:
    web_op.submit_slack_message(args.webhook, item)


@beartype.beartype
def request_url_input(args: web_model.RequestUrlCollectArgs) -> agent_model.AgentItem:
    """Request a url."""

    req = requests.request(
        method=args.request.method, url=args.request.url, headers=args.request.headers
    )
    headers = req.headers
    match_status = req.status_code == args.response.status_code
    response_content = req.text

    match_content = []
    for expected_item in args.response.content:
        match_content.append(expected_item.compare(response_content))

    match_headers = []
    for expected_header in args.response.headers:
        value = headers.get(expected_header.name)
        match_headers.extend(expected_header.compare(value))

    return web_model.UrlResponseResult(
        exit_code=req.status_code,
        match_status=match_status,
        match_content=match_content,
        match_headers=match_headers,
    )


register_io = [
    agent_model.RegisterCollectInput(request_url_input),
    agent_model.RegisterSendOutput(email_message_output),
    agent_model.RegisterSendOutput(slack_message_output),
]
