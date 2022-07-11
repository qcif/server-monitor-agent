"""Module that defines the command actions."""

import logging
from pathlib import Path
from typing import Optional

import yaml

from server_monitor_agent.common import ConfigEntryMixin, RunArgs
from server_monitor_agent.service.device import CheckInstanceCpuEntry
from server_monitor_agent.service.device import CheckInstanceMemoryEntry, CheckDiskEntry
from server_monitor_agent.service.device import CheckFileEntry, NotifyLoggedInUsersEntry
from server_monitor_agent.service.docker import CheckDockerContainerEntry
from server_monitor_agent.service.slack import NotifySlackEntry
from server_monitor_agent.service.systemd import CheckSystemdUnitEntry
from server_monitor_agent.service.web import CheckUrlEntry, NotifyEmailEntry
from server_monitor_agent.service.status_cake import NotifyStatusCakeEntry


class Manager:
    _logger: logging.Logger = logging.getLogger(__name__)
    _known = [
        CheckInstanceCpuEntry,
        CheckInstanceMemoryEntry,
        CheckDiskEntry,
        CheckSystemdUnitEntry,
        CheckUrlEntry,
        CheckFileEntry,
        CheckDockerContainerEntry,
        NotifyLoggedInUsersEntry,
        NotifyEmailEntry,
        NotifyStatusCakeEntry,
        NotifySlackEntry,
    ]

    def config(self, path: Path):
        if not path or not path.exists():
            self._logger.error(f"Invalid config file '{path}'.")
            data = {}
        else:
            with open(path, "rt") as p:
                data = yaml.safe_load(p)

        known_groups = sorted({i.group for i in self._known})
        known_types = sorted({i.type for i in self._known})
        if len(known_types) != len(self._known):
            raise ValueError("The available config types are not unique.")

        errors = []
        items = []

        for group_name, group_items in data.items():
            if group_name not in known_groups:
                errors.append(
                    f"Unknown top-level key '{group_name}'. "
                    f"Choose from '{', '.join(known_groups)}'."
                )
                continue

            for item_name, item_props in group_items.items():
                orig_props = {**item_props}
                item_type = item_props.pop("type")
                if item_type not in known_types:
                    group_types = sorted(
                        {i.type for i in self._known if i.group == group_name}
                    )
                    errors.append(
                        f"Unknown {group_name} type '{item_type}' for '{item_name}'. "
                        f"Choose from '{', '.join(group_types)}'."
                    )
                    continue
                item_class = next(i for i in self._known if i.type == item_type)
                try:
                    item = item_class.load(**{**item_props, "key": item_name})
                    items.append(item)
                except (TypeError, AttributeError) as e:
                    errors.append(
                        f"Could not load {group_name} "
                        f"type '{item_type}' "
                        f"for '{item_name}'. "
                        f"Properties '{', '.join(sorted(orig_props))}'. "
                        f"Error {e.__class__.__name__}: {e}"
                    )

        if errors:
            for error in errors:
                self._logger.error(error)
            raise ValueError(f"Could not load config file '{path}'.")

        return items

    def process(self, run_args: RunArgs, config_path: Path):
        group = run_args.group
        name = run_args.name

        config = self.config(config_path)

        # group
        if group == "list":
            self._list(config)
            return

        config_group = [i for i in config if i.group == group]

        # config item
        config_item: Optional[ConfigEntryMixin] = next(
            (i for i in config_group if i.key == name), None
        )
        if config_item is None:
            config_names = sorted([i.key for i in config_group])
            raise ValueError(
                f"Unknown name '{name}'. "
                f"Available names are {', '.join(config_names)}",
            )

        config_item.operation(run_args)

    def _list(self, config: list[ConfigEntryMixin]):
        checks = [i for i in config if i.group == "check"]
        notifications = [i for i in config if i.group == "notify"]

        count = len(checks + notifications)
        self._logger.info(f"Listing {count} configured items.")

        self._logger.info(f"-- Listing {len(checks)} checks --")
        for item in checks:
            self._logger.info(f"{item.key}: {item.type}")

        self._logger.info(f"-- Listing {len(notifications)} notifications --")
        for item in notifications:
            self._logger.info(f"{item.key}: {item.type}")
