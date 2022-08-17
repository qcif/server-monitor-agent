# server-monitor-agent

A Python utility to run checks on a server and send notifications.

This program is an agent that can be run on server instances.

It provides a number of commands that provide source information to run checks.
Each check then has a number of commands that are notification targets.

## Checks

Gather information about the instance and report the result via exit code and formatted output.

-  `consul-checks`: Get a summary of consul check statuses.
-  `cpu`: Get the overall CPU usage.
-  `disk`: Get disk usage.
-  `docker-container`: Get docker container status.
-  `file-input`: Load input from a file.
-  `file-status`: Get information about a file.
-  `memory`: Get the memory usage.
-  `statuscake`: Collect information required for the statuscake agent.
-  `stream-input`: Read input from a stream.
-  `systemd-unit-logs`: Get the logs for a systemd unit.
-  `systemd-unit-status`: Get the status of a systemd unit.
-  `web-app`: Check the response to a url request.

## Notifications

Read information and send a message to an alerting service.

-  `alert-manager`: Send a notification using Alert manager.
-  `email-message`: Send an email.
-  `file-output`: Write to a file.
-  `logged-in-users`: Send an alert to logged-in users.
-  `slack-message`: Send a slack message.
-  `statuscake`: Send server details to statuscake.
-  `stream-output`: Print to an output stream.


## TODO

