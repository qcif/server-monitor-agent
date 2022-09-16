import dataclasses
import datetime

import beartype

from server_monitor_agent.agent import model as agent_model
from server_monitor_agent.service.server import operation as server_op
from server_monitor_agent.service.systemd import (
    model as systemd_model,
    operation as systemd_op,
)


@beartype.beartype
def unit_status_input(
    args: systemd_model.SystemdUnitStatusCollectArgs,
) -> agent_model.AgentItem:

    show = systemd_op.systemctl_show(args.name)
    if show is None:
        raise ValueError()

    hostname = server_op.hostname()

    status_code = str(show.exit_code) if show.exit_code else None
    if status_code is None:
        status_code = (
            agent_model.REPORT_CODE_PASS
            if show.result == "success"
            else agent_model.REPORT_LEVEL_WARN
        )

    match_attrs = []
    for attribute in args.attributes:
        value = getattr(show, attribute.name)
        match_attrs.extend(attribute.compare(value))

    # determine status
    if status_code == agent_model.REPORT_CODE_PASS:
        status = agent_model.REPORT_LEVEL_PASS
    elif status_code == agent_model.REPORT_CODE_WARN:
        status = agent_model.REPORT_LEVEL_WARN
    else:
        status = agent_model.REPORT_LEVEL_CRIT

    dates_available = [
        show.state_change_time_stamp,
        show.exec_main_exit_timestamp,
        show.exec_main_start_timestamp,
        show.active_exit_timestamp,
        show.active_enter_timestamp,
        show.inactive_exit_timestamp,
        show.inactive_enter_timestamp,
    ]
    date_formats = ["%a %Y-%m-%d %H:%M:%S %Z"]
    date = None
    for date_available in dates_available:
        if date_available:
            for date_format in date_formats:
                try:
                    date = datetime.datetime.strptime(date_available, date_format)
                    break
                except ValueError:
                    pass

    if not date:
        raise ValueError(f"None of the available dates provided a usable date.")

    # TODO: build summary, description
    title = ""
    descr = ""

    return agent_model.AgentItem(
        summary=title,
        description=descr.strip(),
        host_name=hostname,
        source_name="systemd",
        check_name="unit-status",
        date=date,
        status_name=status,
        service_name=args.name,
        extra_data={
            k: v
            for k, v in dataclasses.asdict(show).items()
            if v is not None and v != ""
        },
    )


@beartype.beartype
def unit_logs_input(
    args: systemd_model.SystemdUnitLogsCollectArgs,
) -> agent_model.AgentItem:
    hostname = server_op.hostname()
    date = server_op.timezone().now

    logs = systemd_op.journalctl(args.name)

    extra_data = {}
    log_subset = [i.message for i in sorted(logs, key=lambda x: x.timestamp)][:20]
    for index, log in enumerate(log_subset):
        extra_data[f"log{index + 1}"] = log

    # TODO: build summary, description, status
    title = ""
    descr = ""
    status = agent_model.REPORT_LEVEL_PASS

    return agent_model.AgentItem(
        summary=title,
        description=descr.strip(),
        host_name=hostname,
        source_name="systemd",
        check_name="unit-logs",
        date=date,
        status_name=status,
        service_name=args.name,
        extra_data=extra_data,
    )


register_io = [
    agent_model.RegisterCollectInput(unit_status_input),
    agent_model.RegisterCollectInput(unit_logs_input),
]
