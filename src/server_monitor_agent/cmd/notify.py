import logging
from typing import Optional


class Notify:
    _logger: logging.Logger = logging.getLogger(__name__)

    def run(
        self,
        name: str,
        level: Optional[str],
        fmt: str,
        std_int: bool,
        std_err: bool,
        read_file: Optional[str],
    ) -> tuple[bool, str]:
        return True, ""
