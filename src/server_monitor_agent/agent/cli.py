from __future__ import annotations
import argparse
import os
import pathlib

from server_monitor_agent.agent import common, consul, instance, monitor, service


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
    expected_type = service.SERVICE_EXPECTED_STATES[args.expected_type]
    load_state = expected_type["load"]
    active_state = expected_type["active"]
    file_state = expected_type["file"]
    sub_state = expected_type["sub"]
    result_state = expected_type["result"]
    exec_main_status = expected_type["ExecMainStatus"]
    max_age_hours = args.max_age_hours
    return service.service_detail(
        time_zone,
        name,
        load_state,
        active_state,
        file_state,
        sub_state,
        result_state,
        exec_main_status,
        max_age_hours,
    )


def systemd_timer_cli(args: argparse.Namespace):
    time_zone = args.time_zone
    name = args.name
    expected_type = service.TIMER_EXPECTED_STATES[args.expected_type]
    load_state = expected_type["load"]
    active_state = expected_type["active"]
    file_state = expected_type["file"]
    sub_state = expected_type["sub"]
    result_state = expected_type["result"]
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
    parser_systemd_service.add_argument(
        "expected_type",
        type=str,
        choices=sorted(service.SERVICE_EXPECTED_STATES.keys()),
        help="The expected behaviour of the service.",
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
    parser_systemd_timer.add_argument(
        "expected_type",
        type=str,
        choices=sorted(service.TIMER_EXPECTED_STATES.keys()),
        help="The expected behaviour of the timer.",
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
