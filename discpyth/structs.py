from enum import IntEnum
from typing import List

import gopyjson.struct as gpj  # type: ignore


class ActivityType(IntEnum):
    """
    Valid ActivityType values
    https://discord.com/developers/docs/topics/gateway#activity-object-activity-types
    """

    GAME: int = 0
    STREAMING: int = 1
    LISTENING: int = 2
    WATCHING: int = 3
    CUSTOM: int = 4
    COMPETING: int = 5


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


class Ready(metaclass=gpj.Struct):  # pylint: disable=too-few-public-methods;
    """
    Received after Identifying, contains information such as the gateway version used by DiscPyth and much more
    https://discord.com/developers/docs/topics/gateway#ready
    """

    version: int = gpj.field("v")
    user: dict = gpj.field("user")
    guilds: list = gpj.field("guilds")
    session_id: str = gpj.field("session_id")
    shard: List[int] = gpj.field(
        "shard", optional=True
    )  # optional not needed since its only for dumping but ¯\_(ツ)_/¯
    application: dict = gpj.field("application")


class Event(metaclass=gpj.Struct):  # pylint: disable=too-few-public-methods;
    """A class to hold payloads with the data as a raw string
    ```json
    {
        "op": OPERATION__CODE,
        "s": SEQUENCE,
        "t": EVENT_NAME,
        "d": PAYLOAD_DATA_AS_STRING
    }
    ```
    """

    operation: int = gpj.field("op")
    type: int = gpj.field("t")
    sequence: int = gpj.field("s")
    raw_data: str = gpj.field("d", raw_json=True)


class Hello(metaclass=gpj.Struct):  # pylint: disable=too-few-public-methods;
    """
    A class to hold the data for the HELLO Payload recieved from Discord,
    https://discord.com/developers/docs/topics/gateway#hello
    """

    heartbeat_interval: int = gpj.field("heartbeat_interval")
    trace: str = gpj.field("_trace")


class IdentifyProperties(
    metaclass=gpj.Struct
):  # pylint: disable=too-few-public-methods;
    """
    Properties Object of the Identify payload,
    https://discord.com/developers/docs/topics/gateway#identify-identify-connection-properties
    """

    operating_sys: str = gpj.field("$os")
    browser: str = gpj.field("$browser")
    device: str = gpj.field("$device")


class Identify(metaclass=gpj.Struct):  # pylint: disable=too-few-public-methods;
    """
    Identify Payload, sent after establishing a connection with Discord and receiving the HELLO Payload,
    Used to Identify the Bot Account with the gateway and start receiving events for the bot.
    https://discord.com/developers/docs/topics/gateway#identify
    """

    token: str = gpj.field("token")
    properties: IdentifyProperties = gpj.field(
        "properties", default=IdentifyProperties()
    )
    compress: bool = gpj.field("compress", optional=True)
    large_threshold: int = gpj.field("large_threshold", optional=True)
    shard: List[int] = gpj.field("shard", optional=True)
    presence: dict = gpj.field("presence", optional=True)
    intents: int = gpj.field("intents")
