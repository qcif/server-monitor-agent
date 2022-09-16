import beartype
import requests

from server_monitor_agent.agent import model as agent_model
from server_monitor_agent.service.web import model as web_model, operation as web_op


@beartype.beartype
def email_message_output(
    args: web_model.EmailMessageSendArgs, item: agent_model.AgentItem
) -> None:
    subject = item.summary

    # TODO: improve body content
    body_text = item.description

    # TODO: create html version
    body_html = item.description

    web_op.submit_email(
        mail_host=args.host,
        mail_port=args.port,
        mail_user=args.username,
        mail_pass=args.password,
        msg_subject=subject,
        msg_from_address=args.from_address,
        msg_to_addresses=args.to_addresses,
        msg_body_text=body_text,
        msg_body_html=body_html,
    )


@beartype.beartype
def slack_message_output(
    args: web_model.SlackMessageSendArgs, item: agent_model.AgentItem
) -> None:
    # if item.status_name == self._pass:
    #     emoji1 = ":white_check_mark:"
    #     emoji2 = ":large_green_circle:"
    #     prefix = "Passing"
    # elif item.status_name == self._warn:
    #     emoji1 = ":warning:"
    #     emoji2 = ":large_yellow_circle:"
    #     prefix = "Warning"
    # elif item.status_name == self._crit:
    #     emoji1 = ":fire:"
    #     emoji2 = ":red_circle:"
    #     prefix = "Critical"
    # else:
    #     emoji1 = ":grey_question:"
    #     emoji2 = ":white_circle:"
    #     prefix = "Unknown"
    #
    # extra = [
    #     f"Server: {item.host_name}",
    #     f"Source: {item.source_name}",
    #     f"Status: {item.status_name}",
    #     f"Enabled: {'yes' if item.is_enabled is True else '*no*'}",
    #     f"Active: {'yes' if item.is_active is True else '*no*'}",
    # ]
    # if item.date_next:
    #     extra.append(f"Trigger upcoming: {self.date_display(item.date_next)}")
    # if item.date_triggered:
    #     extra.append(f"Triggered on: {self.date_display(item.date_triggered)}")
    # if item.trigger_by:
    #     extra.append(f"Triggered by: {item.trigger_by}")
    # if item.trigger_for:
    #     extra.append(f"Trigger for: {item.trigger_for}")
    #
    # extra_str = "\n".join([f"- {i}" for i in extra])
    # check_str = f"Check: {item.check_name}  |  {item.check_type}"
    # descr = "\n".join([i for i in [item.title, item.description] if i and i.strip()])
    # notify_str = f"{emoji2}  *The check for {item.name} is {item.status}.*"
    #
    # if isinstance(item.date.tzinfo, ZoneInfo):
    #     time_zone = str(item.date.tzinfo)
    # elif isinstance(item.date.tzinfo, StaticTzInfo):
    #     time_zone = item.date.tzinfo.tzname(None)
    # else:
    #     time_zone = None
    # date_str = f"Occurred *{self.date_display(item.date)}*"
    # if time_zone and time_zone not in date_str:
    #     date_str += f" ({time_zone})"
    #
    # header_str = f"{emoji1}  {prefix}: {item.name} \non {item.hostname}"
    #
    # blocks = [
    #     {"type": "header", "text": {"type": "plain_text", "text": header_str}},
    #     {"type": "context", "elements": [{"type": "mrkdwn", "text": date_str}]},
    #     {"type": "divider"},
    #     {"type": "section", "text": {"type": "mrkdwn", "text": notify_str}},
    #     {"type": "section", "text": {"type": "mrkdwn", "text": descr}},
    # ]
    #
    # if item.logs:
    #     logs_raw = "\n".join([">" + i for i in item.logs])
    #     logs_str = f"Logs:\n{logs_raw}" if item.logs else "No logs."
    #     blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": logs_str}})
    #
    # blocks.extend(
    #     [
    #         {"type": "section", "text": {"type": "mrkdwn", "text": extra_str}},
    #         {
    #             "type": "context",
    #             "elements": [{"type": "mrkdwn", "text": check_str}],
    #         },
    #     ]
    # )
    #
    # msg = {"blocks": blocks}
    # print(msg)
    # return msg

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

    payload = {}

    web_op.submit_slack_message(args.webhook, payload)


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
