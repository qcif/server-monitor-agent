import dataclasses
import logging
import pathlib
import typing

LOG_LEVEL_CRIT = "critical"
LOG_CODE_CRIT = logging.CRITICAL

LOG_LEVEL_ERROR = "error"
LOG_CODE_ERROR = logging.ERROR

LOG_LEVEL_WARN = "warning"
LOG_CODE_WARN = logging.WARNING

LOG_LEVEL_INFO = "info"
LOG_CODE_INFO = logging.INFO

LOG_LEVEL_DEBUG = "debug"
LOG_CODE_DEBUG = logging.DEBUG

LOG_LEVELS = [
    LOG_LEVEL_CRIT,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_WARN,
    LOG_LEVEL_INFO,
    LOG_LEVEL_DEBUG,
]
LOG_CODES = [
    LOG_CODE_CRIT,
    LOG_CODE_ERROR,
    LOG_CODE_WARN,
    LOG_CODE_INFO,
    LOG_CODE_DEBUG,
]
LOG_ITEMS = {
    LOG_LEVEL_CRIT: LOG_CODE_CRIT,
    LOG_LEVEL_ERROR: LOG_CODE_ERROR,
    LOG_LEVEL_WARN: LOG_CODE_WARN,
    LOG_LEVEL_INFO: LOG_CODE_INFO,
    LOG_LEVEL_DEBUG: LOG_CODE_DEBUG,
}


@dataclasses.dataclass
class CliArgs:
    log_level: str = LOG_LEVEL_INFO
    config_file: typing.Optional[pathlib.Path] = None
