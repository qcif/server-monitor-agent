import dataclasses
import datetime
import functools
import typing

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

from server_monitor_agent.agent import model as agent_model


@dataclasses.dataclass
class CpuArgs(agent_model.CollectArgs):
    threshold: int = 80
    interval: float = 2.0

    @property
    def io_module(self) -> str:
        return "server.io"

    @property
    def io_func_prefix(self) -> str:
        return "cpu"


@dataclasses.dataclass
class MemoryArgs(agent_model.CollectArgs):
    threshold: int = 80

    @property
    def io_module(self) -> str:
        return "server.io"

    @property
    def io_func_prefix(self) -> str:
        return "memory"


@dataclasses.dataclass
class LoggedInUsersArgs(agent_model.SendArgs):
    user_group: str

    @property
    def io_func_suffix(self) -> str:
        return "logged_in_users"


@dataclasses.dataclass
class StreamInputArgs(agent_model.CollectArgs):
    source: str
    format: str

    @property
    def io_module(self) -> str:
        return "server.io"

    @property
    def io_func_prefix(self) -> str:
        return "stream_input"


@dataclasses.dataclass
class StreamOutputArgs(agent_model.SendArgs):
    target: str
    format: str

    @property
    def io_func_suffix(self) -> str:
        return "stream_output"


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


@dataclasses.dataclass
class MemoryResult(agent_model.OpResult):
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


@dataclasses.dataclass
class ProcessResult(agent_model.OpResult):
    user: typing.Optional[str] = None
    pid: typing.Optional[int] = None
    cpu_percent: typing.Optional[float] = None
    mem_percent: typing.Optional[float] = None
    vms: typing.Optional[int] = None
    rss: typing.Optional[int] = None
    cmdline: typing.Optional[str] = None


@dataclasses.dataclass
class TimeZoneResult(agent_model.OpResult):
    raw: typing.Optional[str]

    @functools.cached_property
    def zone_info(self) -> typing.Optional[zoneinfo.ZoneInfo]:
        if not self.raw:
            return None
        return zoneinfo.ZoneInfo(self.raw)

    @property
    def now(self) -> typing.Optional[datetime.datetime]:
        if not self.raw:
            return None
        return datetime.datetime.now(tz=self.zone_info)
