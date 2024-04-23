import dataclasses
import datetime
import functools

import beartype
from beartype import typing

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

from server_monitor_agent.agent import model as agent_model


@beartype.beartype
@dataclasses.dataclass
class CpuCollectArgs(agent_model.CollectArgs):
    threshold: int = 80
    interval: float = 2.0


@beartype.beartype
@dataclasses.dataclass
class MemoryCollectArgs(agent_model.CollectArgs):
    threshold: int = 80


@beartype.beartype
@dataclasses.dataclass
class LoggedInUsersSendArgs(agent_model.SendArgs):
    user_group: typing.Optional[str] = None


@beartype.beartype
@dataclasses.dataclass
class StreamInputCollectArgs(agent_model.CollectArgs):
    source: str
    format: str


@beartype.beartype
@dataclasses.dataclass
class StreamOutputSendArgs(agent_model.SendArgs):
    target: str
    format: str


@beartype.beartype
@dataclasses.dataclass
class NetworkResult(agent_model.OpResult):
    name: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int


@beartype.beartype
@dataclasses.dataclass
class MemoryResult(agent_model.OpResult):
    total: int
    available: int
    percent: float
    used: int
    free: int
    active: int
    inactive: int
    buffers: int
    cached: int
    wired: int
    shared: int


@beartype.beartype
@dataclasses.dataclass
class ProcessResult(agent_model.OpResult):
    user: typing.Optional[str] = None
    pid: typing.Optional[int] = None
    cpu_percent: typing.Optional[float] = None
    """gauge of percent of total system cpu usage since last call"""
    mem_percent: typing.Optional[float] = None
    """gauge of percent of total system memory used by process rss"""
    vms: typing.Optional[int] = None
    """gauge of 'Virtual Memory Size', the total amount of virtual memory used by a process"""
    rss: typing.Optional[int] = None
    """gauge of 'Resident Set Size', the non-swapped physical memory used by a process"""
    cmdline: typing.Optional[str] = None
    io_read_ops_count: typing.Optional[int] = None
    """counter (cumulative) of number of process I/O read operations"""
    io_write_ops_count: typing.Optional[int] = None
    """counter (cumulative) of number of process I/O write operations"""
    io_read_bytes_count: typing.Optional[int] = None
    """counter (cumulative) of number of process I/O bytes read"""
    io_write_bytes_count: typing.Optional[int] = None
    """counter (cumulative) of number of process I/O bytes written"""
    cpu_time_count: typing.Optional[float] = None
    """counter (cumulative) of cpu time used by system and user"""
    cpu_usable_count: typing.Optional[int] = None
    """gauge of number of cpus process can use"""


@beartype.beartype
@dataclasses.dataclass
class TimeZoneResult(agent_model.OpResult):
    raw: typing.Optional[str]

    @functools.cached_property
    @beartype.beartype
    def zone_info(self) -> typing.Optional[zoneinfo.ZoneInfo]:
        if not self.raw:
            return None
        return zoneinfo.ZoneInfo(self.raw)

    @property
    @beartype.beartype
    def now(self) -> typing.Optional[datetime.datetime]:
        if not self.raw:
            return None
        return datetime.datetime.now(tz=self.zone_info)
