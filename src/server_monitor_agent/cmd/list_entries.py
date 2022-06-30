import logging

from server_monitor_agent.cmd.config import ConfigItemMixin


class ListEntries:
    _logger: logging.Logger = logging.getLogger(__name__)

    def __init__(self, config: list[ConfigItemMixin]):
        self._config = config

    def run(self):

        checks = [i for i in self._config if i.group == "check"]
        notifications = [i for i in self._config if i.group == "notify"]

        count = len(checks + notifications)
        self._logger.info(f"Listing {count} configured items.")

        self._logger.info(f"-- Listing {len(checks)} checks --")
        for item in checks:
            self._logger.info(f"{item.key}: {item.type}")

        self._logger.info(f"-- Listing {len(notifications)} notifications --")
        for item in notifications:
            self._logger.info(f"{item.key}: {item.type}")

        return True, None
