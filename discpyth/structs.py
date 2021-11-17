from typing import List

import go_json

__all__ = ()


class Event(go_json.Struct):
    operation = go_json.field("op")
    sequence = go_json.field("s")
    type = go_json.field("t")
    raw_data = go_json.field("d", raw_json=True)


class Hello(go_json.Struct):
    heartbeat_interval = go_json.field("heartbeat_interval")
    trace = go_json.field("_trace")


class IdentifyProperties(go_json.Struct):
    op_sys = go_json.field("$os")
    browser = go_json.field("$browser")
    device = go_json.field("$device")


class Identify(go_json.Struct):
    token: str = go_json.field("token")
    properties: IdentifyProperties = go_json.field(
        "properties", json_object=IdentifyProperties
    )
    compress: bool = go_json.field("compress", optional=True)
    large_threshold: int = go_json.field("large_threshold", optional=True)
    shard: List[int] = go_json.field("shard", optional=True)
    presence = go_json.field("presence", optional=True)
    intents: int = go_json.field("intents")
