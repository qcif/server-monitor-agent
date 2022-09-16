"""Models that can be used by agent services."""

import abc
import dataclasses
import datetime
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
FORMAT_DEFAULT = "agent-item"
FORMATS = [
    "agent-item",
    "prom-alert-manager",
    "consul-watch-check",
    "consul-health-check-state",
]

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

    pass


@beartype.beartype
@dataclasses.dataclass
class SendArgs(abc.ABC):
    """Arguments for sending information."""

    pass


@beartype.beartype
@dataclasses.dataclass
class OpResult(abc.ABC):
    """The result from running an operation."""

    exit_code: int


@beartype.beartype
@dataclasses.dataclass
class ExternalItem(abc.ABC):
    """A data item for external structured input and output."""

    @classmethod
    @abc.abstractmethod
    def data_type_name(cls):
        raise NotImplementedError("Must implement format_name.")

    @abc.abstractmethod
    @beartype.beartype
    def to_dict(self) -> typing.Dict:
        raise NotImplementedError("Must implement to_dict.")

    @classmethod
    @abc.abstractmethod
    @beartype.beartype
    def from_dict(cls, item: typing.Dict) -> "ExternalItem":
        raise NotImplementedError("Must implement from_dict.")


@beartype.beartype
@dataclasses.dataclass
class AgentItemConvertMixin(abc.ABC):
    @abc.abstractmethod
    @beartype.beartype
    def to_agent_item(self) -> "AgentItem":
        raise NotImplementedError("Must implement to_agent_item.")

    @classmethod
    @abc.abstractmethod
    @beartype.beartype
    def from_agent_item(cls, item: "AgentItem") -> "ExternalItem":
        raise NotImplementedError("Must implement from_agent_item.")


@beartype.beartype
@dataclasses.dataclass
class AgentItem(ExternalItem, AgentItemConvertMixin):
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
    """Status of the check - one of 'passing', 'warning', 'critical'."""

    service_name: str
    """The name of the service that was checked."""

    extra_data: typing.Dict[str, typing.Any] = dataclasses.field(default_factory=dict)
    """Optional key=value entries for arbitrary information.
    This may not be displayed."""

    @classmethod
    def data_type_name(cls):
        return "agent-item"

    @beartype.beartype
    def to_dict(self) -> typing.Dict:
        data = dataclasses.asdict(self)

        date_fields = ["date"]
        for date_field in date_fields:
            if data[date_field]:
                data[date_field] = data[date_field].isoformat(timespec="seconds")

        return data

    @classmethod
    @beartype.beartype
    def from_dict(cls, item: typing.Dict) -> "AgentItem":
        raw = {**item}
        if "date" in raw and raw["date"]:
            raw["date"] = datetime.datetime.fromisoformat(raw["date"])
        return cls(**raw)

    @beartype.beartype
    def to_agent_item(self) -> "AgentItem":
        return self

    @classmethod
    @beartype.beartype
    def from_agent_item(cls, item: "AgentItem") -> "ExternalItem":
        return item


@beartype.beartype
@dataclasses.dataclass
class TextCompare:
    comparison: str
    expected: str
    actual: str
    outcome: bool


@beartype.beartype
@dataclasses.dataclass
class TextCompareEntry:
    comparison: str
    value: str

    def compare(self, value: str) -> TextCompare:
        if self.comparison == "contains":
            return TextCompare(
                comparison=self.comparison,
                expected=self.value,
                actual=value,
                outcome=self.value is not None and self.value in value,
            )

        elif self.comparison == "not_contains":
            return TextCompare(
                comparison=self.comparison,
                expected=self.value,
                actual=value,
                outcome=self.value is not None and self.value not in value,
            )

        else:
            raise ValueError(f"Unknown comparison '{self.comparison}'.")

    @classmethod
    def from_tuple_list(cls, items: typing.List[typing.Tuple[str, str]]):
        return [TextCompareEntry(comparison=c, value=v) for c, v in items]


@beartype.beartype
@dataclasses.dataclass
class NameValueComparisonsEntry:
    name: str
    comparisons: typing.List[TextCompareEntry]

    @classmethod
    def from_tuple_list(cls, items: typing.Sequence[typing.Tuple[str, str, str]]):
        raw = {}
        for name, comparison, value in items:
            if name not in raw:
                raw[name] = []
            raw[name].append((comparison, value))

        result = []
        for name, comp in raw.items():
            comparisons = TextCompareEntry.from_tuple_list(comp)
            entry = NameValueComparisonsEntry(name=name, comparisons=comparisons)
            result.append(entry)
        return result

    def compare(self, value: str) -> typing.Iterable[TextCompare]:
        results = []
        for comparison in self.comparisons:
            results.append(comparison.compare(value))
        return results


@beartype.beartype
@dataclasses.dataclass
class RegisterCmd(abc.ABC):
    """Register a command."""

    pass


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


@beartype.beartype
@dataclasses.dataclass
class RegisterIO(abc.ABC):
    """Register an input or output."""

    pass


TypeCollectArgs = typing.TypeVar("T", bound=CollectArgs, covariant=True)


@beartype.beartype
@dataclasses.dataclass
class RegisterCollectInput(RegisterIO):
    """Register a source input."""

    func: typing.Callable[[TypeCollectArgs], AgentItem]


TypeSendArgs = typing.TypeVar("T", bound=SendArgs, covariant=True)


@beartype.beartype
@dataclasses.dataclass
class RegisterSendOutput(RegisterCmd):
    """Register a target output."""

    func: typing.Callable[[TypeSendArgs, AgentItem], None]
    collect_only: typing.Optional[typing.Iterable[str]] = None
