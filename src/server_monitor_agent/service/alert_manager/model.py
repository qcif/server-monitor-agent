import dataclasses
import datetime

import beartype
from beartype import typing

from server_monitor_agent.agent import model as agent_model


@beartype.beartype
@dataclasses.dataclass
class AlertManagerSendArgs(agent_model.SendArgs):
    @property
    @beartype.beartype
    def io_func_suffix(self) -> str:
        return "alert_manager"


@beartype.beartype
@dataclasses.dataclass
class AlertManagerExternalItem(agent_model.ExternalItem):
    labels: dict
    generator_url: typing.Optional[str] = None
    starts_at: typing.Optional[datetime.datetime] = None
    ends_at: typing.Optional[datetime.datetime] = None
    annotations: dict = dataclasses.field(default_factory=dict)
    additional_properties: dict = dataclasses.field(default_factory=dict)
