import beartype

from server_monitor_agent.service.alert_manager import operation as alert_op
from server_monitor_agent.service.disk import operation as disk_op
from server_monitor_agent.service.server import (
    model as server_model,
    operation as server_op,
)
from server_monitor_agent.service.web import model as web_model
from server_monitor_agent.service.web import build as web_build


@beartype.beartype
def collect_request_url_send_alert_manager(
    collect_args: web_model.WebAppStatusCollectArgs,
    send_args: server_model.StreamOutputSendArgs,
):
    data = web_build.request_url(collect_args)
    item = to_alert_manager(data)
    alert_op.submit_alerts(item)
    return data


@beartype.beartype
def collect_request_url_send_file_output(
    collect_args: web_model.WebAppStatusCollectArgs,
    send_args: server_model.StreamOutputSendArgs,
):
    data = web_build.request_url(collect_args)
    item = to_format(send_args.format, data)
    disk_op.write_file(send_args, item)
    return data


@beartype.beartype
def collect_request_url_send_logged_in_users(
    collect_args: web_model.WebAppStatusCollectArgs,
    send_args: server_model.StreamOutputSendArgs,
):
    data = web_build.request_url(collect_args)
    item = to_user_message(data)
    server_op.user_message(send_args, item)
    return data


@beartype.beartype
def collect_request_url_send_stream_output(
    collect_args: web_model.WebAppStatusCollectArgs,
    send_args: server_model.StreamOutputSendArgs,
):
    data = web_build.request_url(collect_args)
    item = to_format(send_args.format, data)
    server_op.write_stream(send_args, item)
    return data
