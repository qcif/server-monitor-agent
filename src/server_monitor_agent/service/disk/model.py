import dataclasses
import functools
import pathlib
import uuid

import beartype
from beartype import typing

from server_monitor_agent.agent import model as agent_model


@beartype.beartype
@dataclasses.dataclass
class DiskCollectArgs(agent_model.CollectArgs):
    threshold: int = 80
    path: typing.Optional[pathlib.Path] = None
    device: typing.Optional[pathlib.Path] = None
    disk_uuid: typing.Optional[uuid.UUID] = None
    label: typing.Optional[str] = None

    @property
    @beartype.beartype
    def io_module(self) -> str:
        return "disk"

    @property
    @beartype.beartype
    def io_func_prefix(self) -> str:
        return "disk_status"

    @beartype.beartype
    def validate(self):
        items = [self.path, self.device, self.disk_uuid, self.label]
        if not any([i for i in items if i]):
            raise ValueError(
                "Must specify at least one disk identifier (path,device,uuid,label)"
            )


@beartype.beartype
@dataclasses.dataclass
class FileStatusCollectArgs(agent_model.CollectArgs):
    path: pathlib.Path
    state: str
    content: typing.List[agent_model.TextCompareEntry]

    @property
    @beartype.beartype
    def io_module(self) -> str:
        return "disk"

    @property
    @beartype.beartype
    def io_func_prefix(self) -> str:
        return "file_status"


@beartype.beartype
@dataclasses.dataclass
class FileInputCollectArgs(agent_model.CollectArgs):
    path: pathlib.Path
    format: str

    @property
    @beartype.beartype
    def io_module(self) -> str:
        return "disk"

    @property
    @beartype.beartype
    def io_func_prefix(self) -> str:
        return "file_input"


@beartype.beartype
@dataclasses.dataclass
class FileOutputSendArgs(agent_model.SendArgs):
    path: pathlib.Path
    format: str

    @property
    @beartype.beartype
    def io_func_suffix(self) -> str:
        return "file_output"


@beartype.beartype
@dataclasses.dataclass
class FindMntResult(agent_model.OpResult):
    name: str
    target: typing.Optional[str] = None
    source: typing.Optional[str] = None
    size: typing.Optional[int] = None
    fstype: typing.Optional[str] = None
    uuid: typing.Optional[str] = None
    options: typing.Optional[str] = None
    label: typing.Optional[str] = None


@beartype.beartype
@dataclasses.dataclass
class LsBlkResult(agent_model.OpResult):
    name: typing.Optional[str] = None
    size: typing.Optional[int] = None
    mountpoint: typing.Optional[str] = None
    serial: typing.Optional[str] = None
    type: typing.Optional[str] = None


@beartype.beartype
@dataclasses.dataclass
class DfResult(agent_model.OpResult):
    source: typing.Optional[str] = None
    fstype: typing.Optional[str] = None
    size: typing.Optional[str] = None
    used: typing.Optional[str] = None
    available: typing.Optional[str] = None
    percent: typing.Optional[float] = None
    from_file: typing.Optional[str] = None
    target: typing.Optional[str] = None


@beartype.beartype
@dataclasses.dataclass
class PartitionResult(agent_model.OpResult):
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

    @functools.cached_property
    @beartype.beartype
    def percent_usage(self):
        return self.percent / 100.0
