from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

_LOGGING_LEVEL_COLORS = {
    "DEBUG": "\033[94m",
    "INFO": "\033[92m",
    "WARNING": "\033[93m",
    "ERROR": "\033[91m",
    "CRITICAL": "\033[91m",
}

_LOG_LEVEL_NAMES = {
    10: "DEBUG",
    20: "INFO",
    30: "WARNING",
    40: "ERROR",
    50: "CRITICAL",
}


class WrappedLogger:
    __slots__ = {"logger"}

    logger: Logger

    def __init__(self, logger: Logger):
        self.logger = logger

    def log(self, level, msg, *args, **kwargs):
        print(_LOGGING_LEVEL_COLORS[_LOG_LEVEL_NAMES[level]], end="")
        self.logger.log(level, msg, *args, **kwargs)
        print("\033[0m", end="")

    def debug(self, msg, *args, **kwargs):
        self.log(10, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.log(20, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.log(30, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.log(40, msg, *args, **kwargs)
