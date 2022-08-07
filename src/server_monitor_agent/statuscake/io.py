from server_monitor_agent.alert_manager import model as alert_model
from server_monitor_agent.disk import model as disk_model
from server_monitor_agent.server import model as server_model, operation as server_op
from server_monitor_agent.statuscake import model as sc_model, operation as sc_op


def collect_statuscake_send_alert_manager(
    collect_args: sc_model.StatusCakeCollectArgs,
    send_args: alert_model.AlertManagerArgs,
):
    raise NotImplementedError()


def collect_statuscake_send_file_output(
    collect_args: sc_model.StatusCakeCollectArgs, send_args: disk_model.FileOutputArgs
):
    raise NotImplementedError()


def collect_statuscake_send_logged_in_users(
    collect_args: sc_model.StatusCakeCollectArgs,
    send_args: server_model.LoggedInUsersArgs,
):
    raise NotImplementedError()


def collect_statuscake_send_stream_output(
    collect_args: sc_model.StatusCakeCollectArgs,
    send_args: server_model.StreamOutputArgs,
):
    raise NotImplementedError()


def collect_statuscake_send_statuscake(
    collect_args: sc_model.StatusCakeCollectArgs,
    send_args: sc_model.StatusCakeSendArgs,
):
    raise NotImplementedError()


def statuscake(
    cmd_name: str, args: sc_model.StatusCakeCollectArgs
) -> sc_model.StatusCakeResult:
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
    return sc_model.StatusCakeResult(
        exit_code=0,
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
