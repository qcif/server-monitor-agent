import argparse
import os
import pathlib
import typing

from server_monitor_agent.agent import consul, instance, monitor, service, common


def memory_usage_cli(args: argparse.Namespace):
    time_zone = args.time_zone
    threshold = args.threshold
    return instance.memory_usage_detail(time_zone, threshold)


def cpu_usage_cli(args: argparse.Namespace):
    time_zone = args.time_zone
    threshold = args.threshold
    interval = args.interval
    return instance.cpu_usage_detail(time_zone, threshold, interval)


def disk_usage_cli(args: argparse.Namespace):
    time_zone = args.time_zone
    threshold = args.threshold
    mount_path = args.mount_path
    return instance.disk_usage_detail(time_zone, threshold, mount_path)


def systemd_service_cli(args: argparse.Namespace):
    time_zone = args.time_zone
    name = args.name
    load_state = args.expected_load_state
    active_state = args.expected_active_state
    file_state = args.expected_file_state
    sub_state = args.expected_sub_state
    result_state = args.expected_result_state
    max_age_hours = args.max_age_hours
    return service.service_detail(
        time_zone,
        name,
        load_state,
        active_state,
        file_state,
        sub_state,
        result_state,
        max_age_hours,
    )


def systemd_timer_cli(args: argparse.Namespace):
    time_zone = args.time_zone
    name = args.name
    load_state = args.expected_load_state
    active_state = args.expected_active_state
    file_state = args.expected_file_state
    sub_state = args.expected_sub_state
    result_state = args.expected_result_state
    return service.timer_detail(
        time_zone, name, load_state, active_state, file_state, sub_state, result_state
    )


def consul_report_cli(args: argparse.Namespace):
    time_zone = args.time_zone
    cloud_name = args.cloud_name

    # get consul connection info and slack url from env vars
    http_addr = os.getenv("CONSUL_HTTP_ADDR") or None
    http_ssl = os.getenv("CONSUL_HTTP_SSL") or None
    http_ssl_verify = os.getenv("CONSUL_HTTP_SSL_VERIFY") or None
    ca_cert = os.getenv("CONSUL_CACERT") or None
    ca_path = os.getenv("CONSUL_CAPATH") or None
    client_cert = os.getenv("CONSUL_CLIENT_CERT") or None
    client_key = os.getenv("CONSUL_CLIENT_KEY") or None
    conn = consul.ConsulConnection(
        http_ssl_enabled=http_ssl == "true",
        http_ssl_verify=http_ssl_verify == "true",
        http_addr=http_addr,
        ca_cert_file=pathlib.Path(ca_cert) if ca_cert else None,
        ca_cert_dir=pathlib.Path(ca_path) if ca_path else None,
        client_cert=pathlib.Path(client_cert) if client_cert else None,
        client_key=pathlib.Path(client_key) if client_key else None,
    )

    slack_url = os.getenv("SLACK_WEBHOOK_URL_CONSUL")
    return monitor.consul_checks_to_slack(time_zone, cloud_name, conn, slack_url)


