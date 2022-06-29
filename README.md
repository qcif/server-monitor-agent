# server-monitor-agent

A simple Python application for running checks on a server and sending formatted notifications.

This program is an agent that can be run on server instances.
It provides a number of commands to do common tasks.

## Commands

### Check

Gather information about the instance and report the result via 
exit code and json-formatted output.

### Notify

Send a message to an alerting service.
One message contains details about one service.
