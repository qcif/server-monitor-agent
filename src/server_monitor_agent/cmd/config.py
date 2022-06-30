import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class ConfigItemMixin:
    group: str
    key: str

    @classmethod
    def _remove_type(cls, **kwargs):
        assert kwargs.pop("type") == cls.type
        return kwargs


@dataclass
class CheckInstanceCpuEntry(ConfigItemMixin):
    type = "instance-cpu-status"
    threshold: float

    @classmethod
    def load(cls, **kwargs):
        kwargs = cls._remove_type(**kwargs)
        return CheckInstanceCpuEntry(**kwargs)


@dataclass
class CheckInstanceMemoryEntry(ConfigItemMixin):
    type = "instance-memory-status"
    threshold: float

    @classmethod
    def load(cls, **kwargs):
        kwargs = cls._remove_type(**kwargs)
        return CheckInstanceMemoryEntry(**kwargs)


@dataclass
class CheckDiskEntry(ConfigItemMixin):
    type = "instance-disk-status"
    threshold: float
    path: str
    device: str
    uuid: str
    label: str

    @classmethod
    def load(cls, **kwargs):
        kwargs = cls._remove_type(**kwargs)
        return CheckDiskEntry(**kwargs)


@dataclass
class CheckSystemdUnitEntry(ConfigItemMixin):
    type = "systemd-unit-status"
    name: str

    @classmethod
    def load(cls, **kwargs):
        kwargs = cls._remove_type(**kwargs)
        return CheckSystemdUnitEntry(**kwargs)


@dataclass
class TextCompareEntry:
    comparison: str
    value: str

    @classmethod
    def load(cls, **kwargs):
        return TextCompareEntry(**kwargs)


@dataclass
class DateTimeCompareEntry:
    comparison: str
    value: str

    @classmethod
    def load(cls, **kwargs):
        return DateTimeCompareEntry(**kwargs)


@dataclass
class UrlHeadersEntry:
    name: str
    comparisons: list[TextCompareEntry]

    @classmethod
    def load(cls, **kwargs):
        kwargs["comparisons"] = [
            TextCompareEntry.load(comparison=k, value=v)
            for i in kwargs.get("comparisons", [])
            for k, v in i.items()
        ]
        return UrlHeadersEntry(**kwargs)


@dataclass
class CheckUrlEntry(ConfigItemMixin):
    type = "web-app-status"
    url: str
    headers: list[UrlHeadersEntry]
    content: list[TextCompareEntry]

    @classmethod
    def load(cls, **kwargs):
        kwargs = cls._remove_type(**kwargs)
        kwargs["headers"] = [
            UrlHeadersEntry.load(name=k, comparisons=v)
            for k, v in kwargs.get("headers", {}).items()
        ]
        kwargs["content"] = [
            TextCompareEntry.load(comparison=k, value=v)
            for i in kwargs.get("content", [])
            for k, v in i.items()
        ]
        return CheckUrlEntry(**kwargs)


@dataclass
class CheckFileEntry(ConfigItemMixin):
    type = "file-status"
    path: Optional[Path]
    state: str
    content: list[TextCompareEntry]
    age: list[DateTimeCompareEntry]

    @classmethod
    def load(cls, **kwargs):
        kwargs = cls._remove_type(**kwargs)
        kwargs["content"] = [
            TextCompareEntry.load(comparison=k, value=v)
            for i in kwargs.get("content", [])
            for k, v in i.items()
        ]
        kwargs["age"] = [
            DateTimeCompareEntry.load(comparison=k, value=v)
            for i in kwargs.get("age", [])
            for k, v in i.items()
        ]
        kwargs["path"] = Path(kwargs.get("path")) if kwargs.get("path") else None
        return CheckFileEntry(**kwargs)


@dataclass
class CheckDockerContainerEntry(ConfigItemMixin):
    type = "docker-container-status"
    name: str

    @classmethod
    def load(cls, **kwargs):
        kwargs = cls._remove_type(**kwargs)
        return CheckDockerContainerEntry(**kwargs)


@dataclass
class NotifyLoggedInUsersEntry(ConfigItemMixin):
    type = "logged-in-users"
    user_group: Optional[str]

    @classmethod
    def load(cls, **kwargs):
        kwargs = cls._remove_type(**kwargs)
        return NotifyLoggedInUsersEntry(**kwargs)


@dataclass
class NotifyEmailEntry(ConfigItemMixin):
    type = "email"
    address: str

    @classmethod
    def load(cls, **kwargs):
        kwargs = cls._remove_type(**kwargs)
        return NotifyEmailEntry(**kwargs)


@dataclass
class NotifyStatusCakeEntry(ConfigItemMixin):
    type = "statuscake-agent"

    @classmethod
    def load(cls, **kwargs):
        kwargs = cls._remove_type(**kwargs)
        return NotifyStatusCakeEntry(**kwargs)


@dataclass
class NotifySlackEntry(ConfigItemMixin):
    type = "slack"
    webhook: str

    @classmethod
    def load(cls, **kwargs):
        kwargs = cls._remove_type(**kwargs)
        return NotifySlackEntry(**kwargs)


class Config:
    _logger: logging.Logger = logging.getLogger(__name__)
    _known = {
        "check": {
            CheckInstanceCpuEntry.type: CheckInstanceCpuEntry,
            CheckInstanceMemoryEntry.type: CheckInstanceMemoryEntry,
            CheckDiskEntry.type: CheckDiskEntry,
            CheckSystemdUnitEntry.type: CheckSystemdUnitEntry,
            CheckUrlEntry.type: CheckUrlEntry,
            CheckFileEntry.type: CheckFileEntry,
            CheckDockerContainerEntry.type: CheckDockerContainerEntry,
        },
        "notify": {
            NotifyLoggedInUsersEntry.type: NotifyLoggedInUsersEntry,
            NotifyEmailEntry.type: NotifyEmailEntry,
            NotifyStatusCakeEntry.type: NotifyStatusCakeEntry,
            NotifySlackEntry.type: NotifySlackEntry,
        },
    }

    def __init__(self, path: Path):
        self._path = path

    def load(self) -> list[ConfigItemMixin]:
        if not self._path or not self._path.exists():
            self._logger.error(f"Invalid config file '{self._path}'.")
            data = {}
        else:
            with open(self._path, "rt") as p:
                data = yaml.safe_load(p)

        errors = []
        items = []

        for group_name, group_items in data.items():
            if group_name not in self._known:
                errors.append(
                    f"Unknown top-level key '{group_name}'. "
                    f"Choose from '{', '.join(sorted(self._known.keys()))}'."
                )
                continue
            group_data = self._known[group_name]

            for item_name, item_props in group_items.items():
                item_type = item_props.get("type")
                if item_type not in group_data:
                    errors.append(
                        f"Unknown {group_name} type '{item_type}' for '{item_name}'. "
                        f"Choose from '{', '.join(sorted(group_data.keys()))}'."
                    )
                    continue
                item_class = group_data[item_type]
                try:
                    item = item_class.load(
                        **{**item_props, "key": item_name, "group": group_name}
                    )
                    items.append(item)
                except (TypeError, AttributeError) as e:
                    errors.append(
                        f"Could not load {group_name} type '{item_type}' for '{item_name}'. "
                        f"Properties '{', '.join(sorted(item_props))}'. "
                        f"Error {e.__class__.__name__}: {e}"
                    )

        if errors:
            for error in errors:
                self._logger.error(error)
            raise ValueError(f"Could not load config file '{self._path}'.")

        return items
