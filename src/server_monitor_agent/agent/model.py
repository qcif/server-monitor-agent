"""Models that can be used by agent services."""

import abc
import dataclasses
import datetime
import json
import typing

# application
APP_NAME_DASH = "server-monitor-agent"
APP_NAME_UNDER = "server_monitor_agent"

# reporting
REPORT_LEVEL_PASS = "passing"
REPORT_CODE_PASS = "0"

REPORT_LEVEL_WARN = "warning"
REPORT_CODE_WARN = "1"

REPORT_LEVEL_CRIT = "critical"
REPORT_CODE_CRIT = "2"

# input and output
FORMAT_AGENT = "agent"
FORMAT_CONSUL_WATCH = "consul-watch"

STREAM_STDOUT = "stdout"
STREAM_STDERR = "stderr"
STREAM_STDIN = "stdin"

IN_FORMATS = [FORMAT_AGENT, FORMAT_CONSUL_WATCH]
OUT_FORMATS = [FORMAT_AGENT]

STREAM_SOURCES = [STREAM_STDIN]
STREAM_TARGETS = [STREAM_STDOUT, STREAM_STDERR]


@dataclasses.dataclass
class CollectArgs(abc.ABC):
    """Arguments for collecting information."""

    @property
    @abc.abstractmethod
    def io_module(self) -> str:
        """The name of the io module."""
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def io_func_prefix(self) -> str:
        """The prefix of the io function."""
        raise NotImplementedError()


@dataclasses.dataclass
class SendArgs(abc.ABC):
    """Arguments for sending information."""

    @property
    @abc.abstractmethod
    def io_func_suffix(self) -> str:
        """The suffix of the io function."""
        raise NotImplementedError()


@dataclasses.dataclass
class OpResult(abc.ABC):
    """The result from running an operation."""

    exit_code: int


@dataclasses.dataclass
class DataItem(abc.ABC):
    """A data item for structured input and output."""


@dataclasses.dataclass
class AgentItem(DataItem):
    service_name: str
    """The name of the service."""

    host_name: str
    """Name of the server where the event occurred or node name."""

    source_name: str
    """Name of the source of this information, e.g. systemd."""

    status_code: str
    """Code from the service, e.g. 0 for program success or 200 for http ok."""

    status_name: str
    """Status of the check: one of 'passing', 'warning', 'critical'."""

    title: str
    """The headline summary for the check."""

    description: str
    """A free-text description of the service status.
    For a non-passing check, this should include the reason for the failure.
    It might also include hints regarding how to restore the service."""

    check_type: str
    """The type of check."""

    date: datetime.datetime
    """When the information in this item generated or when the event occurred."""

    tags: typing.Dict[str, str] = dataclasses.field(default_factory=dict)
    """Optional key=value entries for arbitrary information.
    This may not be displayed in all notifications."""

    def to_json(self) -> str:
        data = dataclasses.asdict(self)

        date_fields = ["date"]
        for date_field in date_fields:
            if data[date_field]:
                data[date_field] = data[date_field].isoformat(timespec="seconds")

        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, value: str) -> "AgentItem":
        try:
            raw = json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not read input in agent format: '{value}'.") from e

        if not isinstance(raw, dict):
            raise ValueError(f"Could not read input in agent format: '{value}'.")

        item = AgentItem(**raw)
        return item

    @classmethod
    def from_consul_watch(cls, value: str) -> "AgentItem":
        raise NotImplementedError()


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
