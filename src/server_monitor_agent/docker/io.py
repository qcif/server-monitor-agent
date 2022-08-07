try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

from server_monitor_agent.agent import model as agent_model
from server_monitor_agent.alert_manager import model as alert_model
from server_monitor_agent.disk import model as disk_model, operation as server_op
from server_monitor_agent.docker import model as docker_model, operation as docker_op
from server_monitor_agent.server import model as server_model, operation as server_op


def collect_container_status_send_alert_manager(
    collect_args: docker_model.DockerContainerStatusArgs,
    send_args: alert_model.AlertManagerArgs,
):
    raise NotImplementedError()


def collect_container_status_send_file_output(
    collect_args: docker_model.DockerContainerStatusArgs,
    send_args: disk_model.FileOutputArgs,
):
    raise NotImplementedError()


def collect_container_status_send_logged_in_users(
    collect_args: docker_model.DockerContainerStatusArgs,
    send_args: server_model.LoggedInUsersArgs,
):
    raise NotImplementedError()


def collect_container_status_send_stream_output(
    collect_args: docker_model.DockerContainerStatusArgs,
    send_args: server_model.StreamOutputArgs,
):
    raise NotImplementedError()


def docker_container_status(
    cmd_name: str, args: docker_model.DockerContainerStatusArgs
) -> agent_model.AgentItem:
    states_running = "running"
    states_not_running = "not-running"
    states_available = [states_running, states_not_running]

    healths_healthy = "healthy"
    healths_ignore = "ignore"
    healths_available = [healths_healthy, healths_ignore]

    if args.state not in states_available:
        raise ValueError(
            f"State must be one of '{', '.join(states_available)}' "
            f"for check '{cmd_name}'."
        )

    if args.health not in healths_available:
        raise ValueError(
            f"Health must be one of '{', '.join(healths_available)}' "
            f"for check '{cmd_name}'."
        )

    container_name = args.name

    show = docker_op.container_ls(container_name)

    if show is None:
        exit_code = 2
        state = ""
        health = None
    else:
        exit_code = show.exit_code
        container_name = show.name
        state = show.state
        health = show.health

    status = agent_model.REPORT_LEVEL_PASS
    status_code = agent_model.REPORT_CODE_PASS

    descr_items = []
    if args.state == states_running and state != states_running:
        status = agent_model.REPORT_LEVEL_CRIT
        status_code = agent_model.REPORT_CODE_CRIT
        descr_items.append("Container was expected to be running, but was not.")

    if args.health == healths_healthy and health is None:
        status = agent_model.REPORT_LEVEL_WARN
        status_code = agent_model.REPORT_CODE_WARN
        descr_items.append(
            "Container health was expected to be healthy, but was not available."
        )

    if args.health == healths_healthy and health != healths_healthy:
        status = agent_model.REPORT_LEVEL_CRIT
        status_code = agent_model.REPORT_CODE_CRIT
        descr_items.append(
            "Container health was expected to be healthy, but it was not."
        )

    if exit_code != 0:
        status = agent_model.REPORT_LEVEL_CRIT
        status_code = agent_model.REPORT_CODE_CRIT
        descr_items.append("Container state check was not successful.")

    hostname = server_op.hostname()
    date = server_op.timezone().now

    if health is None:
        health = "(no health check)"

    if status == agent_model.REPORT_LEVEL_PASS:
        title = f"Normal container {container_name} state"
        descr = f"Normal container {container_name} state {state} health {health}."
    else:
        title = f"Unexpected container {container_name} state"
        descr = (
            f"Unexpected container {container_name} state {state} health {health}. "
            f"{' '.join(descr_items)}"
        )

    return agent_model.AgentItem(
        service_name=f"container {container_name}",
        host_name=hostname,
        source_name="docker",
        status_code=status_code,
        status_name=status,
        title=title,
        description=descr.strip(),
        check_type=cmd_name,
        date=date,
        tags={},
    )
