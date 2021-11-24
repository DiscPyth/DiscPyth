# flake8: noqa

__all__ = (
    "Ready",
    "Resumed",
    "Reconnect",
    "ChannelCreate",
    "ChannelDelete",
    "ChannelPinsUpdate",
    "ChannelUpdate",
    "ThreadCreate",
    "ThreadDelete",
    "ThreadUpdate",
    "ThreadListSync",
    "ThreadMemberUpdate",
    "ThreadMembersUpdate",
    "GuildCreate",
    "GuildDelete",
    "GuildUpdate",
    "GuildBanAdd",
    "GuildBanRemove",
    "GuildEmojisUpdate",
    "GuildIntegrationsUpdate",
    "GuildStickersUpdate",
    "GuildMemberAdd",
    "GuildMemberRemove",
    "GuildMemberUpdate",
    "GuildMembersChunk",
    "GuildRoleCreate",
    "GuildRoleDelete",
    "GuildRoleUpdate",
    "GuildScheduledEventCreate",
    "GuildScheduledEventDelete",
    "GuildScheduledEventUpdate",
    "GuildScheduledEventUserAdd",
    "GuildScheduledEventUserRemove",
    "IntegrationCreate",
    "IntegrationDelete",
    "IntegrationUpdate",
    "InviteCreate",
    "InviteDelete",
    "InteractionCreate",
    "MessageCreate",
    "MessageUpdate",
    "MessageDelete",
    "MessageDeleteBulk",
    "MessageReactionAdd",
    "MessageReactionRemove",
    "MessageReactionRemoveAll",
    "MessageReactionRemoveEmoji",
    "PresenceUpdate",
    "StageInstanceCreate",
    "StageInstanceDelete",
    "StageInstanceUpdate",
    "TypingStart",
    "UserUpdate",
    "VoiceStateUpdate",
    "VoiceServerUpdate",
    "WebhooksUpdate",
)

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


# EVENTS


# Genral Events
class Ready(Struct):
    __name__ = "READY"


class Resumed(Struct):
    __name__ = "RESUMED"


class Reconnect(Struct):
    __name__ = "RECONNECT"


# Channel related Events
class ChannelCreate(Struct):
    __name__ = "CHANNEL_CREATE"


class ChannelDelete(Struct):
    __name__ = "CHANNEL_DELETE"


class ChannelPinsUpdate(Struct):
    __name__ = "CHANNEL_PINS_UPDATE"


class ChannelUpdate(Struct):
    __name__ = "CHANNEL_UPDATE"


class ThreadCreate(Struct):
    __name__ = "THREAD_CREATE"


class ThreadDelete(Struct):
    __name__ = "THREAD_DELETE"


class ThreadUpdate(Struct):
    __name__ = "THREAD_UPDATE"


class ThreadListSync(Struct):
    __name__ = "THREAD_LIST_SYNC"


class ThreadMemberUpdate(Struct):
    __name__ = "THREAD_MEMBER_UPDATE"


class ThreadMembersUpdate(Struct):
    __name__ = "THREAD_MEMBERS_UPDATE"


# Guild related Events
class GuildCreate(Struct):
    __name__ = "GUILD_CREATE"


class GuildDelete(Struct):
    __name__ = "GUILD_DELETE"


class GuildUpdate(Struct):
    __name__ = "GUILD_UPDATE"


class GuildBanAdd(Struct):
    __name__ = "GUILD_BAN_ADD"


class GuildBanRemove(Struct):
    __name__ = "GUILD_BAN_REMOVE"


class GuildEmojisUpdate(Struct):
    __name__ = "GUILD_EMOJIS_UPDATE"


class GuildIntegrationsUpdate(Struct):
    __name__ = "GUILD_INTEGRATIONS_UPDATE"


class GuildStickersUpdate(Struct):
    __name__ = "GUILD_STICKERS_UPDATE"


class GuildMemberAdd(Struct):
    __name__ = "GUILD_MEMBER_ADD"


class GuildMemberRemove(Struct):
    __name__ = "GUILD_MEMBER_REMOVE"


class GuildMemberUpdate(Struct):
    __name__ = "GUILD_MEMBER_UPDATE"


class GuildMembersChunk(Struct):
    __name__ = "GUILD_MEMBERS_CHUNK"


class GuildRoleCreate(Struct):
    __name__ = "GUILD_ROLE_CREATE"


class GuildRoleDelete(Struct):
    __name__ = "GUILD_ROLE_DELETE"


class GuildRoleUpdate(Struct):
    __name__ = "GUILD_ROLE_UPDATE"


class GuildScheduledEventCreate(Struct):
    __name__ = "GUILD_SCHEDULED_EVENT_CREATE"


class GuildScheduledEventDelete(Struct):
    __name__ = "GUILD_SCHEDULED_EVENT_DELETE"


class GuildScheduledEventUpdate(Struct):
    __name__ = "GUILD_SCHEDULED_EVENT_UPDATE"


class GuildScheduledEventUserAdd(Struct):
    __name__ = "GUILD_SCHEDULED_EVENT_USER_ADD"


class GuildScheduledEventUserRemove(Struct):
    __name__ = "GUILD_SCHEDULED_EVENT_USER_REMOVE"


class IntegrationCreate(Struct):
    __name__ = "INTEGRATION_CREATE"


class IntegrationDelete(Struct):
    __name__ = "INTEGRATION_DELETE"


class IntegrationUpdate(Struct):
    __name__ = "INTEGRATION_UPDATE"


class InviteCreate(Struct):
    __name__ = "INVITE_CREATE"


class InviteDelete(Struct):
    __name__ = "INVITE_DELETE"


# Interaction Create
class InteractionCreate(Struct):
    __name__ = "INTERACTION_CREATE"


# Message related Events
class MessageCreate(Struct):
    __name__ = "MESSAGE_CREATE"


class MessageUpdate(Struct):
    __name__ = "MESSAGE_UPDATE"


class MessageDelete(Struct):
    __name__ = "MESSAGE_DELETE"


class MessageDeleteBulk(Struct):
    __name__ = "MESSAGE_DELETE_BULK"


class MessageReactionAdd(Struct):
    __name__ = "MESSAGE_REACTION_ADD"


class MessageReactionRemove(Struct):
    __name__ = "MESSAGE_REACTION_REMOVE"


class MessageReactionRemoveAll(Struct):
    __name__ = "MESSAGE_REACTION_REMOVE_ALL"


class MessageReactionRemoveEmoji(Struct):
    __name__ = "MESSAGE_REACTION_REMOVE_EMOJI"


# Presence Update
class PresenceUpdate(Struct):
    __name__ = "PRESENCE_UPDATE"


# Stage related Events
class StageInstanceCreate(Struct):
    __name__ = "STAGE_INSTANCE_CREATE"


class StageInstanceDelete(Struct):
    __name__ = "STAGE_INSTANCE_DELETE"


class StageInstanceUpdate(Struct):
    __name__ = "STAGE_INSTANCE_UPDATE"


# Typing Start
class TypingStart(Struct):
    __name__ = "TYPING_START"


# User Update
class UserUpdate(Struct):
    __name__ = "USER_UPDATE"


# Voice related Events
class VoiceStateUpdate(Struct):
    __name__ = "VOICE_STATE_UPDATE"


class VoiceServerUpdate(Struct):
    __name__ = "VOICE_SERVER_UPDATE"


# Webhooks Update
class WebhooksUpdate(Struct):
    __name__ = "WEBHOOKS_UPDATE"


# ======================================================================
#   WEBSOCKET PAYLOADS - END
# ======================================================================
