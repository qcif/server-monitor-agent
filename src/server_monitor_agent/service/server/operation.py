"""Operations on a server instance."""

import datetime
import logging
import platform
import socket
import sys

import beartype
import psutil
from beartype import typing

from server_monitor_agent.agent import model as agent_model, operation as agent_op
from server_monitor_agent.service.server import model as server_model

logger = logging.getLogger(f"{agent_model.APP_NAME_UNDER}.device.instance")


@beartype.beartype
def network() -> typing.List[server_model.NetworkResult]:
    """Get the network information."""

    output = []
    result = psutil.net_io_counters(pernic=True)

    agent_op.log_msg(
        logging.DEBUG, f"Result from psutil.net_io_counters with pernic: {result}"
    )

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


@beartype.beartype
def memory() -> server_model.MemoryResult:
    """Get the memory information."""

    result = psutil.virtual_memory()

    agent_op.log_msg(logging.DEBUG, f"Result from psutil.virtual_memory: {result}")

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


@beartype.beartype
def hostname() -> str:
    """Get the local hostname."""

    output = None

    if not output:
        output = socket.getfqdn()

        agent_op.log_msg(logging.DEBUG, f"Result from socket.getfqdn: {output}")

    if not output:
        output = platform.node()

        agent_op.log_msg(logging.DEBUG, f"Result from platform.node: {output}")

    if output:
        return output

    raise ValueError("Could not get hostname.")


@beartype.beartype
def timezone() -> server_model.TimeZoneResult:
    """Get the configured local time zone."""

    args = ["timedatectl", "show"]
    result = agent_op.execute_process(args)

    agent_op.log_msg(logging.DEBUG, f"Result from '{' '.join(args)}': {result}")

    if result.returncode != 0:
        return server_model.TimeZoneResult(exit_code=result.returncode, raw=None)

    items = dict([i.split("=", maxsplit=1) for i in result.stdout.splitlines()])

    output = items.get("Timezone")
    return server_model.TimeZoneResult(exit_code=result.returncode, raw=output)


@beartype.beartype
def uptime() -> int:
    """Get the time since the local machine booted."""

    output_now = datetime.datetime.now().timestamp()
    output_boot = psutil.boot_time()
    output = int(output_now - output_boot)

    agent_op.log_msg(
        logging.DEBUG,
        f"Result from datetime.now '{output_now}' "
        f"psutil.boot_time '{output_boot}' "
        f"uptime '{output}'",
    )

    return output


@beartype.beartype
def cpu_usage(interval: float = 2.0) -> float:
    """Get the cpu usage."""

    output = psutil.cpu_percent(interval=interval)

    agent_op.log_msg(
        logging.DEBUG,
        f"Result from psutil.cpu_percent with interval {interval}: {output}",
    )

    return float(output)


@beartype.beartype
def processes() -> typing.List[server_model.ProcessResult]:
    """Get a list of the local processes."""

    # Note: Linux doesn't seem to expose easily usable per-process network stats.
    #       Maybe `sudo lsof -niTCP` combined with `iftop`?
    #       See https://github.com/giampaolo/psutil/issues/1900

    result = []
    attrs = {
        "pid": "PID",
        "memory_percent": "%MEM",
        "name": "COMMAND",
        "cmdline": "COMMAND",
        "cpu_percent": "%CPU",
        "memory_info": ["VSZ", "RSS"],
        "username": "USER",
        "io_counters": "",
        "cpu_times": "",
    }
    count = 0
    for p in psutil.process_iter(attrs=list(attrs.keys()), ad_value=None):
        count += 1
        info = p.info if hasattr(p, "info") else p

        user = info.get("username") or "(unknown)"
        if user and psutil.WINDOWS and "\\" in user:
            user = user.split("\\")[1]
        user = user[:9]
        pid = info.get("pid")
        vms = info.get("memory_info").vms if info.get("memory_info") else 0
        rss = info.get("memory_info").rss if info.get("memory_info") else 0

        # ignore a process that is using no memory
        if (vms + rss) < 1:
            continue

        # note that memory percent can be 0 if there is no previous information
        mem_raw = info.get("memory_percent")
        mem_p = round(mem_raw, 1) if mem_raw is not None else None

        # note that cpu percent can be 0 if there is no previous information
        cpu_raw = info.get("cpu_percent")
        cpu_p = round(cpu_raw, 1) if cpu_raw is not None else None

        if info.get("cmdline"):
            cmdline = " ".join(info["cmdline"])
        else:
            cmdline = info.get("name")

        io_counters = info.get("io_counters")
        io_read_ops_count = io_counters.read_count
        io_write_ops_count = io_counters.write_count
        io_read_bytes_count = io_counters.read_bytes
        io_write_bytes_count = io_counters.write_bytes

        cpu_times = info.get("cpu_times")
        cpu_time_count = cpu_times.user + cpu_times.system

        cpu_usable_count = len(p.cpu_affinity())

        result.append(
            server_model.ProcessResult(
                exit_code=0,
                user=user,
                pid=pid,
                cpu_percent=cpu_p,
                mem_percent=mem_p,
                vms=vms,
                rss=rss,
                cmdline=cmdline,
                io_read_ops_count=io_read_ops_count,
                io_write_ops_count=io_write_ops_count,
                io_read_bytes_count=io_read_bytes_count,
                io_write_bytes_count=io_write_bytes_count,
                cpu_time_count=cpu_time_count,
                cpu_usable_count=cpu_usable_count,
            )
        )

    agent_op.log_msg(
        logging.DEBUG, f"Result from psutil.process_iter: {count} processes"
    )

    return result


@beartype.beartype
def user_message(
    item: agent_model.AgentItem, user_group: typing.Optional[str] = None
) -> None:
    """Submit a message to display to all users logged in to the local machine."""
    users = f"users in group {user_group}" if user_group else "all users"

    summary = item.summary
    description = item.description
    host_name = item.host_name
    source_name = item.source_name
    check_name = item.check_name
    date = item.date
    status_name = item.status_name
    service_name = item.service_name
    extra_data = item.extra_data

    date_format = "%a, %d %b %Y %H:%M:%S %Z"
    message = "\n".join(
        [
            f"On {date.strftime(date_format)}, {service_name} (from {source_name}, host {host_name}):",
            "",
            summary,
            description,
            "",
            f"Sent to {users}",
            "",
            f"Status: {status_name}",
            f"Check: {check_name}",
            f"Tags:",
            *[f"{k}={v}" for k, v in extra_data.items()],
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


@beartype.beartype
def write_stream(out_target: str, content: str) -> None:
    if out_target == agent_model.STREAM_STDOUT:
        sys.stdout.write(content)

    elif out_target == agent_model.STREAM_STDERR:
        sys.stderr.write(content)

    else:
        agent_op.raise_options("stream target", out_target, agent_model.STREAM_TARGETS)


@beartype.beartype
def read_stream(in_source: str) -> str:
    if in_source == agent_model.STREAM_STDIN:
        return sys.stdin.read()

    agent_op.raise_options("stream source", in_source, agent_model.STREAM_SOURCES)
