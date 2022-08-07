import pytest


@pytest.fixture(autouse=True)
def no_run_cmd(monkeypatch):
    """Remove method that allows running command for all tests."""

    item = "server_monitor_agent.agent.operation.execute_process"

    def run_cmd(args):
        raise ValueError(f"Must set {item} method for '{args}'.")

    monkeypatch.setattr(item, run_cmd)


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Remove requests.sessions.Session.request for all tests."""

    item = "requests.sessions.Session.request"

    def run_cmd(args):
        raise ValueError(f"Must set {item} method for '{args}'.")

    monkeypatch.setattr(item, run_cmd)


@pytest.fixture(autouse=True)
def replace_psutil_cpu_percent(monkeypatch):
    """Replace psutil.cpu_percent for all tests as it is slow to run."""

    def cpu_percent(interval=None, percpu=False):
        # range is 0 -> (usage in percent, e.g. 10%)
        return 10

    monkeypatch.setattr("psutil.cpu_percent", cpu_percent)
