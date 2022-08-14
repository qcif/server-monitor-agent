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
from server_monitor_agent.service.statuscake import (
    model as sc_model,
    operation as sc_op,
)
from server_monitor_agent.service.statuscake import build as sc_build


@beartype.beartype
def collect_statuscake_send_alert_manager(
    collect_args: sc_model.StatusCakeCollectArgs,
    send_args: alert_model.AlertManagerSendArgs,
):
    data = sc_build.statuscake(collect_args)
    item = to_alert_manager(data)
    alert_op.submit_alerts(item)
    return data


@beartype.beartype
def collect_statuscake_send_file_output(
    collect_args: sc_model.StatusCakeCollectArgs,
    send_args: disk_model.FileOutputSendArgs,
):
    data = sc_build.statuscake(collect_args)
    item = to_format(send_args.format, data)
    disk_op.write_file(send_args, item)
    return data


@beartype.beartype
def collect_statuscake_send_logged_in_users(
    collect_args: sc_model.StatusCakeCollectArgs,
    send_args: server_model.LoggedInUsersSendArgs,
):
    data = sc_build.statuscake(collect_args)
    item = to_user_message(data)
    server_op.user_message(send_args, item)
    return data


@beartype.beartype
def collect_statuscake_send_stream_output(
    collect_args: sc_model.StatusCakeCollectArgs,
    send_args: server_model.StreamOutputSendArgs,
):
    data = sc_build.statuscake(collect_args)
    item = to_format(send_args.format, data)
    server_op.write_stream(send_args, item)
    return data


@beartype.beartype
def collect_statuscake_send_statuscake(
    collect_args: sc_model.StatusCakeCollectArgs,
    send_args: sc_model.StatusCakeSendArgs,
):
    data = sc_build.statuscake(collect_args)
    item = to_statuscake_message(send_args.format, data)
    sc_op.submit_statuscake(item)
    return data
