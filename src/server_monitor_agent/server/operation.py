"""Operations on a server instance."""

import datetime
import logging
import platform
import socket
import typing

import psutil

from server_monitor_agent.agent import model as agent_model, operation as agent_op
from server_monitor_agent.server import model as server_model

logger = logging.getLogger(f"{agent_model.APP_NAME_UNDER}.device.instance")


def network() -> typing.List[server_model.NetworkResult]:
    """Get the network information."""

    output = []
    result = psutil.net_io_counters(pernic=True)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Result from psutil.net_io_counters with pernic: {result}")

    for name, info in result.items():
        output.append(
            server_model.NetworkResult(
                name=name,
                exit_code=0,
                bytes_recv=info.bytes_recv,
                bytes_sent=info.bytes_sent,
                dropin=info.dropin,
                dropout=info.dropout,
                errin=info.errin,
                errout=info.errout,
                packets_recv=info.packets_recv,
                packets_sent=info.packets_sent,
            )
        )
    return output


def memory() -> server_model.MemoryResult:
    """Get the memory information."""

    result = psutil.virtual_memory()

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Result from psutil.virtual_memory: {result}")

    return server_model.MemoryResult(
        exit_code=0,
        total=result.total,
        available=result.available,
        percent=result.percent,
        used=result.used,
        free=result.free,
        active=getattr(result, "active", 0),
        inactive=getattr(result, "inactive", 0),
        buffers=getattr(result, "buffers", 0),
        cached=getattr(result, "cached", 0),
        wired=getattr(result, "wired", 0),
        shared=getattr(result, "shared", 0),
    )


def hostname() -> str:
    """Get the local hostname."""

    output = None

    if not output:
        output = socket.getfqdn()

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Result from socket.getfqdn: {output}")

    if not output:
        output = platform.node()

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Result from platform.node: {output}")

    if output:
        return output

    raise ValueError("Could not get hostname.")


def timezone() -> server_model.TimeZoneResult:
    """Get the configured local time zone."""

    args = ["timedatectl", "show"]
    result = agent_op.execute_process(args)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Result from '{' '.join(args)}': {result}")

    if result.returncode != 0:
        return server_model.TimeZoneResult(exit_code=result.returncode, raw=None)

    items = dict([i.split("=", maxsplit=1) for i in result.stdout.splitlines()])

    output = items.get("Timezone")
    return server_model.TimeZoneResult(exit_code=result.returncode, raw=output)


def uptime() -> int:
    """Get the time since the local machine booted."""

    output_now = datetime.datetime.now().timestamp()
    output_boot = psutil.boot_time()
    output = int(output_now - output_boot)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            f"Result from datetime.now '{output_now}' "
            f"psutil.boot_time '{output_boot}' "
            f"uptime '{output}'"
        )

    return output


def cpu_usage(interval: float = 2.0) -> float:
    """Get the cpu usage."""

    output = psutil.cpu_percent(interval=interval)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            f"Result from psutil.cpu_percent with interval {interval}: {output}"
        )

    return output


def processes() -> typing.List[server_model.ProcessResult]:
    """Get a list of the local processes."""

    result = []
    attrs = {
        "pid": "PID",
        "memory_percent": "%MEM",
        "name": "COMMAND",
        "cmdline": "COMMAND",
        "cpu_percent": "%CPU",
        "memory_info": ["VSZ", "RSS"],
        "username": "USER",
    }
    count = 0
    for p in psutil.process_iter(list(attrs.keys()), ad_value=None):
        count += 1
        info = p.info

        user = info.get("username") or "(unknown)"
        if user and psutil.WINDOWS and "\\" in user:
            user = user.split("\\")[1]
        user = user[:9]
        pid = info["pid"]
        vms = info["memory_info"].vms or 0
        rss = info["memory_info"].rss or 0

        mem_raw = info["memory_percent"]
        memp = round(mem_raw, 1) if mem_raw is not None else None

        cpu_raw = info["cpu_percent"]
        cpup = round(cpu_raw, 1) if cpu_raw is not None else None

        if info["cmdline"]:
            cmdline = " ".join(info["cmdline"])
        else:
            cmdline = info["name"]

        result.append(
            server_model.ProcessResult(
                exit_code=0,
                user=user,
                pid=pid,
                cpu_percent=cpup,
                mem_percent=memp,
                vms=vms,
                rss=rss,
                cmdline=cmdline,
            )
        )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Result from psutil.process_iter: {count} processes")

    return result


def user_message(
    args: server_model.LoggedInUsersArgs, item: agent_model.AgentItem
) -> None:
    """Submit a message to display to all users logged in to the local machine."""

    user_group = args.user_group
    users = f"users in group {user_group}" if user_group else "all users"

    check_type = item.check_type
    date = item.date
    description = item.description
    host_name = item.host_name
    service_name = item.service_name
    source_name = item.source_name
    status_code = item.status_code
    status_name = item.status_name
    title = item.title

    message = "\n".join(
        [
            f"On {date}, {service_name} (from {source_name}, host {host_name}):",
            "",
            title,
            description,
            "",
            f"Sent to {users}",
            "",
            f"Status: {status_name} ({status_code})",
            f"Check: {check_type}",
        ]
    )

    if not message or not message.strip():
        raise ValueError("Must provide a message to send.")

    cmd = ["wall", "--timeout", "30"]

    if user_group and user_group.strip():
        cmd.extend(["--group", user_group.strip()])

    cmd.append(message)

    result = agent_op.execute_process(cmd)

    if result.returncode != 0:
        raise ValueError(f"Could not send local system message due to :{result}")
