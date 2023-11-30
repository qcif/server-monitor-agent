# import json
# import logging
# import re
# from importlib_resources import files, as_file
# from subprocess import CompletedProcess
#
# from server_monitor_agent.common import ProgramMixin
# from server_monitor_agent.entry import main
# from tests.helpers import check_logs, log_debug_msgs
#
#
# def test_check_instance_memory(caplog, capsys, monkeypatch):
#     caplog.set_level(logging.DEBUG)
#     source = files("tests.resources").joinpath("config-pass.yml")
#     with as_file(source) as p:
#         config_file = str(p)
#
#     def run_cmd(self, args):
#         if args == ["timedatectl", "show"]:
#             return CompletedProcess(
#                 args=["timedatectl", "show"],
#                 returncode=0,
#                 stdout="\n".join(
#                     [
#                         "Timezone=Australia/Brisbane",
#                         "LocalRTC=no",
#                         "CanNTP=yes",
#                         "NTP=no",
#                         "NTPSynchronized=no",
#                         "TimeUSec=Mon 2022-07-04 20:36:56 AEST",
#                         "RTCTimeUSec=Mon 2022-07-04 20:36:55 AEST",
#                         "",
#                     ]
#                 ),
#                 stderr="",
#             )
#         else:
#             raise ValueError()
#
#     monkeypatch.setattr(ProgramMixin, "_run_cmd", run_cmd)
#
#     cmd = "instance_memory_status"
#     main_result = main(
#         ["check", cmd, "--std-out", "--config", config_file, "--log-level", "debug"]
#     )
#
#     assert main_result == 0
#
#     msgs = log_debug_msgs("check", cmd, config_file, "stdout")
#     check_logs(caplog.record_tuples, msgs)
#
#     out, err = capsys.readouterr()
#
#     assert err == ""
#
#     actual = out
#     actual = re.sub('"total": ".*?",\n', '"total": "REPLACED",\n', actual)
#     actual = re.sub('"available": ".*?",\n', '"available": "REPLACED",\n', actual)
#     actual = re.sub('"percent": ".*?",\n', '"percent": "45.1",\n', actual)
#     actual = re.sub('"used": ".*?",\n', '"used": "REPLACED",\n', actual)
#     actual = re.sub('"free": ".*?"\n', '"free": "REPLACED"\n', actual)
#     actual = re.sub('"date": ".*?",\n', '"date": "REPLACED",\n', actual)
#     actual = re.sub(
#         '"description": ".*?",\n',
#         '"description": "Normal memory use of 45.1% (0.52GiB, threshold 80.0%).",\n',
#         actual,
#     )
#     assert actual == json.dumps(
#         {
#             "service_name": "memory",
#             "host_name": "server-monitor-agent",
#             "source_name": "instance",
#             "status_code": "0",
#             "status_name": "passing",
#             "title": "Normal memory use",
#             "description": "Normal memory use of 45.1% (0.52GiB, threshold 80.0%).",
#             "check_name": "instance_memory_status",
#             "check_type": "instance-memory-status",
#             "date": "REPLACED",
#             "tags": {
#                 "total": "REPLACED",
#                 "available": "REPLACED",
#                 "percent": "45.1",
#                 "used": "REPLACED",
#                 "free": "REPLACED",
#             },
#         },
#         indent=2,
#     )
#
#
# def test_check_systemctl_show(caplog, capsys, monkeypatch):
#     caplog.set_level(logging.DEBUG)
#     source = files("tests.resources").joinpath("config-pass.yml")
#     with as_file(source) as p:
#         config_file = str(p)
#
#     def run_cmd(self, args):
#         args1 = ["systemctl", "show", "logrotate.timer", "--all"]
#         if args == args1:
#             return CompletedProcess(
#                 args=args1,
#                 returncode=0,
#                 stdout="Unit=logrotate.service\nTimersCalendar={ OnCalendar=*-*-* 00:00:00 ; next_elapse=Tue 2022-07-05 00:00:00 AEST }\nOnClockChange=no\nOnTimezoneChange=no\nNextElapseUSecRealtime=Tue 2022-07-05 00:00:00 AEST\nNextElapseUSecMonotonic=0\nLastTriggerUSec=Mon 2022-07-04 18:56:33 AEST\nLastTriggerUSecMonotonic=3.259839s\nResult=success\nAccuracyUSec=12h\nRandomizedDelayUSec=0\nPersistent=yes\nWakeSystem=no\nRemainAfterElapse=yes\nId=logrotate.timer\nNames=logrotate.timer\nFollowing=\nRequires=-.mount sysinit.target\nRequisite=\nWants=\nBindsTo=\nPartOf=\nRequiredBy=\nRequisiteOf=\nWantedBy=timers.target\nBoundBy=\nConsistsOf=\nConflicts=shutdown.target\nConflictedBy=\nBefore=logrotate.service timers.target shutdown.target\nAfter=time-sync.target -.mount sysinit.target\nOnFailure=\nTriggers=logrotate.service\nTriggeredBy=\nPropagatesReloadTo=\nReloadPropagatedFrom=\nJoinsNamespaceOf=\nRequiresMountsFor=/var/lib/systemd/timers\nDocumentation=man:logrotate(8) man:logrotate.conf(5)\nDescription=Daily rotation of log files\nLoadState=loaded\nActiveState=active\nSubState=waiting\nFragmentPath=/lib/systemd/system/logrotate.timer\nSourcePath=\nDropInPaths=\nUnitFileState=enabled\nUnitFilePreset=enabled\nStateChangeTimestamp=Mon 2022-07-04 18:56:33 AEST\nStateChangeTimestampMonotonic=3597223\nInactiveExitTimestamp=Mon 2022-07-04 18:56:33 AEST\nInactiveExitTimestampMonotonic=3257598\nActiveEnterTimestamp=Mon 2022-07-04 18:56:33 AEST\nActiveEnterTimestampMonotonic=3257598\nActiveExitTimestamp=\nActiveExitTimestampMonotonic=0\nInactiveEnterTimestamp=\nInactiveEnterTimestampMonotonic=0\nCanStart=yes\nCanStop=yes\nCanReload=no\nCanIsolate=no\nCanClean=state\nJob=\nStopWhenUnneeded=no\nRefuseManualStart=no\nRefuseManualStop=no\nAllowIsolate=no\nDefaultDependencies=yes\nOnFailureJobMode=replace\nIgnoreOnIsolate=no\nNeedDaemonReload=no\nJobTimeoutUSec=infinity\nJobRunningTimeoutUSec=infinity\nJobTimeoutAction=none\nJobTimeoutRebootArgument=\nConditionResult=yes\nAssertResult=yes\nConditionTimestamp=Mon 2022-07-04 18:56:33 AEST\nConditionTimestampMonotonic=3257568\nAssertTimestamp=Mon 2022-07-04 18:56:33 AEST\nAssertTimestampMonotonic=3257570\nConditions=[unprintable]\nAsserts=[unprintable]\nLoadError=\nTransient=no\nPerpetual=no\nStartLimitIntervalUSec=10s\nStartLimitBurst=5\nStartLimitAction=none\nFailureAction=none\nFailureActionExitStatus=[not set]\nSuccessAction=none\nSuccessActionExitStatus=[not set]\nRebootArgument=\nInvocationID=6aaab19bbae44920a228d3765519a9ca\nCollectMode=inactive\nRefs=\n",
#                 stderr="",
#             )
#
#         args2 = [
#             "journalctl",
#             "--no-hostname",
#             "--all",
#             "--no-pager",
#             "--output=json-pretty",
#             "--unit",
#             "logrotate.timer",
#             "--output-fields=MESSAGE,JOB_RESULT,UNIT,_HOSTNAME,__REALTIME_TIMESTAMP",
#         ]
#         if args == args2:
#             return CompletedProcess(
#                 args=args2,
#                 returncode=0,
#                 stdout='{\n\t"_HOSTNAME" : "ubuntu2004.localdomain",\n\t"MESSAGE" : "Started Daily rotation of log files.",\n\t"__REALTIME_TIMESTAMP" : "1656492955118769",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=28a;b=d621914a53c74c79997ba4e18dd7fdf1;m=30b47c;t=5e2925229acb1;x=8b247a251787dc5b",\n\t"__MONOTONIC_TIMESTAMP" : "3191932",\n\t"_BOOT_ID" : "d621914a53c74c79997ba4e18dd7fdf1",\n\t"UNIT" : "logrotate.timer",\n\t"JOB_RESULT" : "done"\n}\n{\n\t"_BOOT_ID" : "d621914a53c74c79997ba4e18dd7fdf1",\n\t"MESSAGE" : "logrotate.timer: Succeeded.",\n\t"__MONOTONIC_TIMESTAMP" : "10883007676",\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"UNIT" : "logrotate.timer",\n\t"__REALTIME_TIMESTAMP" : "1656503834934513",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=5f1;b=d621914a53c74c79997ba4e18dd7fdf1;m=288ad84bc;t=5e294daa67cf1;x=b0665ab456526726"\n}\n{\n\t"__REALTIME_TIMESTAMP" : "1656503834934741",\n\t"MESSAGE" : "Stopped Daily rotation of log files.",\n\t"__MONOTONIC_TIMESTAMP" : "10883007905",\n\t"UNIT" : "logrotate.timer",\n\t"_BOOT_ID" : "d621914a53c74c79997ba4e18dd7fdf1",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=5f2;b=d621914a53c74c79997ba4e18dd7fdf1;m=288ad85a1;t=5e294daa67dd5;x=9265ffda6c288b67",\n\t"JOB_RESULT" : "done",\n\t"_HOSTNAME" : "server-monitor-agent"\n}\n{\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"UNIT" : "logrotate.timer",\n\t"__MONOTONIC_TIMESTAMP" : "3198728",\n\t"MESSAGE" : "Started Daily rotation of log files.",\n\t"_BOOT_ID" : "0774337e1eaf4273b2758100eeba89a6",\n\t"__REALTIME_TIMESTAMP" : "1656583463118452",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=971;b=0774337e1eaf4273b2758100eeba89a6;m=30cf08;t=5e2a764dc2674;x=680bdc9f74b5675e",\n\t"JOB_RESULT" : "done"\n}\n{\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=bb5;b=0774337e1eaf4273b2758100eeba89a6;m=3473b69e1;t=5e2aaabe6c14d;x=829ba61b659b5bd",\n\t"UNIT" : "logrotate.timer",\n\t"__REALTIME_TIMESTAMP" : "1656597539897677",\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"_BOOT_ID" : "0774337e1eaf4273b2758100eeba89a6",\n\t"MESSAGE" : "logrotate.timer: Succeeded.",\n\t"__MONOTONIC_TIMESTAMP" : "14079977953"\n}\n{\n\t"JOB_RESULT" : "done",\n\t"MESSAGE" : "Stopped Daily rotation of log files.",\n\t"__REALTIME_TIMESTAMP" : "1656597539897852",\n\t"UNIT" : "logrotate.timer",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=bb6;b=0774337e1eaf4273b2758100eeba89a6;m=3473b6a8f;t=5e2aaabe6c1fc;x=bdd7f8753874f5cb",\n\t"_BOOT_ID" : "0774337e1eaf4273b2758100eeba89a6",\n\t"__MONOTONIC_TIMESTAMP" : "14079978127",\n\t"_HOSTNAME" : "server-monitor-agent"\n}\n{\n\t"_BOOT_ID" : "21477bd6b4aa4e3c95f6ae2d137c4896",\n\t"UNIT" : "logrotate.timer",\n\t"__MONOTONIC_TIMESTAMP" : "3249850",\n\t"MESSAGE" : "Started Daily rotation of log files.",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=f34;b=21477bd6b4aa4e3c95f6ae2d137c4896;m=3196ba;t=5e2b595968d61;x=2a7492db7d583cde",\n\t"JOB_RESULT" : "done",\n\t"__REALTIME_TIMESTAMP" : "1656644410183009",\n\t"_HOSTNAME" : "server-monitor-agent"\n}\n{\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=190d;b=21477bd6b4aa4e3c95f6ae2d137c4896;m=abd725f05;t=5e2c052d755ac;x=e80da992fba23a6a",\n\t"__MONOTONIC_TIMESTAMP" : "46128062213",\n\t"UNIT" : "logrotate.timer",\n\t"_BOOT_ID" : "21477bd6b4aa4e3c95f6ae2d137c4896",\n\t"__REALTIME_TIMESTAMP" : "1656690534995372",\n\t"MESSAGE" : "logrotate.timer: Succeeded.",\n\t"_HOSTNAME" : "server-monitor-agent"\n}\n{\n\t"_BOOT_ID" : "21477bd6b4aa4e3c95f6ae2d137c4896",\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"UNIT" : "logrotate.timer",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=190e;b=21477bd6b4aa4e3c95f6ae2d137c4896;m=abd725f3d;t=5e2c052d755e4;x=88486a450905e0d1",\n\t"MESSAGE" : "Stopped Daily rotation of log files.",\n\t"__MONOTONIC_TIMESTAMP" : "46128062269",\n\t"JOB_RESULT" : "done",\n\t"__REALTIME_TIMESTAMP" : "1656690534995428"\n}\n{\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"JOB_RESULT" : "done",\n\t"__REALTIME_TIMESTAMP" : "1656724892285290",\n\t"MESSAGE" : "Started Daily rotation of log files.",\n\t"_BOOT_ID" : "f12d448f81f84ef9baee9f66a08526c7",\n\t"UNIT" : "logrotate.timer",\n\t"__MONOTONIC_TIMESTAMP" : "3348863",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=1c9a;b=f12d448f81f84ef9baee9f66a08526c7;m=33197f;t=5e2c852b1f96a;x=58fe8fe3f5340a5c"\n}\n{\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"UNIT" : "logrotate.timer",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=2405;b=f12d448f81f84ef9baee9f66a08526c7;m=e2ebb4761;t=5e2e0ac77e2e7;x=7b2be38a8d68f756",\n\t"_BOOT_ID" : "f12d448f81f84ef9baee9f66a08526c7",\n\t"MESSAGE" : "logrotate.timer: Succeeded.",\n\t"__REALTIME_TIMESTAMP" : "1656829477642983",\n\t"__MONOTONIC_TIMESTAMP" : "60913567585"\n}\n{\n\t"__MONOTONIC_TIMESTAMP" : "60913569747",\n\t"UNIT" : "logrotate.timer",\n\t"JOB_RESULT" : "done",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=2406;b=f12d448f81f84ef9baee9f66a08526c7;m=e2ebb4fd3;t=5e2e0ac77eb59;x=5d2ec45875ae4ec4",\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"_BOOT_ID" : "f12d448f81f84ef9baee9f66a08526c7",\n\t"MESSAGE" : "Stopped Daily rotation of log files.",\n\t"__REALTIME_TIMESTAMP" : "1656829477645145"\n}\n{\n\t"_BOOT_ID" : "3facf06aafaa44da9b0f883df6025f82",\n\t"MESSAGE" : "Started Daily rotation of log files.",\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"__MONOTONIC_TIMESTAMP" : "3238487",\n\t"JOB_RESULT" : "done",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=27e6;b=3facf06aafaa44da9b0f883df6025f82;m=316a57;t=5e2e11bf5abf7;x=9f9975c3fd9a42c",\n\t"__REALTIME_TIMESTAMP" : "1656831348157431",\n\t"UNIT" : "logrotate.timer"\n}\n{\n\t"UNIT" : "logrotate.timer",\n\t"MESSAGE" : "logrotate.timer: Succeeded.",\n\t"__REALTIME_TIMESTAMP" : "1656846180373998",\n\t"_BOOT_ID" : "3facf06aafaa44da9b0f883df6025f82",\n\t"__MONOTONIC_TIMESTAMP" : "14835455054",\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=32f6;b=3facf06aafaa44da9b0f883df6025f82;m=37443144e;t=5e2e4900755ee;x=a3655c851e93d447"\n}\n{\n\t"__REALTIME_TIMESTAMP" : "1656846180374300",\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"UNIT" : "logrotate.timer",\n\t"JOB_RESULT" : "done",\n\t"__MONOTONIC_TIMESTAMP" : "14835455355",\n\t"MESSAGE" : "Stopped Daily rotation of log files.",\n\t"_BOOT_ID" : "3facf06aafaa44da9b0f883df6025f82",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=32f8;b=3facf06aafaa44da9b0f883df6025f82;m=37443157b;t=5e2e49007571c;x=8adc0e50b3b966b0"\n}\n{\n\t"_HOSTNAME" : "server-monitor-agent",\n\t"MESSAGE" : "Started Daily rotation of log files.",\n\t"UNIT" : "logrotate.timer",\n\t"__CURSOR" : "s=4aa13044ddd94ea0b377cfcdee865d34;i=36cc;b=a217c18d86764c14b6e4ee9553f20505;m=31c963;t=5e2f6e9a380a1;x=239fbddd52b88114",\n\t"__REALTIME_TIMESTAMP" : "1656924993192097",\n\t"JOB_RESULT" : "done",\n\t"__MONOTONIC_TIMESTAMP" : "3262819",\n\t"_BOOT_ID" : "a217c18d86764c14b6e4ee9553f20505"\n}\n',
#                 stderr="",
#             )
#         else:
#             raise ValueError()
#
#     monkeypatch.setattr(ProgramMixin, "_run_cmd", run_cmd)
#
#     cmd = "logrotate_status"
#     main_result = main(
#         ["check", cmd, "--std-out", "--config", config_file, "--log-level", "debug"]
#     )
#
#     assert main_result == 0
#
#     msgs = log_debug_msgs("check", cmd, config_file, "stdout")
#     check_logs(caplog.record_tuples, msgs)
#
#     out, err = capsys.readouterr()
#
#     assert err == ""
#     actual = out
#     assert actual == json.dumps(
#         {
#             "service_name": "systemd unit logrotate.timer",
#             "host_name": "server-monitor-agent",
#             "source_name": "systemd",
#             "status_code": "0",
#             "status_name": "passing",
#             "title": "",
#             "description": "",
#             "check_name": "logrotate_status",
#             "check_type": "systemd-unit-status",
#             "date": "2022-07-04T18:56:33+10:00",
#             "tags": {
#                 "exit_code": 0,
#                 "name": "logrotate.timer",
#                 "id": "logrotate.timer",
#                 "load_state": "loaded",
#                 "active_state": "active",
#                 "sub_state": "waiting",
#                 "description": "Daily rotation of log files",
#                 "unit_file_state": "enabled",
#                 "unit_file_preset": "enabled",
#                 "inactive_exit_timestamp": "Mon 2022-07-04 18:56:33 AEST",
#                 "active_enter_timestamp": "Mon 2022-07-04 18:56:33 AEST",
#                 "can_start": "yes",
#                 "can_stop": "yes",
#                 "result": "success",
#                 "unit": "logrotate.service",
#                 "next_elapse_u_sec_realtime": "Tue 2022-07-05 00:00:00 AEST",
#                 "last_trigger_u_sec": "Mon 2022-07-04 18:56:33 AEST",
#                 "triggers": "logrotate.service",
#                 "log1": "Started Daily rotation of log files.",
#                 "log2": "logrotate.timer: Succeeded.",
#                 "log3": "Stopped Daily rotation of log files.",
#                 "log4": "Started Daily rotation of log files.",
#                 "log5": "logrotate.timer: Succeeded.",
#                 "log6": "Stopped Daily rotation of log files.",
#             },
#         },
#         indent=2,
#     )
#
#
# def test_check_file_present(caplog, capsys, monkeypatch):
#     caplog.set_level(logging.DEBUG)
#     source = files("tests.resources").joinpath("config-pass.yml")
#     with as_file(source) as p:
#         config_file = str(p)
#
#     def run_cmd(self, args):
#         args1 = ["timedatectl", "show"]
#         if args == args1:
#             return CompletedProcess(
#                 args=args1,
#                 returncode=0,
#                 stdout="\n".join(
#                     [
#                         "Timezone=Australia/Brisbane",
#                         "LocalRTC=no",
#                         "CanNTP=yes",
#                         "NTP=no",
#                         "NTPSynchronized=no",
#                         "TimeUSec=Mon 2022-07-04 20:36:56 AEST",
#                         "RTCTimeUSec=Mon 2022-07-04 20:36:55 AEST",
#                         "",
#                     ]
#                 ),
#                 stderr="",
#             )
#         else:
#             raise ValueError()
#
#     monkeypatch.setattr(ProgramMixin, "_run_cmd", run_cmd)
#
#     cmd = "bashrc_file"
#     main_result = main(
#         ["check", cmd, "--std-out", "--config", config_file, "--log-level", "debug"]
#     )
#
#     assert main_result == 0
#
#     msgs = log_debug_msgs("check", cmd, config_file, "stdout")
#     check_logs(caplog.record_tuples, msgs)
#
#     out, err = capsys.readouterr()
#
#     assert err == ""
#     actual = out
#     actual = re.sub('"date": ".*?",\n', '"date": "REPLACED",\n', actual)
#     assert actual == json.dumps(
#         {
#             "service_name": "file /etc/bash.bashrc",
#             "host_name": "server-monitor-agent",
#             "source_name": "instance",
#             "status_code": "0",
#             "status_name": "passing",
#             "title": "Normal file /etc/bash.bashrc state",
#             "description": "Normal file /etc/bash.bashrc state. "
#             "File was found, as expected. "
#             "File does not contain content 'error', as expected.",
#             "check_name": "bashrc_file",
#             "check_type": "file-status",
#             "date": "REPLACED",
#             "tags": {},
#         },
#         indent=2,
#     )
#
#
# def test_check_file_missing(caplog, capsys, monkeypatch):
#     caplog.set_level(logging.DEBUG)
#     source = files("tests.resources").joinpath("config-pass.yml")
#     with as_file(source) as p:
#         config_file = str(p)
#
#     def run_cmd(self, args):
#         args1 = ["timedatectl", "show"]
#         if args == args1:
#             return CompletedProcess(
#                 args=args1,
#                 returncode=0,
#                 stdout="\n".join(
#                     [
#                         "Timezone=Australia/Brisbane",
#                         "LocalRTC=no",
#                         "CanNTP=yes",
#                         "NTP=no",
#                         "NTPSynchronized=no",
#                         "TimeUSec=Mon 2022-07-04 20:36:56 AEST",
#                         "RTCTimeUSec=Mon 2022-07-04 20:36:55 AEST",
#                         "",
#                     ]
#                 ),
#                 stderr="",
#             )
#         else:
#             raise ValueError()
#
#     monkeypatch.setattr(ProgramMixin, "_run_cmd", run_cmd)
#
#     cmd = "missing_file"
#     main_result = main(
#         ["check", cmd, "--std-out", "--config", config_file, "--log-level", "debug"]
#     )
#
#     assert main_result == 0
#
#     msgs = log_debug_msgs("check", cmd, config_file, "stdout")
#     check_logs(caplog.record_tuples, msgs)
#
#     out, err = capsys.readouterr()
#
#     assert err == ""
#     actual = out
#     actual = re.sub('"date": ".*?",\n', '"date": "REPLACED",\n', actual)
#     assert actual == json.dumps(
#         {
#             "service_name": "file /does/not/exist",
#             "host_name": "server-monitor-agent",
#             "source_name": "instance",
#             "status_code": "0",
#             "status_name": "passing",
#             "title": "Normal file /does/not/exist state",
#             "description": "Normal file /does/not/exist state. File was absent, as expected.",
#             "check_name": "missing_file",
#             "check_type": "file-status",
#             "date": "REPLACED",
#             "tags": {},
#         },
#         indent=2,
#     )
#
#
# def test_check_url(caplog, capsys, monkeypatch):
#     caplog.set_level(logging.DEBUG)
#     source = files("tests.resources").joinpath("config-pass.yml")
#     with as_file(source) as p:
#         config_file = str(p)
#
#     cmd = "github_octocat_status"
#     main_result = main(
#         ["check", cmd, "--std-out", "--config", config_file, "--log-level", "debug"]
#     )
#
#     assert main_result == 0
#     msgs = log_debug_msgs("check", cmd, config_file, "stdout")
#     check_logs(caplog.record_tuples, msgs)
#
#     out, err = capsys.readouterr()
#     assert err == ""
#     assert out == ""
#
#
# def test_check_container(caplog, capsys, monkeypatch):
#     caplog.set_level(logging.DEBUG)
#     source = files("tests.resources").joinpath("config-pass.yml")
#     with as_file(source) as p:
#         config_file = str(p)
#
#     def run_cmd(self, args):
#         args1 = ["timedatectl", "show"]
#         args2 = [
#             "docker",
#             "inspect",
#             "--format",
#             '{"ID":"{{ .Id }}", "Inspect": {{json .State }}, "Name":"{{ .Name }}"}',
#             "consul",
#         ]
#         if args == args1:
#             return CompletedProcess(
#                 args=args1,
#                 returncode=0,
#                 stdout="\n".join(
#                     [
#                         "Timezone=Australia/Brisbane",
#                         "LocalRTC=no",
#                         "CanNTP=yes",
#                         "NTP=no",
#                         "NTPSynchronized=no",
#                         "TimeUSec=Mon 2022-07-04 20:36:56 AEST",
#                         "RTCTimeUSec=Mon 2022-07-04 20:36:55 AEST",
#                         "",
#                     ]
#                 ),
#                 stderr="",
#             )
#
#         elif args == args2:
#             return CompletedProcess(
#                 args=args1,
#                 returncode=0,
#                 stdout='{"ID":"0c75363484ff552017795a8cd1810e1bc7c2689cf936b99e219d50cd2504e166", "Inspect": {"Dead":false,"Error":"","ExitCode":0,"FinishedAt":"2022-07-04T12:09:27.743600549Z","OOMKilled":false,"Paused":false,"Pid":6654,"Restarting":false,"Running":true,"StartedAt":"2022-07-07T09:28:27.103848434Z","Status":"running"}, "Name":"/consul"}\n',
#                 stderr="",
#             )
#         else:
#             raise ValueError()
#
#     monkeypatch.setattr(ProgramMixin, "_run_cmd", run_cmd)
#
#     cmd = "consul_container"
#     main_result = main(
#         ["check", cmd, "--std-out", "--config", config_file, "--log-level", "debug"]
#     )
#
#     assert main_result == 0
#
#     msgs = log_debug_msgs("check", cmd, config_file, "stdout")
#     check_logs(caplog.record_tuples, msgs)
#
#     out, err = capsys.readouterr()
#
#     assert err == ""
#     actual = out
#     actual = re.sub('"date": ".*?",\n', '"date": "REPLACED",\n', actual)
#     assert actual == json.dumps(
#         {
#             "service_name": "container consul",
#             "host_name": "server-monitor-agent",
#             "source_name": "docker",
#             "status_code": "0",
#             "status_name": "passing",
#             "title": "Normal container consul state",
#             "description": "Normal container consul state running health (no health check).",
#             "check_name": "consul_container",
#             "check_type": "docker-container-status",
#             "date": "REPLACED",
#             "tags": {},
#         },
#         indent=2,
#     )

