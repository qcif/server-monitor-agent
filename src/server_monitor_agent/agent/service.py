import dataclasses
import pathlib
import typing
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import dateparser
import humanize

from server_monitor_agent.agent import common

SERVICE_EXPECTED_STATES = {
    "auto-infinite": {
        "description": "A continuous process that should start automatically "
        "and continues running.",
        "load": ["loaded"],
        "active": ["active", "activating"],
        "file": ["static", "enabled"],
        "sub": ["start-pre", "start", "start-post", "running"],
        "result": ["success"],
        "ExecMainStatus": [0],
    },
    "auto-finite-on-going": {
        "description": "A limited-time process that should start automatically "
        "and is treated as continuing to run.",
        "load": ["loaded"],
        "active": ["active", "activating"],
        "file": ["static", "enabled"],
        "sub": ["start-pre", "start", "start-post", "running", "exited"],
        "result": ["success"],
        "ExecMainStatus": [0],
    },
    "manual-finite-stop": {
        "description": "A limited-time process that is started manually "
        "and is treated as successful when stopping with exit code 0.",
        "load": ["loaded"],
        "active": ["inactive", "active", "activating"],
        "file": ["static", "disabled"],
        "sub": ["start-pre", "start", "start-post", "running", "dead"],
        "result": ["success"],
        "ExecMainStatus": [0],
    },
    "timer-finite-stop": {
        "description": "A limited-time process that is started manually "
        "and is treated as successful when stopping with exit code 0.",
        "load": ["loaded"],
        "active": ["inactive", "active", "activating"],
        "file": ["static", "disabled"],
        "sub": ["start-pre", "start", "start-post", "running", "dead"],
        "result": ["success"],
        "ExecMainStatus": [0],
    },
}

TIMER_EXPECTED_STATES = {
    "auto-infinite": {
        "description": "A continuous timer that should start automatically "
        "and trigger at pre-defined times of day.",
        "load": ["loaded"],
        "active": ["active", "activating"],
        "file": ["static", "enabled"],
        "sub": ["waiting", "running"],
        "result": ["success"],
    },
}


def service_detail(
    time_zone: str,
    name: str,
    load_state: list[str],
    active_state: list[str],
    file_state: list[str],
    sub_state: list[str],
    result_state: list[str],
    exec_main_status: list[int],
    max_age_hours: int,
):
    info = get_systemd_service_status(
        time_zone,
        name,
        ".service",
        load_state,
        active_state,
        file_state,
        sub_state,
        result_state,
        exec_main_status,
        max_age_hours,
    )

    if info.check_status:
        return common.report_ok(
            time_zone=time_zone,
            check_type="systemd-service",
            check_name=info.unit_name,
            description=" \n".join(
                [f"Service '{info.unit_name}' is as expected."] + info.ok_lines + [""]
            ),
            resolution="The service has been set to the expected state.",
        )
    else:
        return common.report_problem(
            time_zone=time_zone,
            check_type="systemd-service",
            check_name=info.unit_name,
            description=" \n".join(
                [f"Service '{info.unit_name}' is in an unexpected state."]
                + info.problem_lines
                + [""],
            ),
            impact="A service that is not in the expected state "
            "might cause degraded service. "
            "For example, backups might not be created, "
            "or database maintenance may not be not performed.",
            action="Check the service status using "
            f"'sudo systemctl status {info.unit_name}' "
            "and 'sudo journalctl --no-hostname --no-pager "
            f"-u {info.unit_name} | less +G'. "
            "Determine the problem with the service process and fix it.",
        )


def timer_detail(
    time_zone: str,
    name: str,
    load_state: list[str],
    active_state: list[str],
    file_state: list[str],
    sub_state: list[str],
    result_state: list[str],
):
    info = get_systemd_service_status(
        time_zone,
        name,
        ".timer",
        load_state,
        active_state,
        file_state,
        sub_state,
        result_state,
        None,
        None,
    )

    time_prev_diff_str, timestamp_prev_str = timestamp_info(info, "LastTriggerUSec")
    prev_trigger = (
        f"The previous run was at '{timestamp_prev_str}' ({time_prev_diff_str})."
    )

    time_next_diff_str, timestamp_next_str = timestamp_info(
        info, "NextElapseUSecRealtime"
    )
    next_trigger = f"The next run is at '{timestamp_next_str}' ({time_next_diff_str})."

    if info.check_status:
        return common.report_ok(
            time_zone=time_zone,
            check_type="systemd-timer",
            check_name=info.unit_name,
            description=" \n".join(
                [
                    f"Timer '{info.unit_name}' is as expected.",
                    prev_trigger,
                    next_trigger,
                ]
                + info.ok_lines
                + [""]
            ),
            resolution="The timer has been set to the expected state.",
        )
    else:
        return common.report_problem(
            time_zone=time_zone,
            check_type="systemd-timer",
            check_name=info.unit_name,
            description=" \n".join(
                [
                    f"Timer '{info.unit_name}' is in an unexpected state.",
                    prev_trigger,
                    next_trigger,
                ]
                + info.problem_lines
                + [""],
            ),
            impact="A timer not in the expected state could mean that scheduled tasks do not run.",
            action=f"Check the timer status using 'systemctl status {info.unit_name}'. "
            f"Determine whether the time should be running or not.",
        )


