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


@pytest.fixture(autouse=True)
def no_smtplib_login(monkeypatch):
    """Remove smtplib.SMTP_SSL for all tests."""
    monkeypatch.delattr("smtplib.SMTP.login")


@pytest.fixture(autouse=True)
def replace_psutil_cpu_percent(monkeypatch):
    """Replace psutil.cpu_percent for all tests."""

    def cpu_percent(interval=None, percpu=False):
        # range is 0 -> (usage in percent, e.g. 10%)
        return 10

    monkeypatch.setattr("psutil.cpu_percent", cpu_percent)
