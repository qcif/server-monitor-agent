import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import dataclasses
from boltons.strutils import camel2under

from server_monitor_agent.common import ProgramMixin, ConfigEntryMixin, RunArgs
from server_monitor_agent.common import ReportMixin, DateTimeMixin
from server_monitor_agent.common import ResultMixin
from server_monitor_agent.core.local import LocalProgram
from server_monitor_agent.service.agent import AgentItem


@dataclass
class CheckSystemdUnitEntry(ConfigEntryMixin, ReportMixin, DateTimeMixin):

    key: str
    name: str
    group: str = "check"
    type: str = "systemd-unit-status"

    def operation(self, run_args: RunArgs):
        level = run_args.level

        systemd = SystemdProgram()
        show = systemd.systemctl_show(self.name)
        if show is None:
            raise ValueError()
        logs = systemd.journalctl(self.name)

        local = LocalProgram()
        hostname = local.hostname()

        status_code = str(show.exit_code) if show.exit_code else None
        if status_code is None:
            status_code = (
                self._pass_code if show.result == "success" else self._warn_code
            )

        # determine status
        if level:
            status = level
        elif status_code == self._pass_code:
            status = self._pass
        elif status_code == self._warn_code:
            status = self._warn
        else:
            status = self._crit

        date = self.date_parse(
            show.state_change_time_stamp
            or show.exec_main_exit_timestamp
            or show.exec_main_start_timestamp
            or show.active_exit_timestamp
            or show.active_enter_timestamp
            or show.inactive_exit_timestamp
            or show.inactive_enter_timestamp
        )

        title = ""
        descr = ""

        tags = dict(
            [
                (k, v)
                for k, v in dataclasses.asdict(show).items()
                if v is not None and v != ""
            ]
        )

        log_subset = [i.message for i in sorted(logs, key=lambda x: x.timestamp)][:6]
        for index, log in enumerate(log_subset):
            tags[f"log{index + 1}"] = log

        item = AgentItem(
            service_name=f"systemd unit {self.name}",
            host_name=hostname,
            source_name="systemd",
            status_code=status_code,
            status_name=status,
            title=title,
            description=descr.strip(),
            check_name=self.key,
            check_type=self.type,
            date=date,
            tags=tags,
        )
        self._do_output(run_args, item)


@dataclass
class SystemCtlShowResult(ResultMixin):
    name: str

    id: Optional[str] = None
    load_state: Optional[str] = None
    active_state: Optional[str] = None
    sub_state: Optional[str] = None
    description: Optional[str] = None
    unit_file_state: Optional[str] = None
    unit_file_preset: Optional[str] = None
    state_change_time_stamp: Optional[str] = None
    inactive_exit_timestamp: Optional[str] = None
    active_enter_timestamp: Optional[str] = None
    active_exit_timestamp: Optional[str] = None
    inactive_enter_timestamp: Optional[str] = None
    can_start: Optional[str] = None
    can_stop: Optional[str] = None
    exec_main_start_timestamp: Optional[str] = None
    exec_main_exit_timestamp: Optional[str] = None
    exec_main_code: Optional[str] = None
    exec_main_status: Optional[str] = None
    standard_output: Optional[str] = None
    standard_error: Optional[str] = None
    user: Optional[str] = None
    group: Optional[str] = None
    triggered_by: Optional[str] = None
    result: Optional[str] = None
    unit: Optional[str] = None
    next_elapse_u_sec_realtime: Optional[str] = None
    last_trigger_u_sec: Optional[str] = None
    triggers: Optional[str] = None


@dataclass
class JournalCtlResult(ResultMixin):
    name: str

    message: Optional[str] = None
    timestamp: Optional[datetime] = None
    hostname: Optional[str] = None
    unit: Optional[str] = None


class SystemdProgram(ProgramMixin):
    def systemctl_show(self, name: str) -> Optional[SystemCtlShowResult]:
        if not name or not name.strip():
            return None

        args = ["systemctl", "show", name, "--all"]
        result = self._run_cmd(args)
        if result.returncode != 0:
            return SystemCtlShowResult(name=name, exit_code=result.returncode)

        keys = [
            "Id",
            "LoadState",
            "ActiveState",
            "SubState",
            "Description",
            "UnitFileState",
            "UnitFilePreset",
            "StateChangeTimeStamp",
            "InactiveExitTimestamp",
            "ActiveEnterTimestamp",
            "ActiveExitTimestamp",
            "InactiveEnterTimestamp",
            "CanStart",
            "CanStop",
            "ExecMainStartTimestamp",
            "ExecMainExitTimestamp",
            "ExecMainCode",
            "ExecMainStatus",
            "StandardOutput",
            "StandardError",
            "User",
            "Group",
            "TriggeredBy",
            "Result",
            "Unit",
            "NextElapseUSecRealtime",
            "LastTriggerUSec",
            "Triggers",
        ]

        data = {}
        props = result.stdout.splitlines()
        for prop in props:
            k, v = prop.split("=", 1)
            key = camel2under(k)
            if k not in keys:
                continue
            if key in data:
                raise ValueError(f"Duplicate key '{k}' in systemctl output.")
            data[key] = v

        return SystemCtlShowResult(name=name, exit_code=result.returncode, **data)

    def journalctl(self, name: str) -> Optional[list[JournalCtlResult]]:
        if not name or not name.strip():
            return None

        args = [
            "journalctl",
            "--no-hostname",
            "--all",
            "--no-pager",
            "--output=json-pretty",
            "--unit",
            name,
            "--output-fields=MESSAGE,JOB_RESULT,UNIT,_HOSTNAME,__REALTIME_TIMESTAMP",
        ]
        result = self._run_cmd(args)

        if result.returncode != 0:
            return [JournalCtlResult(name=name, exit_code=result.returncode)]
        data = json.loads("[" + result.stdout.replace("}\n{", "},{") + "]")

        date_key = "__REALTIME_TIMESTAMP"
        result = [
            JournalCtlResult(
                name=name,
                exit_code=result.returncode,
                message=i.get("MESSAGE"),
                timestamp=datetime.fromtimestamp(int(float(i.get(date_key)) / 1000000))
                if i.get(date_key)
                else None,
                hostname=i.get("_HOSTNAME"),
                unit=i.get("UNIT"),
            )
            for i in data
        ]
        return result
