from importlib.resources import files, as_file
from pathlib import Path

import pytest

from server_monitor_agent.cmd import config


def test_load_pass():
    source = files("tests.resources").joinpath("config-pass.yml")
    with as_file(source) as yml:
        data = config.Config(yml)

    config_data = data.load()

    items = [
        config.CheckInstanceCpuEntry(
            key="instance_cpu_status", threshold=80, group="check"
        ),
        config.CheckInstanceMemoryEntry(
            key="instance_memory_status", threshold=80, group="check"
        ),
        config.CheckDiskEntry(
            key="instance_disk_status",
            threshold=80,
            path="/",
            device="/dev/sda3",
            uuid="181d63cf-913b-4f0e-a279-6aeb32aa70a1",
            label="",
            group="check",
        ),
        config.CheckSystemdUnitEntry(
            key="ufw_status", name="ufw.service", group="check"
        ),
        config.CheckSystemdUnitEntry(
            key="logrotate_status", name="logrotate.timer", group="check"
        ),
        config.CheckSystemdUnitEntry(
            key="network_online_status", name="network-online.target", group="check"
        ),
        config.CheckUrlEntry(
            key="github_octocat_status",
            url="https://api.github.com/octocat",
            headers=[
                config.UrlHeadersEntry(
                    name="content_type",
                    comparisons=[
                        config.TextCompareEntry(
                            comparison="contains", value="text/plain"
                        )
                    ],
                )
            ],
            content=[config.TextCompareEntry(comparison="contains", value="MMMMM")],
            group="check",
        ),
        config.CheckFileEntry(
            key="apt_history_file",
            path=Path("/var/log/apt/history.log"),
            state="present",
            content=[config.TextCompareEntry(comparison="not_contains", value="error")],
            age=[config.DateTimeCompareEntry(comparison="not_newer", value="now")],
            group="check",
        ),
        config.CheckDockerContainerEntry(
            key="consul_container", name="consul", group="check"
        ),
        config.NotifyLoggedInUsersEntry(
            key="test_user_message", user_group="vagrant", group="notify"
        ),
        config.NotifyEmailEntry(
            key="test_email", address="example@example.com", group="notify"
        ),
        config.NotifyStatusCakeEntry(key="statuscake_agent", group="notify"),
        config.NotifySlackEntry(
            key="testing_slack", webhook="https://example.com/services", group="notify"
        ),
    ]

    for index, item in enumerate(items):
        assert item == config_data[index]


def test_load_fail(caplog):
    source = files("tests.resources").joinpath("config-fail.yml")
    with as_file(source) as yml:
        data = config.Config(yml)

    with pytest.raises(ValueError) as e:
        data.load()

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
            "Properties 'content, headers, type, url'.",
            "Error AttributeError: 'str' object has no attribute 'items'",
        ],
        [
            "Could not load check type 'web-app-status' for 'check_item_invalid_text_compare2'.",
            "Properties 'content, headers, type, url'.",
            "Error AttributeError: 'str' object has no attribute 'items'",
        ],
        [
            "Could not load check type 'file-status' for 'check_item_invalid_text_compare3'.",
            "Properties 'age, content, path, state, type'.",
            "Error AttributeError: 'str' object has no attribute 'items'",
        ],
        [
            "Could not load check type 'file-status' for 'check_item_invalid_date_compare1'.",
            "Properties 'age, content, path, state, type'.",
            "Error AttributeError: 'str' object has no attribute 'items'",
        ],
        [
            "Unknown notify type 'blah' for 'blah'. Choose from 'email, logged-in-users, slack, statuscake-agent'."
        ],
    ]
    assert len(caplog.records) == len(msgs)
    for index, record in enumerate(caplog.records):
        for msg in msgs[index]:
            assert msg in record.msg
