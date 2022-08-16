import beartype


try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

from server_monitor_agent.agent import model as agent_model
from server_monitor_agent.service.docker import (
    model as docker_model,
    operation as docker_op,
)
from server_monitor_agent.service.disk import operation as server_op
from server_monitor_agent.service.server import operation as server_op


@beartype.beartype
def container_status_input(
    args: docker_model.ContainerStatusCollectArgs,
) -> agent_model.AgentItem:
    states_running = "running"
    states_not_running = "not-running"
    states_available = [states_running, states_not_running]

    healths_healthy = "healthy"
    healths_ignore = "ignore"
    healths_available = [healths_healthy, healths_ignore]

    expected_state = args.state
    if expected_state not in states_available:
        raise ValueError(f"State must be one of '{', '.join(states_available)}'.")

    expected_health = args.health
    if expected_health not in healths_available:
        raise ValueError(f"Health must be one of '{', '.join(healths_available)}'.")

    expected_name = args.name

    show = docker_op.container_ls(expected_name)

    if show is None:
        exit_code = 2
        actual_state = ""
        actual_health = None
        actual_name = expected_name
    else:
        exit_code = show.exit_code
        actual_name = show.name
        actual_state = show.state
        actual_health = show.health

    status = agent_model.REPORT_LEVEL_PASS

    descr_items = []
    if expected_state == states_running and actual_state != states_running:
        status = agent_model.REPORT_LEVEL_CRIT
        descr_items.append("Container was expected to be running, but was not.")

    if expected_health == healths_healthy and actual_health is None:
        status = agent_model.REPORT_LEVEL_WARN
        descr_items.append(
            "Container health was expected to be healthy, but was not available."
        )

    if expected_health == healths_healthy and actual_health != healths_healthy:
        status = agent_model.REPORT_LEVEL_CRIT
        descr_items.append(
            "Container health was expected to be healthy, but it was not."
        )

    if exit_code != 0:
        status = agent_model.REPORT_LEVEL_CRIT
        descr_items.append("Container state check was not successful.")

    hostname = server_op.hostname()
    date = server_op.timezone().now

    if actual_health is None:
        actual_health = "(no health check)"

    if status == agent_model.REPORT_LEVEL_PASS:
        title = f"Expected container {actual_name} state"
        descr = f"Expected container {actual_name} state {actual_state} health {actual_health}."
    else:
        title = f"Unexpected container {actual_name} state"
        descr = (
            f"Unexpected container {actual_name} state {actual_state} health {actual_health}. "
            f"{' '.join(descr_items)}"
        )

    return agent_model.AgentItem(
        summary=title,
        description=descr.strip(),
        host_name=hostname,
        source_name="docker",
        check_name="container",
        date=date,
        status_name=status,
        service_name=args.name,
        tags={
            "container_name": actual_name,
            "expected_state": args.state,
            "expected_health": args.health,
            "actual_state": actual_state,
            "actual_health": actual_health,
        },
    )


register_io = [
    agent_model.RegisterCollectInput(container_status_input),
]
