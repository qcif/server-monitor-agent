"""Functions to obtain information about disks and files."""

import json
import logging
import pathlib
import uuid

import beartype
import psutil
from beartype import typing

from server_monitor_agent.agent import model as agent_model, operation as agent_op
from server_monitor_agent.agent.operation import make_options
from server_monitor_agent.service.disk import model as disk_model

logger = logging.getLogger(f"{agent_model.APP_NAME_UNDER}.device.disk")


def partitions() -> typing.List[disk_model.PartitionResult]:
    """Get details of the disks available."""

    output = []
    result = psutil.disk_partitions()

    agent_op.log_msg(logging.DEBUG, f"Result from psutil.disk_partitions: {result}")

    for partition in result:
        usage = psutil.disk_usage(partition.mountpoint)
        output.append(
            disk_model.PartitionResult(
                exit_code=0,
                device=partition.device,
                mountpoint=partition.mountpoint,
                fstype=partition.fstype,
                maxfile=partition.maxfile,
                maxpath=partition.maxpath,
                opts=partition.opts,
                total=usage.total,
                used=usage.used,
                free=usage.free,
                percent=usage.percent,
            )
        )
    return output


def disk_partitions(
    path: typing.Optional[pathlib.Path] = None,
    device: typing.Optional[pathlib.Path] = None,
    source: typing.Optional[str] = None,
    target: typing.Optional[str] = None,
):
    items = partitions()
    partition: typing.Optional[disk_model.PartitionResult] = None
    for item in items:
        if device and device != item.device and item.device == source:
            continue
        if path and path != item.mountpoint and item.mountpoint == target:
            continue
        partition = item
        break

    if partition is None:
        raise ValueError(f"No partition matched path '{path}' device '{device}'.")
    return partition


def findmnt() -> typing.List[disk_model.FindMntResult]:
    """Get details of the available disk mounts."""

    common = [
        "findmnt",
        "--json",
        "--list",
        "--noheadings",
        "--ascii",
        "--notruncate",
        "--bytes",
        # "--all",
        "--real",
        "--types=notmpfs,sysfs,cgroup,cgroup2,securityfs,tracefs",
        "--canonicalize",
        "--output=TARGET,SOURCE,SIZE,FSTYPE,UUID,OPTIONS,LABEL",
    ]
    sources = {
        "kernel": "--kernel",
        "fstab": "--fstab",
        "mtab": "--mtab",
    }

    output = []
    for k, v in sources.items():
        args = [*common, v]
        result = agent_op.execute_process(args)

        agent_op.log_msg(logging.DEBUG, f"Result from '{' '.join(args)}': {result}")

        if result.returncode != 0:
            output.append(disk_model.FindMntResult(name=k, exit_code=result.returncode))
        else:
            data = json.loads(result.stdout)
            output.extend(
                [
                    disk_model.FindMntResult(name=k, exit_code=result.returncode, **i)
                    for i in data.get("filesystems")
                ]
            )
    return output


def disk_mounts(
    path: typing.Optional[pathlib.Path] = None,
    device: typing.Optional[pathlib.Path] = None,
    disk_uuid: typing.Optional[uuid.UUID] = None,
    label: typing.Optional[str] = None,
):
    items = findmnt()
    item: typing.Optional[disk_model.FindMntResult] = None
    for item in items:
        if device and device != item.source:
            continue
        if path and path != item.target:
            continue
        if disk_uuid and item.uuid and disk_uuid != item.uuid:
            continue
        if label and item.label and label != item.label:
            continue
        item = item
        break

    if not item:
        raise ValueError(
            f"No disk matched "
            f"path '{path}' "
            f"device '{device}' "
            f"uuid '{disk_uuid}' "
            f"label '{label}'."
        )
    return item


def lsblk() -> typing.List[disk_model.LsBlkResult]:
    """Get details of the available local devices."""
    args = [
        "lsblk",
        "--json",
        "--list",
        "--noheadings",
        "--ascii",
        "--all",
        "--bytes",
        "--paths",
        "--output=NAME,SIZE,MOUNTPOINT,SERIAL,TYPE",
    ]
    result = agent_op.execute_process(args)

    agent_op.log_msg(logging.DEBUG, f"Result from '{' '.join(args)}': {result}")

    if result.returncode != 0:
        return [disk_model.LsBlkResult(exit_code=result.returncode)]

    data = json.loads(result.stdout)
    output = [
        disk_model.LsBlkResult(exit_code=result.returncode, **i)
        for i in data.get("blockdevices")
    ]

    return output


def df() -> typing.List[disk_model.DfResult]:
    """Get details of the space on local disks."""

    headers = [
        "source",
        "fstype",
        "size",
        "used",
        "avail",
        "pcent",
        "file",
        "target",
    ]
    args = [
        "df",
        "--block-size=1",
        "--exclude-type=tmpfs",
        "--exclude-type=devtmpfs",
        f"--output={','.join(headers)}",
    ]
    result = agent_op.execute_process(args)

    agent_op.log_msg(logging.DEBUG, f"Result from '{' '.join(args)}': {result}")

    if result.returncode != 0:
        return [disk_model.DfResult(exit_code=result.returncode)]

    output = []
    for line in result.stdout.splitlines():
        if "Filesystem" in line:
            continue

        items = line.split()
        percent = float(items[headers.index("pcent")].replace("%", "")) / 100
        output.append(
            disk_model.DfResult(
                exit_code=result.returncode,
                source=items[headers.index("source")],
                fstype=items[headers.index("fstype")],
                size=items[headers.index("size")],
                used=items[headers.index("used")],
                available=items[headers.index("avail")],
                percent=percent,
                from_file=items[headers.index("file")],
                target=items[headers.index("target")],
            )
        )
    return output


@beartype.beartype
def write_file(out_target: pathlib.Path, item: agent_model.ExternalItem) -> None:
    # get content
    if out_format == agent_model.FORMAT_AGENT:
        content = item.to_json()
    else:
        options = make_options(agent_model.FORMATS_OUT)
        raise ValueError(
            f"Unrecognised format for file output: {out_format}. "
            f"Must be one of {options}."
        )

    # write content
    if not out_target:
        raise ValueError(f"Must provide path to write.")

    out_target.parent.mkdir(parents=True, exist_ok=True)
    out_target.write_text(content, encoding="utf8")


@beartype.beartype
def read_file(
    in_format: str,
    in_target: pathlib.Path,
) -> agent_model.AgentItem:
    # read content
    if not in_target or not in_target.exists():
        raise ValueError(f"File to read must exist: '{in_target}'.")

    content = in_target.read_text(encoding="utf8")

    # get content
    if in_format == agent_model.FORMAT_AGENT:
        return agent_model.AgentItem.from_json(content)

    if in_format == agent_model.FORMAT_CONSUL_WATCH:
        return agent_model.AgentItem.from_consul_watch(content)

    options = make_options(agent_model.FORMATS_IN)
    raise ValueError(
        f"Unrecognised format for file input: {in_format}. Must be one of {options}"
    )
