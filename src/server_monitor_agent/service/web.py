from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL, SMTPException
from typing import Any

import requests

from server_monitor_agent.common import ProgramMixin
from server_monitor_agent.common import (
    TextCompareEntry,
    ConfigEntryMixin,
    RunArgs,
    ResultMixin,
)


@dataclass
class UrlHeadersEntry:
    name: str
    comparisons: list[TextCompareEntry]

    @classmethod
    def load(cls, **kwargs) -> "UrlHeadersEntry":
        kwargs["comparisons"] = [
            TextCompareEntry.load(comparison=k, value=v)
            for i in kwargs.get("comparisons", [])
            for k, v in i.items()
        ]
        return cls(**kwargs)


@dataclass
class UrlRequestEntry:
    url: str
    method: str
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class UrlResponseEntry:
    status_code: int
    headers: list[UrlHeadersEntry]
    content: list[TextCompareEntry]

    @classmethod
    def load(cls, **kwargs) -> "UrlResponseEntry":
        kwargs["headers"] = [
            UrlHeadersEntry.load(name=k, comparisons=v)
            for k, v in kwargs.get("headers", {}).items()
        ]
        kwargs["content"] = [
            TextCompareEntry.load(comparison=k, value=v)
            for i in kwargs.get("content", [])
            for k, v in i.items()
        ]
        return cls(**kwargs)


@dataclass
class CheckUrlEntry(ConfigEntryMixin):
    request: UrlRequestEntry
    response: UrlResponseEntry
    group: str = "check"
    type: str = "web-app-status"

    @classmethod
    def load(cls, **kwargs) -> "CheckUrlEntry":
        kwargs["request"] = UrlRequestEntry(**kwargs.get("request", {}))
        kwargs["response"] = UrlResponseEntry.load(**kwargs.get("response", {}))
        return cls(**kwargs)

    def operation(self, run_args: RunArgs) -> None:
        method = self.request.method.lower()
        url = self.request.url
        headers = dict(
            (k.replace("_", "-").lower(), v) for k, v in self.request.headers.items()
        )

        web_program = WebProgram()
        response_check = web_program.url(
            method,
            url,
            headers,
            self.response.status_code,
            self.response.content,
            self.response.headers,
        )

        raise NotImplementedError()


@dataclass
class NotifyEmailEntry(ConfigEntryMixin):
    key: str
    address: str
    group: str = "notify"
    type: str = "email"

    def operation(self, run_args: RunArgs) -> None:
        item = self._get_input(run_args)

        mail_host = ""
        mail_port = 0
        mail_user = ""
        mail_pass = ""
        msg_subject = ""
        msg_from_addr = ""
        msg_to = []
        msg_body_text = ""
        msg_body_html = ""

        prog = WebProgram()
        email_result = prog.email(
            mail_host,
            mail_port,
            mail_user,
            mail_pass,
            msg_subject,
            msg_from_addr,
            msg_to,
            msg_body_text,
            msg_body_html,
        )
        if "error" in email_result:
            msg = (
                f"Error sending email: "
                f"login: '{email_result.get('login', '')}' "
                f"send: '{email_result.get('send', '')}'"
            )
            raise ValueError(msg) from email_result.get("error")

        raise NotImplementedError()


@dataclass
class UrlResponseResult(ResultMixin):
    match_status: bool
    match_content: list[dict]
    match_headers: list[dict]


class WebProgram(ProgramMixin):
    def url(
        self,
        method: str,
        url: str,
        headers: dict[str, Any],
        expected_status: int,
        expected_content: list[TextCompareEntry],
        expected_headers: list[UrlHeadersEntry],
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

        return UrlResponseResult(
            exit_code=req.status_code,
            match_status=match_status,
            match_content=match_content,
            match_headers=match_headers,
        )

    def email(
        self,
        mail_host: str,
        mail_port: int,
        mail_user: str,
        mail_pass: str,
        msg_subject: str,
        msg_from_addr: str,
        msg_to: list[str],
        msg_body_text: str,
        msg_body_html: str,
    ) -> dict:
        """Send an email."""

        # build message
        # based on https://stackoverflow.com/questions/9087158/amazon-ses-smtp-python-usage
        # use MIME type is multipart/alternative for AWS SES
        msg = MIMEMultipart("alternative")
        msg["Subject"] = msg_subject
        msg["From"] = msg_from_addr
        msg["To"] = ", ".join(msg_to)

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(msg_body_text, "plain")
        part2 = MIMEText(msg_body_html, "html")

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        # send message
        from_addr = msg_from_addr
        to_addrs = msg_to

        result = {}
        try:
            with SMTP_SSL(mail_host, mail_port) as server:
                result["login"] = server.login(mail_user, mail_pass)
                result["send"] = server.sendmail(from_addr, to_addrs, msg.as_string())
                server.close()

        except SMTPException as e:
            result["error"] = e

        return result
