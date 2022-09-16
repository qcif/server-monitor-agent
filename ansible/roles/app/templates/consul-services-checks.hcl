# instance node level checks
checks = [
  {
    id       = "system-cpu",
    name     = "system-cpu",
    notes    = "This health check for the instance's cpu usage.",
    interval = "1m",
    timeout  = "30s",
    args     = [
      #  cpu
      "{{ app_bin_path }}",
      "10"
    ]
  },
  {
    id       = "system-disk",
    name     = "system-disk",
    notes    = "This health check for the instance's disk usage.",
    interval = "1m",
    timeout  = "30s",
    args     = [
      #  disk
      "{{ app_bin_path }}",
      "80"
    ]
  },
  {
    id       = "system-mem",
    name     = "system-mem",
    notes    = "This health check for the instance's memory usage.",
    interval = "1m",
    timeout  = "30s",
    args     = [
      #  memory
      "{{ app_bin_path }}",
      "15"
    ]
  },
]

# per-service checks
services {
  id   = "automatic-updates"
  name = "automatic-updates"
  tags = [
    "application",
    "security",
  ]
  checks  = [
    #  systemd-unit-status
    {
      id       = "automatic-updates-systemd",
      name     = "automatic-updates-systemd",
      notes    = "A heath check for the automatic updates service and information about any updates performed.",
      interval = "1m",
      timeout  = "30s",
      args     = [
        "{{ app_bin_path }}",
        "systemd-unit-status",
        "--name",
        "unattended-upgrades.service",
        # stream-output
        "stream-output"
      ],
      status = "warning"
    },
    #  file-status
    {
      id       = "automatic-updates-reboot-required",
      name     = "automatic-updates-reboot-required",
      notes    = "A heath check for whether a system reboot is required.",
      interval = "1m",
      timeout  = "30s",
      args     = [
        "{{ app_bin_path }}",
        "file-status",
        "--state",
        "absent",
        "--path",
        "/var/run/reboot-required",
        # email-message
        "email-message",
        "--host", "localhost",
        "--port", "1025",
        "--from", "sender@localhost",
        "--to", "recipient@localhost",
      ],
    },
  ]
}

services {
  id   = "ssh"
  name = "ssh"
  tags = [
    "communication",
    "security",
  ]
  checks  = [
    #  systemd-unit-logs
    {
      id       = "ssh-journald",
      name     = "ssh-journald",
      notes    = "A heath check for the ssh service logs.",
      interval = "1m",
      timeout  = "30s",
      args     = [
        "{{ app_bin_path }}",
        "systemd-unit-logs",
        "--name",
        "ssh.service",
        "stream-output"
      ],
    },
    ]
}

services {
    id   = "email"
  name = "email"
  tags = [
    "communication",
    "docker",
  ]
  checks  = [
    #  docker-container
    {
      id       = "email-docker",
      name     = "email-docker",
      notes    = "A heath check for the email docker container.",
      interval = "1m",
      timeout  = "30s",
      args     = [
        "{{ app_bin_path }}",
        "docker-container",
        "--name",
        "email",
        "--state",
        "running",
        "--health",
        "healthy",
        # logged-in-users
        "logged-in-users",
        "--user-group",
        "vagrant",
      ],
      status = "warning",
    },
    ]
}


# /var/run/reboot-required
# /var/run/reboot-required.pkgs
# /var/lib/apt/periodic/unattended-upgrades-stamp
# /var/lib/apt/periodic/update-success-stamp

# TODO: other potential things to check
# tail -n 15 /var/log/unattended-upgrades/*
# cat /var/run/reboot-required
# apt list --upgradeable
# ls -halt /var/log/apt
# ls -halt /var/lib/apt/periodic

# stamp="/var/lib/update-notifier/updates-available"
# [ ! -r "$stamp" ] || cat "$stamp"

# in:
#  consul-checks        Get a summary of consul check statuses.
#  file-input           Load input from a file.
#  statuscake           Collect data for the statuscake agent.
#  stream-input         Read input from a stream.
#  web-app              Check the response to a url request.

# out:
# file-output      Write to a file.
# slack-message    Send a slack message.
