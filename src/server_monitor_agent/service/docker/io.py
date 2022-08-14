import beartype

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

from server_monitor_agent.service.docker import (
    build as docker_build,
    model as docker_model,
)
from server_monitor_agent.service.alert_manager import (
    model as alert_model,
    operation as alert_op,
)
from server_monitor_agent.service.disk import model as disk_model, operation as disk_op
from server_monitor_agent.service.server import (
    model as server_model,
    operation as server_op,
)


@beartype.beartype
def collect_container_status_send_alert_manager(
    collect_args: docker_model.ContainerStatusCollectArgs,
    send_args: alert_model.AlertManagerSendArgs,
):
    data = docker_build.container_status(collect_args)
    item = to_alert_manager(data)
    alert_op.submit_alerts(item)
    return data


@beartype.beartype
def collect_container_status_send_file_output(
    collect_args: docker_model.ContainerStatusCollectArgs,
    send_args: disk_model.FileOutputSendArgs,
):
    data = docker_build.container_status(collect_args)
    item = to_format(send_args.format, data)
    disk_op.write_file(send_args, item)
    return data


@beartype.beartype
def collect_container_status_send_logged_in_users(
    collect_args: docker_model.ContainerStatusCollectArgs,
    send_args: server_model.LoggedInUsersSendArgs,
):
    data = docker_build.container_status(collect_args)
    item = to_user_message(data)
    server_op.user_message(send_args.user_group, item)
    return data


@beartype.beartype
def collect_container_status_send_stream_output(
    collect_args: docker_model.ContainerStatusCollectArgs,
    send_args: server_model.StreamOutputSendArgs,
):
    data = docker_build.container_status(collect_args)
    item = to_format(send_args.format, data)
    server_op.write_stream(send_args, item)
    return data
