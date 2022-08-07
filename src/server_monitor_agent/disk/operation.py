"""Functions to obtain information about disks and files."""

import json
import logging
import typing

import psutil

from server_monitor_agent.agent import (
    model as agent_model,
    operation as agent_operation,
)
from server_monitor_agent.disk import model as disk_model

logger = logging.getLogger(f"{agent_model.APP_NAME_UNDER}.device.disk")


def partitions() -> typing.List[disk_model.PartitionResult]:
    """Get details of the disks available."""

    output = []
    result = psutil.disk_partitions()

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Result from psutil.disk_partitions: {result}")

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


def disk_partitions(args: disk_model.DiskCollectArgs, mnt: disk_model.FindMntResult):
    items = partitions()
    partition: typing.Optional[disk_model.PartitionResult] = None
    for item in items:
        if args.device and args.device != item.device and item.device == mnt.source:
            continue
        if args.path and args.path != item.mountpoint and item.mountpoint == mnt.target:
            continue
        partition = item
        break

    if partition is None:
        raise ValueError(
            f"No partition matched path='{args.path}', device='{args.device}'."
        )
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
        "--bytes",
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
        result = agent_operation.execute_process(args)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Result from '{' '.join(args)}': {result}")

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


def disk_mounts(args: disk_model.DiskCollectArgs):
    items = findmnt()
    item: typing.Optional[disk_model.FindMntResult] = None
    for item in items:
        if args.device and args.device != item.source:
            continue
        if args.path and args.path != item.target:
            continue
        if args.disk_uuid and item.uuid and args.disk_uuid != item.uuid:
            continue
        if args.label and item.label and args.label != item.label:
            continue
        item = item
        break

    if not item:
        raise ValueError(
            f"No disk matched path='{args.path}', device='{args.device}', "
            f"uuid='{args.disk_uuid}', label='{args.label}'."
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
    result = agent_operation.execute_process(args)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Result from '{' '.join(args)}': {result}")

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
    result = agent_operation.execute_process(args)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Result from '{' '.join(args)}': {result}")

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
