from __future__ import annotations

__all__ = ("NamedDict", "NamedDictMeta", "JSONConfig")

from typing import (
    Annotated,
    Any,
    Callable,
    Dict,
    Optional,
    Set,
    NamedTuple,
    Union,
    get_origin,
)


class JSONConfig(NamedTuple):
    name: Optional[str] = None
    object: Union[NamedDict, NamedDictMeta] = None

    optional: bool = False
    raw: bool = False

    load_hook: Optional[Callable] = None
    dump_hook: Optional[Callable] = None

    # ===== NOT TO BE MANUALLY SET =====
    default: Any = None
    attrname: Optional[str] = None


class NamedDict(dict):
    """
    `NamedDict` is a subclass of `dict`, but it replaces
    `__getattribute__` and `__setattr__`.

    Methods -
    - `__getattrinute__` tries to call `__getattribute__` and then calls
    `__getitem__` on AttributeError. You may want to use the normal way
    of `instance["items"]` because calling `instance.items` will return
    the `items` method which is not what you want, hence be careful of
    what keys you want to access and how you access them.
    - `__setattr__` same as `instance["key"] = "value"` but
    better, i.e `instance.key = "value"`.

    ```pycon
    >>> class Data(NamedDict):
    ...     __slots__ = ()  # you need to add this line to avoid the
    ...                     # creation of `__dict__`
    ...     value_a: int
    ...     value_b: str
    ...
    >>> data = Data(value_a=1, value_b="hi!")
    >>> print(data)
    {"value_a": 1, "value_b": "hi!"}
    >>> data.value_a
    1
    >>> data.value_b
    "hi!"
    ```
    """

    __slots__: Set[str] = set()
    __mapping__: Dict[str, JSONConfig]
    __names__: Set[str]

    def __init__(self, **kwargs):
        if hasattr(self, "__names__"):
            for config in self.__mapping__.values():
                value = kwargs.get(config.attrname, config.default)
                self.__setattr__(config.attrname, value)
        else:
            super().__init__(**kwargs)

    def __getattribute__(self, __name: str) -> Any:
        try:
            return super().__getattribute__(__name)
        except AttributeError:
            if hasattr(self, "__names__"):
                if __name in self.__names__:
                    return super().__getitem__(__name)
                else:
                    raise AttributeError(
                        f"{self.__class__.__name__} has no attribute {__name}."
                    ) from None
            else:
                return super().__getitem__(__name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        if hasattr(self, "__names__"):
            if __name in self.__names__:
                return super().__setitem__(__name, __value)
            else:
                raise AttributeError(
                    f"{self.__class__.__name__} has no attribute {__name}."
                )
        else:
            return super().__setitem__(__name, __value)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__} {super().__repr__()}"


_empty_config = JSONConfig()


class NamedDictMeta(type):
    def __new__(cls, name: str, bases: tuple, namespace: dict) -> NamedDict:  # type: ignore

        namespace["__slots__"] = set()
        namespace["__names__"] = set()
        namespace["__mapping__"] = {}

        try:
            temp_ns = namespace["__annotations__"].copy()
        except KeyError:
            return type.__new__(cls, name, bases, namespace)  # type: ignore

        for attribute, annotation in temp_ns.items():
            default = None
            _config = _empty_config._replace(
                attrname=attribute, name=attribute
            )
            if attribute in namespace:
                default = namespace.pop(attribute)

            if get_origin(annotation) is Annotated:
                metadata = annotation.__metadata__[0]
                if (  # pylint: disable=unidiomatic-typecheck
                    type(metadata) == JSONConfig
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
                    if metadata.load_hook is not None and callable(
                        metadata.load_hook
                    ):
                        update["load_hook"] = metadata.load_hook
                    if metadata.dump_hook is not None and callable(
                        metadata.dump_hook
                    ):
                        update["dump_hook"] = metadata.dump_hook

                    _config = _config._replace(**update)  # type: ignore

            namespace["__mapping__"][_config.name] = _config
            namespace["__names__"].add(attribute)

        return type.__new__(NamedDictMeta, name, bases, namespace)  # type: ignore


def is_named_dict(obj: Any) -> bool:
    return isinstance(obj, NamedDict)


def is_named_dict_class(obj: Any) -> bool:
    return type(obj) == NamedDictMeta  # pylint: disable=unidiomatic-typecheck


def _get_key_config(obj: NamedDict, key: str) -> JSONConfig:
    if is_named_dict(obj):
        try:
            return obj.__mapping__[key]
        except KeyError:
            return _empty_config
    else:
        return _empty_config
