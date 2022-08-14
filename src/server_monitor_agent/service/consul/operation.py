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
) -> typing.Iterable[consul_model.ConsulHealthCheckExternalItem]:

    if not state or not state.strip():
        state = agent_model.REPORT_LEVEL_ANY

    state = state.lower()

    if state not in agent_model.REPORT_LEVELS_ALL:
        options = agent_op.make_options(agent_model.FORMATS_OUT)
        raise ValueError(f"Unrecognised state: '{state}'. Must be one of {options}.")

    req = settings.request_api(settings, path=f"health/state/{state}")
    data = req.json()
    items = consul_model.ConsulHealthCheckExternalItem.from_items(data)
    return items
