"""Input (parsing) and output (formatting) functions for a server instance."""

import beartype

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

from server_monitor_agent.agent import (
    model as agent_model,
)
from server_monitor_agent.service.alert_manager import (
    model as alert_model,
    operation as alert_op,
)
from server_monitor_agent.service.disk import model as disk_model, operation as disk_op
from server_monitor_agent.service.server import (
    build as server_build,
    model as server_model,
    operation as server_op,
)


@beartype.beartype
def collect_cpu_status_send_alert_manager(
    collect_args: server_model.CpuCollectArgs,
    send_args: alert_model.AlertManagerSendArgs,
):
    item = server_build.cpu_status(collect_args)
    alert_op.submit_alerts(item)
    return item


@beartype.beartype
def collect_cpu_status_send_file_output(
    collect_args: server_model.CpuCollectArgs, send_args: disk_model.FileOutputSendArgs
):
    data = server_build.cpu_status(collect_args)
    item = to_format(send_args.format, data)
    disk_op.write_file(send_args, item)
    return data


@beartype.beartype
def collect_cpu_status_send_stream_output(
    collect_args: server_model.CpuCollectArgs,
    send_args: server_model.StreamOutputSendArgs,
):
    data = server_build.cpu_status(collect_args)
    item = to_user_message(data)
    server_op.write_stream(send_args.format, send_args.target, item)
    return data


@beartype.beartype
def collect_cpu_status_send_logged_in_users(
    collect_args: server_model.CpuCollectArgs,
    send_args: server_model.LoggedInUsersSendArgs,
):
    data = server_build.cpu_status(collect_args)
    item = to_format(send_args.format, data)
    server_op.write_stream(send_args, item)
    return data


@beartype.beartype
def collect_memory_status_send_alert_manager(
    collect_args: server_model.MemoryCollectArgs,
    send_args: alert_model.AlertManagerSendArgs,
):
    data = server_build.device_memory(collect_args)
    item = to_alert_manager(data)
    alert_op.submit_alerts(item)
    return data


@beartype.beartype
def collect_memory_status_send_file_output(
    collect_args: server_model.MemoryCollectArgs,
    send_args: disk_model.FileOutputSendArgs,
):
    data = server_build.device_memory(collect_args)
    item = to_format(send_args.format, data)
    disk_op.write_file(send_args, item)
    return data


@beartype.beartype
def collect_memory_status_send_logged_in_users(
    collect_args: server_model.MemoryCollectArgs,
    send_args: server_model.LoggedInUsersSendArgs,
):
    data = server_build.device_memory(collect_args)
    item = to_user_message(data)
    server_op.user_message(send_args.user_group, item)
    return data


@beartype.beartype
def collect_memory_status_send_stream_output(
    collect_args: server_model.MemoryCollectArgs,
    send_args: server_model.StreamOutputSendArgs,
):
    data = server_build.device_memory(collect_args)
    item = to_format(send_args.format, data)
    server_op.write_stream(send_args, item)
    return data


@beartype.beartype
def collect_stream_input_send_alert_manager(
    collect_args: server_model.StreamInputCollectArgs,
    send_args: alert_model.AlertManagerSendArgs,
):
    data = server_op.read_stream(collect_args.source, collect_args.format)
    item = to_alert_manager(data)
    alert_op.submit_alerts(item)
    return data


@beartype.beartype
def collect_stream_input_send_file_output(
    collect_args: server_model.StreamInputCollectArgs,
    send_args: disk_model.FileOutputSendArgs,
):
    data = server_op.read_stream(collect_args.source, collect_args.format)
    item = to_format(send_args.format, data)
    disk_op.write_file(send_args.format, send_args.path, item)
    return data


@beartype.beartype
def collect_stream_input_send_logged_in_users(
    collect_args: server_model.StreamInputCollectArgs,
    send_args: server_model.LoggedInUsersSendArgs,
):
    data = server_op.read_stream(collect_args.source, collect_args.format)
    item = to_user_message(data)
    server_op.user_message(send_args.user_group, item)
    return data


@beartype.beartype
def collect_stream_input_send_stream_output(
    collect_args: server_model.StreamInputCollectArgs,
    send_args: server_model.StreamOutputSendArgs,
):
    data = server_op.read_stream(collect_args.source, collect_args.format)
    item = to_format(send_args.format, data)
    server_op.write_stream(send_args, item)
    return data


@beartype.beartype
def to_alert_manager(
    data: agent_model.AgentItem,
) -> agent_model.AgentItem:
    return None


@beartype.beartype
def to_format(send_format: str, data: agent_model.AgentItem) -> agent_model.AgentItem:
    return None


@beartype.beartype
def to_user_message(
    data: agent_model.AgentItem,
) -> agent_model.AgentItem:
    return None
