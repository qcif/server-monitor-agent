import beartype

from server_monitor_agent.agent import model as agent_model
from server_monitor_agent.service.server import (
    operation as server_op,
)
from server_monitor_agent.service.statuscake import (
    model as sc_model,
    operation as sc_op,
)


@beartype.beartype
def statuscake_input(
    args: sc_model.StatusCakeCollectArgs,
) -> agent_model.AgentItem:

    hostname = server_op.hostname()
    date = server_op.timezone().now

    uptime = server_op.uptime()

    memory = server_op.memory()
    mem_free = int(memory.available / 1024)
    mem_total = int(memory.total / 1024)

    hdd, thdd, drive_str = sc_op.disks()

    first = sc_op.network()
    cpu_use = server_op.cpu_usage(args.interval)
    second = sc_op.network()

    rx = int((second["rx"] - first["rx"]) / (args.interval * 1024))
    tx = int((second["tx"] - first["tx"]) / (args.interval * 1024))

    process = sc_op.processes()

    ping = ""

    items = {
        "rx": rx,
        "tx": tx,
        "process": process,
        "drives": drive_str,
        "ping": ping,
        "freeMem": mem_free,
        "MemTotal": mem_total,
        "cpuUse": cpu_use,
        "uptime": uptime,
        "hdd": int(hdd),
        "thdd": int(thdd),
    }

    # TODO: build summary, description, status
    title = ""
    descr = ""
    status = agent_model.REPORT_LEVEL_PASS

    return agent_model.AgentItem(
        summary=title,
        description=descr.strip(),
        host_name=hostname,
        source_name="server",
        check_name="statuscake",
        date=date,
        status_name=status,
        service_name="statuscake",
        extra_data={
            "statuscake_agent_items": items,
            "interval": args.interval,
        },
    )


@beartype.beartype
def statuscake_output(
    args: sc_model.StatusCakeSendArgs, item: agent_model.AgentItem
) -> None:
    sc_op.submit_statuscake(item)


register_io = [
    agent_model.RegisterCollectInput(statuscake_input),
    agent_model.RegisterSendOutput(statuscake_output),
]
