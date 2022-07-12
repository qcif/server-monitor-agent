import json
import platform
import socket
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import psutil

from server_monitor_agent.common import ProgramMixin
from server_monitor_agent.common import ResultMixin


@dataclass
class FindMntResult(ResultMixin):
    name: str
    target: Optional[str] = None
    source: Optional[str] = None
    size: Optional[int] = None
    fstype: Optional[str] = None
    uuid: Optional[str] = None
    options: Optional[str] = None
    label: Optional[str] = None


@dataclass
class LsBlkResult(ResultMixin):
    name: Optional[str] = None
    size: Optional[int] = None
    mountpoint: Optional[str] = None
    serial: Optional[str] = None
    type: Optional[str] = None


@dataclass
class DfResult(ResultMixin):
    source: Optional[str] = None
    fstype: Optional[str] = None
    size: Optional[str] = None
    used: Optional[str] = None
    available: Optional[str] = None
    percent: Optional[float] = None
    from_file: Optional[str] = None
    target: Optional[str] = None


@dataclass
class ProcessResult(ResultMixin):
    user: Optional[str] = None
    pid: Optional[int] = None
    cpu_percent: Optional[float] = None
    mem_percent: Optional[float] = None
    vms: Optional[int] = None
    rss: Optional[int] = None
    cmdline: Optional[str] = None


@dataclass
class NetworkResult(ResultMixin):
    name: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int


@dataclass
class MemoryResult(ResultMixin):
    total: int
    available: int
    percent: int
    used: int
    free: int
    active: int
    inactive: int
    buffers: int
    cached: int
    wired: int
    shared: int


@dataclass
class PartitionResult(ResultMixin):
    device: str
    mountpoint: str
    fstype: str
    opts: str
    maxfile: int
    maxpath: int
    total: int
    used: int
    free: int
    percent: float


class LocalProgram(ProgramMixin):
    def hostname(self) -> str:
        hostname = ""

        if not hostname:
            hostname = socket.getfqdn()

        if not hostname:
            hostname = platform.node()

        return hostname

    def timezone(self) -> Optional[str]:
        args = ["timedatectl", "show"]
        result = self._run_cmd(args)
        if result.returncode != 0:
            return None

        items = dict([i.split("=", maxsplit=1) for i in result.stdout.splitlines()])
        return items.get("Timezone")

    def uptime(self) -> int:
        return int(datetime.now().timestamp() - psutil.boot_time())

    def cpu_usage(self, interval: float = 2.0) -> float:
        return psutil.cpu_percent(interval=interval)

    def memory(self) -> MemoryResult:
        memory = psutil.virtual_memory()
        return MemoryResult(
            exit_code=0,
            total=memory.total,
            available=memory.available,
            percent=memory.percent,
            used=memory.used,
            free=memory.free,
            active=getattr(memory, "active", 0),
            inactive=getattr(memory, "inactive", 0),
            buffers=getattr(memory, "buffers", 0),
            cached=getattr(memory, "cached", 0),
            wired=getattr(memory, "wired", 0),
            shared=getattr(memory, "shared", 0),
        )

    def partitions(self) -> list[PartitionResult]:
        output = []
        for partition in psutil.disk_partitions():
            usage = psutil.disk_usage(partition.mountpoint)
            output.append(
                PartitionResult(
                    exit_code=0,
                    device=partition.device,
                    mountpoint=partition.mountpoint,
                    fstype=partition.fstype,
                    maxfile=partition.maxfile,
                    maxpath=partition.maxpath,
                    opts=partition.opts,
                    total=usage.total,
                    used=usage.used,
                    free=usage.free,
                    percent=usage.percent,
                )
            )
        return output

    def findmnt(self) -> list[FindMntResult]:
        common = [
            "findmnt",
            "--json",
            "--list",
            "--noheadings",
            "--ascii",
            "--notruncate",
            "--bytes",
            # "--all",
            "--real",
            "--types=notmpfs,sysfs,cgroup,cgroup2,securityfs,tracefs",
            "--bytes",
            "--canonicalize",
            "--output=TARGET,SOURCE,SIZE,FSTYPE,UUID,OPTIONS,LABEL",
        ]
        sources = {
            "kernel": "--kernel",
            "fstab": "--fstab",
            "mtab": "--mtab",
        }

        output = []
        for k, v in sources.items():
            result = self._run_cmd([*common, v])
            if result.returncode != 0:
                output.append(FindMntResult(name=k, exit_code=result.returncode))
            else:
                data = json.loads(result.stdout)
                output.extend(
                    [
                        FindMntResult(name=k, exit_code=result.returncode, **i)
                        for i in data.get("filesystems")
                    ]
                )
        return output

    def lsblk(self) -> list[LsBlkResult]:
        args = [
            "lsblk",
            "--json",
            "--list",
            "--noheadings",
            "--ascii",
            "--all",
            "--bytes",
            "--paths",
            "--output=NAME,SIZE,MOUNTPOINT,SERIAL,TYPE",
        ]
        result = self._run_cmd(args)
        if result.returncode != 0:
            return [LsBlkResult(exit_code=result.returncode)]

        data = json.loads(result.stdout)
        output = [
            LsBlkResult(exit_code=result.returncode, **i)
            for i in data.get("blockdevices")
        ]

        return output

    def df(self) -> list[DfResult]:
        headers = [
            "source",
            "fstype",
            "size",
            "used",
            "avail",
            "pcent",
            "file",
            "target",
        ]
        args = [
            "df",
            "--block-size=1",
            "--exclude-type=tmpfs",
            "--exclude-type=devtmpfs",
            f"--output={','.join(headers)}",
        ]
        result = self._run_cmd(args)
        if result.returncode != 0:
            return [DfResult(exit_code=result.returncode)]

        output = []
        for line in result.stdout.splitlines():
            if "Filesystem" in line:
                continue

            items = line.split()
            percent = float(items[headers.index("pcent")].replace("%", "")) / 100
            output.append(
                DfResult(
                    exit_code=result.returncode,
                    source=items[headers.index("source")],
                    fstype=items[headers.index("fstype")],
                    size=items[headers.index("size")],
                    used=items[headers.index("used")],
                    available=items[headers.index("avail")],
                    percent=percent,
                    from_file=items[headers.index("file")],
                    target=items[headers.index("target")],
                )
            )
        return output

    def processes(self) -> list[ProcessResult]:
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
        for p in psutil.process_iter(list(attrs.keys()), ad_value=None):
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
                ProcessResult(
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
        return result

    def network(self) -> list[NetworkResult]:
        output = []
        for name, info in psutil.net_io_counters(pernic=True).items():
            output.append(
                NetworkResult(
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
