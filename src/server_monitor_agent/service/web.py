from dataclasses import dataclass, field
from typing import Any

import requests

from server_monitor_agent.common import (
    TextCompareEntry,
    ConfigEntryMixin,
    RunArgs,
    ResultMixin,
)
from server_monitor_agent.common import ProgramMixin


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
        # run_args
        # cmd_io = {str} 'std_out'
        # file_path = {NoneType} None
        # fmt = {str} 'agent'
        # group = {str} 'check'
        # is_file = {bool} False
        # is_std_err = {bool} False
        # is_std_io = {bool} True
        # level = {NoneType} None
        # name = {str} 'github_octocat_status'
        # std_err = {bool} False
        # std_io = {bool} True

        # self
        # group = {str} 'check'
        # key = {str} 'github_octocat_status'
        # request = {UrlRequestEntry} UrlRequestEntry(url='https://api.github.com/octocat', method='GET', headers={'test_header': 'test header value'})
        #  headers = {dict: 1} {'test_header': 'test header value'}
        #  method = {str} 'GET'
        #  url = {str} 'https://api.github.com/octocat'
        # response = {UrlResponseEntry} UrlResponseEntry(status_code=200, headers=[UrlHeadersEntry(name='content_type', comparisons=[TextCompareEntry(comparison='contains', value='text/plain')])], content=[TextCompareEntry(comparison='contains', value='MMMMM')])
        #  content = {list: 1} [TextCompareEntry(comparison='contains', value='MMMMM')]
        #  headers = {list: 1} [UrlHeadersEntry(name='content_type', comparisons=[TextCompareEntry(comparison='contains', value='text/plain')])]
        #  status_code = {int} 200
        # type = {str} 'web-app-status'
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

        pass


@dataclass
class NotifyEmailEntry(ConfigEntryMixin):
    key: str
    address: str
    group: str = "notify"
    type: str = "email"

    def operation(self, run_args: RunArgs) -> None:
        item = self._get_input(run_args)
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

    def email(self):
        """Send an email."""
        # https://docs.python.org/3.10/library/email.examples.html
        raise NotImplementedError()
