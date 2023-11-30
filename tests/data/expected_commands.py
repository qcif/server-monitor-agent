expected_items = {
    "collect": [
        {"command": "consul-checks", "args": "HealthCheckCollectArgs"},
        {"command": "disk", "args": "DiskCollectArgs"},
        {"command": "file-status", "args": "FileInputCollectArgs"},
        {"command": "file-input", "args": "FileStatusCollectArgs"},
        {"command": "docker-container", "args": "ContainerStatusCollectArgs"},
        {"command": "cpu", "args": "CpuCollectArgs"},
        {"command": "memory", "args": "MemoryCollectArgs"},
        {"command": "stream-input", "args": "StreamInputCollectArgs"},
        {"command": "statuscake", "args": "StatusCakeCollectArgs"},
        {"command": "systemd-unit-status", "args": "SystemdUnitLogsCollectArgs"},
        {"command": "systemd-unit-logs", "args": "SystemdUnitStatusCollectArgs"},
        {"command": "web-app", "args": "RequestUrlCollectArgs"},
    ],
    "send": [
        # {"command": "alert-manager", "args": "AlertManagerSendArgs"},
        {"command": "file-output", "args": "FileOutputSendArgs"},
        {"command": "logged-in-users", "args": "LoggedInUsersSendArgs"},
        {"command": "stream-output", "args": "StreamOutputSendArgs"},
        {"command": "statuscake", "args": "StatusCakeSendArgs"},
        {"command": "email-message", "args": "EmailMessageSendArgs"},
        {"command": "slack-message", "args": "SlackMessageSendArgs"},
    ],
    "exclusions": [
        ("consul-checks", "statuscake"),
        ("disk", "statuscake"),
        ("file-status", "statuscake"),
        ("file-input", "statuscake"),
        ("docker-container", "statuscake"),
        ("cpu", "statuscake"),
        ("memory", "statuscake"),
        ("stream-input", "statuscake"),
        ("systemd-unit-status", "statuscake"),
        ("systemd-unit-logs", "statuscake"),
        ("web-app", "statuscake"),
    ],
    "pairs": [],
}


for c in expected_items["collect"]:
    for s in expected_items["send"]:
        find = (c["command"], s["command"])
        if find not in expected_items["exclusions"]:
            expected_items["pairs"].append(find)
