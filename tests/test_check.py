import json
import logging
import re
from importlib.resources import files, as_file
from subprocess import CompletedProcess

from server_monitor_agent.common import ProgramMixin
from server_monitor_agent.entry import main
from tests.helpers import check_logs, log_debug_msgs


def test_check_instance_memory(caplog, capsys, monkeypatch):
    caplog.set_level(logging.DEBUG)
    source = files("tests.resources").joinpath("config-pass.yml")
    with as_file(source) as p:
        config_file = str(p)

    def run_cmd(self, args):
        if args == ["timedatectl", "show"]:
            return CompletedProcess(
                args=["timedatectl", "show"],
                returncode=0,
                stdout="\n".join(
                    [
                        "Timezone=Australia/Brisbane",
                        "LocalRTC=no",
                        "CanNTP=yes",
                        "NTP=no",
                        "NTPSynchronized=no",
                        "TimeUSec=Mon 2022-07-04 20:36:56 AEST",
                        "RTCTimeUSec=Mon 2022-07-04 20:36:55 AEST",
                        "",
                    ]
                ),
                stderr="",
            )
        else:
            raise ValueError()

    monkeypatch.setattr(ProgramMixin, "_run_cmd", run_cmd)

    cmd = "instance_memory_status"
    main_result = main(
        ["check", cmd, "--std-out", "--config", config_file, "--log-level", "debug"]
    )

    assert main_result == 0

    msgs = log_debug_msgs("check", cmd, config_file, "stdout")
    check_logs(caplog.record_tuples, msgs)

    out, err = capsys.readouterr()

    assert err == ""

    actual = out
    actual = re.sub('"total": ".*?",\n', '"total": "REPLACED",\n', actual)
    actual = re.sub('"available": ".*?",\n', '"available": "REPLACED",\n', actual)
    actual = re.sub('"percent": ".*?",\n', '"percent": "45.1",\n', actual)
    actual = re.sub('"used": ".*?",\n', '"used": "REPLACED",\n', actual)
    actual = re.sub('"free": ".*?"\n', '"free": "REPLACED"\n', actual)
    actual = re.sub('"date": ".*?",\n', '"date": "REPLACED",\n', actual)
    actual = re.sub(
        '"description": ".*?",\n',
        '"description": "Normal memory use of 45.1% (0.52GiB, threshold 80.0%).",\n',
        actual,
    )
    assert actual == json.dumps(
        {
            "service_name": "memory",
            "host_name": "server-monitor-agent",
            "source_name": "instance",
            "status_code": "0",
            "status_name": "passing",
            "title": "Normal memory use",
            "description": "Normal memory use of 45.1% (0.52GiB, threshold 80.0%).",
            "check_name": "instance_memory_status",
            "check_type": "instance-memory-status",
            "date": "REPLACED",
            "tags": {
                "total": "REPLACED",
                "available": "REPLACED",
                "percent": "45.1",
                "used": "REPLACED",
                "free": "REPLACED",
            },
        },
        indent=2,
    )


