import dataclasses

import beartype

from server_monitor_agent.agent import model as agent_model


@beartype.beartype
@dataclasses.dataclass
class StatusCakeCollectArgs(agent_model.CollectArgs):
    interval: float = 2.0


@beartype.beartype
@dataclasses.dataclass
class StatusCakeSendArgs(agent_model.SendArgs):
    """"""
