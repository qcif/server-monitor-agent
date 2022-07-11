import pytest


@pytest.fixture(autouse=True)
def no_run_cmd(monkeypatch):
    """Remove method that allows running command for all tests."""

    def run_cmd(self, args):
        raise ValueError(f"Must set _run_cmd method for '{args}'.")

    monkeypatch.setattr("server_monitor_agent.common.ProgramMixin._run_cmd", run_cmd)


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Remove requests.sessions.Session.request for all tests."""
    monkeypatch.delattr("requests.sessions.Session.request")
    # pass
