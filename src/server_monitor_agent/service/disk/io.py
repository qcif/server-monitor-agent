"""Input (parsing) and output (formatting) functions for disks and files."""
import beartype

from server_monitor_agent.service.disk.build import disk_status, file_status

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

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
def collect_disk_status_send_file_output(
    collect_args: disk_model.DiskCollectArgs, send_args: disk_model.FileOutputSendArgs
):
    item = disk_status(collect_args)
    disk_op.write_file(send_args.format, send_args.path, item)
    return item


@beartype.beartype
def collect_disk_status_send_alert_manager(
    collect_args: disk_model.DiskCollectArgs,
    send_args: alert_model.AlertManagerSendArgs,
):
    item = disk_status(collect_args)
    alert_op.submit_alerts(item)
    return item


@beartype.beartype
def collect_disk_status_send_logged_in_users(
    collect_args: disk_model.DiskCollectArgs,
    send_args: server_model.LoggedInUsersSendArgs,
):
    item = disk_status(collect_args)
    server_op.user_message(send_args, item)
    return item


@beartype.beartype
def collect_disk_status_send_stream_output(
    collect_args: disk_model.DiskCollectArgs,
    send_args: server_model.StreamOutputSendArgs,
):
    item = disk_status(collect_args)
    server_op.write_stream(send_args.format, send_args.target, item)
    return item


@beartype.beartype
def collect_file_status_send_file_output(
    collect_args: disk_model.FileStatusCollectArgs,
    send_args: disk_model.FileOutputSendArgs,
):
    item = file_status(collect_args)
    disk_op.write_file(send_args.format, send_args.path, item)
    return item


@beartype.beartype
def collect_file_status_send_alert_manager(
    collect_args: disk_model.FileStatusCollectArgs,
    send_args: alert_model.AlertManagerSendArgs,
):
    item = file_status(collect_args)
    alert_op.submit_alerts(item)
    return item


@beartype.beartype
def collect_file_status_send_logged_in_users(
    collect_args: disk_model.FileStatusCollectArgs,
    send_args: server_model.LoggedInUsersSendArgs,
):
    item = file_status(collect_args)
    server_op.user_message(send_args, item)
    return item


@beartype.beartype
def collect_file_status_send_stream_output(
    collect_args: disk_model.FileStatusCollectArgs,
    send_args: server_model.StreamOutputSendArgs,
):
    item = file_status(collect_args)
    server_op.write_stream(send_args.format, send_args.target, item)
    return item


@beartype.beartype
def collect_file_input_send_file_output(
    collect_args: disk_model.FileInputCollectArgs,
    send_args: disk_model.FileOutputSendArgs,
):
    item = disk_op.read_file(collect_args.format, collect_args.path)
    disk_op.write_file(send_args.format, send_args.path, item)
    return item


@beartype.beartype
def collect_file_input_send_alert_manager(
    collect_args: disk_model.FileInputCollectArgs,
    send_args: alert_model.AlertManagerSendArgs,
):
    item = disk_op.read_file(collect_args.format, collect_args.path)
    alert_op.submit_alerts(item)
    return item


@beartype.beartype
def collect_file_input_send_logged_in_users(
    collect_args: disk_model.FileInputCollectArgs,
    send_args: server_model.LoggedInUsersSendArgs,
):
    item = disk_op.read_file(collect_args.format, collect_args.path)
    server_op.user_message(send_args, item)
    return item


@beartype.beartype
def collect_file_input_send_stream_output(
    collect_args: disk_model.FileInputCollectArgs,
    send_args: server_model.StreamOutputSendArgs,
):
    item = disk_op.read_file(collect_args.format, collect_args.path)
    server_op.write_stream(send_args.format, send_args.target, item)
    return item
