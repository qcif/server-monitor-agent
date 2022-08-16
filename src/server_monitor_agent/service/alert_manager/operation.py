import beartype
import requests

from server_monitor_agent.agent import model as agent_model


@beartype.beartype
def submit_alerts(base_url: str, item: agent_model.AgentItem) -> None:
    url = f"{base_url}/alerts"
    data = item.tags.get("alert_manager_items", [])
    response = requests.post(url=url, json=data)
    if not response.status_code != 200:
        raise ValueError(f"Unexpected response from slack: {response}")
