"""Models that can be used by agent services."""

import abc
import dataclasses
import datetime
import json
import logging
import pathlib

import beartype
import click
from beartype import typing

# application
APP_NAME_DASH = "server-monitor-agent"
APP_NAME_UNDER = "server_monitor_agent"

# logging
LOG_LEVEL_CRIT = "critical"
LOG_CODE_CRIT = logging.CRITICAL
LOG_LEVEL_ERROR = "error"
LOG_CODE_ERROR = logging.ERROR
LOG_LEVEL_WARN = "warning"
LOG_CODE_WARN = logging.WARNING
LOG_LEVEL_INFO = "info"
LOG_CODE_INFO = logging.INFO
LOG_LEVEL_DEBUG = "debug"
LOG_CODE_DEBUG = logging.DEBUG
LOG_LEVELS = [
    LOG_LEVEL_CRIT,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_WARN,
    LOG_LEVEL_INFO,
    LOG_LEVEL_DEBUG,
]
LOG_CODES = [
    LOG_CODE_CRIT,
    LOG_CODE_ERROR,
    LOG_CODE_WARN,
    LOG_CODE_INFO,
    LOG_CODE_DEBUG,
]
LOG_ITEMS = {
    LOG_LEVEL_CRIT: LOG_CODE_CRIT,
    LOG_LEVEL_ERROR: LOG_CODE_ERROR,
    LOG_LEVEL_WARN: LOG_CODE_WARN,
    LOG_LEVEL_INFO: LOG_CODE_INFO,
    LOG_LEVEL_DEBUG: LOG_CODE_DEBUG,
}


# reporting
REPORT_LEVEL_ANY = "any"
REPORT_CODE_ANY = "-1"

REPORT_LEVEL_PASS = "passing"
REPORT_CODE_PASS = "0"

REPORT_LEVEL_WARN = "warning"
REPORT_CODE_WARN = "1"

REPORT_LEVEL_CRIT = "critical"
REPORT_CODE_CRIT = "2"

REPORT_LEVELS = [
    REPORT_LEVEL_PASS,
    REPORT_LEVEL_WARN,
    REPORT_LEVEL_CRIT,
]
REPORT_LEVELS_ALL = [
    REPORT_LEVEL_ANY,
    REPORT_LEVEL_PASS,
    REPORT_LEVEL_WARN,
    REPORT_LEVEL_CRIT,
]

REPORT_CODES = [
    REPORT_CODE_PASS,
    REPORT_CODE_WARN,
    REPORT_CODE_CRIT,
]

# input and output formats
FORMAT_AGENT = "agent"
FORMAT_CONSUL_WATCH = "consul-watch"

FORMATS_IN = [FORMAT_AGENT, FORMAT_CONSUL_WATCH]
FORMATS_OUT = [FORMAT_AGENT]

# input and output streams
STREAM_STDOUT = "stdout"
STREAM_STDERR = "stderr"
STREAM_STDIN = "stdin"

STREAM_SOURCES = [STREAM_STDIN]
STREAM_TARGETS = [STREAM_STDOUT, STREAM_STDERR]

TEXT_CHOOSE_NOTIFICATION = "Choose a notification target from the Commands."


@beartype.beartype
@dataclasses.dataclass
class CliArgs:
    debug: bool = False
    config_file: typing.Optional[pathlib.Path] = None


@beartype.beartype
@dataclasses.dataclass
class CollectArgs(abc.ABC):
    """Arguments for collecting information."""

    @property
    @abc.abstractmethod
    @beartype.beartype
    def io_module(self) -> str:
        """The name of the io module."""
        raise NotImplementedError("Must implement io_module for CollectArgs.")

    @property
    @abc.abstractmethod
    @beartype.beartype
    def io_func_prefix(self) -> str:
        """The prefix of the io function."""
        raise NotImplementedError("Must implement io_func_prefix for CollectArgs.")


@beartype.beartype
@dataclasses.dataclass
class SendArgs(abc.ABC):
    """Arguments for sending information."""

    @property
    @abc.abstractmethod
    @beartype.beartype
    def io_func_suffix(self) -> str:
        """The suffix of the io function."""
        raise NotImplementedError("Must implement io_func_suffix for SendArgs.")


