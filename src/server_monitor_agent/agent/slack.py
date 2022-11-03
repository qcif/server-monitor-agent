import requests


def slack_webhook(url: str, text: str):
    req = requests.post(url, json={"text": text})
    if req.status_code != 200:
        raise ValueError(f"Slack webhook post error {req.status_code}: {req.text}")
    return req