def test_check_systemctl_show(caplog, capsys, monkeypatch):
    caplog.set_level(logging.DEBUG)
    source = files("tests.resources").joinpath("config-pass.yml")
    with as_file(source) as p:
        config_file = str(p)

    def run_cmd(self, args):
        args1 = ["systemctl", "show", "logrotate.timer", "--all"]
        if args == args1:
            return CompletedProcess(
                args=args1,
                returncode=0,
                stdout="Unit=logrotate.service\nTimersCalendar={ OnCalendar=*-*-* 00:00:00 ; next_elapse=Tue 2022-07-05 00:00:00 AEST }\nOnClockChange=no\nOnTimezoneChange=no\nNextElapseUSecRealtime=Tue 2022-07-05 00:00:00 AEST\nNextElapseUSecMonotonic=0\nLastTriggerUSec=Mon 2022-07-04 18:56:33 AEST\nLastTriggerUSecMonotonic=3.259839s\nResult=success\nAccuracyUSec=12h\nRandomizedDelayUSec=0\nPersistent=yes\nWakeSystem=no\nRemainAfterElapse=yes\nId=logrotate.timer\nNames=logrotate.timer\nFollowing=\nRequires=-.mount sysinit.target\nRequisite=\nWants=\nBindsTo=\nPartOf=\nRequiredBy=\nRequisiteOf=\nWantedBy=timers.target\nBoundBy=\nConsistsOf=\nConflicts=shutdown.target\nConflictedBy=\nBefore=logrotate.service timers.target shutdown.target\nAfter=time-sync.target -.mount sysinit.target\nOnFailure=\nTriggers=logrotate.service\nTriggeredBy=\nPropagatesReloadTo=\nReloadPropagatedFrom=\nJoinsNamespaceOf=\nRequiresMountsFor=/var/lib/systemd/timers\nDocumentation=man:logrotate(8) man:logrotate.conf(5)\nDescription=Daily rotation of log files\nLoadState=loaded\nActiveState=active\nSubState=waiting\nFragmentPath=/lib/systemd/system/logrotate.timer\nSourcePath=\nDropInPaths=\nUnitFileState=enabled\nUnitFilePreset=enabled\nStateChangeTimestamp=Mon 2022-07-04 18:56:33 AEST\nStateChangeTimestampMonotonic=3597223\nInactiveExitTimestamp=Mon 2022-07-04 18:56:33 AEST\nInactiveExitTimestampMonotonic=3257598\nActiveEnterTimestamp=Mon 2022-07-04 18:56:33 AEST\nActiveEnterTimestampMonotonic=3257598\nActiveExitTimestamp=\nActiveExitTimestampMonotonic=0\nInactiveEnterTimestamp=\nInactiveEnterTimestampMonotonic=0\nCanStart=yes\nCanStop=yes\nCanReload=no\nCanIsolate=no\nCanClean=state\nJob=\nStopWhenUnneeded=no\nRefuseManualStart=no\nRefuseManualStop=no\nAllowIsolate=no\nDefaultDependencies=yes\nOnFailureJobMode=replace\nIgnoreOnIsolate=no\nNeedDaemonReload=no\nJobTimeoutUSec=infinity\nJobRunningTimeoutUSec=infinity\nJobTimeoutAction=none\nJobTimeoutRebootArgument=\nConditionResult=yes\nAssertResult=yes\nConditionTimestamp=Mon 2022-07-04 18:56:33 AEST\nConditionTimestampMonotonic=3257568\nAssertTimestamp=Mon 2022-07-04 18:56:33 AEST\nAssertTimestampMonotonic=3257570\nConditions=[unprintable]\nAsserts=[unprintable]\nLoadError=\nTransient=no\nPerpetual=no\nStartLimitIntervalUSec=10s\nStartLimitBurst=5\nStartLimitAction=none\nFailureAction=none\nFailureActionExitStatus=[not set]\nSuccessAction=none\nSuccessActionExitStatus=[not set]\nRebootArgument=\nInvocationID=6aaab19bbae44920a228d3765519a9ca\nCollectMode=inactive\nRefs=\n",
                stderr="",
            )

        args2 = [
            "journalctl",
            "--no-hostname",
            "--all",
            "--no-pager",
            "--output=json-pretty",
            "--unit",
            "logrotate.timer",
            "--output-fields=MESSAGE,JOB_RESULT,UNIT,_HOSTNAME,__REALTIME_TIMESTAMP",
        ]
        if args == args2:
            return CompletedProcess(
                args=args2,
                returncode=0,
                stdout='{\n\t"_HOSTNAME" : "ubuntu2004.localdomain",\n\t"MESSAGE" : "Started Daily rotation of log files.",\n\t"__REALTIME_TIMESTAMP" : "1656492955118769",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=28a;b=d621914a53c74c79997ba4e18dd7fdf1;m=30b47c;t=5e2925229acb1;x=8b247a251787dc5b",\n\t"__MONOTONIC_TIMESTAMP" : "3191932",\n\t"_BOOT_ID" : "d621914a53c74c79997ba4e18dd7fdf1",\n\t"UNIT" : "logrotate.timer",\n\t"JOB_RESULT" : "done"\n}\n{\n\t"_BOOT_ID" : "d621914a53c74c79997ba4e18dd7fdf1",\n\t"MESSAGE" : "logrotate.timer: Succeeded.",\n\t"__MONOTONIC_TIMESTAMP" : "10883007676",\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"UNIT" : "logrotate.timer",\n\t"__REALTIME_TIMESTAMP" : "1656503834934513",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=5f1;b=d621914a53c74c79997ba4e18dd7fdf1;m=288ad84bc;t=5e294daa67cf1;x=b0665ab456526726"\n}\n{\n\t"__REALTIME_TIMESTAMP" : "1656503834934741",\n\t"MESSAGE" : "Stopped Daily rotation of log files.",\n\t"__MONOTONIC_TIMESTAMP" : "10883007905",\n\t"UNIT" : "logrotate.timer",\n\t"_BOOT_ID" : "d621914a53c74c79997ba4e18dd7fdf1",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=5f2;b=d621914a53c74c79997ba4e18dd7fdf1;m=288ad85a1;t=5e294daa67dd5;x=9265ffda6c288b67",\n\t"JOB_RESULT" : "done",\n\t"_HOSTNAME" : "server-monitor-agent"\n}\n{\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"UNIT" : "logrotate.timer",\n\t"__MONOTONIC_TIMESTAMP" : "3198728",\n\t"MESSAGE" : "Started Daily rotation of log files.",\n\t"_BOOT_ID" : "0774337e1eaf4273b2758100eeba89a6",\n\t"__REALTIME_TIMESTAMP" : "1656583463118452",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=971;b=0774337e1eaf4273b2758100eeba89a6;m=30cf08;t=5e2a764dc2674;x=680bdc9f74b5675e",\n\t"JOB_RESULT" : "done"\n}\n{\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=bb5;b=0774337e1eaf4273b2758100eeba89a6;m=3473b69e1;t=5e2aaabe6c14d;x=829ba61b659b5bd",\n\t"UNIT" : "logrotate.timer",\n\t"__REALTIME_TIMESTAMP" : "1656597539897677",\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"_BOOT_ID" : "0774337e1eaf4273b2758100eeba89a6",\n\t"MESSAGE" : "logrotate.timer: Succeeded.",\n\t"__MONOTONIC_TIMESTAMP" : "14079977953"\n}\n{\n\t"JOB_RESULT" : "done",\n\t"MESSAGE" : "Stopped Daily rotation of log files.",\n\t"__REALTIME_TIMESTAMP" : "1656597539897852",\n\t"UNIT" : "logrotate.timer",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=bb6;b=0774337e1eaf4273b2758100eeba89a6;m=3473b6a8f;t=5e2aaabe6c1fc;x=bdd7f8753874f5cb",\n\t"_BOOT_ID" : "0774337e1eaf4273b2758100eeba89a6",\n\t"__MONOTONIC_TIMESTAMP" : "14079978127",\n\t"_HOSTNAME" : "server-monitor-agent"\n}\n{\n\t"_BOOT_ID" : "21477bd6b4aa4e3c95f6ae2d137c4896",\n\t"UNIT" : "logrotate.timer",\n\t"__MONOTONIC_TIMESTAMP" : "3249850",\n\t"MESSAGE" : "Started Daily rotation of log files.",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=f34;b=21477bd6b4aa4e3c95f6ae2d137c4896;m=3196ba;t=5e2b595968d61;x=2a7492db7d583cde",\n\t"JOB_RESULT" : "done",\n\t"__REALTIME_TIMESTAMP" : "1656644410183009",\n\t"_HOSTNAME" : "server-monitor-agent"\n}\n{\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=190d;b=21477bd6b4aa4e3c95f6ae2d137c4896;m=abd725f05;t=5e2c052d755ac;x=e80da992fba23a6a",\n\t"__MONOTONIC_TIMESTAMP" : "46128062213",\n\t"UNIT" : "logrotate.timer",\n\t"_BOOT_ID" : "21477bd6b4aa4e3c95f6ae2d137c4896",\n\t"__REALTIME_TIMESTAMP" : "1656690534995372",\n\t"MESSAGE" : "logrotate.timer: Succeeded.",\n\t"_HOSTNAME" : "server-monitor-agent"\n}\n{\n\t"_BOOT_ID" : "21477bd6b4aa4e3c95f6ae2d137c4896",\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"UNIT" : "logrotate.timer",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=190e;b=21477bd6b4aa4e3c95f6ae2d137c4896;m=abd725f3d;t=5e2c052d755e4;x=88486a450905e0d1",\n\t"MESSAGE" : "Stopped Daily rotation of log files.",\n\t"__MONOTONIC_TIMESTAMP" : "46128062269",\n\t"JOB_RESULT" : "done",\n\t"__REALTIME_TIMESTAMP" : "1656690534995428"\n}\n{\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"JOB_RESULT" : "done",\n\t"__REALTIME_TIMESTAMP" : "1656724892285290",\n\t"MESSAGE" : "Started Daily rotation of log files.",\n\t"_BOOT_ID" : "f12d448f81f84ef9baee9f66a08526c7",\n\t"UNIT" : "logrotate.timer",\n\t"__MONOTONIC_TIMESTAMP" : "3348863",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=1c9a;b=f12d448f81f84ef9baee9f66a08526c7;m=33197f;t=5e2c852b1f96a;x=58fe8fe3f5340a5c"\n}\n{\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"UNIT" : "logrotate.timer",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=2405;b=f12d448f81f84ef9baee9f66a08526c7;m=e2ebb4761;t=5e2e0ac77e2e7;x=7b2be38a8d68f756",\n\t"_BOOT_ID" : "f12d448f81f84ef9baee9f66a08526c7",\n\t"MESSAGE" : "logrotate.timer: Succeeded.",\n\t"__REALTIME_TIMESTAMP" : "1656829477642983",\n\t"__MONOTONIC_TIMESTAMP" : "60913567585"\n}\n{\n\t"__MONOTONIC_TIMESTAMP" : "60913569747",\n\t"UNIT" : "logrotate.timer",\n\t"JOB_RESULT" : "done",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=2406;b=f12d448f81f84ef9baee9f66a08526c7;m=e2ebb4fd3;t=5e2e0ac77eb59;x=5d2ec45875ae4ec4",\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"_BOOT_ID" : "f12d448f81f84ef9baee9f66a08526c7",\n\t"MESSAGE" : "Stopped Daily rotation of log files.",\n\t"__REALTIME_TIMESTAMP" : "1656829477645145"\n}\n{\n\t"_BOOT_ID" : "3facf06aafaa44da9b0f883df6025f82",\n\t"MESSAGE" : "Started Daily rotation of log files.",\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"__MONOTONIC_TIMESTAMP" : "3238487",\n\t"JOB_RESULT" : "done",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=27e6;b=3facf06aafaa44da9b0f883df6025f82;m=316a57;t=5e2e11bf5abf7;x=9f9975c3fd9a42c",\n\t"__REALTIME_TIMESTAMP" : "1656831348157431",\n\t"UNIT" : "logrotate.timer"\n}\n{\n\t"UNIT" : "logrotate.timer",\n\t"MESSAGE" : "logrotate.timer: Succeeded.",\n\t"__REALTIME_TIMESTAMP" : "1656846180373998",\n\t"_BOOT_ID" : "3facf06aafaa44da9b0f883df6025f82",\n\t"__MONOTONIC_TIMESTAMP" : "14835455054",\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=32f6;b=3facf06aafaa44da9b0f883df6025f82;m=37443144e;t=5e2e4900755ee;x=a3655c851e93d447"\n}\n{\n\t"__REALTIME_TIMESTAMP" : "1656846180374300",\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"UNIT" : "logrotate.timer",\n\t"JOB_RESULT" : "done",\n\t"__MONOTONIC_TIMESTAMP" : "14835455355",\n\t"MESSAGE" : "Stopped Daily rotation of log files.",\n\t"_BOOT_ID" : "3facf06aafaa44da9b0f883df6025f82",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=32f8;b=3facf06aafaa44da9b0f883df6025f82;m=37443157b;t=5e2e49007571c;x=8adc0e50b3b966b0"\n}\n{\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"MESSAGE" : "Started Daily rotation of log files.",\n\t"UNIT" : "logrotate.timer",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=36cc;b=a217c18d86764c14b6e4ee9553f20505;m=31c963;t=5e2f6e9a380a1;x=239fbddd52b88114",\n\t"__REALTIME_TIMESTAMP" : "1656924993192097",\n\t"JOB_RESULT" : "done",\n\t"__MONOTONIC_TIMESTAMP" : "3262819",\n\t"_BOOT_ID" : "a217c18d86764c14b6e4ee9553f20505"\n}\n',
                stderr="",
            )
        else:
            raise ValueError()

    monkeypatch.setattr(ProgramMixin, "_run_cmd", run_cmd)

    cmd = "logrotate_status"
    main_result = main(
        ["check", cmd, "--std-out", "--config", config_file, "--log-level", "debug"]
    )

    assert main_result == 0

    msgs = log_debug_msgs("check", cmd, config_file, "stdout")
    check_logs(caplog.record_tuples, msgs)

    out, err = capsys.readouterr()

    assert err == ""
    actual = out
    assert actual == json.dumps(
        {
            "service_name": "systemd unit logrotate.timer",
            "host_name": "server-monitor-agent",
            "source_name": "systemd",
            "status_code": "0",
            "status_name": "passing",
            "title": "",
            "description": "",
            "check_name": "logrotate_status",
            "check_type": "systemd-unit-status",
            "date": "2022-07-04T18:56:33+10:00",
            "tags": {
                "exit_code": 0,
                "name": "logrotate.timer",
                "id": "logrotate.timer",
                "load_state": "loaded",
                "active_state": "active",
                "sub_state": "waiting",
                "description": "Daily rotation of log files",
                "unit_file_state": "enabled",
                "unit_file_preset": "enabled",
                "inactive_exit_timestamp": "Mon 2022-07-04 18:56:33 AEST",
                "active_enter_timestamp": "Mon 2022-07-04 18:56:33 AEST",
                "can_start": "yes",
                "can_stop": "yes",
                "result": "success",
                "unit": "logrotate.service",
                "next_elapse_u_sec_realtime": "Tue 2022-07-05 00:00:00 AEST",
                "last_trigger_u_sec": "Mon 2022-07-04 18:56:33 AEST",
                "triggers": "logrotate.service",
                "log1": "Started Daily rotation of log files.",
                "log2": "logrotate.timer: Succeeded.",
                "log3": "Stopped Daily rotation of log files.",
                "log4": "Started Daily rotation of log files.",
                "log5": "logrotate.timer: Succeeded.",
            },
        },
        indent=2,
    )