@beartype.beartype
@dataclasses.dataclass
class OpResult(abc.ABC):
    """The result from running an operation."""

    exit_code: int


@beartype.beartype
@dataclasses.dataclass
class ExternalItem(abc.ABC):
    """A data item for external structured input and output."""

    pass


@beartype.beartype
@dataclasses.dataclass
class AgentItem(ExternalItem):
    """The data required for the agent input and output format."""

    summary: str
    """The headline title or short summary for the check."""

    description: str
    """A longer free-text description of the service status.
    For a non-passing check, this should include the reason for the failure.
    It might also include hints regarding how to restore the service."""

    host_name: str
    """Name of the server or node where the event occurred."""

    source_name: str
    """Name of the source of this information."""

    check_name: str
    """The name of the check tha was run."""

    date: datetime.datetime
    """When the information in this item was generated or when the event occurred."""

    status_name: str
    """Status of the check: one of 'passing', 'warning', 'critical'."""

    service_name: str
    """The name of the service that was checked."""

    tags: typing.Dict[str, str] = dataclasses.field(default_factory=dict)
    """Optional key=value entries for arbitrary information.
    This may not be displayed."""

    @beartype.beartype
    def to_json(self) -> str:
        data = dataclasses.asdict(self)

        date_fields = ["date"]
        for date_field in date_fields:
            if data[date_field]:
                data[date_field] = data[date_field].isoformat(timespec="seconds")

        return json.dumps(data, indent=2)

    @classmethod
    @beartype.beartype
    def from_json(cls, value: str) -> "AgentItem":
        try:
            raw = json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not read input in agent format: '{value}'.") from e

        if not isinstance(raw, dict):
            raise ValueError(f"Could not read input in agent format: '{value}'.")

        item = AgentItem(**raw)
        return item


@beartype.beartype
@dataclasses.dataclass
class TextCompareEntry:
    comparison: str
    value: str

    def compare(self, value: str):
        if self.comparison == "contains":
            return self.value is not None and self.value in value
        elif self.comparison == "not_contains":
            return self.value is not None and self.value not in value
        else:
            raise ValueError(f"Unknown comparison '{self.comparison}'.")


@beartype.beartype
@dataclasses.dataclass
class RegisterCmd:
    """Register a command."""


@beartype.beartype
@dataclasses.dataclass
class RegisterCollectCmd(RegisterCmd):
    """Register a collect command."""

    group: click.Group


@beartype.beartype
@dataclasses.dataclass
class RegisterSendCmd(RegisterCmd):
    """Register a send command."""

    command: click.Command
    collect_only: typing.Optional[typing.Iterable[str]] = None


#
# class LoggingMixin:
#     _crit = ("critical", logging.CRITICAL)
#     _err = ("error", logging.ERROR)
#     _warn = ("warning", logging.WARNING)
#     _info = ("info", logging.INFO)
#     _debug = ("debug", logging.DEBUG)
#
#     @classmethod
#     def logging_choices(cls) -> typing.List[str]:
#         return [cls._crit[0], cls._err[0], cls._warn[0], cls._info[0], cls._debug[0]]
#
#     @classmethod
#     def logging_value(cls, name: str) -> int:
#         options: dict = {
#             k: v for k, v in [cls._crit, cls._err, cls._warn, cls._info, cls._debug]
#         }
#         if not name:
#             raise ValueError("Must specify a logging level.")
#         if name not in options:
#             raise ValueError(
#                 f"Invalid logging level '{name}'. "
#                 f"Available names are {', '.join(cls.logging_choices())}"
#             )
#         return options[name]
#
#
# class DateTimeMixin:
#     _display = "%a, %d %b %Y %H:%M:%S %Z"
#
#     def date_display(self, value: datetime) -> str:
#         return value.strftime(self._display)
#
#     def date_parse(self, value: str) -> Optional[datetime]:
#         if not value or not value.strip():
#             return None
#         return dateparser.parse(value)
