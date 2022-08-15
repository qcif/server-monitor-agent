import dataclasses

import beartype
from beartype import typing

from server_monitor_agent.agent import model as agent_model


@beartype.beartype
@dataclasses.dataclass
class ContainerStatusCollectArgs(agent_model.CollectArgs):
    name: str
    state: str
    health: str


@beartype.beartype
@dataclasses.dataclass
class ContainerStatusResult(agent_model.OpResult):
    name: str

    id: typing.Optional[str] = None
    state: typing.Optional[str] = None
    health: typing.Optional[str] = None