def test_check_file_present(caplog, capsys, monkeypatch):
    caplog.set_level(logging.DEBUG)
    source = files("tests.resources").joinpath("config-pass.yml")
    with as_file(source) as p:
        config_file = str(p)

    def run_cmd(self, args):
        args1 = ["timedatectl", "show"]
        if args == args1:
            return CompletedProcess(
                args=args1,
                returncode=0,
                stdout="\n".join(
                    [
                        "Timezone=Australia/Brisbane",
                        "LocalRTC=no",
                        "CanNTP=yes",
                        "NTP=no",
                        "NTPSynchronized=no",
                        "TimeUSec=Mon 2022-07-04 20:36:56 AEST",
                        "RTCTimeUSec=Mon 2022-07-04 20:36:55 AEST",
                        "",
                    ]
                ),
                stderr="",
            )
        else:
            raise ValueError()

    monkeypatch.setattr(ProgramMixin, "_run_cmd", run_cmd)

    cmd = "bashrc_file"
    main_result = main(
        ["check", cmd, "--std-out", "--config", config_file, "--log-level", "debug"]
    )

    assert main_result == 0

    msgs = log_debug_msgs("check", cmd, config_file, "stdout")
    check_logs(caplog.record_tuples, msgs)

    out, err = capsys.readouterr()

    assert err == ""
    actual = out
    actual = re.sub('"date": ".*?",\n', '"date": "REPLACED",\n', actual)
    assert actual == json.dumps(
        {
            "service_name": "file /etc/bash.bashrc",
            "host_name": "server-monitor-agent",
            "source_name": "instance",
            "status_code": "0",
            "status_name": "passing",
            "title": "Normal file /etc/bash.bashrc state",
            "description": "Normal file /etc/bash.bashrc state. "
            "File was found, as expected. "
            "File does not contain content 'error', as expected.",
            "check_name": "bashrc_file",
            "check_type": "file-status",
            "date": "REPLACED",
            "tags": {},
        },
        indent=2,
    )