def timestamp_unit(
    data: dict,
) -> typing.Tuple[typing.Optional[str], typing.Optional[datetime]]:
    actual_active_state = data.get("ActiveState")

    if actual_active_state in ["active", "reloading"]:
        timestamp = data.get("ActiveEnterTimestamp")
    elif actual_active_state in ["inactive", "failed"]:
        timestamp = data.get("InactiveEnterTimestamp")
    elif actual_active_state in ["activating"]:
        timestamp = data.get("InactiveExitTimestamp")
    else:
        timestamp = data.get("ActiveExitTimestamp")

    if timestamp:
        timestamp_date = dateparser.parse(timestamp.strip())
        return timestamp, timestamp_date
    else:
        return None, None


def timestamp_diff(
    timestamp: datetime, now: datetime
) -> typing.Tuple[str, typing.Optional[timedelta]]:
    if timestamp:
        time_diff = now - timestamp
        time_diff_str = humanize.naturaltime(time_diff)
    else:
        time_diff = None
        time_diff_str = None

    return time_diff_str, time_diff


def timestamp_info(info: "SystemdServiceInfo", key: str) -> typing.Tuple[str, str]:
    ts_str = info.data.get(key)
    if ts_str:
        ts = dateparser.parse(ts_str.strip())
        diff_str, diff_ts = timestamp_diff(ts, info.timestamp_now)
    else:
        diff_str = SystemdServiceInfo.not_avail()

    return diff_str, ts_str


@dataclasses.dataclass
class SystemdServiceInfo:
    time_zone: str
    name: str
    load_state: list[str]
    active_state: list[str]
    file_state: list[str]
    sub_state: list[str]
    result_state: list[str]
    max_age_hours: int

    unit_name: str
    data: dict

    expected_load_state: list[str]
    actual_load_state: str
    match_load_state: bool

    expected_active_state: list[str]
    actual_active_state: str
    match_active_state: bool

    expected_file_state: list[str]
    actual_file_state: str
    match_file_state: bool

    expected_sub_state: list[str]
    actual_sub_state: str
    match_sub_state: bool

    expected_result_state: list[str]
    actual_result_state: str
    match_result_state: bool

    expected_exec_main_status: typing.Optional[list[int]]
    actual_exec_main_status: int
    match_exec_main_status: bool

    timestamp_last_change_str: str
    timestamp_last_change: datetime
    timestamp_now: datetime
    timespan_str: str
    timespan: timedelta

    logs: list[str]

    @classmethod
    def not_avail(cls):
        return "not available"

    @property
    def problem_lines(self) -> list[str]:
        descr_lines = [
            f"State last changed '{self.timestamp_last_change_str}' "
            f"({self.timespan_str}).",
            f"Unit is '{self.actual_load_state}' (expected {self.expected_load_state}).",
            f"File is '{self.actual_file_state}' (expected {self.expected_file_state}).",
            f"Active state is '{self.actual_active_state}' (expected {self.expected_active_state}).",
            f"Sub state is '{self.actual_sub_state}' (expected {self.expected_sub_state}).",
            f"Result is '{self.actual_result_state}' (expected {self.expected_result_state}).",
            f"Exec main status is '{self.actual_exec_main_status}' (expected {self.expected_exec_main_status}).",
            "",
            "Logs:",
        ] + self.logs
        return descr_lines

    @property
    def ok_lines(self) -> list[str]:
        descr_lines = [
            f"State last changed '{self.timestamp_last_change_str}' "
            f"({self.timespan_str}).",
            f"Unit is '{self.actual_load_state}' "
            f"and file is '{self.actual_file_state}'.",
            f"Active state is '{self.actual_active_state}' "
            f"and sub state is '{self.actual_sub_state}'.",
            f"Exec main status is '{self.actual_exec_main_status}' "
            f"and result is '{self.actual_result_state}'.",
        ]
        return descr_lines

    @property
    def check_status(self):
        return all(
            [
                self.match_load_state,
                self.match_active_state,
                self.match_file_state,
                self.match_sub_state,
                self.match_result_state,
                self.match_exec_main_status,
            ]
        )


