from __future__ import annotations

__all__ = ("Struct", "is_struct_class", "is_struct_instance")

import inspect
from typing import (  # type: ignore
    Any,
    Dict,
    ForwardRef,
    List,
    NamedTuple,
    Set,
    Tuple,
    Type,
    TypeVar,
    _AnnotatedAlias,
    _eval_type,
    _is_dunder,
)

T = TypeVar("T")


class AttributeData(NamedTuple):
    name: str
    object: Type[Struct]
    raw: bool
    string: bool
    optional: bool
    lock: bool
    hook: Any
    default: Any


_empty_data = AttributeData(None, None, False, False, False, True, None, None)  # type: ignore


class StructMeta(type):
    r"""
    :meth:`class StructMeta`
    ----------
    ::
    Here is where all the magic happens.\
    Never use this class directly as `Name(metaclass=fur_json.struct.StructMeta)`,
    instead use `Name(fur_json.Struct)`.\
    This metaclass does the following
    - Create :meth:`__init__` method for the class.
    - Add attributes to `__slots__`.
    - Create necessary "mappings" for the decoder and encoder to work
    properly with the class.
    ::
    """

    def __new__(  # pylint: disable=too-many-locals
        cls, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]
    ) -> StructMeta:
        temp_namespace = namespace.copy()

        namespace["__slots__"] = set()
        slots_add = namespace["__slots__"].add

        namespace["__mapping__"] = ({}, {})

        namespace.pop(f"_{name}__locked", None)

        for attr, anno in temp_namespace.get("__annotations__", {}).items():
            if not _is_dunder(attr):
                default = namespace.pop(attr, None)
                data = _empty_data._replace(name=attr)

                if isinstance(default, str):
                    default = f"'{str(default)}'"
                elif default is not None:
                    default = str(default)

                slots_add(attr)
                if isinstance(anno, _AnnotatedAlias):
                    if isinstance(anno.__metadata__[0], dict):
                        if anno.__metadata__[0].get("name", None) is None:
                            anno.__metadata__[0]["name"] = attr

                        anno.__metadata__[0]["default"] = default
                        data = _empty_data._replace(**anno.__metadata__[0])
                namespace["__mapping__"][1].update(**{data.name: attr})
                namespace["__mapping__"][0].update(**{attr: data})

        del temp_namespace

        slots_add("__locked")

        new_obj: StructMeta = super().__new__(cls, name, bases, namespace)

        return new_obj


def is_struct_instance(obj) -> bool:
    r"""
    Returns ``True`` if the passed `obj` is an instance of StructMeta.
    >>> is_struct_instance(fur_json.Struct)
    ... False
    >>> is_struct_instance(fur_json.Struct())
    ... True
    """
    return isinstance(type(obj), StructMeta)


def is_struct_class(obj) -> bool:
    r"""
    Returns ``True`` if the passed `obj` is a class derived from StructMeta.
    >>> is_struct_class(fur_json.Struct())
    ... False
    >>> is_struct_class(fur_json.Struct)
    ... True
    """
    return type(obj) is StructMeta  # pylint: disable=unidiomatic-typecheck


class Struct(metaclass=StructMeta):
    r"""
    :meth:`class Struct`
    -------------------
    All your JSON structs **must** inherit from this class.

    Methods
    ::
    - :meth:`lock()`      - Lock the :meth:`Struct` instance, this prevents
                        from setting attributes.
    - :meth:`items()`     - Return a list containing tuples of key, value pairs.
    ::
    """
    __slots__: Set[str] = set()
    __mapping__: Tuple[Dict[str, AttributeData], Dict[str, str]]

    def __init__(self, **kwargs) -> None:
        for json, attr in self.__mapping__[1].items():
            setattr(
                self, attr, kwargs.get(json, self.__mapping__[0][attr].default)
            )

        setattr(self, f"_{self.__class__.__name__}__locked", False)

    def __repr__(self, sort=False) -> str:
        if len(self.__slots__) >= 1:
            ret = self.__class__.__qualname__
            ret += "{ "
            slots: Set[str] = self.__slots__
            if sort:
                slots: List[str] = sorted(self.__slots__)  # type: ignore
            for name in slots:
                if name == "__locked":
                    continue
                attr_val = getattr(self, name, None)
                ret += name + ": " + str(attr_val) + ", "
            ret = ret[:-2] + " }"
            return ret
        return super().__repr__()

    def __setattr__(self, name, value) -> None:
        if hasattr(self, f"_{self.__class__.__name__}__locked"):
            if getattr(  # pylint: disable=no-else-raise
                self, f"_{self.__class__.__name__}__locked"
            ):
                raise AttributeError(
                    "Cannot set attribute after struct has been locked"
                )
            else:
                super().__setattr__(name, value)
        else:
            super().__setattr__(name, value)

    def items(self) -> List[Tuple[str, Any]]:
        r"""
        Return a list containing tuples of key, value pairs,
        >>> DataStruct(v1="hi", v2="there").items() == [(v1, "hi"), (v2, "there")]
        """
        ret = []
        slots = sorted(self.__slots__)
        for key in slots:
            if key != "__locked":
                attr: AttributeData = self.__mapping__[0][key]
                val = getattr(self, key)
                if val is None and attr.optional:
                    continue
                ret.append((attr.name, val))
        return ret

    def lock(self) -> None:
        r"""
        Lock the :meth:`Struct` instance, this prevents from setting attributes.
        """
        if not getattr(self, f"_{self.__class__.__name__}__locked", False):
            super().__setattr__(f"_{self.__class__.__name__}__locked", True)

    def __getitem__(self, key: str) -> Any:
        return getattr(
            self, key, getattr(self, self.__mapping__[1].get(key, ""), None)
        )


def get_field(obj: Type[Struct], name: str) -> AttributeData:
    r"""
    Return the :meth:`AttributeData` of the passed key, or return a
    placeholder if key doesn't exist or `obj` is not a Struct.
    """
    if is_struct_instance(obj):
        ret = obj.__mapping__[0].get(
            obj.__mapping__[1].get(name, ""), _empty_data
        )
        if isinstance(ret.object, str):
            globalns = inspect.getmodule(obj).__dict__
            obj.__mapping__[0][obj.__mapping__[1][name]] = ret._replace(
                object=_eval_type(ForwardRef(ret.object), globalns, {})
            )
        return obj.__mapping__[0].get(
            obj.__mapping__[1].get(name, ""), _empty_data
        )
    return _empty_data