def test_check_file_missing(caplog, capsys, monkeypatch):
    caplog.set_level(logging.DEBUG)
    source = files("tests.resources").joinpath("config-pass.yml")
    with as_file(source) as p:
        config_file = str(p)

    def run_cmd(self, args):
        args1 = ["timedatectl", "show"]
        if args == args1:
            return CompletedProcess(
                args=args1,
                returncode=0,
                stdout="\n".join(
                    [
                        "Timezone=Australia/Brisbane",
                        "LocalRTC=no",
                        "CanNTP=yes",
                        "NTP=no",
                        "NTPSynchronized=no",
                        "TimeUSec=Mon 2022-07-04 20:36:56 AEST",
                        "RTCTimeUSec=Mon 2022-07-04 20:36:55 AEST",
                        "",
                    ]
                ),
                stderr="",
            )
        else:
            raise ValueError()

    monkeypatch.setattr(ProgramMixin, "_run_cmd", run_cmd)

    cmd = "missing_file"
    main_result = main(
        ["check", cmd, "--std-out", "--config", config_file, "--log-level", "debug"]
    )

    assert main_result == 0

    msgs = log_debug_msgs("check", cmd, config_file, "stdout")
    check_logs(caplog.record_tuples, msgs)

    out, err = capsys.readouterr()

    assert err == ""
    actual = out
    actual = re.sub('"date": ".*?",\n', '"date": "REPLACED",\n', actual)
    assert actual == json.dumps(
        {
            "service_name": "file /does/not/exist",
            "host_name": "server-monitor-agent",
            "source_name": "instance",
            "status_code": "0",
            "status_name": "passing",
            "title": "Normal file /does/not/exist state",
            "description": "Normal file /does/not/exist state. File was absent, as expected.",
            "check_name": "missing_file",
            "check_type": "file-status",
            "date": "REPLACED",
            "tags": {},
        },
        indent=2,
    )


