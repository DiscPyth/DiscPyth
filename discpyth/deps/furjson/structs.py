from __future__ import annotations

__all__ = ("Struct", "StructMeta", "JSONConfig")

from typing import (
    Annotated,
    Any,
    Callable,
    Dict,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Union,
    get_origin,
)


class JSONConfig(NamedTuple):
    name: Optional[str] = None
    object: Optional[Struct] = None

    optional: bool = False
    raw: bool = False

    load_hook: Optional[Callable] = None
    dump_hook: Optional[Callable] = None

    # ===== NOT TO BE MANUALLY SET =====
    default: Any = None
    attrname: str = None  # type: ignore


_empty_config = JSONConfig()


class Struct:
    __slots__: Set[str] = set()

    __mapping__: Dict[str, JSONConfig]
    __names__: Dict[str, str]
    _locked: bool

    def __init__(self, **kwargs) -> None:
        self._locked = False
        for _, _, opt, _, _, _, defa, name in self.__mapping__.values():
            defa = kwargs.get(name, defa)
            if not opt:
                setattr(self, name, defa)

    def __setattr__(self, __name: str, __value: Any) -> None:
        if hasattr(self, "_locked"):
            if not self._locked:
                if __name in self.__names__:
                    return super().__setattr__(__name, __value)
                raise AttributeError(
                    f"{self.__class__.__name__} has no attribute {__name}."
                )
        else:
            if __name in self.__names__ or __name == "_locked":
                return super().__setattr__(__name, __value)
            raise AttributeError(
                f"{self.__class__.__name__} has no attribute {__name}."
            )
        raise AttributeError(
            f"Attribute {__name} of {self.__class__.__name__} is read-only."
        )

    def __repr__(self) -> str:
        data: str = ""
        for name, value in self.items():
            data += f"{name}: {value}, "

        return f"{self.__class__.__name__} {{{data[:-2]}}}"

    def items(self) -> Tuple[Tuple[str, Any]]:
        ret = ()
        for _, _, opt, _, _, _, _, name in self.__mapping__.values():
            attr = getattr(self, name)
            if not opt:
                ret += ((name, attr),)  # type: ignore

        return ret  # type: ignore

    def lock(self):
        super().__setattr__("_locked", True)


class StructMeta(type):
    def __new__(cls, name: str, bases: tuple, namespace: dict):

        namespace["__mapping__"] = {}
        namespace["__names__"] = {}

        namespace["__slots__"] = {"_locked"}

        namespace.pop("_locked", None)

        try:
            anno: Dict[str, Any] = namespace["__annotations__"]
        except KeyError:
            raise AttributeError(
                "Structs must have annotated fields for them to be included."
            ) from None

        for attr, annotation in anno.items():
            default = namespace.pop(attr, None)
            _config = _empty_config._replace(attrname=attr, name=attr)
            if get_origin(annotation) is Annotated:
                metadata = annotation.__metadata__[0]
                if (  # pylint: disable=unidiomatic-typecheck
                    type(metadata) is JSONConfig
                ):
                    update: Dict[str, Union[str, bool, Callable, None]] = {}
                    default = metadata.default or default
                    if metadata.name is not None:
                        update["name"] = metadata.name
                    if default is not None:
                        update["default"] = default
                    if metadata.optional:
                        update["optional"] = True
                    if metadata.raw:
                        update["raw"] = True
                    if metadata.load_hook is not None and callable(metadata.load_hook):
                        update["load_hook"] = metadata.load_hook
                    if metadata.dump_hook is not None and callable(metadata.dump_hook):
                        update["dump_hook"] = metadata.dump_hook
                    if metadata.object is not None and callable(metadata.object):
                        update["object"] = metadata.object

                    _config = _config._replace(**update)  # type: ignore

            namespace["__mapping__"][_config.name] = _config
            namespace["__names__"][attr] = _config.name
            namespace["__slots__"].add(attr)

        ret = type.__new__(cls, name, bases, namespace)

        return ret


def is_struct_class(obj) -> bool:
    return type(obj) == StructMeta  # pylint: disable=unidiomatic-typecheck


def is_struct(obj) -> bool:
    return isinstance(obj, Struct)


def _get_key_config(obj: Struct, key: str) -> JSONConfig:
    if is_struct(obj):
        return obj.__mapping__.get(key, _empty_config)
    return _empty_config
