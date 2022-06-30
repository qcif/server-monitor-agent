import logging
from typing import Optional

from server_monitor_agent.cmd.config import ConfigItemMixin


class Notify:
    _logger: logging.Logger = logging.getLogger(__name__)

    def __init__(self, config: list[ConfigItemMixin]):
        self._config = config

    def run(
        self,
        name: str,
        level: Optional[str],
        fmt: str,
        std_int: bool,
        std_err: bool,
        read_file: Optional[str],
    ) -> tuple[bool, Optional[str]]:
        return False, None
