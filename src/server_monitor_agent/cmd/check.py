"""Module to run checks."""


import logging
from typing import Optional

# from server_monitor_agent.service.instance import Instance
from server_monitor_agent.cmd.config import ConfigItemMixin

# from server_monitor_agent.service.web import StatusCake


class Check:
    """Run a check."""

    _logger: logging.Logger = logging.getLogger(__name__)

    def __init__(self, config: list[ConfigItemMixin]):
        self._config = config

    def run(
        self,
        name: str,
        fmt: str,
        std_out: bool,
        std_err: bool,
        write_file: Optional[str],
    ) -> tuple[bool, Optional[str]]:
        """Run a check specified by the name
        with output to the given target in format fmt."""

        # inst = Instance()
        # h = inst.hostname

        # sc = StatusCake()
        # sc.calc_payload()

        return False, None
