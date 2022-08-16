import logging
import math

import beartype
import requests
from beartype import typing

from server_monitor_agent.agent import model as agent_model, operation as agent_op
from server_monitor_agent.service.disk import operation as disk_op
from server_monitor_agent.service.server import (
    model as server_model,
    operation as server_op,
)


@beartype.beartype
def disks() -> typing.Tuple[int, int, str]:
    hdd = 0
    thdd = 0
    drives = []
    for partition in disk_op.partitions():
        usage_total = partition.total / 1024
        usage_used = partition.used / 1024

        usage_total_g = math.ceil(usage_total / pow(1024, 3))
        usage_used_g = math.ceil(usage_used / pow(1024, 3))

        thdd += usage_total
        hdd += usage_used
        drives.append(
            "|".join([f"{usage_used_g}G", f"{usage_total_g}G", partition.device])
        )
    drive_str = ":".join(drives) + ":"

    return int(hdd), int(thdd), drive_str


@beartype.beartype
def network() -> typing.Dict[str, typing.Union[str, int]]:
    selected: typing.Optional[server_model.NetworkResult] = None
    device_network = server_op.network()

    # TODO: devise a better way to select the interface
    # as a very simple way to choose, pick the interface with the most data sent
    for item in device_network:
        if not selected or item.bytes_sent > selected.bytes_sent:
            selected = item
            break

    if selected is None:
        raise ValueError()

    return {
        "network_name": selected.name,
        "rx": selected.bytes_recv,
        "tx": selected.bytes_sent,
    }


@beartype.beartype
def processes() -> str:
    item_sep = ":::"
    attr_sep = "|"

    result = server_op.processes()
    output = item_sep.join(
        [
            attr_sep.join(
                [
                    p.user,
                    str(p.pid),
                    str(p.cpu_percent),
                    str(p.mem_percent),
                    str(p.vms),
                    str(p.rss),
                    p.cmdline,
                ]
            )
            for p in result
        ]
    )
    return output


@beartype.beartype
def submit_statuscake(item: agent_model.AgentItem) -> None:
    """Send data to statuscake url."""

    url = ""  # "https://agent.statuscake.com"

    response = requests.post(url=url, json=item.tags.get("statuscake_agent_items", {}))

    agent_op.log_msg(logging.DEBUG, f"Result from '{url}': {response}")

    if not response.status_code != 200:
        raise ValueError(f"Unexpected response from StatusCake: {response}")
