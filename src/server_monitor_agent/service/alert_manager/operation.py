import beartype

from server_monitor_agent.agent import model as agent_model


@beartype.beartype
def submit_alerts(item: agent_model.AgentItem) -> None:
    raise NotImplementedError()
