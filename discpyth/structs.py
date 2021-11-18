__all__ = (
    "User",
    "ActivityTypes",
    "Activity",
    "Intents",
    "Ready",
    "Resumed",
    "Reconnect",
    "InvalidSession",
    "ChannelCreate",
    "ChannelDelete",
    "ChannelPinsUpdate",
    "ChannelUpdate",
    "ThreadCreate",
    "ThreadDelete",
    "ThreadListSync",
    "ThreadMembersUpdate",
    "ThreadMemberUpdate",
    "ThreadUpdate",
    "GuildCreate",
    "GuildDelete",
    "GuildUpdate",
    "GuildBanAdd",
    "GuildBanRemove",
    "GuildEmojisUpdate",
    "GuildStickersUpdate",
    "GuildIntegrationsUpdate",
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
    "InteractionCreate",
    "InviteCreate",
    "InviteDelete",
    "MessageCreate",
    "MessageDelete",
    "MessageUpdate",
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
    "VoiceServerUpdate",
    "VoiceStateUpdate",
    "WebhooksUpdate",
)

from enum import IntEnum
from typing import List

import go_json  # type: ignore


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


class User(go_json.Struct):
    id: str = go_json.field("id")
    username: str = go_json.field("username")
    discriminator: str = go_json.field("discriminator")
    avatar: str = go_json.field("avatar")
    bot: bool = go_json.field("bot", optional=True)
    system: bool = go_json.field("system", optional=True)
    mfa_enabled: bool = go_json.field("mfa_enabled", optional=True)
    banner: str = go_json.field("banner", optional=True)
    accent_color: int = go_json.field("accent_color", optional=True)
    locale: str = go_json.field("locale", optional=True)
    verified: bool = go_json.field("verified", optional=True)
    email: str = go_json.field("email", optional=True)
    flags: int = go_json.field("flags", optional=True)
    premium_type: int = go_json.field("premium_type", optional=True)
    public_flags: int = go_json.field("public_flags", optional=True)

    @property
    def tag(self):
        return self.username + "#" + self.discriminator


class ActivityTypes(IntEnum):
    GAME = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    CUSTOM = 4
    COMPETING = 5


class Activity(go_json.Struct):
    name: str = go_json.field("name")
    type: int = go_json.field("type")
    url: str = go_json.field("url", optional=True)
    created_at: int = go_json.field("created_at")
    timestamps = go_json.field("timestamps", optional=True)
    application_id: str = go_json.field("application_id", optional=True)
    details: str = go_json.field("details", optional=True)
    state: str = go_json.field("state", optional=True)
    emoji = go_json.field("emoji", optional=True)
    party = go_json.field("party", optional=True)
    assets = go_json.field("assets", optional=True)
    secrets = go_json.field("secrets", optional=True)
    instance: bool = go_json.field("instance", optional=True)
    flags: int = go_json.field("flags", optional=True)
    buttons = go_json.field("buttons", optional=True)


class Intents(IntEnum):
    # fmt: off
    GUILDS                          =   (1 << 0)  # noqa: E221, E222
    GUILD_MEMBERS                   =   (1 << 1)  # noqa: E221, E222
    GUILD_BANS                      =   (1 << 2)  # noqa: E221, E222
    GUILD_EMOJIS_AND_STICKERS       =   (1 << 3)  # noqa: E221, E222
    GUILD_INTEGRATIONS              =   (1 << 4)  # noqa: E221, E222
    GUILD_WEBHOOKS                  =   (1 << 5)  # noqa: E221, E222
    GUILD_INVITES                   =   (1 << 6)  # noqa: E221, E222
    GUILD_VOICE_STATES              =   (1 << 7)  # noqa: E221, E222
    GUILD_PRESENCES                 =   (1 << 8)  # noqa: E221, E222
    GUILD_MESSAGES                  =   (1 << 9)  # noqa: E221, E222
    GUILD_MESSAGE_REACTIONS         =   (1 << 10)  # noqa: E221, E222
    GUILD_MESSAGE_TYPING            =   (1 << 11)  # noqa: E221, E222
    DIRECT_MESSAGES                 =   (1 << 12)  # noqa: E221, E222
    DIRECT_MESSAGE_REACTIONS        =   (1 << 13)  # noqa: E221, E222
    DIRECT_MESSAGE_TYPING           =   (1 << 14)  # noqa: E221, E222
    GUILD_SCHEDULED_EVENTS          =   (1 << 16)  # noqa: E221, E222
    # fmt: on


class GetGateway(go_json.Struct):
    url: str = go_json.field("url")


class SessionStartLimit(go_json.Struct):
    total: int = go_json.field("total")
    remaining: int = go_json.field("remaining")
    reset_after: int = go_json.field("reset_after")
    max_concurrency: int = go_json.field("max_concurrency")


class GetGatewayBot(go_json.Struct):
    url: str = go_json.field("url")
    shards: int = go_json.field("shards")
    ses_start_limit: SessionStartLimit = go_json.field(
        "session_start_limit", json_object=SessionStartLimit
    )


class Ready(go_json.Struct):
    __name__ = "READY"
    version = go_json.field("v")
    user: User = go_json.field("user", json_object=User)
    guilds = go_json.field("guilds")
    session_id = go_json.field("session_id")
    shard = go_json.field("shard")
    application = go_json.field("application")


class Resumed(go_json.Struct):
    __name__ = "RESUMED"


class Reconnect(go_json.Struct):
    __name__ = "RECONNECT"


class InvalidSession(go_json.Struct):
    __name__ = "INVALID_SESSION"


class ChannelCreate(go_json.Struct):
    __name__ = "CHANNEL_CREATE"


