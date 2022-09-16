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
