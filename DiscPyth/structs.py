from enum import IntEnum
from typing import Any, List, Tuple

from .ext import gopyjson as gpj


# Dynamically create API structs, 'cus hell
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
    ["Operation", "Sequence", "Type", "RawData"],
    ["op", "s", "t", "d"],
    optional_map=[1, 2],
    rawjson_map=[3],
)
"""A message/payload received by the client from Discord in the following format:
```
{
    "op": OP_CODE, 
    "t": EVENT_NAME, 
    "s": SEQUENCE, 
    "d": PAYLOAD_DATA
}
```
"""

HELLO = new_type(
    "Hello", ["HeartbeatInterval", "Trace"], ["heartbeat_interval", "_trace"]
)
"""[R] The `d` key of the payload with an Operation Code of 10.
https://discord.com/developers/docs/topics/gateway#hello"""

IDENTIFY_PROPERTIES = new_type(
    "Identify_Properties", ["os", "browser", "device"], ["$os", "$browser", "$device"]
)
"""[S] The `d.properties` key of the payload with an Operation Code of 2.
https://discord.com/developers/docs/topics/gateway#identify-identify-connection-properties"""

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
"""[S] The `d` key of the payload with an Operation Code of 2.
https://discord.com/developers/docs/topics/gateway#identify"""

RESUME = new_type(
    "Resume", ["Token", "SessionID", "Sequence"], ["token", "session_id", "seq"]
)
"""[S] The `d` key of the payload with an Operation Code of 6.
https://discord.com/developers/docs/topics/gateway#resume-resume-structure"""


class Permissions(IntEnum):
    """Constants for the different bit offsets of text channel permissions
    https://discord.com/developers/docs/topics/permissions
    """

    # Constants for the different bit offsets of text channel permissions
    SEND_MESSAGES: int = 0x0000000800
    SEND_MESSAGES_IN_THREADS: int = 0x4000000000
    SEND_TTS_MESSAGES: int = 0x0000001000
    CREATE_PUBLIC_THREADS: int = 0x0800000000
    CREATE_PRIVATE_THREADS: int = 0x1000000000
    EMBED_LINKS: int = 0x0000004000
    ATTACH_FILES: int = 0x0000008000
    READ_MESSAGE_HISTORY: int = 0x0000010000
    MENTION_EVERYONE: int = 0x0000020000
    USE_EXTERNAL_STICKERS: int = 0x2000000000
    USE_EXTERNAL_EMOJIS: int = 0x0000040000
    USE_APPLICATION_COMMANDS: int = 0x0080000000

    # Constants for the different bit offsets of voice permissions
    PRIORITY_SPEAKER: int = 0x0000000100
    STREAM: int = 0x0000000200
    CONNECT: int = 0x0000100000
    SPEAK: int = 0x0000200000
    MUTE_MEMBERS: int = 0x0000400000
    DEAFEN_MEMBERS: int = 0x0000800000
    MOVE_MEMBERS: int = 0x0001000000
    USE_VAD: int = 0x0002000000
    REQUEST_TO_SPEAK: int = 0x0100000000
    START_EMBEDDED_ACTIVITIES: int = 0x8000000000

    # Constants for general management.
    CHANGE_NICKNAME: int = 0x0004000000
    MANAGE_MESSAGES: int = 0x0000002000
    MANAGE_NICKNAMES: int = 0x0008000000
    MANAGE_ROLES: int = 0x0010000000
    MANAGE_WEBHOOKS: int = 0x0020000000
    MANAGE_EMOJIS_AND_STICKERS: int = 0x0040000000

    # Constants for the different bit offsets of general permissions
    CREATE_INSTANT_INVITE: int = 0x0000000001
    KICK_MEMBERS: int = 0x0000000002
    BAN_MEMBERS: int = 0x0000000004
    ADMINISTRATOR: int = 0x0000000008
    MANAGE_CHANNELS: int = 0x0000000010
    MANAGE_THREADS: int = 0x0400000000
    MANAGE_GUILD: int = 0x0000000020
    ADD_REACTIONS: int = 0x0000000040
    VIEW_AUDIT_LOG: int = 0x0000000080
    VIEW_CHANNEL: int = 0x0000000400
    VIEW_GUILD_INSIGHTS: int = 0x0000080000


class Intents(IntEnum):
    """Constants for the different bit offsets of intents
    https://discord.com/developers/docs/topics/gateway#gateway-intents
    """

    GUILDS: int = 1 << 0
    GUILD_MEMBERS: int = 1 << 1
    GUILD_BANS: int = 1 << 2
    GUILD_EMOJIS: int = 1 << 3
    GUILD_INTEGRATIONS: int = 1 << 4
    GUILD_WEBHOOKS: int = 1 << 5
    GUILD_INVITES: int = 1 << 6
    GUILD_VOICE_STATES: int = 1 << 7
    GUILD_PRESENCES: int = 1 << 8
    GUILD_MESSAGES: int = 1 << 9
    GUILD_MESSAGE_REACTIONS: int = 1 << 10
    GUILD_MESSAGE_TYPING: int = 1 << 11
    DIRECT_MESSAGES: int = 1 << 12
    DIRECT_MESSAGE_REACTIONS: int = 1 << 13
    DIRECT_MESSAGE_TYPING: int = 1 << 14

    ALL_WITHOUT_PRIVILEGED: int = (
        GUILDS
        | GUILD_BANS
        | GUILD_EMOJIS
        | GUILD_INTEGRATIONS
        | GUILD_WEBHOOKS
        | GUILD_INVITES
        | GUILD_VOICE_STATES
        | GUILD_MESSAGES
        | GUILD_MESSAGE_REACTIONS
        | GUILD_MESSAGE_TYPING
        | DIRECT_MESSAGES
        | DIRECT_MESSAGE_REACTIONS
        | DIRECT_MESSAGE_TYPING
    )
    ALL: int = ALL_WITHOUT_PRIVILEGED | GUILD_MEMBERS | GUILD_PRESENCES
    NONE: int = 0
