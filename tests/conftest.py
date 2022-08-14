import subprocess
from beartype import typing

import pytest


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


@pytest.fixture(autouse=True)
def methods_return_known(monkeypatch):
    """Replace real results with known results."""

    items = {
        # range is 0 -> (usage in percent, e.g. 10%)
        "psutil.cpu_percent": 10,
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
def execute_process_unknown():
    def execute_process(args):
        raise ValueError(f"Must handle args '{args}'.")

    return execute_process


@pytest.fixture
def execute_process_setup(monkeypatch):
    def setup_func(fixtures: typing.List):
        def execute_process(args):
            items = fixtures
            for item in items:
                item_result = item(args)
                if item_result is not None:
                    return item_result

        monkeypatch.setattr(
            "server_monitor_agent.agent.operation.execute_process", execute_process
        )

    return setup_func


@pytest.fixture
def execute_process_timedatectl_show():
    def execute_process(args):
        expected = ["timedatectl", "show"]
        if args == expected:
            return subprocess.CompletedProcess(
                args=expected,
                returncode=0,
                stdout="\n".join(
                    [
                        "Timezone=Australia/Brisbane",
                        "LocalRTC=no",
                        "CanNTP=yes",
                        "NTP=no",
                        "NTPSynchronized=no",
                        "TimeUSec=Mon 2022-07-04 20:36:56 AEST",
                        "RTCTimeUSec=Mon 2022-07-04 20:36:55 AEST",
                        "",
                    ]
                ),
                stderr="",
            )
        return None

    return execute_process
