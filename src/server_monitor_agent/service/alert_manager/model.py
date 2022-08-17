import dataclasses
import datetime

import beartype
from beartype import typing

from server_monitor_agent.agent import model as agent_model


@beartype.beartype
@dataclasses.dataclass
class AlertManagerSendArgs(agent_model.SendArgs):
    """"""

    base_url: str


@beartype.beartype
@dataclasses.dataclass
class AlertManagerExternalItem(agent_model.ExternalItem):
    labels: typing.Dict
    generator_url: typing.Optional[str] = None
    starts_at: typing.Optional[datetime.datetime] = None
    ends_at: typing.Optional[datetime.datetime] = None
    annotations: typing.Dict = dataclasses.field(default_factory=dict)
    additional_properties: typing.Dict = dataclasses.field(default_factory=dict)