# import logging
# from importlib_resources import files, as_file
# from pathlib import Path
#
# import pytest
#
# from server_monitor_agent.web import UrlResponseEntry, UrlRequestEntry
# from tests.helpers import check_logs
# from server_monitor_agent import common
# from server_monitor_agent.common import RunArgs
# from server_monitor_agent.core.manage import Manager
# from server_monitor_agent import device
# from server_monitor_agent import systemd
# from server_monitor_agent import web
# from server_monitor_agent import docker
# from server_monitor_agent.service import slack
# from server_monitor_agent import status_cake
#
#
# def test_manage_config_pass():
#     source = files("tests.resources").joinpath("config-pass.yml")
#     manage = Manager()
#     with as_file(source) as p:
#         config = manage.config(p)
#
#     items = [
#         device.CheckInstanceCpuEntry(
#             key="instance_cpu_status", threshold=80, group="check"
#         ),
#         device.CheckInstanceMemoryEntry(
#             key="instance_memory_status", threshold=80, group="check"
#         ),
#         device.CheckDiskEntry(
#             key="instance_disk_status",
#             threshold=80,
#             path="/",
#             device="/dev/sda3",
#             uuid="181d63cf-913b-4f0e-a279-6aeb32aa70a1",
#             label="",
#             group="check",
#         ),
#         systemd.CheckSystemdUnitEntry(
#             key="ufw_status", name="ufw.service", group="check"
#         ),
#         systemd.CheckSystemdUnitEntry(
#             key="logrotate_status", name="logrotate.timer", group="check"
#         ),
#         systemd.CheckSystemdUnitEntry(
#             key="network_online_status", name="network-online.target", group="check"
#         ),
#         web.CheckUrlEntry(
#             key="github_octocat_status",
#             request=UrlRequestEntry(
#                 url="https://api.github.com/octocat",
#                 method="GET",
#                 headers={"test_header": "test header value"},
#             ),
#             response=UrlResponseEntry(
#                 status_code=200,
#                 headers=[
#                     web.UrlHeadersEntry(
#                         name="content_type",
#                         comparisons=[
#                             common.TextCompareEntry(
#                                 comparison="contains", value="text/plain"
#                             )
#                         ],
#                     )
#                 ],
#                 content=[common.TextCompareEntry(comparison="contains", value="MMMMM")],
#             ),
#             group="check",
#         ),
#         device.CheckFileEntry(
#             key="bashrc_file",
#             path=Path("/etc/bash.bashrc"),
#             state="present",
#             content=[common.TextCompareEntry(comparison="not_contains", value="error")],
#             group="check",
#         ),
#         device.CheckFileEntry(
#             key="missing_file",
#             path=Path("/does/not/exist"),
#             state="absent",
#             content=[],
#             group="check",
#         ),
#         docker.CheckDockerContainerEntry(
#             key="consul_container",
#             name="consul",
#             state="running",
#             health="ignore",
#             group="check",
#         ),
#         device.NotifyLoggedInUsersEntry(
#             key="test_user_message", user_group="vagrant", group="notify"
#         ),
#         web.NotifyEmailEntry(
#             key="test_email", address="example@example.com", group="notify"
#         ),
#         status_cake.NotifyStatusCakeEntry(key="statuscake_agent", group="notify"),
#         slack.NotifySlackEntry(
#             key="testing_slack", webhook="https://example.com/services", group="notify"
#         ),
#     ]
#
#     for index, item in enumerate(items):
#         assert item == config[index]
#
#
# def test_manage_config_fail(caplog):
#     source = files("tests.resources").joinpath("config-fail.yml")
#     manage = Manager()
#     with as_file(source) as p:
#         with pytest.raises(ValueError) as e:
#             manage.config(p)
#
#     assert "Could not load config file" in str(e.value)
#
#     msgs = [
#         ["Unknown top-level key 'top_level_fail'. Choose from 'check, notify'."],
#         ["Unknown check type 'unknown-type' for 'check_item_fail'. Choose from"],
#         [
#             "Could not load check type 'instance-memory-status' for 'check_item_prop_missing'.",
#             "Properties 'type'.",
#             "missing 1 required positional argument: 'threshold'",
#         ],
#         [
#             "Could not load check type 'systemd-unit-status' for 'check_item_extra_prop'.",
#             "Properties 'name, something, type'.",
#             "got an unexpected keyword argument 'something'",
#         ],
#         [
#             "Could not load check type 'web-app-status' for 'check_item_invalid_text_compare1'.",
#             "Properties 'request, response, type'.",
#             "Error AttributeError: 'str' object has no attribute 'items'",
#         ],
#         [
#             "Could not load check type 'web-app-status' for 'check_item_invalid_text_compare2'.",
#             "Properties 'request, response, type'.",
#             "Error AttributeError: 'str' object has no attribute 'items'",
#         ],
#         [
#             "Could not load check type 'file-status' for 'check_item_invalid_text_compare3'.",
#             "Properties 'content, path, state, type'.",
#             "Error AttributeError: 'str' object has no attribute 'items'",
#         ],
#         [
#             "Unknown notify type 'blah' for 'blah'.",
#             "Choose from 'email, logged-in-users, slack, statuscake-agent'.",
#         ],
#     ]
#     check_logs(caplog.record_tuples, msgs)
#
#
# def test_process_list(caplog):
#     caplog.set_level(logging.DEBUG)
#
#     source = files("tests.resources").joinpath("config-pass.yml")
#     manage = Manager()
#     with as_file(source) as p:
#         run_args = RunArgs(
#             group="list",
#             name=None,
#             level=None,
#             fmt=None,
#             std_io=True,
#             std_err=False,
#             file_path=None,
#         )
#         manage.process(run_args=run_args, config_path=p)
#
#     msgs = [
#         ["Listing 14 configured items."],
#         ["-- Listing 10 checks --"],
#         ["instance_cpu_status: instance-cpu-status"],
#         ["instance_memory_status: instance-memory-status"],
#         ["instance_disk_status: instance-disk-status"],
#         ["ufw_status: systemd-unit-status"],
#         ["logrotate_status: systemd-unit-status"],
#         ["network_online_status: systemd-unit-status"],
#         ["github_octocat_status: web-app-status"],
#         ["bashrc_file: file-status"],
#         ["missing_file: file-status"],
#         ["consul_container: docker-container-status"],
#         ["-- Listing 4 notifications --"],
#         ["test_user_message: logged-in-users"],
#         ["test_email: email"],
#         ["statuscake_agent: statuscake-agent"],
#         ["testing_slack: slack"],
#     ]
#
#     check_logs(caplog.record_tuples, msgs)


