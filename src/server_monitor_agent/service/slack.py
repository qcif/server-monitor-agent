from dataclasses import dataclass
from zoneinfo import ZoneInfo

from dateparser.timezone_parser import StaticTzInfo

from server_monitor_agent.common import ConfigEntryMixin, ProgramMixin, RunArgs
from server_monitor_agent.common import ReportMixin, DateTimeMixin
from server_monitor_agent.service.agent import AgentItem


@dataclass
class NotifySlackEntry(ConfigEntryMixin):
    key: str
    webhook: str
    group: str = "notify"
    type: str = "slack"

    def operation(self, run_args: RunArgs) -> None:
        item = self._get_input(run_args)
        raise NotImplementedError()


class SlackProgram(ProgramMixin, ReportMixin, DateTimeMixin):
    def create_message(self, item: AgentItem):
        if item.status == self._pass:
            emoji1 = ":white_check_mark:"
            emoji2 = ":large_green_circle:"
            prefix = "Passing"
        elif item.status == self._warn:
            emoji1 = ":warning:"
            emoji2 = ":large_yellow_circle:"
            prefix = "Warning"
        elif item.status == self._crit:
            emoji1 = ":fire:"
            emoji2 = ":red_circle:"
            prefix = "Critical"
        else:
            emoji1 = ":grey_question:"
            emoji2 = ":white_circle:"
            prefix = "Unknown"

        extra = [
            f"Server: {item.hostname}",
            f"Source: {item.source}",
            f"Status code: {item.status_code}",
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
        descr = "\n".join(
            [i for i in [item.title, item.description] if i and i.strip()]
        )
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
            blocks.append(
                {"type": "section", "text": {"type": "mrkdwn", "text": logs_str}}
            )

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
