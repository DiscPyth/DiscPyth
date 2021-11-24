import sys
import time


class WSAlreadyOpenError(Exception):
    def __init__(self, shard_id):
        self.msg = f"WebSocket already open for shard {shard_id}"
        super().__init__(self.msg)


class WSClosedError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
        self.rmsg = f"{code if code != '' or code is not None else ''}{' - '+msg if msg != '' or msg is not None else ''}"
        super().__init__(self.rmsg)


class WSError(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(msg)


_LEVEL_S_NAMES = {
    "unset": 0,
    "spam": 5,
    "debug": 10,
    "info": 20,
    "warning": 30,
    "warn": 30,
    "error": 40,
    "critical": 50,
}

_LEVEL_NAMES = {
    5: "SPAM",
    10: "DEBUG",
    20: "INFO",
    30: "WARNING",
    40: "ERROR",
    50: "CRITICAL",
}

_LEVEL_COLORS = {
    5: "\u001b[38;5;7m",
    10: "\u001b[38;5;15m",
    20: "\u001b[38;5;39m",
    30: "\u001b[38;5;208m",
    40: "\u001b[38;5;160m",
    50: "\u001b[38;5;196m",
}


class Logging:  # pylint: disable=too-many-instance-attributes
    __slots__ = {
        "out",
        "level",
        "to_file",
        "fname",
        "lname",
        "fmt",
    }

    def __init__(  # pylint: disable=too-many-arguments;
        self,
        name,
        log_level=30,
        to_file=False,
        file="logs.log",
        fmt="[{name}] [{time}] [{module}] [{level}] | {msg}",
    ):
        self.out = sys.stdout
        self.level = self._get_level(log_level)
        self.to_file = to_file
        self.fname = file
        self.lname = name
        self.fmt = fmt

    def _get_level(self, level):  # pylint: disable=no-self-use;
        if level not in (
            0,
            5,
            10,
            20,
            30,
            40,
            50,
        ):
            return 30
        if isinstance(level, str):
            return _LEVEL_S_NAMES.get(level, 30)
        return level

    def log_message(self, lvl, msg, mod):
        if lvl not in (5, 10, 20, 30, 40, 50):
            lvl = 5
        rmsg = self.fmt.format(
            name=self.lname,
            time=time.ctime(time.time()),
            module=mod,
            level=_LEVEL_NAMES[lvl],
            msg=msg,
        )
        return (_LEVEL_COLORS[lvl] + rmsg + "\u001b[0m"), rmsg

    def _write(self, msg):
        rmsg = msg[1]
        msg = msg[0] + "\n"
        if self.level != 0:
            self.out.write(msg)
        if self.to_file:
            with open(self.fname, "a", encoding="utf-8") as file:
                file.write(rmsg)

    def log(self, lvl, msg, mod=""):
        if self.level <= lvl:
            self._write(self.log_message(lvl, msg, mod))

    def spam(self, msg, mod=""):
        self.log(5, msg, mod)

    def debug(self, msg, mod=""):
        self.log(10, msg, mod)

    def info(self, msg, mod=""):
        self.log(20, msg, mod)

    def warn(self, msg, mod=""):
        self.log(30, msg, mod)

    def error(self, msg, mod=""):
        self.log(40, msg, mod)

    def critical(self, msg, mod=""):
        self.log(50, msg, mod)
