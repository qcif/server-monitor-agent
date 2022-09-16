#!/usr/bin/env bash

# Runs an example of each of the server-monitor-agent collect and send commands.

# clear the stores for a new run
# file output dir (file-output)
# maildev (email-message)
# restart python script that acts as webhook (alert-manager, statuscake, slack-message)


# collect examples to file-output
server-monitor-agent consul-checks \
  file-output
server-monitor-agent cpu \
  file-output
server-monitor-agent disk \
  file-output
server-monitor-agent docker-container \
  file-output
server-monitor-agent file-input \
  file-output
server-monitor-agent file-status \
  file-output
server-monitor-agent memory \
  file-output
server-monitor-agent statuscake \
  file-output
server-monitor-agent stream-input \
  file-output
server-monitor-agent systemd-unit-logs \
  file-output
server-monitor-agent systemd-unit-status \
  file-output
server-monitor-agent web-app \
  file-output

# send examples
server-monitor-agent systemd-unit-status \
  alert-manager
server-monitor-agent systemd-unit-status \
  file-output
server-monitor-agent systemd-unit-status \
  logged-in-users
server-monitor-agent systemd-unit-status \
  stream-output
server-monitor-agent systemd-unit-status \
  statuscake
server-monitor-agent systemd-unit-status \
  email-message
server-monitor-agent systemd-unit-status \
  slack-message
