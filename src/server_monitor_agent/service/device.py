import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

from boltons.strutils import bytes2human

from server_monitor_agent.common import ConfigEntryMixin, ReportMixin, RunArgs
from server_monitor_agent.common import TextCompareEntry
from server_monitor_agent.core.local import LocalProgram
from server_monitor_agent.service.agent import AgentItem


@dataclass
class CheckInstanceCpuEntry(ConfigEntryMixin, ReportMixin):
    threshold: float
    group: str = "check"
    type: str = "instance-cpu-status"

    def operation(self, run_args: RunArgs) -> None:

        local = LocalProgram()
        hostname = local.hostname()
        usage = local.cpu_usage(interval=2.0)
        test = float(self.threshold) / 100.0

        status, status_code = self._report_evaluate(usage, test)

        timezone_str = local.timezone()
        timezone = ZoneInfo(timezone_str)
        date = datetime.now(tz=timezone)

        if status == self._pass:
            title = "Normal CPU use"
            descr = f"Normal CPU use of {usage:.1%} (threshold {test:.1%})."
        else:
            title = "High CPU use"
            descr = (
                f"High CPU use of {usage:.1%} (threshold {test:.1%}). "
                f"Check instance for excessive or faulty processes."
            )

        item = AgentItem(
            service_name="cpu",
            host_name=hostname,
            source_name="instance",
            status_code=status_code,
            status_name=status,
            title=title,
            description=descr.strip(),
            check_name=self.key,
            check_type=self.type,
            date=date,
            tags={},
        )
        self._do_output(run_args, item)


@dataclass
class CheckInstanceMemoryEntry(ConfigEntryMixin, ReportMixin):

    threshold: float
    group: str = "check"
    type: str = "instance-memory-status"

    def operation(self, run_args: RunArgs) -> None:
        local = LocalProgram()
        hostname = local.hostname()
        usage = local.memory()
        usage_percent = float(usage.percent) / 100.0
        usage_amount_gib = round(usage.available / (math.pow(1024, 3)), 2)
        test = float(self.threshold) / 100.0

        status, status_code = self._report_evaluate(usage_percent, test)

        timezone_str = local.timezone()
        timezone = ZoneInfo(timezone_str)
        date = datetime.now(tz=timezone)

        if status == self._pass:
            title = "Normal memory use"
            descr = (
                f"Normal memory use of {usage_percent:.1%} "
                f"({usage_amount_gib}GiB, threshold {test:.1%})."
            )
        else:
            title = "High memory use"
            descr = (
                f"High memory use of {usage_percent:.1%} "
                f"({usage_amount_gib}GiB, threshold {test:.1%}). "
                f"Check instance for excessive or changed memory use."
            )

        item = AgentItem(
            service_name="memory",
            host_name=hostname,
            source_name="instance",
            status_code=status_code,
            status_name=status,
            title=title,
            description=descr.strip(),
            check_name=self.key,
            check_type=self.type,
            date=date,
            tags={
                "total": str(usage.total),
                "available": str(usage.available),
                "percent": str(usage.percent),
                "used": str(usage.used),
                "free": str(usage.free),
            },
        )
        self._do_output(run_args, item)


@dataclass
class CheckDiskEntry(ConfigEntryMixin, ReportMixin):

    threshold: float
    path: str
    device: str
    uuid: str
    label: str
    group: str = "check"
    type: str = "instance-disk-status"

    def operation(self, run_args: RunArgs) -> None:

        if not self.path and not self.device and not self.uuid and not self.label:
            raise ValueError(
                "Must specify at least one disk identifier (path,device,uuid,label"
            )

        local = LocalProgram()
        hostname = local.hostname()
        timezone_str = local.timezone()
        timezone = ZoneInfo(timezone_str)
        date = datetime.now(tz=timezone)

        findmnt = local.findmnt()
        mnt = None
        for mnt in findmnt:
            if self.device and self.device != mnt.source:
                continue
            if self.path and self.path != mnt.target:
                continue
            if self.uuid and mnt.uuid and self.uuid != mnt.uuid:
                continue
            if self.label and mnt.label and self.label != mnt.label:
                continue
            mnt = mnt
            break

        if not mnt:
            raise ValueError(
                f"No disk matched path='{self.path}', device='{self.device}', "
                f"uuid='{self.uuid}', label='{self.label}'."
            )

        partitions = local.partitions()
        partition = None
        for part in partitions:
            if self.device and self.device != part.device and part.device == mnt.source:
                continue
            if (
                self.path
                and self.path != part.mountpoint
                and part.mountpoint == mnt.target
            ):
                continue
            partition = part
            break

        if partition is None:
            raise ValueError(
                f"No partition matched path='{self.path}', device='{self.device}'."
            )

        usage = partition.percent / 100.0
        test = float(self.threshold) / 100.0
        status, status_code = self._report_evaluate(usage, test)

        mount_point = partition.mountpoint
        path = mnt.target

        if status == self._pass:
            title = f"Normal disk {path} use"
            descr = (
                f"Normal disk {path} ({mount_point}) "
                f"use of {usage:.1%} (threshold {test:.1%})."
            )
        else:
            title = f"High disk {path} use"
            descr = (
                f"High disk {path} ({mount_point}) "
                f"use of {usage:.1%} (threshold {test:.1%}). "
                "Check instance for excessive log files or "
                "increased application storage use."
            )

        item = AgentItem(
            service_name=f"disk {path}",
            host_name=hostname,
            source_name="instance",
            status_code=status_code,
            status_name=status,
            title=title,
            description=descr.strip(),
            check_name=self.key,
            check_type=self.type,
            date=date,
            tags={
                "fstype": str(partition.fstype),
                "device": str(partition.device),
                "uuid": str(mnt.uuid),
                "options": str(mnt.options),
                "total": str(bytes2human(partition.total)),
                "free": str(bytes2human(partition.free)),
                "used": str(bytes2human(partition.used)),
            },
        )
        self._do_output(run_args, item)


