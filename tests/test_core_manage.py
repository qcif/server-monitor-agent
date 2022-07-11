import logging
from importlib.resources import files, as_file
from pathlib import Path

import pytest

from server_monitor_agent.service.web import UrlResponseEntry, UrlRequestEntry
from tests.helpers import check_logs
from server_monitor_agent import common
from server_monitor_agent.common import RunArgs
from server_monitor_agent.core.manage import Manager
from server_monitor_agent.service import device
from server_monitor_agent.service import systemd
from server_monitor_agent.service import web
from server_monitor_agent.service import docker
from server_monitor_agent.service import slack
from server_monitor_agent.service import status_cake


def test_manage_config_pass():
    source = files("tests.resources").joinpath("config-pass.yml")
    manage = Manager()
    with as_file(source) as p:
        config = manage.config(p)

    items = [
        device.CheckInstanceCpuEntry(
            key="instance_cpu_status", threshold=80, group="check"
        ),
        device.CheckInstanceMemoryEntry(
            key="instance_memory_status", threshold=80, group="check"
        ),
        device.CheckDiskEntry(
            key="instance_disk_status",
            threshold=80,
            path="/",
            device="/dev/sda3",
            uuid="181d63cf-913b-4f0e-a279-6aeb32aa70a1",
            label="",
            group="check",
        ),
        systemd.CheckSystemdUnitEntry(
            key="ufw_status", name="ufw.service", group="check"
        ),
        systemd.CheckSystemdUnitEntry(
            key="logrotate_status", name="logrotate.timer", group="check"
        ),
        systemd.CheckSystemdUnitEntry(
            key="network_online_status", name="network-online.target", group="check"
        ),
        web.CheckUrlEntry(
            key="github_octocat_status",
            request=UrlRequestEntry(
                url="https://api.github.com/octocat",
                method="GET",
                headers={"test_header": "test header value"},
            ),
            response=UrlResponseEntry(
                status_code=200,
                headers=[
                    web.UrlHeadersEntry(
                        name="content_type",
                        comparisons=[
                            common.TextCompareEntry(
                                comparison="contains", value="text/plain"
                            )
                        ],
                    )
                ],
                content=[common.TextCompareEntry(comparison="contains", value="MMMMM")],
            ),
            group="check",
        ),
        device.CheckFileEntry(
            key="bashrc_file",
            path=Path("/etc/bash.bashrc"),
            state="present",
            content=[common.TextCompareEntry(comparison="not_contains", value="error")],
            group="check",
        ),
        device.CheckFileEntry(
            key="missing_file",
            path=Path("/does/not/exist"),
            state="absent",
            content=[],
            group="check",
        ),
        docker.CheckDockerContainerEntry(
            key="consul_container",
            name="consul",
            state="running",
            health="ignore",
            group="check",
        ),
        device.NotifyLoggedInUsersEntry(
            key="test_user_message", user_group="vagrant", group="notify"
        ),
        web.NotifyEmailEntry(
            key="test_email", address="example@example.com", group="notify"
        ),
        status_cake.NotifyStatusCakeEntry(key="statuscake_agent", group="notify"),
        slack.NotifySlackEntry(
            key="testing_slack", webhook="https://example.com/services", group="notify"
        ),
    ]

    for index, item in enumerate(items):
        assert item == config[index]


def test_manage_config_fail(caplog):
    source = files("tests.resources").joinpath("config-fail.yml")
    manage = Manager()
    with as_file(source) as p:
        with pytest.raises(ValueError) as e:
            manage.config(p)

    assert "Could not load config file" in str(e.value)

    msgs = [
        ["Unknown top-level key 'top_level_fail'. Choose from 'check, notify'."],
        ["Unknown check type 'unknown-type' for 'check_item_fail'. Choose from"],
        [
            "Could not load check type 'instance-memory-status' for 'check_item_prop_missing'.",
            "Properties 'type'.",
            "missing 1 required positional argument: 'threshold'",
        ],
        [
            "Could not load check type 'systemd-unit-status' for 'check_item_extra_prop'.",
            "Properties 'name, something, type'.",
            "got an unexpected keyword argument 'something'",
        ],
        [
            "Could not load check type 'web-app-status' for 'check_item_invalid_text_compare1'.",
            "Properties 'request, response, type'.",
            "Error AttributeError: 'str' object has no attribute 'items'",
        ],
        [
            "Could not load check type 'web-app-status' for 'check_item_invalid_text_compare2'.",
            "Properties 'request, response, type'.",
            "Error AttributeError: 'str' object has no attribute 'items'",
        ],
        [
            "Could not load check type 'file-status' for 'check_item_invalid_text_compare3'.",
            "Properties 'content, path, state, type'.",
            "Error AttributeError: 'str' object has no attribute 'items'",
        ],
        [
            "Unknown notify type 'blah' for 'blah'.",
            "Choose from 'email, logged-in-users, slack, statuscake-agent'.",
        ],
    ]
    check_logs(caplog.record_tuples, msgs)


def test_process_list(caplog):
    caplog.set_level(logging.DEBUG)

    source = files("tests.resources").joinpath("config-pass.yml")
    manage = Manager()
    with as_file(source) as p:
        run_args = RunArgs(
            group="list",
            name=None,
            level=None,
            fmt=None,
            std_io=True,
            std_err=False,
            file_path=None,
        )
        manage.process(run_args=run_args, config_path=p)

    msgs = [
        ["Listing 14 configured items."],
        ["-- Listing 10 checks --"],
        ["instance_cpu_status: instance-cpu-status"],
        ["instance_memory_status: instance-memory-status"],
        ["instance_disk_status: instance-disk-status"],
        ["ufw_status: systemd-unit-status"],
        ["logrotate_status: systemd-unit-status"],
        ["network_online_status: systemd-unit-status"],
        ["github_octocat_status: web-app-status"],
        ["bashrc_file: file-status"],
        ["missing_file: file-status"],
        ["consul_container: docker-container-status"],
        ["-- Listing 4 notifications --"],
        ["test_user_message: logged-in-users"],
        ["test_email: email"],
        ["statuscake_agent: statuscake-agent"],
        ["testing_slack: slack"],
    ]

    check_logs(caplog.record_tuples, msgs)
