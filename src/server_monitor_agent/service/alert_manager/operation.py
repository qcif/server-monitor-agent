import dataclasses

import beartype
import requests

from server_monitor_agent.service.alert_manager import model as alert_model


@beartype.beartype
def submit_alerts(base_url: str, item: alert_model.AlertManagerItem) -> None:
    url = f"{base_url}/alerts"
    response = requests.post(url=url, json=dataclasses.asdict(item))
    if not response.status_code != 200:
        raise ValueError(f"Unexpected response from slack: {response}")
