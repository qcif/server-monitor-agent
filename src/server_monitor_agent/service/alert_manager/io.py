from server_monitor_agent.agent import model as agent_model
from server_monitor_agent.service.alert_manager import (
    model as alert_model,
    operation as alert_op,
)


def alert_manager_output(
    args: alert_model.AlertManagerSendArgs, item: agent_model.AgentItem
) -> None:
    data = alert_model.AlertManagerItem.from_agent_item(item)
    alert_op.submit_alerts(args.base_url, data)


register_io = [
    # agent_model.RegisterSendOutput(alert_manager_output),
]
