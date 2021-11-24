# flake8: noqa

__all__ = ()

from typing import Annotated, List, Literal

from go_json import Struct

# The following file contains ALL API types
# IK this will be a mess but in true discordgo copy-paste spirit I will
# not bother separating these
# The following is the format to keep things a little bit organized
# - General Types (ex: User, Channel, Guild...)
# - REST Endpoint payloads (ex: GetGateway, GetGatewayBot...)
# - WebSocket payloads (ex: Resume, Hello...)


# ======================================================================
#   REST PAYLOADS - START
# ======================================================================


class GetGateway(Struct):
    url: str


class SessionStartLimit(Struct):
    total: int
    remaining: int
    reset_after: int
    max_concurrency: int


class GetGatewayBot(Struct):
    url: str
    shards: List[int]
    session_start_limit: Annotated[
        SessionStartLimit, {"object": SessionStartLimit}
    ]


# ======================================================================
#   REST PAYLOADS - END
# ======================================================================


# ======================================================================
#   WEBSOCKET PAYLOADS - START
# ======================================================================


class Event(Struct):
    operation: Annotated[
        Literal[0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11], {"name": "op"}
    ]
    type: Annotated[str, {"name": "t", "optional": True}]
    seq: Annotated[int, {"name": "s", "optional": True}]
    raw_data: Annotated[str, {"name": "d", "raw": True}]


class Hello(Struct):
    heartbeat_interval: int
    trace: Annotated[str, {"name": "_trace", "raw": True}]


class IdentifyProperties(Struct):
    os: Annotated[str, {"name": "$os"}]
    browser: Annotated[str, {"name": "$browser"}]
    device: Annotated[str, {"name": "$device"}]


class Identify(Struct):
    token: str
    properties: Annotated[IdentifyProperties, {"object": IdentifyProperties}]
    compress: Annotated[bool, {"optional": True}]
    large_threshold: Annotated[int, {"optional": True}]
    shard: Annotated[List[int], {"optional": True}]
    presence: Annotated[dict, {"optional": True}]
    intents: int = 513


# ======================================================================
#   WEBSOCKET PAYLOADS - END
# ======================================================================