FAILED tests/test_cli.py::test_cli_commands[consul-checks-alert-manager] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb763857d60>,)' kw...
FAILED tests/test_cli.py::test_cli_commands[consul-checks-file-output] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb7633fc310>,)' kwar...
FAILED tests/test_cli.py::test_cli_commands[consul-checks-logged-in-users] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb763491d60>,)' ...
FAILED tests/test_cli.py::test_cli_commands[consul-checks-stream-output] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb763519910>,)' kw...
FAILED tests/test_cli.py::test_cli_commands[consul-checks-email-message] - assert "Usage: serve.../ '--host'.\n" == ''
FAILED tests/test_cli.py::test_cli_commands[consul-checks-slack-message] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb763524ac0>,)' kw...
FAILED tests/test_cli.py::test_cli_commands[disk-alert-manager] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb7636ea6d0>,)' kwargs '{'m...
FAILED tests/test_cli.py::test_cli_commands[disk-file-output] - NotImplementedError
FAILED tests/test_cli.py::test_cli_commands[disk-stream-output] - NotImplementedError
FAILED tests/test_cli.py::test_cli_commands[disk-email-message] - assert "Usage: serve.../ '--host'.\n" == ''
FAILED tests/test_cli.py::test_cli_commands[disk-slack-message] - NameError: name 'self' is not defined
FAILED tests/test_cli.py::test_cli_commands[file-status-alert-manager] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb763760490>,)' kwar...
FAILED tests/test_cli.py::test_cli_commands[file-status-file-output] - NotImplementedError
FAILED tests/test_cli.py::test_cli_commands[file-status-stream-output] - NotImplementedError
FAILED tests/test_cli.py::test_cli_commands[file-status-email-message] - assert "Usage: serve.../ '--host'.\n" == ''
FAILED tests/test_cli.py::test_cli_commands[file-status-slack-message] - NameError: name 'self' is not defined
FAILED tests/test_cli.py::test_cli_commands[file-input-alert-manager] - ValueError: File to read must exist: '/tmp/pytest-of-vagrant/pytest-3/test_cli_commands_file_input_a0/tmpo478u89_/file-input.txt'.
FAILED tests/test_cli.py::test_cli_commands[file-input-file-output] - ValueError: File to read must exist: '/tmp/pytest-of-vagrant/pytest-3/test_cli_commands_file_input_f0/tmpt477fuku/file-input.txt'.
FAILED tests/test_cli.py::test_cli_commands[file-input-logged-in-users] - ValueError: File to read must exist: '/tmp/pytest-of-vagrant/pytest-3/test_cli_commands_file_input_l0/tmp9p_la6wa/file-input.txt'.
FAILED tests/test_cli.py::test_cli_commands[file-input-stream-output] - ValueError: File to read must exist: '/tmp/pytest-of-vagrant/pytest-3/test_cli_commands_file_input_s0/tmpxx2fp4xm/file-input.txt'.
FAILED tests/test_cli.py::test_cli_commands[file-input-email-message] - assert "Usage: serve.../ '--host'.\n" == ''
FAILED tests/test_cli.py::test_cli_commands[file-input-slack-message] - ValueError: File to read must exist: '/tmp/pytest-of-vagrant/pytest-3/test_cli_commands_file_input_s1/tmp1x1jvtyn/file-input.txt'.
FAILED tests/test_cli.py::test_cli_commands[docker-container-alert-manager] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb76354c5e0>,)'...
FAILED tests/test_cli.py::test_cli_commands[docker-container-file-output] - NotImplementedError
FAILED tests/test_cli.py::test_cli_commands[docker-container-stream-output] - NotImplementedError
FAILED tests/test_cli.py::test_cli_commands[docker-container-email-message] - assert "Usage: serve.../ '--host'.\n" == ''
FAILED tests/test_cli.py::test_cli_commands[docker-container-slack-message] - NameError: name 'self' is not defined
FAILED tests/test_cli.py::test_cli_commands[cpu-alert-manager] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb763777940>,)' kwargs '{'me...
FAILED tests/test_cli.py::test_cli_commands[cpu-file-output] - NotImplementedError
FAILED tests/test_cli.py::test_cli_commands[cpu-stream-output] - NotImplementedError
FAILED tests/test_cli.py::test_cli_commands[cpu-email-message] - assert "Usage: serve.../ '--host'.\n" == ''
FAILED tests/test_cli.py::test_cli_commands[cpu-slack-message] - NameError: name 'self' is not defined
FAILED tests/test_cli.py::test_cli_commands[memory-alert-manager] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb7636c58b0>,)' kwargs '{...
FAILED tests/test_cli.py::test_cli_commands[memory-file-output] - NotImplementedError
FAILED tests/test_cli.py::test_cli_commands[memory-stream-output] - NotImplementedError
FAILED tests/test_cli.py::test_cli_commands[memory-email-message] - assert "Usage: serve.../ '--host'.\n" == ''
FAILED tests/test_cli.py::test_cli_commands[memory-slack-message] - NameError: name 'self' is not defined
FAILED tests/test_cli.py::test_cli_commands[stream-input-alert-manager] - ValueError: Could not read input in agent format: ''.
FAILED tests/test_cli.py::test_cli_commands[stream-input-file-output] - ValueError: Could not read input in agent format: ''.
FAILED tests/test_cli.py::test_cli_commands[stream-input-logged-in-users] - ValueError: Could not read input in agent format: ''.
FAILED tests/test_cli.py::test_cli_commands[stream-input-stream-output] - ValueError: Could not read input in agent format: ''.
FAILED tests/test_cli.py::test_cli_commands[stream-input-email-message] - assert "Usage: serve.../ '--host'.\n" == ''
FAILED tests/test_cli.py::test_cli_commands[stream-input-slack-message] - ValueError: Could not read input in agent format: ''.
FAILED tests/test_cli.py::test_cli_commands[statuscake-alert-manager] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb76350afd0>,)' kwarg...
FAILED tests/test_cli.py::test_cli_commands[statuscake-file-output] - NotImplementedError
FAILED tests/test_cli.py::test_cli_commands[statuscake-stream-output] - NotImplementedError
FAILED tests/test_cli.py::test_cli_commands[statuscake-statuscake] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb76340e4f0>,)' kwargs '...
FAILED tests/test_cli.py::test_cli_commands[statuscake-email-message] - assert "Usage: serve.../ '--host'.\n" == ''
FAILED tests/test_cli.py::test_cli_commands[statuscake-slack-message] - NameError: name 'self' is not defined
FAILED tests/test_cli.py::test_cli_commands[systemd-unit-status-alert-manager] - AttributeError: 'SystemdUnitStatusCollectArgs' object has no attribute 'date_parse'
FAILED tests/test_cli.py::test_cli_commands[systemd-unit-status-file-output] - AttributeError: 'SystemdUnitStatusCollectArgs' object has no attribute 'date_parse'
FAILED tests/test_cli.py::test_cli_commands[systemd-unit-status-logged-in-users] - AttributeError: 'SystemdUnitStatusCollectArgs' object has no attribute 'date_parse'
FAILED tests/test_cli.py::test_cli_commands[systemd-unit-status-stream-output] - AttributeError: 'SystemdUnitStatusCollectArgs' object has no attribute 'date_parse'
FAILED tests/test_cli.py::test_cli_commands[systemd-unit-status-email-message] - assert "Usage: serve.../ '--host'.\n" == ''
FAILED tests/test_cli.py::test_cli_commands[systemd-unit-status-slack-message] - AttributeError: 'SystemdUnitStatusCollectArgs' object has no attribute 'date_parse'
FAILED tests/test_cli.py::test_cli_commands[systemd-unit-logs-alert-manager] - ValueError: Must handle args '['journalctl', '--no-hostname', '--all', '--no-pager', '--output=json-pretty', '--unit', 'docker....
FAILED tests/test_cli.py::test_cli_commands[systemd-unit-logs-file-output] - ValueError: Must handle args '['journalctl', '--no-hostname', '--all', '--no-pager', '--output=json-pretty', '--unit', 'docker.se...
FAILED tests/test_cli.py::test_cli_commands[systemd-unit-logs-logged-in-users] - ValueError: Must handle args '['journalctl', '--no-hostname', '--all', '--no-pager', '--output=json-pretty', '--unit', 'docke...
FAILED tests/test_cli.py::test_cli_commands[systemd-unit-logs-stream-output] - ValueError: Must handle args '['journalctl', '--no-hostname', '--all', '--no-pager', '--output=json-pretty', '--unit', 'docker....
FAILED tests/test_cli.py::test_cli_commands[systemd-unit-logs-email-message] - assert "Usage: serve.../ '--host'.\n" == ''
FAILED tests/test_cli.py::test_cli_commands[systemd-unit-logs-slack-message] - ValueError: Must handle args '['journalctl', '--no-hostname', '--all', '--no-pager', '--output=json-pretty', '--unit', 'docker....
FAILED tests/test_cli.py::test_cli_commands[web-app-alert-manager] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb76352ae80>,)' kwargs '...
FAILED tests/test_cli.py::test_cli_commands[web-app-file-output] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb76355ed00>,)' kwargs '{'...
FAILED tests/test_cli.py::test_cli_commands[web-app-logged-in-users] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb7632a6640>,)' kwargs...
FAILED tests/test_cli.py::test_cli_commands[web-app-stream-output] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb7637216a0>,)' kwargs '...
FAILED tests/test_cli.py::test_cli_commands[web-app-email-message] - assert "Usage: serve.../ '--host'.\n" == ''
FAILED tests/test_cli.py::test_cli_commands[web-app-slack-message] - ValueError: Must set requests.sessions.Session.request method for args '(<requests.sessions.Session object at 0x7fb7636ff2b0>,)' kwargs '...
67 failed, 10 passed in 24.98s
ERROR: InvocationError for command /home/vagrant/tox-app/py39/bin/coverage run
