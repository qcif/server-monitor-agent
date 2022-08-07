import dataclasses

from server_monitor_agent.agent import model as agent_model


@dataclasses.dataclass
class AlertManagerArgs(agent_model.SendArgs):
    @property
    def io_func_suffix(self) -> str:
        return "alert_manager"
