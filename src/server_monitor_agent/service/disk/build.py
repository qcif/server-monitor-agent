import beartype
from boltons import strutils

from server_monitor_agent.agent import (
    model as agent_model,
    operation as agent_operation,
)
from server_monitor_agent.service.disk import model as disk_model, operation as disk_op
from server_monitor_agent.service.server import operation as server_op


@beartype.beartype
def disk_status(args: disk_model.DiskCollectArgs) -> agent_model.AgentItem:
    """Build the agent item for the device disk usage."""

    hostname = server_op.hostname()
    date = server_op.timezone().now

    mnt = disk_op.disk_mounts(args)
    partition = disk_op.disk_partitions(args, mnt)

    usage = partition.percent_usage
    test = float(args.threshold) / 100.0
    status, status_code = agent_operation.report_evaluate(usage, test)

    mount_point = partition.mountpoint
    path = mnt.target

    if status == agent_model.REPORT_LEVEL_PASS:
        title = f"Typical disk {path} use"
        descr = (
            f"Typical disk {path} ({mount_point}) "
            f"use of {usage:.1%} (threshold {test:.1%})."
        )
    else:
        title = f"High disk {path} use"
        descr = (
            f"High disk {path} ({mount_point}) "
            f"use of {usage:.1%} (threshold {test:.1%}). "
            "Check instance for excessive log files or "
            "increased application storage use."
        )

    return agent_model.AgentItem(
        service_name=f"disk {path}",
        host_name=hostname,
        source_name="instance",
        status_code=status_code,
        status_name=status,
        title=title,
        description=descr.strip(),
        check_type=cmd_name,
        date=date,
        tags={
            "fstype": str(partition.fstype),
            "device": str(partition.device),
            "uuid": str(mnt.uuid),
            "options": str(mnt.options),
            "total": str(strutils.bytes2human(partition.total)),
            "free": str(strutils.bytes2human(partition.free)),
            "used": str(strutils.bytes2human(partition.used)),
        },
    )


@beartype.beartype
def file_status(args: disk_model.FileStatusCollectArgs) -> agent_model.AgentItem:
    """Build the agent item for a file status."""

    if not args.path:
        raise ValueError("Must specify path to check.")

    if args.state == "absent" and args.content:
        raise ValueError(
            "Cannot specify content "
            f"when file is expected to be absent for '{args.path}'."
        )

    if not args.path.is_absolute():
        raise ValueError(f"Must provide an absolute path '{args.path}'.")

    states_present = "present"
    states_absent = "absent"
    states_available = [states_present, states_absent]

    if args.state not in states_available:
        raise ValueError(
            f"State must be one of '{', '.join(states_available)}' "
            f"for check '{cmd_name}'."
        )

    content_contains = "contains"
    content_not_contains = "not_contains"
    content_available = [content_contains, content_not_contains]

    exists = args.path.exists()

    if exists:
        stat = args.path.stat()
        max_bytes = 20000000  # 20MB
        if stat.st_size > max_bytes:
            raise ValueError(
                "Cannot check a file larger than 20MB: "
                f"'{args.path}' is {strutils.bytes2human(stat.st_size)}."
            )

    hostname = server_op.hostname()
    date = server_op.timezone().now

    status = agent_model.REPORT_LEVEL_PASS
    status_code = agent_model.REPORT_CODE_PASS

    descr_state = ""
    if args.state == states_present and exists:
        status = agent_model.REPORT_LEVEL_PASS
        status_code = agent_model.REPORT_CODE_PASS
        descr_state = "File was found, as expected."

    if args.state == states_present and not exists:
        status = agent_model.REPORT_LEVEL_CRIT
        status_code = agent_model.REPORT_CODE_CRIT
        descr_state = "Could not find file in expected path."

    if args.state == "absent" and not exists:
        status = agent_model.REPORT_LEVEL_PASS
        status_code = agent_model.REPORT_CODE_PASS
        descr_state = "File was absent, as expected."

    if args.state == "absent" and exists:
        status = agent_model.REPORT_LEVEL_CRIT
        status_code = agent_model.REPORT_CODE_CRIT
        descr_state = "Found file that was expected to not exist."

    if args.content:
        file_content = args.path.read_text("utf8")
    else:
        file_content = ""

    descr_content = []
    for i in args.content:
        if i.comparison not in content_available:
            raise ValueError(f"Unknown file content comparison '{i.comparison}'.")

        has_content = i.value in file_content
        if i.comparison == content_contains and not has_content:
            status = agent_model.REPORT_LEVEL_CRIT
            status_code = agent_model.REPORT_CODE_CRIT
            descr_content.append(f"File did not contain expected content '{i.value}'.")

        if i.comparison == content_contains and has_content:
            descr_content.append(f"File contains expected content '{i.value}'.")

        if i.comparison == content_not_contains and has_content:
            status = agent_model.REPORT_LEVEL_CRIT
            status_code = agent_model.REPORT_CODE_CRIT
            descr_content.append(f"File contains unexpected content '{i.value}'.")

        if i.comparison == content_not_contains and not has_content:
            descr_content.append(
                f"File does not contain content '{i.value}', as expected."
            )

    path = args.path

    if status == agent_model.REPORT_LEVEL_PASS:
        title = f"Expected file {path} state"
        descr = (
            f"Expected file {path} state. "
            f"{descr_state} "
            f"{' '.join(descr_content)}"
        )
    else:
        title = f"Unexpected file {path} state"
        descr = (
            f"Unexpected file {path} state. "
            f"{descr_state} "
            f"{' '.join(descr_content)}"
            " Check instance for excessive log files or "
            "increased application storage use."
        )

    return agent_model.AgentItem(
        service_name=f"file {path}",
        host_name=hostname,
        source_name="instance",
        status_code=status_code,
        status_name=status,
        title=title,
        description=descr.strip(),
        check_type=cmd_name,
        date=date,
    )
