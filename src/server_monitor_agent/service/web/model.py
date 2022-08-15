import dataclasses

import beartype
from beartype import typing

from server_monitor_agent.agent import model as agent_model


@beartype.beartype
@dataclasses.dataclass
class UrlHeadersEntry:
    name: str
    comparisons: typing.List[agent_model.TextCompareEntry]


@beartype.beartype
@dataclasses.dataclass
class UrlRequestEntry:
    url: str
    method: str = dataclasses.field(default="GET")
    headers: typing.Dict[str, str] = dataclasses.field(default_factory=dict)


@beartype.beartype
@dataclasses.dataclass
class UrlResponseEntry:
    status_code: int = dataclasses.field(default=200)
    headers: typing.List[UrlHeadersEntry] = dataclasses.field(default_factory=list)
    content: typing.List[agent_model.TextCompareEntry] = dataclasses.field(
        default_factory=list
    )


@beartype.beartype
@dataclasses.dataclass
class RequestUrlCollectArgs(agent_model.CollectArgs):
    request: UrlRequestEntry
    response: UrlResponseEntry


@beartype.beartype
@dataclasses.dataclass
class UrlResponseResult(agent_model.OpResult):
    match_status: bool
    match_content: typing.List[dict]
    match_headers: typing.List[dict]


@beartype.beartype
@dataclasses.dataclass
class EmailMessageSendArgs(agent_model.SendArgs):
    host: str
    port: int
    username: str
    password: str
    from_address: str
    to_addresses: typing.Sequence[str]


@beartype.beartype
@dataclasses.dataclass
class SlackMessageSendArgs(agent_model.SendArgs):
    webhook: str