class ChannelDelete(go_json.Struct):
    __name__ = "CHANNEL_DELETE"


class ChannelPinsUpdate(go_json.Struct):
    __name__ = "CHANNEL_PINS_UPDATE"


class ChannelUpdate(go_json.Struct):
    __name__ = "CHANNEL_UPDATE"


class ThreadCreate(go_json.Struct):
    __name__ = "THREAD_CREATE"


class ThreadDelete(go_json.Struct):
    __name__ = "THREAD_DELETE"


class ThreadListSync(go_json.Struct):
    __name__ = "THREAD_LIST_SYNC"


class ThreadMembersUpdate(go_json.Struct):
    __name__ = "THREAD_MEMBERS_UPDATE"


class ThreadMemberUpdate(go_json.Struct):
    __name__ = "THREAD_MEMBER_UPDATE"


class ThreadUpdate(go_json.Struct):
    __name__ = "THREAD_UPDATE"


class GuildCreate(go_json.Struct):
    __name__ = "GUILD_CREATE"


class GuildDelete(go_json.Struct):
    __name__ = "GUILD_DELETE"


class GuildUpdate(go_json.Struct):
    __name__ = "GUILD_UPDATE"


class GuildBanAdd(go_json.Struct):
    __name__ = "GUILD_BAN_ADD"


class GuildBanRemove(go_json.Struct):
    __name__ = "GUILD_BAN_REMOVE"


class GuildEmojisUpdate(go_json.Struct):
    __name__ = "GUILD_EMOJIS_UPDATE"


class GuildStickersUpdate(go_json.Struct):
    __name__ = "GUILD_STICKERS_UPDATE"


class GuildIntegrationsUpdate(go_json.Struct):
    __name__ = "GUILD_INTEGRATIONS_UPDATE"


class GuildMemberAdd(go_json.Struct):
    __name__ = "GUILD_MEMBER_ADD"


class GuildMemberRemove(go_json.Struct):
    __name__ = "GUILD_MEMBER_REMOVE"


class GuildMemberUpdate(go_json.Struct):
    __name__ = "GUILD_MEMBER_UPDATE"


class GuildMembersChunk(go_json.Struct):
    __name__ = "GUILD_MEMBERS_CHUNK"


class GuildRoleCreate(go_json.Struct):
    __name__ = "GUILD_ROLE_CREATE"


class GuildRoleDelete(go_json.Struct):
    __name__ = "GUILD_ROLE_DELETE"


class GuildRoleUpdate(go_json.Struct):
    __name__ = "GUILD_ROLE_UPDATE"


class GuildScheduledEventCreate(go_json.Struct):
    __name__ = "GUILD_SCHEDULED_EVENT_CREATE"


class GuildScheduledEventDelete(go_json.Struct):
    __name__ = "GUILD_SCHEDULED_EVENT_DELETE"


class GuildScheduledEventUpdate(go_json.Struct):
    __name__ = "GUILD_SCHEDULED_EVENT_UPDATE"


class GuildScheduledEventUserAdd(go_json.Struct):
    __name__ = "GUILD_SCHEDULED_EVENT_USER_ADD"


class GuildScheduledEventUserRemove(go_json.Struct):
    __name__ = "GUILD_SCHEDULED_EVENT_USER_REMOVE"


class IntegrationCreate(go_json.Struct):
    __name__ = "INTEGRATION_CREATE"


class IntegrationDelete(go_json.Struct):
    __name__ = "INTEGRATION_DELETE"


class IntegrationUpdate(go_json.Struct):
    __name__ = "INTEGRATION_UPDATE"


class InteractionCreate(go_json.Struct):
    __name__ = "INTERACTION_CREATE"


class InviteCreate(go_json.Struct):
    __name__ = "INVITE_CREATE"


class InviteDelete(go_json.Struct):
    __name__ = "INVITE_DELETE"


class MessageCreate(go_json.Struct):
    __name__ = "MESSAGE_CREATE"


class MessageDelete(go_json.Struct):
    __name__ = "MESSAGE_DELETE"


class MessageUpdate(go_json.Struct):
    __name__ = "MESSAGE_UPDATE"


class MessageDeleteBulk(go_json.Struct):
    __name__ = "MESSAGE_DELETE_BULK"


class MessageReactionAdd(go_json.Struct):
    __name__ = "MESSAGE_REACTION_ADD"


class MessageReactionRemove(go_json.Struct):
    __name__ = "MESSAGE_REACTION_REMOVE"


class MessageReactionRemoveAll(go_json.Struct):
    __name__ = "MESSAGE_REACTION_REMOVE_ALL"


class MessageReactionRemoveEmoji(go_json.Struct):
    __name__ = "MESSAGE_REACTION_REMOVE_EMOJI"


class PresenceUpdate(go_json.Struct):
    __name__ = "PRESENCE_UPDATE"


class StageInstanceCreate(go_json.Struct):
    __name__ = "STAGE_INSTANCE_CREATE"


class StageInstanceDelete(go_json.Struct):
    __name__ = "STAGE_INSTANCE_DELETE"


class StageInstanceUpdate(go_json.Struct):
    __name__ = "STAGE_INSTANCE_UPDATE"


class TypingStart(go_json.Struct):
    __name__ = "TYPING_START"


class UserUpdate(go_json.Struct):
    __name__ = "USER_UPDATE"


class VoiceServerUpdate(go_json.Struct):
    __name__ = "VOICE_SERVER_UPDATE"


class VoiceStateUpdate(go_json.Struct):
    __name__ = "VOICE_STATE_UPDATE"


class WebhooksUpdate(go_json.Struct):
    __name__ = "WEBHOOKS_UPDATE"
