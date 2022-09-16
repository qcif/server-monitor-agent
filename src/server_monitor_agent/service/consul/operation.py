import beartype
from beartype import typing

from server_monitor_agent.agent import model as agent_model, operation as agent_op
from server_monitor_agent.service.consul import model as consul_model


@beartype.beartype
def leader_private_ipv4(settings: consul_model.ConsulConnectionSettings) -> str:
    req = settings.request_api(settings, path="status/leader")
    return req.text


@beartype.beartype
def health_checks(
    settings: consul_model.ConsulConnectionSettings,
    state: typing.Optional[str] = None,
) -> typing.Iterable[consul_model.ConsulHealthCheckStateItem]:

    if not state or not state.strip():
        state = agent_model.REPORT_LEVEL_ANY

    state = state.lower()

    if state not in agent_model.REPORT_LEVELS_ALL:
        agent_op.raise_options("state", state, agent_model.FORMATS)

    req = settings.request_api(f"health/state/{state}")
    data = req.json()
    items = [consul_model.ConsulHealthCheckStateItem.from_dict(i) for i in data]
    return items