def build():
    parser = argparse.ArgumentParser(
        prog=common.APP_NAME_DASH,
        description="Run a check on the local machine.",
        allow_abbrev=False,
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {common.get_version()}"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Turn on debug mode.",
    )
    subparsers = parser.add_subparsers(
        title="Available checks",
        description="Specify the check command to run",
        metavar="check_command",
        dest="subparser_name",
    )

    # subparser: memory
    parser_memory_usage = subparsers.add_parser(
        "memory",
        help="Check the current memory usage.",
    )
    add_common_arguments(parser_memory_usage)
    parser_memory_usage.add_argument(
        "--threshold",
        type=int,
        default=80,
        help="Warn over this percentage use (range 0 - 100, default 80).",
    )
    parser_memory_usage.set_defaults(func=memory_usage_cli)

    # subparser: cpu
    parser_cpu_usage = subparsers.add_parser(
        "cpu",
        help="Check the current cpu usage.",
    )
    add_common_arguments(parser_cpu_usage)
    parser_cpu_usage.add_argument(
        "--threshold",
        type=int,
        default=80,
        help="Warn over this percentage use (range 0 - 100, default 80).",
    )
    parser_cpu_usage.add_argument(
        "--interval",
        type=float,
        default=2,
        help="The number of seconds to wait between CPU samples (range 0 - 10, default 2).",
    )
    parser_cpu_usage.set_defaults(func=cpu_usage_cli)

    # subparser: disk
    parser_disk_usage = subparsers.add_parser(
        "disk",
        help="Check the current free space for a disk.",
    )
    add_common_arguments(parser_disk_usage)
    parser_disk_usage.add_argument(
        "--mount-path",
        type=pathlib.Path,
        default=pathlib.Path("/"),
        help="The mount path of the disk to check (default '/').",
    )
    parser_disk_usage.add_argument(
        "--threshold",
        type=int,
        default=80,
        help="Warn over this percentage used space (range 0 - 100, default 80).",
    )
    parser_disk_usage.set_defaults(func=disk_usage_cli)

    # subparser: systemd service
    parser_systemd_service = subparsers.add_parser(
        "systemd-service",
        help="Check the current status of a systemd service.",
    )
    add_common_arguments(parser_systemd_service)
    parser_systemd_service.add_argument(
        "name",
        help="The name of the service to check.",
    )
    add_systemd_unit_arguments(
        parser_systemd_service,
        [
            "dead",
            "condition",
            "start-pre",
            "start",
            "start-post",
            "running",
            "exited",
            "reload",
            "stop",
            "stop-watchdog",
            "stop-sigterm",
            "stop-sigkill",
            "stop-post",
            "final-sigterm",
            "final-sigkill",
            "failed",
            "auto-restart",
            "cleaning",
        ],
        [
            "start-pre",
            "start",
            "start-post",
            "running",
            "reload",
            "auto-restart",
        ],
    )
    parser_systemd_service.add_argument(
        "--expected-result-state",
        action="extend",
        nargs="+",
        type=str,
        default=list(["success"]),
        choices=[
            "success",
            "protocol",
            "timeout",
            "exit-code",
            "signal",
            "core-dump",
            "watchdog",
            "start-limit-hit",
            "resources",
        ],
        help="The expected result status of the process controlled by this service "
        "(default 'success').",
    )
    parser_systemd_service.add_argument(
        "--max-age-hours",
        type=float,
        help="The maximum allowed time since the service last changed state.",
    )
    parser_systemd_service.set_defaults(func=systemd_service_cli)

    # subparser: systemd timer
    parser_systemd_timer = subparsers.add_parser(
        "systemd-timer",
        help="Check the current status of a systemd timer.",
    )
    add_common_arguments(parser_systemd_timer)
    parser_systemd_timer.add_argument(
        "name",
        help="The name of the timer to check.",
    )
    add_systemd_unit_arguments(
        parser_systemd_timer,
        [
            "dead",
            "waiting",
            "running",
            "elapsed",
            "failed",
        ],
        ["waiting", "running"],
    )
    parser_systemd_timer.add_argument(
        "--expected-result-state",
        action="extend",
        nargs="+",
        type=str,
        default=list(["success"]),
        choices=[
            "success",
        ],
        help="The expected result status of the service controlled by this timer "
        "(default 'success').",
    )
    parser_systemd_timer.set_defaults(func=systemd_timer_cli)

    # subparser: consul report
    parser_consul_report = subparsers.add_parser(
        "consul-report",
        help="Report the current state of all consul checks for this datacenter.",
    )
    add_common_arguments(parser_consul_report)
    parser_consul_report.add_argument(
        "cloud_name",
        help="The name of the cloud provider.",
    )
    parser_consul_report.set_defaults(func=consul_report_cli)

    return parser


def add_common_arguments(parser):
    parser.add_argument(
        "--time_zone",
        default="Australia/Brisbane",
        help="The timezone to use for dates and times.",
    )


def add_systemd_unit_arguments(
    parser, sub_state_options: typing.List[str], sub_state_default: typing.List[str]
):
    # system stats - find the states using systemctl --state=help

    parser.add_argument(
        "--expected-load-state",
        action="extend",
        nargs="+",
        type=str,
        default=list(["loaded"]),
        choices=[
            "stub",
            "loaded",
            "not-found",
            "bad-setting",
            "error",
            "merged",
            "masked",
        ],
        help="The expected unit definition state " "(default 'loaded').",
    )
    parser.add_argument(
        "--expected-file-state",
        action="extend",
        nargs="+",
        type=str,
        default=list(["enabled", "enabled-runtime"]),
        choices=[
            "enabled",
            "enabled-runtime",
            "linked",
            "linked-runtime",
            "masked",
            "masked-runtime",
            "static",
            "disabled",
            "indirect",
            "generated",
            "transient",
            "bad",
        ],
        help="The expected unit file state " "(default 'enabled,enabled-runtime').",
    )
    parser.add_argument(
        "--expected-active-state",
        action="extend",
        nargs="+",
        type=str,
        default=list(["active", "reloading", "activating"]),
        choices=[
            "active",
            "reloading",
            "inactive",
            "failed",
            "activating",
            "deactivating",
            "maintenance",
        ],
        help="The expected unit activation state "
        "(default 'active,reloading,activating').",
    )

    parser.add_argument(
        "--expected-sub-state",
        action="extend",
        nargs="+",
        type=str,
        default=list(sub_state_default),
        choices=sub_state_options,
        help=f"The expected sub-state (default '{sorted(sub_state_default)}').",
    )