# import io
# import logging
# from datetime import datetime
# from importlib_resources import files, as_file
# from subprocess import CompletedProcess
# from tempfile import NamedTemporaryFile
#
# from server_monitor_agent.common import ProgramMixin
# from server_monitor_agent.entry import main
# from server_monitor_agent.service.agent import AgentItem
# from tests.helpers import check_logs, log_debug_msgs
#
#
# def test_notify_user_message_file(caplog, capsys, monkeypatch):
#     caplog.set_level(logging.DEBUG)
#     source = files("tests.resources").joinpath("config-pass.yml")
#     with as_file(source) as p:
#         config_file = str(p)
#
#     item = AgentItem(
#         service_name="service_name",
#         host_name="host_name",
#         source_name="source_name",
#         status_code="status_code",
#         status_name="status_name",
#         title="title",
#         description="description",
#         check_name="check_name",
#         check_type="check_type",
#         date=datetime.now(),
#         tags={"tag1key": "tag1value", "tag2key": "tag2value"},
#     )
#
#     def run_cmd(self, args):
#         if args[0:5] == ["wall", "--timeout", "30", "--group", "vagrant"]:
#             return CompletedProcess(args=args, returncode=0, stdout="", stderr="")
#         else:
#             raise ValueError()
#
#     monkeypatch.setattr(ProgramMixin, "_run_cmd", run_cmd)
#
#     with NamedTemporaryFile(mode="wt") as fp:
#         fp.write(item.to_json())
#         fp.seek(0)
#
#         cmd = "test_user_message"
#         main_result = main(
#             [
#                 "notify",
#                 cmd,
#                 "--read-file",
#                 fp.name,
#                 "--config",
#                 config_file,
#                 "--log-level",
#                 "debug",
#             ]
#         )
#
#     assert main_result == 0
#     msgs = log_debug_msgs("notify", cmd, config_file, "file")
#     check_logs(caplog.record_tuples, msgs)
#
#     out, err = capsys.readouterr()
#     assert err == ""
#     assert out == ""
#
#
# def test_notify_user_message_stdin(caplog, capsys, monkeypatch):
#     caplog.set_level(logging.DEBUG)
#     source = files("tests.resources").joinpath("config-pass.yml")
#     with as_file(source) as p:
#         config_file = str(p)
#
#     item = AgentItem(
#         service_name="service_name",
#         host_name="host_name",
#         source_name="source_name",
#         status_code="status_code",
#         status_name="status_name",
#         title="title",
#         description="description",
#         check_name="check_name",
#         check_type="check_type",
#         date=datetime.now(),
#         tags={"tag1key": "tag1value", "tag2key": "tag2value"},
#     )
#     monkeypatch.setattr("sys.stdin", io.StringIO(item.to_json()))
#
#     def run_cmd(self, args):
#         if args[0:5] == ["wall", "--timeout", "30", "--group", "vagrant"]:
#             return CompletedProcess(args=args, returncode=0, stdout="", stderr="")
#         else:
#             raise ValueError()
#
#     monkeypatch.setattr(ProgramMixin, "_run_cmd", run_cmd)
#
#     cmd = "test_user_message"
#     main_result = main(
#         [
#             "notify",
#             cmd,
#             "--std-in",
#             "--config",
#             config_file,
#             "--log-level",
#             "debug",
#         ]
#     )
#
#     assert main_result == 0
#     msgs = log_debug_msgs("notify", cmd, config_file, "stdin")
#     check_logs(caplog.record_tuples, msgs)
#
#     out, err = capsys.readouterr()
#     assert err == ""
#     assert out == ""
#
#
# def test_notify_email(caplog, capsys, monkeypatch):
#     caplog.set_level(logging.DEBUG)
#     source = files("tests.resources").joinpath("config-pass.yml")
#     with as_file(source) as p:
#         config_file = str(p)
#
#     item = AgentItem(
#         service_name="service_name",
#         host_name="host_name",
#         source_name="source_name",
#         status_code="status_code",
#         status_name="status_name",
#         title="title",
#         description="description",
#         check_name="check_name",
#         check_type="check_type",
#         date=datetime.now(),
#         tags={"tag1key": "tag1value", "tag2key": "tag2value"},
#     )
#
#     with NamedTemporaryFile(mode="wt") as fp:
#         fp.write(item.to_json())
#         fp.seek(0)
#
#         cmd = "test_email"
#         main_result = main(
#             [
#                 "notify",
#                 cmd,
#                 "--read-file",
#                 fp.name,
#                 "--config",
#                 config_file,
#                 "--log-level",
#                 "debug",
#             ]
#         )
#
#     assert main_result == 0
#     msgs = log_debug_msgs("notify", cmd, config_file, "file")
#     check_logs(caplog.record_tuples, msgs)
#
#     out, err = capsys.readouterr()
#     assert err == ""
#     assert out == ""
#
#
# def test_notify_status_cake(caplog, capsys, monkeypatch):
#     caplog.set_level(logging.DEBUG)
#     source = files("tests.resources").joinpath("config-pass.yml")
#     with as_file(source) as p:
#         config_file = str(p)
#
#     with NamedTemporaryFile(mode="wt") as fp:
#         fp.write("")
#         fp.seek(0)
#
#         cmd = "statuscake_agent"
#         main_result = main(
#             [
#                 "notify",
#                 cmd,
#                 "--read-file",
#                 fp.name,
#                 "--config",
#                 config_file,
#                 "--log-level",
#                 "debug",
#             ]
#         )
#
#     assert main_result == 0
#     msgs = log_debug_msgs("notify", cmd, config_file, "file")
#     check_logs(caplog.record_tuples, msgs)
#
#     out, err = capsys.readouterr()
#     assert err == ""
#     assert out == ""
#
#
# def test_notify_slack(caplog, capsys, monkeypatch):
#     caplog.set_level(logging.DEBUG)
#     source = files("tests.resources").joinpath("config-pass.yml")
#     with as_file(source) as p:
#         config_file = str(p)
#
#     item = AgentItem(
#         service_name="service_name",
#         host_name="host_name",
#         source_name="source_name",
#         status_code="status_code",
#         status_name="status_name",
#         title="title",
#         description="description",
#         check_name="check_name",
#         check_type="check_type",
#         date=datetime.now(),
#         tags={"tag1key": "tag1value", "tag2key": "tag2value"},
#     )
#
#     with NamedTemporaryFile(mode="wt") as fp:
#         fp.write(item.to_json())
#         fp.seek(0)
#
#         cmd = "testing_slack"
#         main_result = main(
#             [
#                 "notify",
#                 cmd,
#                 "--read-file",
#                 fp.name,
#                 "--config",
#                 config_file,
#                 "--log-level",
#                 "debug",
#                 "--format",
#                 "consul-watch",
#             ]
#         )
#
#     assert main_result == 0
#     msgs = log_debug_msgs("notify", cmd, config_file, "file")
#     check_logs(caplog.record_tuples, msgs)
#
#     out, err = capsys.readouterr()
#     assert err == ""
#     assert out == ""


