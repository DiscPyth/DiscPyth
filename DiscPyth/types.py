from .ext import gopyjson as gpj
from typing import List, Tuple, Any

# Dynamically create API types, 'cus hell
# its time consuming
def new_type(
    name: str,
    fields: List[str],
    json: List[str],
    default_map: List[Tuple[int, Any]] = list(),
    optional_map: List[int] = list(),
    rawjson_map: List[int] = list(),
):
    d = dict()
    if len(json) == len(fields):
        for idx, field in enumerate(fields):
            d.update(**{field: gpj.field(json[idx])})
        for i, o in default_map:
            d[fields[i]].default = o
        for i in optional_map:
            d[fields[i]].optional = True
        for i in rawjson_map:
            d[fields[i]].raw_json = True

    ntype = gpj.Struct(name, tuple(), d)
    return ntype


EVENT = new_type(
    "Event",
    ["Operation", "Sequence", "Type", "Raw_Data"],
    ["op", "s", "t", "d"],
    rawjson_map=[3],
)

IDENTIFY_PROPERTIES = new_type(
    "Identify_Properties", ["os", "browser", "device"], ["$os", "$browser", "$device"]
)

IDENTIFY = new_type(
    "Identify",
    ["Token", "Properties", "Compress", "Large", "Shard", "Presence", "Intents"],
    [
        "token",
        "properties",
        "compress",
        "large_threshold",
        "shard",
        "presence",
        "intents",
    ],
    default_map=[(1, IDENTIFY_PROPERTIES())],
    optional_map=[5],
)
