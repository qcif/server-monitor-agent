import dataclasses
import typing

from server_monitor_agent.agent import model as agent_model


@dataclasses.dataclass
class UrlHeadersEntry:
    name: str
    comparisons: typing.List[agent_model.TextCompareEntry]


@dataclasses.dataclass
class UrlRequestEntry:
    url: str
    method: str
    headers: typing.Dict[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class UrlResponseEntry:
    status_code: int
    headers: typing.List[UrlHeadersEntry]
    content: typing.List[agent_model.TextCompareEntry]


@dataclasses.dataclass
class WebAppStatusArgs(agent_model.CollectArgs):
    request: UrlRequestEntry
    response: UrlResponseEntry

    @property
    def io_module(self) -> str:
        return "web.io"

    @property
    def io_func_prefix(self) -> str:
        return "web"


@dataclasses.dataclass
class UrlResponseResult(agent_model.OpResult):
    match_status: bool
    match_content: typing.List[dict]
    match_headers: typing.List[dict]