# import pytest
#
# from server_monitor_agent.cli import Cli
# from server_monitor_agent.entry import main
#
#
# @pytest.mark.parametrize("option", (["-h"], ["--help"]))
# def test_main(capsys, option):
#     with pytest.raises(SystemExit) as error:
#         main(option)
#
#     out, err = capsys.readouterr()
#
#     assert out.startswith("usage: server-monitor-agent")
#     assert Cli.description in out
#     assert " --help " in out
#     assert " --version " in out
#     assert " --log-level " in out
#     assert "{sub_command}" in out
#     assert " check " in out
#     assert " notify " in out
#     assert " list " in out
#
#     assert err == ""
#
#     assert error.value.code == 0
#
#
# @pytest.mark.parametrize("option", (["check", "-h"], ["check", "--help"]))
# def test_check(capsys, option):
#     with pytest.raises(SystemExit) as error:
#         main(option)
#
#     out, err = capsys.readouterr()
#
#     assert out.startswith("usage: server-monitor-agent check")
#     assert err == ""
#
#     assert error.value.code == 0
#
#
# @pytest.mark.parametrize("option", (["notify", "-h"], ["notify", "--help"]))
# def test_notify(capsys, option):
#     with pytest.raises(SystemExit) as error:
#         main(option)
#
#     out, err = capsys.readouterr()
#
#     assert out.startswith("usage: server-monitor-agent notify")
#     assert err == ""
#
#     assert error.value.code == 0
#
#
# @pytest.mark.parametrize("option", (["list", "-h"], ["list", "--help"]))
# def test_notify(capsys, option):
#     with pytest.raises(SystemExit) as error:
#         main(option)
#
#     out, err = capsys.readouterr()
#
#     assert out.startswith("usage: server-monitor-agent list")
#     assert err == ""
#
#     assert error.value.code == 0
#
#
# @pytest.mark.parametrize("option", (["check", "name"],))
# def test_check_io_required(capsys, option):
#     with pytest.raises(SystemExit) as error:
#         main(option)
#
#     out, err = capsys.readouterr()
#
#     assert out == ""
#     assert (
#         "\nserver-monitor-agent check: error: "
#         "one of the arguments --std-out --std-err --write-file is required\n" in err
#     )
#
#     assert error.value.code == 2


