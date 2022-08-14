import beartype

from server_monitor_agent.service.alert_manager import (
    model as alert_model,
    operation as alert_op,
)
from server_monitor_agent.service.disk import model as disk_model, operation as disk_op
from server_monitor_agent.service.server import (
    model as server_model,
    operation as server_op,
)
from server_monitor_agent.service.systemd import (
    build as systemd_build,
    model as systemd_model,
)


@beartype.beartype
def collect_unit_status_send_alert_manager(
    collect_args: systemd_model.SystemdUnitStatusCollectArgs,
    send_args: alert_model.AlertManagerSendArgs,
):
    data = systemd_build.unit_status(collect_args)
    item = to_alert_manager(data)
    alert_op.submit_alerts(item)
    return data


@beartype.beartype
def collect_unit_status_send_file_output(
    collect_args: systemd_model.SystemdUnitStatusCollectArgs,
    send_args: disk_model.FileOutputSendArgs,
):
    data = systemd_build.unit_status(collect_args)
    item = to_format(send_args.format, data)
    disk_op.write_file(send_args, item)
    return data


@beartype.beartype
def collect_unit_status_send_logged_in_users(
    collect_args: systemd_model.SystemdUnitStatusCollectArgs,
    send_args: server_model.LoggedInUsersSendArgs,
):
    data = systemd_build.unit_status(collect_args)
    item = to_user_message(data)
    server_op.user_message(send_args, item)
    return data


@beartype.beartype
def collect_unit_status_send_stream_output(
    collect_args: systemd_model.SystemdUnitStatusCollectArgs,
    send_args: server_model.StreamOutputSendArgs,
):
    data = systemd_build.unit_status(collect_args)
    item = to_format(send_args.format, data)
    server_op.write_stream(send_args, item)
    return data


@beartype.beartype
def collect_unit_logs_send_alert_manager(
    collect_args: systemd_model.SystemdUnitLogsCollectArgs,
    send_args: alert_model.AlertManagerSendArgs,
):
    data = systemd_build.unit_logs(collect_args)
    item = to_alert_manager(data)
    alert_op.submit_alerts(item)
    return data


@beartype.beartype
def collect_unit_logs_send_file_output(
    collect_args: systemd_model.SystemdUnitLogsCollectArgs,
    send_args: disk_model.FileOutputSendArgs,
):
    data = systemd_build.unit_logs(collect_args)
    item = to_format(send_args.format, data)
    disk_op.write_file(send_args, item)
    return data


@beartype.beartype
def collect_unit_logs_send_logged_in_users(
    collect_args: systemd_model.SystemdUnitLogsCollectArgs,
    send_args: server_model.LoggedInUsersSendArgs,
):
    data = systemd_build.unit_logs(collect_args)
    item = to_user_message(data)
    server_op.user_message(send_args, item)
    return data


@beartype.beartype
def collect_unit_logs_send_stream_output(
    collect_args: systemd_model.SystemdUnitLogsCollectArgs,
    send_args: server_model.StreamOutputSendArgs,
):
    data = systemd_build.unit_logs(collect_args)
    item = to_format(send_args.format, data)
    server_op.write_stream(send_args, item)
    return data
