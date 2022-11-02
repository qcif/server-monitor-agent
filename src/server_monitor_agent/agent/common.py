import abc
import dataclasses
import socket
import subprocess
import typing
from datetime import datetime
from zoneinfo import ZoneInfo


def get_hostname() -> str:
    """Get the local hostname."""

    result = socket.gethostname()

    # TODO: other options to get the hostname
    # result = socket.getfqdn()
    # result = platform.node()

    return result


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
    check_name: str
    description: str

    def __post_init__(self):
        self._timestamp_formatted = datetime.now(ZoneInfo(self.time_zone)).isoformat(
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
            f"{'PASSING' if self.exit_code == 0 else 'WARNING'}: "
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
            f"⚠️🔴 WARNING: '{self.check_name}' on '{self.hostname}'",
            f"at {self.timestamp_formatted} ({self.time_zone})",
            f"**Problem**: {self.description}",
            f"**Impact**: {self.impact}",
            f"**Action**: {self.action}",
            "----------------------",
        ]


@dataclasses.dataclass
class CheckReportOk(CheckReport):
    resolution: str

    @property
    def content_lines(self) -> typing.Sequence[str]:
        return [
            "----------------------",
            f"✔️🟢 PASSING: '{self.check_name}' on '{self.hostname}'",
            f"at {self.timestamp_formatted}",
            f"**Description**: {self.description}",
            f"**Resolution**: {self.resolution}",
            "----------------------",
        ]


def report_problem(
    time_zone: str, check_name: str, description: str, impact: str, action: str
) -> CheckReportProblem:
    hostname = get_hostname()

    return CheckReportProblem(
        hostname=hostname,
        exit_code=1,
        time_zone=time_zone,
        check_name=check_name,
        description=description,
        impact=impact,
        action=action,
    )


def report_ok(
    time_zone: str, check_name: str, description: str, resolution: str
) -> CheckReportOk:
    hostname = get_hostname()

    return CheckReportOk(
        hostname=hostname,
        exit_code=0,
        time_zone=time_zone,
        check_name=check_name,
        description=description,
        resolution=resolution,
    )
