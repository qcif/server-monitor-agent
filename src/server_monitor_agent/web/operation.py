from server_monitor_agent.agent import model as agent_model
from server_monitor_agent.web import collect, model as model


def request_url(cmd_name: str, args: model.WebAppStatusArgs) -> agent_model.AgentItem:
    method = args.request.method.lower()
    url = args.request.url
    headers = {k.replace("_", "-").lower(): v for k, v in args.request.headers.items()}

    response_check = collect.request_url(
        method,
        url,
        headers,
        args.response.status_code,
        args.response.content,
        args.response.headers,
    )

    raise NotImplementedError()
