__all__ = ["Struct", "field", "getit", "assign", "Mapping", "lock"]

# Main metaclass Struct
class Struct(type):
    def __new__(cls, o, bases, d):
        bases += (BaseStruct,)
        d["__slots__"] = ("__mappings__", "__inversemaps__")
        x = super().__new__(cls, o, bases, d)
        dd = ["__mappings__", "__inversemaps__"]
        tmaps = {}
        timaps = {}
        try:
            for k, v in d.items():
                if isinstance(v, Fields):
                    dd.append(k)
                    tmaps.update(
                        **{v.json: Mapping(k, v.default, v.raw_json, v.optional)}
                    )
                    timaps.update(**{k: v.json})
                    if v.default is MISSING:
                        setattr(x, k, None)
                    else:
                        setattr(x, k, v.default)

        finally:
            setattr(x, "__slots__", dd)
            setattr(x, "__mappings__", tmaps)
            setattr(x, "__inversemaps__", timaps)

        return x

    def __repr__(self):
        return f"<class '{__name__}.Struct.{self.__name__}'>"


class BaseStruct:
    def __setattr__(self, name, value):
        if name in self.__slots__:
            super().__setattr__(name, value)

    def items(self):
        m = self.__inversemaps__
        mm = self.__mappings__
        ret = []
        for k in self.__slots__:
            attr = getattr(self, k)
            if k != "__mappings__":
                if k != "__inversemaps__":
                    if mm[m[k]].optional and attr is None:
                        pass
                    else:
                        ret.append((m[k], attr))
        return ret


# Missing object
class MISSING:
    def __repr__(self) -> str:
        return "..."


# Fields Class to store feild data
class Fields:
    __slots__ = ("default", "json", "raw_json", "overwrite", "optional")

    def __init__(self, default, json, raw_json, optional):
        self.default = default
        self.json = json
        self.raw_json = raw_json
        self.optional = optional


# Fields Class instance generator
def field(json, default=MISSING, raw_json=False, optional=False):
    return Fields(default, json, raw_json, optional)


# Mapping class for json feild maps
class Mapping:
    __slots__ = ("name", "default", "raw_json", "optional")

    def __init__(self, name, default, raw_json, optional):
        self.name = name
        self.default = default
        self.raw_json = raw_json
        self.optional = optional


def getit(obj: Struct, key):
    if isinstance(type(obj), Struct):
        if key in obj.__mappings__:
            return obj.__mappings__[key]
    return obj


def assign(obj, map: Mapping, value):
    x = map
    if isinstance(x, Mapping):
        if isinstance(type(obj), Struct):
            setattr(obj, x.name, value)


def lock(o):
    o.__setattr__ = lambda name, value: None
