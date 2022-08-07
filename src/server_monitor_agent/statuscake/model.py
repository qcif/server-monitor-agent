import dataclasses

from server_monitor_agent.agent import model as agent_model


@dataclasses.dataclass
class StatusCakeCollectArgs(agent_model.CollectArgs):
    interval: float = 2.0

    @property
    def io_module(self) -> str:
        return "statuscake.io"

    @property
    def io_func_prefix(self) -> str:
        return "statuscake"


@dataclasses.dataclass
class StatusCakeSendArgs(agent_model.SendArgs):
    @property
    def io_func_suffix(self) -> str:
        return "statuscake"


@dataclasses.dataclass
class StatusCakeResult(agent_model.OpResult):
    rx: int
    tx: int
    process: str
    drives: str
    ping: str
    freeMem: int
    MemTotal: int
    cpuUse: float
    uptime: int
    hdd: int
    thdd: int