@dataclass
class CheckFileEntry(ConfigEntryMixin, ReportMixin):
    path: Optional[Path]
    state: str
    content: list[TextCompareEntry]
    group: str = "check"
    type: str = "file-status"

    @classmethod
    def load(cls, **kwargs):
        kwargs["content"] = [
            TextCompareEntry.load(comparison=k, value=v)
            for i in kwargs.get("content", [])
            for k, v in i.items()
        ]
        kwargs["path"] = Path(kwargs.get("path")) if kwargs.get("path") else None
        return cls(**kwargs)

    def operation(self, run_args: RunArgs) -> None:
        if not self.path:
            raise ValueError("Must specify path to check.")

        if self.state == "absent" and self.content:
            raise ValueError(
                "Cannot specify content "
                f"when file is expected to be absent for '{self.path}'."
            )

        if not self.path.is_absolute():
            raise ValueError(f"Must provide an absolute path '{self.path}'.")

        states_present = "present"
        states_absent = "absent"
        states_available = [states_present, states_absent]

        if self.state not in states_available:
            raise ValueError(
                f"State must be one of '{', '.join(states_available)}' "
                f"for check '{run_args.name}' ({self.type}'."
            )

        content_contains = "contains"
        content_not_contains = "not_contains"
        content_available = [content_contains, content_not_contains]

        exists = self.path.exists()

        if exists:
            stat = self.path.stat()
            max_bytes = 20000000  # 20MB
            if stat.st_size > max_bytes:
                raise ValueError(
                    f"Cannot check a file larger than 20MB for '{self.path}'."
                )

        local = LocalProgram()
        hostname = local.hostname()
        timezone_str = local.timezone()
        if timezone_str is None:
            raise ValueError()
        timezone = ZoneInfo(timezone_str)
        date = datetime.now(tz=timezone)

        status = self._pass
        status_code = self._pass_code

        descr_state = ""
        if self.state == states_present and exists:
            status = self._pass
            status_code = self._pass_code
            descr_state = "File was found, as expected."

        if self.state == states_present and not exists:
            status = self._crit
            status_code = self._crit_code
            descr_state = "Could not find file in expected path."

        if self.state == "absent" and not exists:
            status = self._pass
            status_code = self._pass_code
            descr_state = "File was absent, as expected."

        if self.state == "absent" and exists:
            status = self._crit
            status_code = self._crit_code
            descr_state = "Found file that was expected to not exist."

        if self.content:
            file_content = self.path.read_text("utf8")
        else:
            file_content = ""

        descr_content = []
        for i in self.content:
            if i.comparison not in content_available:
                raise ValueError(f"Unknown file content comparison '{i.comparison}'.")

            has_content = i.value in file_content
            if i.comparison == content_contains and not has_content:
                status = self._crit
                status_code = self._crit_code
                descr_content.append(
                    f"File did not contain expected content '{i.value}'."
                )

            if i.comparison == content_contains and has_content:
                descr_content.append(f"File contains expected content '{i.value}'.")

            if i.comparison == content_not_contains and has_content:
                status = self._crit
                status_code = self._crit_code
                descr_content.append(f"File contains unexpected content '{i.value}'.")

            if i.comparison == content_not_contains and not has_content:
                descr_content.append(
                    f"File does not contain content '{i.value}', as expected."
                )

        path = self.path

        if status == self._pass:
            title = f"Normal file {path} state"
            descr = (
                f"Normal file {path} state. "
                f"{descr_state} "
                f"{' '.join(descr_content)}"
            )
        else:
            title = f"Unexpected file {path} state"
            descr = (
                f"Unexpected file {path} state. "
                f"{descr_state} "
                f"{' '.join(descr_content)}"
                " Check instance for excessive log files or "
                "increased application storage use."
            )

        item = AgentItem(
            service_name=f"file {path}",
            host_name=hostname,
            source_name="instance",
            status_code=status_code,
            status_name=status,
            title=title,
            description=descr.strip(),
            check_name=self.key,
            check_type=self.type,
            date=date,
        )
        self._do_output(run_args, item)


@dataclass
class NotifyLoggedInUsersEntry(ConfigEntryMixin):
    user_group: Optional[str]
    group: str = "notify"
    type: str = "logged-in-users"

    def operation(self, run_args: RunArgs) -> None:
        item = self._get_input(run_args)
        raise NotImplementedError()