# import logging
#
# import pytest
#
#
# def check_logs(actual, expected):
#     __tracebackhide__ = True
#     for index, (actual_name, actual_level, actual_msg) in enumerate(actual):
#         expected_item = expected[index]
#         if isinstance(expected_item, tuple):
#             expected_name, expected_level, expected_msgs = expected_item
#             assert actual_name == expected_name
#             assert actual_level == expected_level
#         else:
#             expected_msgs = expected_item
#
#         if isinstance(expected_msgs, list):
#             for expected_msg in expected_msgs:
#                 assert expected_msg in actual_msg
#         elif isinstance(expected_msgs, str):
#             assert expected_msgs == actual_msg
#         else:
#             pytest.fail()
#
#     assert len(actual) == len(expected)
#
#
# def log_debug_msgs(
#     group: str,
#     cmd: str,
#     config_file: str,
#     io_name: str,
#     input_format: str = "agent",
# ):
#     lgr = "server-monitor-agent"
#     lvl = logging.DEBUG
#
#     available = {
#         "check": {
#             "file": {
#                 "agent": [
#                     "format='agent'",
#                     "std_out=False,",
#                     "std_err=False,",
#                     "write_file='/",
#                 ]
#             },
#             "stdout": {
#                 "agent": [
#                     "format='agent'",
#                     "std_out=True,",
#                     "std_err=False,",
#                     "write_file=None",
#                 ]
#             },
#             "stderr": {
#                 "agent": [
#                     "format='agent'",
#                     "std_out=False,",
#                     "std_err=True,",
#                     "write_file=None",
#                 ]
#             },
#         },
#         "notify": {
#             "file": {
#                 "agent": [
#                     "format='agent'",
#                     "std_in=False,",
#                     "read_file='/",
#                 ],
#                 "consul-watch": [
#                     "format='consul-watch'",
#                     "std_in=False,",
#                     "read_file='/",
#                 ],
#             },
#             "stdin": {
#                 "agent": [
#                     "format='agent'",
#                     "std_in=True,",
#                     "read_file=None",
#                 ],
#                 "consul-watch": [
#                     "format='consul-watch'",
#                     "std_in=True,",
#                     "read_file=None",
#                 ],
#             },
#         },
#     }
#
#     msgs = [
#         (lgr, lvl, "Running parser with args."),
#         (lgr, lvl, "Starting server-monitor-agent in debug mode."),
#         (
#             lgr,
#             lvl,
#             [
#                 f"Raw arguments: {group} {cmd}",
#                 f"--config {config_file} --log-level debug",
#             ],
#         ),
#         (
#             lgr,
#             lvl,
#             [
#                 "Parsed arguments: Namespace(log_level='debug',",
#                 f"sub_command_name='{group}'",
#                 "func=",
#                 f"name='{cmd}', ",
#                 *available[group][io_name][input_format],
#                 f"config=PosixPath('{config_file}'))",
#             ],
#         ),
#         (lgr, lvl, ["Finished parser func with parsed args in debug mode."]),
#     ]
#
#     return msgs
