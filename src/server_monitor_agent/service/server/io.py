"""Input (parsing) and output (formatting) functions for a server instance."""
import math

import beartype

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

from server_monitor_agent.agent import model as agent_model, operation as agent_op
from server_monitor_agent.service.server import (
    model as server_model,
    operation as server_op,
)


@beartype.beartype
def stream_input(args: server_model.StreamInputCollectArgs) -> agent_model.AgentItem:
    return server_op.read_stream(args.source, args.format).to_agent_item()


@beartype.beartype
def stream_output(
    args: server_model.StreamOutputSendArgs, item: agent_model.AgentItem
) -> None:
    server_op.write_stream(args.target, item.to_format(args.format))


@beartype.beartype
def users_message_output(
    args: server_model.LoggedInUsersSendArgs, item: agent_model.AgentItem
) -> None:
    server_op.user_message(item, args.user_group)


@beartype.beartype
def cpu_status_input(args: server_model.CpuCollectArgs) -> agent_model.AgentItem:
    """Build the agent item for the device cpu usage."""

    hostname = server_op.hostname()
    date = server_op.timezone().now

    usage = server_op.cpu_usage(interval=args.interval)
    threshold = float(args.threshold) / 100.0

    status, status_code = agent_op.report_evaluate(usage, threshold)

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
        summary=title,
        description=descr.strip(),
        host_name=hostname,
        source_name="server",
        check_name="cpu",
        date=date,
        status_name=status,
        service_name="cpu",
        tags={"threshold": args.threshold, "usage": usage},
    )


@beartype.beartype
def memory_status_input(
    args: server_model.MemoryCollectArgs,
) -> agent_model.AgentItem:
    """Build the agent item for the device memory usage."""

    hostname = server_op.hostname()
    date = server_op.timezone().now

    usage = server_op.memory()
    percent = float(usage.percent) / 100.0
    amount_gib = round(usage.available / (math.pow(1024, 3)), 2)
    threshold = float(args.threshold) / 100.0

    status, status_code = agent_op.report_evaluate(percent, threshold)

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
        summary=title,
        description=descr.strip(),
        host_name=hostname,
        source_name="server",
        check_name="memory",
        date=date,
        status_name=status,
        service_name="memory",
        tags={
            "total": str(usage.total),
            "available": str(usage.available),
            "percent": str(usage.percent),
            "used": str(usage.used),
            "free": str(usage.free),
            "percentage": percent,
            "amount_gib": amount_gib,
            "threshold": threshold,
        },
    )


register_io = [
    agent_model.RegisterCollectInput(cpu_status_input),
    agent_model.RegisterCollectInput(memory_status_input),
    agent_model.RegisterCollectInput(stream_input),
    agent_model.RegisterSendOutput(stream_output),
    agent_model.RegisterSendOutput(users_message_output),
]
