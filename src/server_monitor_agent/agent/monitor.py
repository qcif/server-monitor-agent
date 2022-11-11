from datetime import datetime
from zoneinfo import ZoneInfo

from server_monitor_agent.agent import common, consul, slack


def consul_checks_to_slack(
    time_zone: str, cloud_name: str, conn: consul.ConsulConnection, slack_url: str
):
    slack_items, entries = consul_check_report(time_zone, cloud_name, conn)

    consul_leader_ipv4_port = consul.consul_api_status_leader(conn)
    instance_ipv4 = consul.aws_instance_private_ipv4()

    is_leader = consul_leader_ipv4_port.startswith(instance_ipv4)
    if is_leader:
        consul_leader_text = (
            "This instance is the consul leader. Sending report to Slack."
        )
    else:
        consul_leader_text = (
            "This instance is not the consul leader. Not sending report."
        )

    slack_text = "\n".join(slack_items + [consul_leader_text])

    if is_leader:
        if slack_url and slack_text:
            slack.slack_webhook(slack_url, slack_text)
        else:
            raise ValueError(
                f"Invalid slack url '{slack_url or ''}' or no report text."
            )

    return common.report_ok(
        time_zone=time_zone,
        check_type="consul-report",
        check_name="consul-report",
        description=slack_text,
        resolution="Consul report is successfully generated.",
    )


def consul_check_report(time_zone: str, cloud_name: str, conn: consul.ConsulConnection):
    # checks_cli = consul.consul_cli_watch_checks_any(conn)
    checks_api = consul.consul_api_health_checks_any(conn)
    checks_sorted = sorted(
        checks_api,
        key=lambda x: sort_checks(x.get("Node"), x.get("ServiceName"), x.get("Name")),
    )

    report_date = datetime.now(ZoneInfo(time_zone)).strftime(
        "%a, %d %b %Y at %H:%M:%S %z"
    )

    passing = "passing"
    ok = "ok"
    error = "error"

    ok_nodes = 0
    error_nodes = 0

    checks = {}
    for check in checks_sorted:
        node = check.get("Node")
        # check_id = check.get("CheckID")
        name = check.get("Name")
        status = check.get("Status")
        # notes = check.get("Notes")
        # output = check.get("Output")
        # service_id = check.get("ServiceID")
        service_name = check.get("ServiceName")

        if node not in checks:
            checks[node] = {ok: {}, error: {}}

        check_status = ok if status == passing else error

        if service_name not in checks[node][check_status]:
            checks[node][check_status][service_name] = []

        checks[node][check_status][service_name].append(name)

    entries = []
    for node, node_data in checks.items():
        ok_items = node_data[ok]
        ok_count = len(ok_items)

        error_items = node_data[error]
        error_count = len(error_items)

        if error_count < 1:
            ok_nodes += 1
            continue

        error_nodes += 1

        node1, node2 = node.split(".", maxsplit=1)
        entries.append(
            f"-> *{node1}*.{node2} ({error}: {error_count}, {ok}: {ok_count})"
        )

        services_checks = sorted(error_items.items())
        if len(services_checks) > 5:
            rest = services_checks[5:]
            rest_service_count = len([k for k, v in rest])
            rest_checks = [i for k, v in rest for i in v]
            services_checks = services_checks[0:5]
            services_checks.append(
                (f"...and {rest_service_count} more services", rest_checks)
            )

        for service, service_checks in services_checks:
            service_check = (
                ",".join(sorted(service_checks))
                if len(service_checks) < 4
                else f"{len(service_checks)} checks"
            )
            entries.append(f"    - {service or '(instance)'}: {service_check}")

    total_nodes = ok_nodes + error_nodes
    percent_error = round((error_nodes / total_nodes) * 100.0, 1)

    slack_items = [
        f"*{cloud_name}* Consul Daily Error Report {report_date}",
        f"There are {total_nodes} instances, "
        f"{error_nodes} have errors ({percent_error}%).",
        "",
        "These service checks are in a _critical_ or _warning_ state:",
        "```",
        *entries,
        "---",
        "```",
    ]
    return slack_items, entries


def sort_checks(node: str, service: str, check: str):
    key = []

    if "consul" in node:
        key.append("01")
    elif "prod" in node:
        key.append("02")
    elif "test" in node:
        key.append("03")
    else:
        key.append("04")

    key.append(node)
    key.append(service)
    key.append(check)
    return "-".join(key)
