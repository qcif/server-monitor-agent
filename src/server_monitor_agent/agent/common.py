import abc
import dataclasses
import socket
import subprocess
import typing
from datetime import datetime
import importlib_resources
import importlib_metadata

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

APP_NAME_DASH = "server-monitor-agent"
APP_NAME_UNDER = "server_monitor_agent"


def get_hostname() -> str:
    """Get the local hostname."""

    result = socket.gethostname()

    # TODO: other options to get the hostname
    # result = socket.getfqdn()
    # result = platform.node()

    return result


def get_version() -> typing.Optional[str]:
    """Get the version of this package."""
    try:
        dist = importlib_metadata.distribution(APP_NAME_DASH)
        return dist.version
    except importlib_metadata.PackageNotFoundError:
        # ignore error
        pass

    try:
        with importlib_resources.path(APP_NAME_UNDER, "entry.py") as p:
            return (p.parent.parent.parent / "VERSION").read_text().strip()
    except FileNotFoundError:
        # ignore error
        pass

    return "(version not available)"


def execute_process(args: typing.Sequence[str]):
    """Execute a process using the given args."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            shell=False,
            timeout=10,
            check=False,
            text=True,
        )
        # print(f"Process result: {result}", file=sys.stderr)
        return result
    except FileNotFoundError as e:
        raise ValueError(f"Error running '{' '.join(args)}'") from e


@dataclasses.dataclass
class CheckReport(abc.ABC):
    hostname: str
    exit_code: int
    time_zone: str
    check_type: str
    check_name: str
    description: str

    def __post_init__(self):
        self._timestamp_formatted = datetime.now(zoneinfo.ZoneInfo(self.time_zone)).isoformat(
            timespec="seconds"
        )

    @property
    def timestamp_formatted(self) -> str:
        return self._timestamp_formatted

    @property
    def content_lines(self) -> typing.Sequence[str]:
        raise NotImplementedError()

    @property
    def content(self) -> str:
        return "\n".join(self.content_lines)

    def __str__(self):
        return (
            f"{'PASSING' if self.exit_code == 0 else 'PROBLEM'}: "
            f"for '{self.check_name}' "
            f"on '{self.hostname}' "
            f"at {self.timestamp_formatted}"
        )


@dataclasses.dataclass
class CheckReportProblem(CheckReport):
    impact: str
    action: str

    @property
    def content_lines(self) -> typing.Sequence[str]:
        return [
            "----------------------",
            f"⚠️🔴 *PROBLEM*: `{self.check_name}` on `{self.hostname}`",
            f"at {self.timestamp_formatted} ({self.time_zone}) for {self.check_type}",
            f"_Description_: {self.description}",
            f"_Impact_: {self.impact}",
            f"_Action_: {self.action}",
            "----------------------",
        ]


@dataclasses.dataclass
class CheckReportOk(CheckReport):
    resolution: str

    @property
    def content_lines(self) -> typing.Sequence[str]:
        return [
            "----------------------",
            f"✔️🟢 *PASSING*: `{self.check_name}` on `{self.hostname}`",
            f"at {self.timestamp_formatted} ({self.time_zone}) for {self.check_type}",
            f"_Description_: {self.description}",
            f"_Resolution_: {self.resolution}",
            "----------------------",
        ]


def report_problem(
    time_zone: str,
    check_type: str,
    check_name: str,
    description: str,
    impact: str,
    action: str,
) -> CheckReportProblem:
    hostname = get_hostname()

    return CheckReportProblem(
        hostname=hostname,
        exit_code=2,
        time_zone=time_zone,
        check_type=check_type,
        check_name=check_name,
        description=description,
        impact=impact,
        action=action,
    )


def report_ok(
    time_zone: str, check_type: str, check_name: str, description: str, resolution: str
) -> CheckReportOk:
    hostname = get_hostname()

    return CheckReportOk(
        hostname=hostname,
        exit_code=0,
        time_zone=time_zone,
        check_type=check_type,
        check_name=check_name,
        description=description,
        resolution=resolution,
    )
