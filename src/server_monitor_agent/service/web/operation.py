import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import beartype
import requests
from beartype import typing

from server_monitor_agent.agent import model as agent_model
from server_monitor_agent.service.web import collect as web_collect, model as web_model


@beartype.beartype
def request_url(
    request: web_model.UrlRequestEntry,
    response: web_model.UrlResponseEntry,
) -> agent_model.AgentItem:
    method = request.method.lower()
    url = request.url
    headers = {k.replace("_", "-").lower(): v for k, v in request.headers.items()}

    response_check = web_collect.request_url(
        method,
        url,
        headers,
        response.status_code,
        response.content,
        response.headers,
    )

    raise NotImplementedError()


@beartype.beartype
def submit_email(
    mail_host: str,
    mail_port: int,
    mail_user: str,
    mail_pass: str,
    msg_subject: str,
    msg_from_address: str,
    msg_to_addresses: typing.Sequence[str],
    msg_body_text: str,
    msg_body_html: str,
) -> typing.Dict:
    """Send an email."""

    # build message
    # based on https://stackoverflow.com/questions/9087158/amazon-ses-smtp-python-usage
    # use MIME type 'multipart/alternative' - for AWS SES
    msg = MIMEMultipart("alternative")
    msg["Subject"] = msg_subject
    msg["From"] = msg_from_address
    msg["To"] = ", ".join(msg_to_addresses)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(msg_body_text, "plain")
    part2 = MIMEText(msg_body_html, "html")

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # send message
    result = {}
    try:
        with smtplib.SMTP_SSL(mail_host, mail_port) as server:
            result["login"] = server.login(mail_user, mail_pass)
            result["send"] = server.sendmail(
                msg_from_address, msg_to_addresses, msg.as_string()
            )
            server.close()

    except smtplib.SMTPException as e:
        result["error"] = e

    return result


@beartype.beartype
def submit_slack_message(webhook: str, payload: typing.Any):
    # send the post request with json body
    response = requests.post(url=webhook, json=payload)
    if not response.status_code != 200:
        raise ValueError(f"Unexpected response from slack: {response}")
