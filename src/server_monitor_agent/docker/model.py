import dataclasses
import typing

from server_monitor_agent.agent import model as agent_model


@dataclasses.dataclass
class DockerContainerStatusArgs(agent_model.CollectArgs):
    name: str
    state: str
    health: str

    @property
    def io_module(self) -> str:
        return "docker.io"

    @property
    def io_func_prefix(self) -> str:
        return "container_status"


@dataclasses.dataclass
class DockerContainerResult(agent_model.OpResult):
    name: str

    id: typing.Optional[str] = None
    state: typing.Optional[str] = None
    health: typing.Optional[str] = None
