from server_monitor_agent.agent import (
    model as agent_model,
    operation as agent_op,
)
from server_monitor_agent.alert_manager import (
    model as alert_model,
    operation as alert_op,
)
from server_monitor_agent.consul import model as consul_model
from server_monitor_agent.disk import model as disk_model
from server_monitor_agent.server import model as server_model, operation as server_op


def collect_consul_checks_send_alert_manager(
    collect_args: consul_model.HealthCheckCollectArg,
    send_args: alert_model.AlertManagerArgs,
):
    item = health_checks(collect_args)
    alert_op.submit_alerts(send_args, item)
    return item


def collect_consul_checks_send_file_output(
    collect_args: consul_model.HealthCheckCollectArg,
    send_args: disk_model.FileOutputArgs,
):
    item = health_checks(collect_args)
    agent_op.write_file(send_args.format, send_args.path, item)
    return item


def collect_consul_checks_send_logged_in_users(
    collect_args: consul_model.HealthCheckCollectArg,
    send_args: server_model.LoggedInUsersArgs,
):
    item = health_checks(collect_args)
    server_op.user_message(send_args, item)
    return item


def collect_consul_checks_send_stream_output(
    collect_args: consul_model.HealthCheckCollectArg,
    send_args: server_model.StreamOutputArgs,
):
    item = health_checks(collect_args)
    agent_op.write_stream(send_args.format, send_args.target, item)
    return item


def health_checks(args: consul_model.HealthCheckCollectArg) -> agent_model.AgentItem:
    raise NotImplementedError()