def test_check_url(caplog, capsys, monkeypatch):
    caplog.set_level(logging.DEBUG)
    source = files("tests.resources").joinpath("config-pass.yml")
    with as_file(source) as p:
        config_file = str(p)

    cmd = "github_octocat_status"
    main_result = main(
        ["check", cmd, "--std-out", "--config", config_file, "--log-level", "debug"]
    )

    assert main_result == 0
    msgs = log_debug_msgs("check", cmd, config_file, "stdout")
    check_logs(caplog.record_tuples, msgs)

    out, err = capsys.readouterr()
    assert err == ""
    assert out == ""


def test_check_container(caplog, capsys, monkeypatch):
    caplog.set_level(logging.DEBUG)
    source = files("tests.resources").joinpath("config-pass.yml")
    with as_file(source) as p:
        config_file = str(p)

    def run_cmd(self, args):
        args1 = ["timedatectl", "show"]
        args2 = [
            "docker",
            "inspect",
            "--format",
            '{"ID":"{{ .Id }}", "Inspect": {{json .State }}, "Name":"{{ .Name }}"}',
            "consul",
        ]
        if args == args1:
            return CompletedProcess(
                args=args1,
                returncode=0,
                stdout="\n".join(
                    [
                        "Timezone=Australia/Brisbane",
                        "LocalRTC=no",
                        "CanNTP=yes",
                        "NTP=no",
                        "NTPSynchronized=no",
                        "TimeUSec=Mon 2022-07-04 20:36:56 AEST",
                        "RTCTimeUSec=Mon 2022-07-04 20:36:55 AEST",
                        "",
                    ]
                ),
                stderr="",
            )

        elif args == args2:
            return CompletedProcess(
                args=args1,
                returncode=0,
                stdout='{"ID":"0c75363484ff552017795a8cd1810e1bc7c2689cf936b99e219d50cd2504e166", "Inspect": {"Dead":false,"Error":"","ExitCode":0,"FinishedAt":"2022-07-04T12:09:27.743600549Z","OOMKilled":false,"Paused":false,"Pid":6654,"Restarting":false,"Running":true,"StartedAt":"2022-07-07T09:28:27.103848434Z","Status":"running"}, "Name":"/consul"}\n',
                stderr="",
            )
        else:
            raise ValueError()

    monkeypatch.setattr(ProgramMixin, "_run_cmd", run_cmd)

    cmd = "consul_container"
    main_result = main(
        ["check", cmd, "--std-out", "--config", config_file, "--log-level", "debug"]
    )

    assert main_result == 0

    msgs = log_debug_msgs("check", cmd, config_file, "stdout")
    check_logs(caplog.record_tuples, msgs)

    out, err = capsys.readouterr()

    assert err == ""
    actual = out
    actual = re.sub('"date": ".*?",\n', '"date": "REPLACED",\n', actual)
    assert actual == json.dumps(
        {
            "service_name": "container consul",
            "host_name": "server-monitor-agent",
            "source_name": "docker",
            "status_code": "0",
            "status_name": "passing",
            "title": "Normal container consul state",
            "description": "Normal container consul state running health (no health check).",
            "check_name": "consul_container",
            "check_type": "docker-container-status",
            "date": "REPLACED",
            "tags": {},
        },
        indent=2,
    )
