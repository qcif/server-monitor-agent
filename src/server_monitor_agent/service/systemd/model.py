import dataclasses
import datetime

import beartype
from beartype import typing

from server_monitor_agent.agent import model as agent_model


@beartype.beartype
@dataclasses.dataclass
class SystemdUnitStatusCollectArgs(agent_model.CollectArgs):
    name: str


@beartype.beartype
@dataclasses.dataclass
class SystemdUnitLogsCollectArgs(agent_model.CollectArgs):
    name: str


@beartype.beartype
@dataclasses.dataclass
class SystemCtlShowResult(agent_model.OpResult):
    name: str

    identifier: typing.Optional[str] = None
    load_state: typing.Optional[str] = None
    active_state: typing.Optional[str] = None
    sub_state: typing.Optional[str] = None
    description: typing.Optional[str] = None
    unit_file_state: typing.Optional[str] = None
    unit_file_preset: typing.Optional[str] = None
    state_change_time_stamp: typing.Optional[str] = None
    inactive_exit_timestamp: typing.Optional[str] = None
    active_enter_timestamp: typing.Optional[str] = None
    active_exit_timestamp: typing.Optional[str] = None
    inactive_enter_timestamp: typing.Optional[str] = None
    can_start: typing.Optional[str] = None
    can_stop: typing.Optional[str] = None
    exec_main_start_timestamp: typing.Optional[str] = None
    exec_main_exit_timestamp: typing.Optional[str] = None
    exec_main_code: typing.Optional[str] = None
    exec_main_status: typing.Optional[str] = None
    standard_output: typing.Optional[str] = None
    standard_error: typing.Optional[str] = None
    user: typing.Optional[str] = None
    group: typing.Optional[str] = None
    triggered_by: typing.Optional[str] = None
    result: typing.Optional[str] = None
    unit: typing.Optional[str] = None
    next_elapse_u_sec_realtime: typing.Optional[str] = None
    last_trigger_u_sec: typing.Optional[str] = None
    triggers: typing.Optional[str] = None


@beartype.beartype
@dataclasses.dataclass
class JournalCtlResult(agent_model.OpResult):
    name: str

    message: typing.Optional[str] = None
    timestamp: typing.Optional[datetime.datetime] = None
    hostname: typing.Optional[str] = None
    unit: typing.Optional[str] = None
