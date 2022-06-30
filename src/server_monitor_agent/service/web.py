import math
from dataclasses import dataclass
from datetime import datetime

import psutil


class Web:
    pass


@dataclass
class StatusCakePayload:
    rx: int
    tx: int
    process: str
    drives: str
    ping: str
    freeMem: int
    MemTotal: int
    cpuUse: float
    uptime: int
    hdd: int
    thdd: int


class StatusCake:
    def calc_payload(self) -> StatusCakePayload:
        interval = 2.0

        ping = ""

        uptime = int(datetime.now().timestamp() - psutil.boot_time())

        memory = psutil.virtual_memory()
        mem_free = int(memory.available / 1024)
        mem_total = int(memory.total / 1024)

        hdd = 0
        thdd = 0
        drives = []
        for partition in psutil.disk_partitions():
            usage = psutil.disk_usage(partition.mountpoint)
            usage_total = usage.total / 1024
            usage_used = usage.used / 1024

            usage_total_g = math.ceil(usage_total / pow(1024, 3))
            usage_used_g = math.ceil(usage_used / pow(1024, 3))

            thdd += usage_total
            hdd += usage_used
            drives.append(
                "|".join([f"{usage_used_g}G", f"{usage_total_g}G", partition.device])
            )
        drive_str = ":".join(drives) + ":"

        first = self._network()
        cpu_use = psutil.cpu_percent(interval=interval)
        second = self._network()

        rx = int((second["rx"] - first["rx"]) / (interval * 1024))
        tx = int((second["tx"] - first["tx"]) / (interval * 1024))

        process = self._processes()

        return StatusCakePayload(
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

    def _network(self):
        # as a very simple way to choose, pick the interface with the most data sent
        item_info = None
        item_name = None
        for name, info in psutil.net_io_counters(pernic=True).items():
            if not item_info or info.bytes_sent > item_info.bytes_sent:
                item_name = name
                item_info = info

        return {
            "network_name": item_name,
            "rx": item_info.bytes_recv,
            "tx": item_info.bytes_sent,
        }

    def _processes(self):
        item_sep = ":::"
        attr_sep = "|"

        result = []

        # USER|PID|%CPU|%MEM|VSZ|RSS|COMMAND:::
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

            user = info["username"] or "(unknown)"
            if not user and psutil.POSIX:
                try:
                    user = p.uids()[0]
                except psutil.Error:
                    pass
            if user and psutil.WINDOWS and "\\" in user:
                user = user.split("\\")[1]
            user = user[:9]
            pid = info["pid"]
            vms = info["memory_info"].vms or 0
            rss = info["memory_info"].rss or 0
            memp = (
                round(info["memory_percent"], 1)
                if info["memory_percent"] is not None
                else ""
            )
            cpup = (
                round(info["memory_percent"], 1)
                if info["memory_percent"] is not None
                else ""
            )

            if info["cmdline"]:
                cmdline = " ".join(info["cmdline"])
            else:
                cmdline = info["name"]

            result.append(
                attr_sep.join(
                    [user, str(pid), str(cpup), str(memp), str(vms), str(rss), cmdline]
                )
            )
        return item_sep.join(result)
