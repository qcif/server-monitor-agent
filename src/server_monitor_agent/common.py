import logging
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence, Optional

import dateparser

from server_monitor_agent.service.agent import AgentItem


@dataclass
class RunArgs:
    group: str
    name: Optional[str]
    level: Optional[str]
    fmt: Optional[str]
    std_io: bool
    std_err: bool
    file_path: Optional[str]

    @property
    def is_std_io(self) -> bool:
        self._check_io()
        return self.std_io is True

    @property
    def is_std_err(self) -> bool:
        self._check_io()
        return self.std_err is True

    @property
    def is_file(self) -> bool:
        self._check_io()
        return True if self.file_path and self.file_path.strip() else False

    @property
    def cmd_io(self) -> str:
        self._check_io()
        if self.is_std_io and self.group == "notify":
            cmd_io = "std_in"
        elif self.is_std_io and self.group == "check":
            cmd_io = "std_out"
        elif self.is_std_err and self.group == "check":
            cmd_io = "std_err"
        elif self.is_file and self.group == "notify":
            cmd_io = "read_file"
        elif self.is_file and self.group == "check":
            cmd_io = "write_file"
        else:
            cmd_io = None
        return cmd_io

    def _check_io(self) -> None:
        options_io = [
            self.std_io is True,
            self.std_err is True,
            (True if self.file_path and self.file_path.strip() else False),
        ]
        options_count = len([i for i in options_io if i is True])
        if options_count != 1:
            raise ValueError(
                "A single source of input or output is required. "
                "Choose only one of std in/out, std err, or read/write file. "
                f"There were {options_count} specified."
            )


@dataclass
class ConfigEntryMixin:
    key: str

    @classmethod
    def load(cls, **kwargs) -> "ConfigEntryMixin":
        return cls(**kwargs)

    def operation(self, run_args: RunArgs) -> None:
        raise NotImplementedError()

    def _do_output(self, run_args: RunArgs, item: AgentItem) -> None:
        # content
        if run_args.fmt == "agent":
            content = item.to_json()
        else:
            raise ValueError()

        # write
        if run_args.cmd_io == "std_out":
            sys.stdout.write(content)
        elif run_args.cmd_io == "std_err":
            sys.stdout.write(content)
        elif run_args.cmd_io == "write_file":
            Path(run_args.file_path).write_text(content, encoding="utf8")
        else:
            raise ValueError()

    def _get_input(self, run_args: RunArgs) -> AgentItem:
        # read
        if run_args.cmd_io == "std_in":
            content = sys.stdin.read()
        elif run_args.cmd_io == "read_file":
            content = Path(run_args.file_path).read_text(encoding="utf8")
        else:
            raise ValueError()

        # content
        if run_args.fmt == "agent":
            return AgentItem.from_json(content)
        elif run_args.fmt == "consul-watch":
            return AgentItem.from_consul_watch(content)
        else:
            raise ValueError()


@dataclass
class TextCompareEntry:
    comparison: str
    value: str

    @classmethod
    def load(cls, **kwargs) -> "TextCompareEntry":
        return cls(**kwargs)

    def compare(self, value: str):
        if self.comparison == "contains":
            return self.value is not None and self.value in value
        elif self.comparison == "not_contains":
            return self.value is not None and self.value not in value
        else:
            raise ValueError(f"Unknown comparison '{self.comparison}'.")


@dataclass
class ResultMixin:
    exit_code: int


@dataclass
class OutputMixin:
    pass


class ProgramMixin:
    def _run_cmd(self, args: Sequence[str]):
        result = subprocess.run(
            args,
            capture_output=True,
            shell=False,
            timeout=10,
            check=False,
            text=True,
        )
        return result


class ReportMixin:
    _pass = "passing"
    _pass_code = "0"
    _warn = "warning"
    _warn_code = "1"
    _crit = "critical"
    _crit_code = "2"

    @classmethod
    def report_choices(cls) -> list[str]:
        return [cls._pass, cls._warn, cls._crit]

    @classmethod
    def code_from_level(cls, level: str):
        if level == cls._pass:
            return cls._pass_code
        elif level == cls._warn:
            return cls._warn_code
        elif level == cls._crit:
            return cls._crit_code
        else:
            raise ValueError()

    @classmethod
    def level_from_code(cls, code: str):
        if code == cls._pass_code:
            return cls._pass
        elif code == cls._warn_code:
            return cls._warn
        elif code == cls._crit_code:
            return cls._crit
        else:
            raise ValueError()

    def _report_evaluate(self, value, test) -> tuple[str, str]:
        if value > test:
            status_code = self._crit_code
            status = self._crit
        elif value == test:
            status_code = self._warn_code
            status = self._warn
        else:
            status_code = self._pass_code
            status = self._pass

        return status, status_code


class LoggingMixin:
    _crit = ("critical", logging.CRITICAL)
    _err = ("error", logging.ERROR)
    _warn = ("warning", logging.WARNING)
    _info = ("info", logging.INFO)
    _debug = ("debug", logging.DEBUG)

    @classmethod
    def logging_choices(cls) -> list[str]:
        return [cls._crit[0], cls._err[0], cls._warn[0], cls._info[0], cls._debug[0]]

    @classmethod
    def logging_value(cls, name: str) -> int:
        options: dict = {
            k: v for k, v in [cls._crit, cls._err, cls._warn, cls._info, cls._debug]
        }
        if not name:
            raise ValueError("Must specify a logging level.")
        if name not in options:
            raise ValueError(
                f"Invalid logging level '{name}'. "
                f"Available names are {', '.join(cls.logging_choices())}"
            )
        return options[name]


class DateTimeMixin:
    _display = "%a, %d %b %Y %H:%M:%S %Z"

    def date_display(self, value: datetime) -> str:
        return value.strftime(self._display)

    def date_parse(self, value: str) -> Optional[datetime]:
        if not value or not value.strip():
            return None
        return dateparser.parse(value)