def get_systemd_service_status(
    time_zone: str,
    name: str,
    expected_suffix: str,
    load_state: list[str],
    active_state: list[str],
    file_state: list[str],
    sub_state: list[str],
    result_state: list[str],
    exec_main_status: typing.Optional[list[int]],
    max_age_hours: typing.Optional[int],
):
    suffix = pathlib.Path(name).suffix
    if suffix and suffix != expected_suffix:
        raise ValueError(
            f"Invalid systemd service name '{name}' "
            "(must have no suffix or .service suffix)."
        )
    unit_name = name if name.endswith(expected_suffix) else f"{name}{expected_suffix}"
    args = ["systemctl", "show", "--no-pager", unit_name, "--all"]
    result = common.execute_process(args)
    data = dict(i.split("=", maxsplit=1) for i in result.stdout.splitlines())

    actual_load_state = data.get("LoadState")
    match_load_state = actual_load_state in load_state

    actual_active_state = data.get("ActiveState")
    match_active_state = actual_active_state in active_state

    actual_file_state = data.get("UnitFileState")
    match_file_state = actual_file_state in file_state

    actual_sub_state = data.get("SubState")
    match_sub_state = actual_sub_state in sub_state

    actual_result_state = data.get("Result")
    match_result_state = (
        (actual_result_state in result_state)
        if (actual_result_state and result_state)
        else True
    )

    actual_exec_main_status = int(data.get("ExecMainStatus", "-1") or "-1")
    if exec_main_status:
        match_exec_main_status = actual_exec_main_status in exec_main_status
    else:
        exec_main_status = [0]
        actual_exec_main_status = 0
        match_exec_main_status = True

    # date time
    datetime_now = datetime.now(ZoneInfo(time_zone))
    timestamp_str, timestamp_date = timestamp_unit(data)

    if timestamp_date:
        time_diff_str, time_diff = timestamp_diff(timestamp_date, datetime_now)
    else:
        timestamp_date = None
        timestamp_str = SystemdServiceInfo.not_avail()
        time_diff = None
        time_diff_str = SystemdServiceInfo.not_avail()

    log_args = [
        "journalctl",
        "--no-hostname",
        "--no-pager",
        "-u",
        unit_name,
        "-n",
        "7",
    ]
    log_result = common.execute_process(log_args)
    log_lines = log_result.stdout.splitlines()

    # NOTES:
    # the c code that creates the display for `systemctl status`:
    # https://github.com/systemd/systemd/blob/main/src/systemctl/systemctl-show.c#L315

    # timestamp = STRPTR_IN_SET(i->active_state, "active", "reloading") ? i->active_enter_timestamp :
    #                     STRPTR_IN_SET(i->active_state, "inactive", "failed")  ? i->inactive_enter_timestamp :
    #                     STRPTR_IN_SET(i->active_state, "activating")          ? i->inactive_exit_timestamp :
    #                                                                             i->active_exit_timestamp;

    # dict([(k,v) for k, v in data.items() if ('2022' in v or 'stamp' in k) and 'Monotonic' not in k])
    # dict([(k,v) for k, v in data.items() if 'Result' in k])

    return SystemdServiceInfo(
        time_zone=time_zone,
        name=name,
        load_state=load_state,
        active_state=active_state,
        file_state=file_state,
        sub_state=sub_state,
        result_state=result_state,
        max_age_hours=max_age_hours,
        unit_name=unit_name,
        data=data,
        expected_load_state=load_state,
        actual_load_state=actual_load_state,
        match_load_state=match_load_state,
        expected_active_state=active_state,
        actual_active_state=actual_active_state,
        match_active_state=match_active_state,
        expected_file_state=file_state,
        actual_file_state=actual_file_state,
        match_file_state=match_file_state,
        expected_sub_state=sub_state,
        actual_sub_state=actual_sub_state,
        match_sub_state=match_sub_state,
        expected_result_state=result_state,
        actual_result_state=actual_result_state,
        match_result_state=match_result_state,
        expected_exec_main_status=exec_main_status,
        actual_exec_main_status=actual_exec_main_status,
        match_exec_main_status=match_exec_main_status,
        timestamp_last_change_str=timestamp_str,
        timestamp_last_change=timestamp_date,
        timestamp_now=datetime_now,
        timespan_str=time_diff_str,
        timespan=time_diff,
        logs=log_lines,
    )
