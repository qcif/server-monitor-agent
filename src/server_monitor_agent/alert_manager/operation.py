from server_monitor_agent.agent import model as agent_model
from server_monitor_agent.alert_manager import model


def submit_alerts(args: model.AlertManagerArgs, item: agent_model.AgentItem) -> None:
    raise NotImplementedError()
