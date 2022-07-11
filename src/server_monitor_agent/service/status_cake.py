import math
from dataclasses import dataclass
from typing import Optional

from server_monitor_agent.common import OutputMixin, RunArgs
from server_monitor_agent.common import ProgramMixin, ConfigEntryMixin
from server_monitor_agent.core.local import LocalProgram, NetworkResult


@dataclass
class NotifyStatusCakeEntry(ConfigEntryMixin):
    def operation(self, run_args: RunArgs) -> None:

        # this entry ignores any input provided
        # it collects all data itself
        # payload = StatusCakeProgram().calc_payload()

        # send data to statuscake url

        raise NotImplementedError()

    key: str
    group: str = "notify"
    type: str = "statuscake-agent"


@dataclass
class StatusCakeOutput(OutputMixin):
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


class StatusCakeProgram(ProgramMixin):
    def __init__(self):
        self._local = LocalProgram()

    def calc_payload(self) -> StatusCakeOutput:
        interval = 2.0

        ping = ""

        uptime = self._local.uptime()

        memory = self._local.memory()
        mem_free = int(memory.available / 1024)
        mem_total = int(memory.total / 1024)

        hdd = 0
        thdd = 0
        drives = []
        for partition in self._local.partitions():
            usage_total = partition.total / 1024
            usage_used = partition.used / 1024

            usage_total_g = math.ceil(usage_total / pow(1024, 3))
            usage_used_g = math.ceil(usage_used / pow(1024, 3))

            thdd += usage_total
            hdd += usage_used
            drives.append(
                "|".join([f"{usage_used_g}G", f"{usage_total_g}G", partition.device])
            )
        drive_str = ":".join(drives) + ":"

        first = self._network()
        cpu_use = self._local.cpu_usage(interval)
        second = self._network()

        rx = int((second["rx"] - first["rx"]) / (interval * 1024))
        tx = int((second["tx"] - first["tx"]) / (interval * 1024))

        process = self._processes()

        return StatusCakeOutput(
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
        selected: Optional[NetworkResult] = None
        network = self._local.network()
        for item in network:
            if not selected or item.bytes_sent > selected.bytes_sent:
                selected = item
                break

        if selected is None:
            raise ValueError()

        return {
            "network_name": selected.name,
            "rx": selected.bytes_recv,
            "tx": selected.bytes_sent,
        }

    def _processes(self):
        item_sep = ":::"
        attr_sep = "|"

        result = self._local.processes()
        output = item_sep.join(
            [
                attr_sep.join(
                    [
                        p.user,
                        str(p.pid),
                        str(p.cpu_percent),
                        str(p.mem_percent),
                        str(p.vms),
                        str(p.rss),
                        p.cmdline,
                    ]
                )
                for p in result
            ]
        )
        return output
