from enum import IntEnum
from typing import List, Literal

import go_json as gj  # type: ignore


class UpdateStatusData(gj.Struct):
    since: int = gj.field("since")
    activities: list = gj.field("activities")
    status: Literal["online", "idle", "dnd", "invisible"] = gj.field("status")
    afk: bool = gj.field("afk")


class Event(gj.Struct):
    __partial = True  # pylint: disable=unused-private-member
    operation: int = gj.field("op")
    sequence: int = gj.field("seq")
    type: str = gj.field("t")
    raw_data: str = gj.field("d", raw_json=True)


class Hello(gj.Struct):
    heartbeat_interval: int = gj.field("heartbeat_interval")
    trace: str = gj.field("_trace", raw_json=True)


class Intents(IntEnum):
    # fmt: off
    GUILDS                          =   (1 << 0)
    GUILD_MEMBERS                   =   (1 << 1)
    GUILD_BANS                      =   (1 << 2)
    GUILD_EMOJIS_AND_STICKERS       =   (1 << 3)
    GUILD_INTEGRATIONS              =   (1 << 4)
    GUILD_WEBHOOKS                  =   (1 << 5)
    GUILD_INVITES                   =   (1 << 6)
    GUILD_VOICE_STATES              =   (1 << 7)
    GUILD_PRESENCES                 =   (1 << 8)
    GUILD_MESSAGES                  =   (1 << 9)
    GUILD_MESSAGE_REACTIONS         =   (1 << 10)
    GUILD_MESSAGE_TYPING            =   (1 << 11)
    DIRECT_MESSAGES                 =   (1 << 12)
    DIRECT_MESSAGE_REACTIONS        =   (1 << 13)
    DIRECT_MESSAGE_TYPING           =   (1 << 14)
    # fmt: on


class IdentifyProperties(gj.Struct):
    __partial = True  # pylint: disable=unused-private-member
    os: str = gj.field("$os")  # pylint: disable=invalid-name
    browser: str = gj.field("$browser")
    device: str = gj.field("$device")


class Identify(gj.Struct):
    __partial = True  # pylint: disable=unused-private-member
    token: str = gj.field("token")
    properties: IdentifyProperties = gj.field(
        "properties", json_object=IdentifyProperties
    )
    compress: bool = gj.field("compress", optional=True)
    large_threshold: int = gj.field("large_threshold", optional=True)
    shard: List[int] = gj.field("shard", optional=True)
    presence = gj.field("presence", optional=True)
    intents: int = gj.field("intents")

"""
Hello
Ready
Resumed
Reconnect
Invalid Session
Channel Create
Channel Update
Channel Delete
Channel Pins Update
Thread Create
Thread Update
Thread Delete
Thread List Sync
Thread Member Update
Thread Members Update
Guild Create
Guild Update
Guild Delete
Guild Ban Add
Guild Ban Remove
Guild Emojis Update
Guild Stickers Update
Guild Integrations Update
Guild Member Add
Guild Member Remove
Guild Member Update
Guild Members Chunk
Guild Role Create
Guild Role Update
Guild Role Delete
Integration Create
Integration Update
Integration Delete
Interaction Create
Invite Create
Invite Delete
Message Create
Message Update
Message Delete
Message Delete Bulk
Message Reaction Add
Message Reaction Remove
Message Reaction Remove All
Message Reaction Remove Emoji
Presence Update
Stage Instance Create
Stage Instance Delete
Stage Instance Update
Typing Start
User Update
Voice State Update
Voice Server Update
Webhooks Update
"""