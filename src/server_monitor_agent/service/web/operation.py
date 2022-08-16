from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPException, SMTP_SSL
from zoneinfo import ZoneInfo

import beartype
from beartype import typing
from pytz.tzinfo import StaticTzInfo

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
) -> dict:
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
        with SMTP_SSL(mail_host, mail_port) as server:
            result["login"] = server.login(mail_user, mail_pass)
            result["send"] = server.sendmail(
                msg_from_address, msg_to_addresses, msg.as_string()
            )
            server.close()

    except SMTPException as e:
        result["error"] = e

    return result


@beartype.beartype
def submit_slack_message(webhook: str, item: agent_model.AgentItem):
    if item.status_name == self._pass:
        emoji1 = ":white_check_mark:"
        emoji2 = ":large_green_circle:"
        prefix = "Passing"
    elif item.status_name == self._warn:
        emoji1 = ":warning:"
        emoji2 = ":large_yellow_circle:"
        prefix = "Warning"
    elif item.status_name == self._crit:
        emoji1 = ":fire:"
        emoji2 = ":red_circle:"
        prefix = "Critical"
    else:
        emoji1 = ":grey_question:"
        emoji2 = ":white_circle:"
        prefix = "Unknown"

    extra = [
        f"Server: {item.host_name}",
        f"Source: {item.source_name}",
        f"Status: {item.status_name}",
        f"Enabled: {'yes' if item.is_enabled is True else '*no*'}",
        f"Active: {'yes' if item.is_active is True else '*no*'}",
    ]
    if item.date_next:
        extra.append(f"Trigger upcoming: {self.date_display(item.date_next)}")
    if item.date_triggered:
        extra.append(f"Triggered on: {self.date_display(item.date_triggered)}")
    if item.trigger_by:
        extra.append(f"Triggered by: {item.trigger_by}")
    if item.trigger_for:
        extra.append(f"Trigger for: {item.trigger_for}")

    extra_str = "\n".join([f"- {i}" for i in extra])
    check_str = f"Check: {item.check_name}  |  {item.check_type}"
    descr = "\n".join([i for i in [item.title, item.description] if i and i.strip()])
    notify_str = f"{emoji2}  *The check for {item.name} is {item.status}.*"

    if isinstance(item.date.tzinfo, ZoneInfo):
        time_zone = str(item.date.tzinfo)
    elif isinstance(item.date.tzinfo, StaticTzInfo):
        time_zone = item.date.tzinfo.tzname(None)
    else:
        time_zone = None
    date_str = f"Occurred *{self.date_display(item.date)}*"
    if time_zone and time_zone not in date_str:
        date_str += f" ({time_zone})"

    header_str = f"{emoji1}  {prefix}: {item.name} \non {item.hostname}"

    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": header_str}},
        {"type": "context", "elements": [{"type": "mrkdwn", "text": date_str}]},
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": notify_str}},
        {"type": "section", "text": {"type": "mrkdwn", "text": descr}},
    ]

    if item.logs:
        logs_raw = "\n".join([">" + i for i in item.logs])
        logs_str = f"Logs:\n{logs_raw}" if item.logs else "No logs."
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": logs_str}})

    blocks.extend(
        [
            {"type": "section", "text": {"type": "mrkdwn", "text": extra_str}},
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": check_str}],
            },
        ]
    )

    msg = {"blocks": blocks}
    print(msg)
    return msg

    # https://projects.iamcal.com/emoji-data/table.htm

    # attributes
    # node / server: 🖥️ 	desktop computer 	:desktop_computer:
    # date: 📅 	calendar 	:date:

    # passing:
    # 🟢 	large green circle 	:large_green_circle:
    # 🔵 	large blue circle 	:large_blue_circle:
    # 🏅 	sports medal 	:sports_medal:
    # 🎉 	party popper 	:tada:
    # 🙂 	slightly smiling face 	:slightly_smiling_face:
    # 🧯 	fire extinguisher 	:fire_extinguisher:
    # ⭐ 	white medium star 	:star:

    # warning:
    # 🟠 	large orange circle 	:large_orange_circle:
    # 🟡 	large yellow circle 	:large_yellow_circle:
    # ⚠️ 	warning sign 	:warning:
    # 🏃 	runner 	:runner:
    # 😐 	neutral face 	:neutral_face:
    # 🐛 	bug 	:bug:

    # critical:
    # 🔴 	large red circle 	:red_circle:
    # 💥 	collision symbol 	:boom:
    # 🚨 	police cars revolving light 	:rotating_light:
    # 💣 	bomb 	:bomb:
    # 🙁 	slightly frowning face 	:slightly_frowning_face:

    # send the post request with json body
    response = requests.post(url=self.webhook, json=payload)
    if not response.status_code != 200:
        raise ValueError(f"Unexpected response from slack: {response}")
