from __future__ import annotations

__all__ = ("MISSING", "setup_logger", "define", "dumps", "loads", "override")

from functools import partial
from logging import Formatter, Logger, StreamHandler, getLogger
from typing import TYPE_CHECKING, Any, Set, TypeAlias, Union, get_origin
from inspect import stack as istack

from attrs import define, fields
from attrs import has as attrs_has
from attrs import resolve_types
from cattr import override
from cattr._compat import is_generic
from cattr.converters import GenConverter
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn
from colorama import Fore, Style, init

from .constants import LOGGER_FORMAT

try:
    from cattrs.preconf.orjson import configure_converter
    from orjson import dumps as _dumps
    from orjson import loads as _loads

    ORJSON = True
except ImportError:
    from json import dumps as _dumps
    from json import loads as _loads

    from cattrs.preconf.json import configure_converter

    ORJSON = False

if TYPE_CHECKING:
    from logging import LogRecord

    from .constants import T


class Sentinel:
    __instance = None

    def __new__(cls, *args):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls, *args)
        return cls.__instance

    @staticmethod
    def _get_caller_module() -> str:
        stack = istack()

        caller = stack[2][0]
        return caller.f_globals.get("__name__")

    def __init__(self):
        self.__module__ = self._get_caller_module()
        self.name = type(self).__name__

    def __repr__(self):
        return f"<{self.name}>"

    def __reduce__(self):
        return self.name

    def __copy__(self):
        return self

    def __deepcopy__(self, _):
        return self

    def __getattr__(self, _):
        return None

    def __hash__(self):
        return 0

    def __bool__(self):
        return False


class Missing(Sentinel):
    pass


MISSING = Missing()

Absent: TypeAlias = Union[T, Missing]


# fmt: off
_levelToName = {
    50: "CRITICAL ",
    40: "ERROR    ",
    30: "WARNING  ",
    20: "INFO     ",
    10: "DEBUG    ",
    0:  "NOTSET   ",
}
# fmt: on


class _CustomFormatter(Formatter):
    formats: dict[int, str] = {
        10: f"{Fore.CYAN}{LOGGER_FORMAT}{Fore.RESET}",
        20: f"{Fore.GREEN}{LOGGER_FORMAT}{Fore.RESET}",
        30: f"{Fore.YELLOW}{LOGGER_FORMAT}{Fore.RESET}",
        40: f"{Fore.RED}{LOGGER_FORMAT}{Fore.RESET}",
        50: f"{Style.BRIGHT}{Fore.RED}{LOGGER_FORMAT}{Fore.RESET}{Style.RESET_ALL}",
    }

    def __init__(
        self, fmt=None, datefmt=None, style="{", validate=True, *, defaults=None
    ) -> None:
        super().__init__(
            fmt=fmt, datefmt=datefmt, style=style, validate=validate, defaults=defaults
        )
        init(autoreset=True)

    def format(self, record: LogRecord) -> str:
        self._style._fmt = self.formats.get(record.levelno, LOGGER_FORMAT) % {
            "levelname": _levelToName[record.levelno]
        }
        return Formatter.format(self, record)


def setup_logger(log_level: int = 30, logger_name: str = "discpyth") -> Logger:
    logger = getLogger(logger_name)
    logger.setLevel(log_level)
    lh = StreamHandler()
    lh.setFormatter(_CustomFormatter())
    logger.addHandler(lh)
    return logger


define = partial(define, frozen=True, slots=True)


class PatchedConveter(GenConverter):
    def gen_unstructure_attrs_fromdict(self, cl: type[T]) -> dict[str, Any]:
        # from
        # https://github.com/python-attrs/cattrs/blob/main/src/cattr/converters.py#L710-L728
        origin = get_origin(cl)
        attribs = fields(origin or cl)
        if attrs_has(cl) and any(isinstance(a.type, str) for a in attribs):
            # PEP 563 annotations - need to be resolved.
            resolve_types(cl)
        attrib_overrides = {
            a.name: self.type_overrides[a.type]
            for a in attribs
            if a.type in self.type_overrides
        }

        overrides = cl.__overrides__ if hasattr(cl, "__overrides__") else {}

        h = make_dict_unstructure_fn(
            cl,
            self,
            _cattrs_omit_if_default=self.omit_if_default,
            **attrib_overrides,
            **overrides,
        )
        return h

    def gen_structure_attrs_fromdict(self, cl: type[T]) -> T:
        # from
        # https://github.com/python-attrs/cattrs/blob/main/src/cattr/converters.py#L730-L748
        attribs = fields(get_origin(cl) if is_generic(cl) else cl)
        if attrs_has(cl) and any(isinstance(a.type, str) for a in attribs):
            # PEP 563 annotations - need to be resolved.
            resolve_types(cl)
        attrib_overrides = {
            a.name: self.type_overrides[a.type]
            for a in attribs
            if a.type in self.type_overrides
        }

        overrides = cl.__overrides__ if hasattr(cl, "__overrides__") else {}

        h = make_dict_structure_fn(
            cl,
            self,
            _cattrs_forbid_extra_keys=self.forbid_extra_keys,
            _cattrs_prefer_attrib_converters=self._prefer_attrib_converters,
            **attrib_overrides,
            **overrides,
        )
        # only direct dispatch so that subclasses get separately generated
        return h


converter = PatchedConveter(
    omit_if_default=True, unstruct_collection_overrides={Set: list}
)
configure_converter(converter)


def dumps(obj: Any) -> str:
    dump = _dumps(converter.unstructure(obj))
    if ORJSON:
        return dump.decode()
    return dump


def loads(string: str, obj: type[T]) -> T:
    return converter.structure(_loads(string), obj)
