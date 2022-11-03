import pytest


@pytest.fixture(autouse=True)
def no_run_cmd(monkeypatch):
    """Remove method that allows running command for all tests."""

    def run_cmd(self, args):
        raise ValueError(f"Must set execute_process method for '{args}'.")

    monkeypatch.setattr("server_monitor_agent.agent.common.execute_process", run_cmd)


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Remove requests.sessions.Session.request for all tests."""

    def run_cmd(self, args):
        raise ValueError(f"Must set request method for '{args}'.")

    monkeypatch.setattr("requests.sessions.Session.request", run_cmd)
