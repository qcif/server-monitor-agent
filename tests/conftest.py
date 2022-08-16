from collections import namedtuple

import pytest
from psutil._common import sdiskpart, sdiskusage, snetio

import data.completed_process_examples


@pytest.fixture(autouse=True)
def methods_require_mock(monkeypatch):
    """Throw error for methods that are slow or can't be used in tests."""

    items = [
        "server_monitor_agent.agent.operation.execute_process",
        "requests.sessions.Session.request",
    ]

    def create_func(method_name):
        def raise_instead(*args, **kwargs):
            raise ValueError(
                f"Must set {method_name} method for args '{args}' kwargs '{kwargs}'."
            )

        return raise_instead

    for item in items:
        func = create_func(item)
        monkeypatch.setattr(item, func)


svmem = namedtuple(
    "svmem",
    [
        "total",
        "available",
        "percent",
        "used",
        "free",
        "active",
        "inactive",
        "buffers",
        "cached",
        "shared",
        "slab",
    ],
)


@pytest.fixture(autouse=True)
def methods_return_known(monkeypatch):
    """Replace real results with known results."""

    items = {
        # range is 0 -> (usage in percent, e.g. 10%)
        "psutil.cpu_percent": 10,
        "psutil.disk_partitions": [
            sdiskpart(
                device="/dev/sda3",
                mountpoint="/",
                fstype="ext4",
                opts="rw,errors=remount-ro",
                maxfile=255,
                maxpath=4096,
            ),
            sdiskpart(
                device="/dev/sda7",
                mountpoint="/home",
                fstype="ext4",
                opts="rw",
                maxfile=255,
                maxpath=4096,
            ),
        ],
        "psutil.disk_usage": sdiskusage(
            total=21378641920, used=4809781248, free=15482871808, percent=22.5
        ),
        "psutil.process_iter": [
            {"name": "systemd", "pid": 1, "username": "root"},
            {"name": "kthreadd", "pid": 2, "username": "root"},
            {"name": "ksoftirqd/0", "pid": 3, "username": "root"},
        ],
        "psutil.boot_time": 1660649067000.0,
        "psutil.virtual_memory": svmem(
            total=10367352832,
            available=6472179712,
            percent=37.6,
            used=8186245120,
            free=2181107712,
            active=4748992512,
            inactive=2758115328,
            buffers=790724608,
            cached=3500347392,
            shared=787554304,
            slab=199348224,
        ),
        "psutil.net_io_counters": {
            "lo": snetio(
                bytes_sent=547971,
                bytes_recv=547971,
                packets_sent=5075,
                packets_recv=5075,
                errin=0,
                errout=0,
                dropin=0,
                dropout=0,
            ),
            "wlan0": snetio(
                bytes_sent=13921765,
                bytes_recv=62162574,
                packets_sent=79097,
                packets_recv=89648,
                errin=0,
                errout=0,
                dropin=0,
                dropout=0,
            ),
        },
        "socket.getfqdn": "test-instance.example.com",
        "platform.node": "test-instance",
    }

    def create_func(return_value):
        def known_value(*args, **kwargs):
            return return_value

        return known_value

    for k, v in items.items():
        func = create_func(v)
        monkeypatch.setattr(k, func)


@pytest.fixture
def execute_process_setup(monkeypatch):
    def execute_process(args):
        for item in data.completed_process_examples.examples:
            if args == item.args:
                return item
        raise ValueError(f"Must handle args '{args}'.")

    monkeypatch.setattr(
        "server_monitor_agent.agent.operation.execute_process", execute_process
    )

    return execute_process
