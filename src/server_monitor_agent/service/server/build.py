import math

import beartype

from server_monitor_agent.agent import (
    model as agent_model,
    operation as agent_operation,
)
from server_monitor_agent.service.server import (
    model as server_model,
    operation as server_op,
)


@beartype.beartype
def cpu_status(args: server_model.CpuCollectArgs) -> agent_model.AgentItem:
    """Build the agent item for the device cpu usage."""

    hostname_result = server_op.hostname()
    date = server_op.timezone().now

    usage = server_op.cpu_usage(interval=args.interval)
    threshold = float(args.threshold) / 100.0

    status, status_code = agent_operation.report_evaluate(usage, threshold)

    if status == agent_model.REPORT_LEVEL_PASS:
        title = "Typical CPU use"
        descr = f"Typical CPU use of {usage:.1%} " f"(threshold {threshold:.1%})."
    else:
        title = "High CPU use"
        descr = (
            f"High CPU use of {usage:.1%} "
            f"(threshold {threshold:.1%}). "
            f"Check instance for unexpected or faulty processes."
        )

    return agent_model.AgentItem(
        service_name="cpu",
        host_name=hostname_result,
        source_name=args.io_module,
        status_code=status_code,
        status_name=status,
        title=title,
        description=descr.strip(),
        check_type=args.io_func_prefix,
        date=date,
        tags={},
    )


@beartype.beartype
def device_memory(
    args: server_model.MemoryCollectArgs,
) -> agent_model.AgentItem:
    """Build the agent item for the device memory usage."""

    hostname = server_op.hostname()
    date = server_op.timezone().now

    usage = server_op.memory()
    percent = float(usage.percent) / 100.0
    amount_gib = round(usage.available / (math.pow(1024, 3)), 2)
    threshold = float(args.threshold) / 100.0

    status, status_code = agent_operation.report_evaluate(percent, threshold)

    if status == agent_model.REPORT_LEVEL_PASS:
        title = "Typical memory use"
        descr = (
            f"Typical memory use of {percent:.1%} "
            f"({amount_gib}GiB, threshold {threshold:.1%})."
        )
    else:
        title = "High memory use"
        descr = (
            f"High memory use of {percent:.1%} "
            f"({amount_gib}GiB, threshold {threshold:.1%}). "
            f"Check instance for excessive or changed memory use."
        )

    return agent_model.AgentItem(
        service_name="memory",
        host_name=hostname,
        source_name="instance",
        status_code=status_code,
        status_name=status,
        title=title,
        description=descr.strip(),
        check_type=cmd_name,
        date=date,
        tags={
            "total": str(usage.total),
            "available": str(usage.available),
            "percent": str(usage.percent),
            "used": str(usage.used),
            "free": str(usage.free),
        },
    )
