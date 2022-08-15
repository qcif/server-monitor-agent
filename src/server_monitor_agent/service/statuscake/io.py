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
    uptime = server_op.uptime()

    memory = server_op.memory()
    mem_free = int(memory.available / 1024)
    mem_total = int(memory.total / 1024)

    hdd, thdd, drive_str = sc_op.disks()

    first = server_op.network()
    cpu_use = server_op.cpu_usage(args.interval)
    second = server_op.network()

    rx = int((second["rx"] - first["rx"]) / (args.interval * 1024))
    tx = int((second["tx"] - first["tx"]) / (args.interval * 1024))

    process = server_op.processes()

    ping = ""
    return agent_model.AgentItem(
        rx=rx,
        tx=tx,
        process=process,
        drives=drive_str,
        ping=ping,
        freeMem=mem_free,
        MemTotal=mem_total,
        cpuUse=cpu_use,
        uptime=uptime,
        hdd=int(hdd),
        thdd=int(thdd),
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
