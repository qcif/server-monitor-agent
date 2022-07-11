import logging

import pytest


def check_logs(actual, expected):
    __tracebackhide__ = True
    for index, (actual_name, actual_level, actual_msg) in enumerate(actual):
        expected_item = expected[index]
        if isinstance(expected_item, tuple):
            expected_name, expected_level, expected_msgs = expected_item
            assert actual_name == expected_name
            assert actual_level == expected_level
        else:
            expected_msgs = expected_item

        if isinstance(expected_msgs, list):
            for expected_msg in expected_msgs:
                assert expected_msg in actual_msg
        elif isinstance(expected_msgs, str):
            assert expected_msgs == actual_msg
        else:
            pytest.fail()

    assert len(actual) == len(expected)


def log_debug_msgs(
    group: str,
    cmd: str,
    config_file: str,
    io_name: str,
    input_format: str = "agent",
):
    lgr = "server-monitor-agent"
    lvl = logging.DEBUG

    available = {
        "check": {
            "file": {
                "agent": [
                    "format='agent'",
                    "std_out=False,",
                    "std_err=False,",
                    "write_file='/",
                ]
            },
            "stdout": {
                "agent": [
                    "format='agent'",
                    "std_out=True,",
                    "std_err=False,",
                    "write_file=None",
                ]
            },
            "stderr": {
                "agent": [
                    "format='agent'",
                    "std_out=False,",
                    "std_err=True,",
                    "write_file=None",
                ]
            },
        },
        "notify": {
            "file": {
                "agent": [
                    "format='agent'",
                    "std_in=False,",
                    "read_file='/",
                ],
                "consul-watch": [
                    "format='consul-watch'",
                    "std_in=False,",
                    "read_file='/",
                ],
            },
            "stdin": {
                "agent": [
                    "format='agent'",
                    "std_in=True,",
                    "read_file=None",
                ],
                "consul-watch": [
                    "format='consul-watch'",
                    "std_in=True,",
                    "read_file=None",
                ],
            },
        },
    }

    msgs = [
        (lgr, lvl, "Running parser with args."),
        (lgr, lvl, "Starting server-monitor-agent in debug mode."),
        (
            lgr,
            lvl,
            [
                f"Raw arguments: {group} {cmd}",
                f"--config {config_file} --log-level debug",
            ],
        ),
        (
            lgr,
            lvl,
            [
                "Parsed arguments: Namespace(log_level='debug',",
                f"sub_command_name='{group}'",
                "func=",
                f"name='{cmd}', ",
                *available[group][io_name][input_format],
                f"config=PosixPath('{config_file}'))",
            ],
        ),
        (lgr, lvl, ["Finished parser func with parsed args in debug mode."]),
    ]

    return msgs
