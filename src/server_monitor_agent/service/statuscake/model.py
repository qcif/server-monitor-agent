import dataclasses

import beartype

from server_monitor_agent.agent import model as agent_model


@beartype.beartype
@dataclasses.dataclass
class StatusCakeCollectArgs(agent_model.CollectArgs):
    interval: float = 2.0

    @property
    @beartype.beartype
    def io_module(self) -> str:
        return "statuscake"

    @property
    @beartype.beartype
    def io_func_prefix(self) -> str:
        return "statuscake"


@beartype.beartype
@dataclasses.dataclass
class StatusCakeSendArgs(agent_model.SendArgs):
    @property
    @beartype.beartype
    def io_func_suffix(self) -> str:
        return "statuscake"
