import dataclasses

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
    logs = systemd_op.journalctl(args.name)

    hostname = server_op.hostname()

    status_code = str(show.exit_code) if show.exit_code else None
    if status_code is None:
        status_code = (
            agent_model.REPORT_CODE_PASS
            if show.result == "success"
            else agent_model.REPORT_LEVEL_WARN
        )

    # determine status
    if level:
        status = level
    elif status_code == agent_model.REPORT_CODE_PASS:
        status = agent_model.REPORT_LEVEL_PASS
    elif status_code == agent_model.REPORT_CODE_WARN:
        status = agent_model.REPORT_LEVEL_WARN
    else:
        status = agent_model.REPORT_LEVEL_CRIT

    date = args.date_parse(
        show.state_change_time_stamp
        or show.exec_main_exit_timestamp
        or show.exec_main_start_timestamp
        or show.active_exit_timestamp
        or show.active_enter_timestamp
        or show.inactive_exit_timestamp
        or show.inactive_enter_timestamp
    )

    title = ""
    descr = ""

    tags = {
        k: v for k, v in dataclasses.asdict(show).items() if v is not None and v != ""
    }

    log_subset = [i.message for i in sorted(logs, key=lambda x: x.timestamp)][:6]
    for index, log in enumerate(log_subset):
        tags[f"log{index + 1}"] = log

    return agent_model.AgentItem(
        service_name=f"systemd unit {args.name}",
        host_name=hostname,
        source_name="systemd",
        status_code=status_code,
        status_name=status,
        title=title,
        description=descr.strip(),
        check_type=cmd_name,
        date=date,
        tags=tags,
    )


@beartype.beartype
def unit_logs_input(
    args: systemd_model.SystemdUnitLogsCollectArgs,
) -> agent_model.AgentItem:

    # return agent_model.AgentItem(
    #     service_name=f"journald logs {args.name}",
    #     host_name=hostname,
    #     source_name="systemd",
    #     status_code=status_code,
    #     status_name=status,
    #     title=title,
    #     description=descr.strip(),
    #     check_type=cmd_name,
    #     date=date,
    #     tags=tags,
    # )
    return agent_model.AgentItem()


register_io = [
    agent_model.RegisterCollectInput(unit_status_input),
    agent_model.RegisterCollectInput(unit_logs_input),
]
