import json
import typing
from datetime import datetime
from typing import Optional

from boltons.strutils import camel2under

from server_monitor_agent.agent import operation as agent_op
from server_monitor_agent.systemd import model


def systemctl_show(name: str) -> Optional[model.SystemCtlShowResult]:
    if not name or not name.strip():
        return None

    args = ["systemctl", "show", name, "--all"]
    result = agent_op.execute_process(args)
    if result.returncode != 0:
        return model.SystemCtlShowResult(name=name, exit_code=result.returncode)

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
        if k == "id":
            k = "identifier"
        if key in data:
            raise ValueError(f"Duplicate key '{k}' in systemctl output.")
        data[key] = v

    return model.SystemCtlShowResult(
        name=name,
        exit_code=result.returncode,
        **data,
    )


def journalctl(name: str) -> Optional[typing.List[model.JournalCtlResult]]:
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
    result = agent_op.execute_process(args)

    if result.returncode != 0:
        return [model.JournalCtlResult(name=name, exit_code=result.returncode)]
    data = json.loads("[" + result.stdout.replace("}\n{", "},{") + "]")

    date_key = "__REALTIME_TIMESTAMP"
    result = [
        model.JournalCtlResult(
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
