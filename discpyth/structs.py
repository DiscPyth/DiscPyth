from enum import IntEnum
from typing import List, Literal

import go_json as gj  # type: ignore


class User(gj.Struct):
    id: str = gj.field("id")
    username: str = gj.field("username")
    discriminator: str = gj.field("discriminator")
    avatar: str = gj.field("avatar")
    bot: bool = gj.field("bot", optional=True)
    system: bool = gj.field("system", optional=True)
    mfa_enabled: bool = gj.field("mfa_enabled", optional=True)
    banner: str = gj.field("banner", optional=True)
    accent_color: int = gj.field("accent_color", optional=True)
    locale: str = gj.field("locale", optional=True)
    verified: bool = gj.field("verified", optional=True)
    email: str = gj.field("email", optional=True)
    flags: int = gj.field("flags", optional=True)
    premium_type: int = gj.field("premium_type", optional=True)
    public_flags: int = gj.field("public_flags", optional=True)

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


class Activity(gj.Struct):
    name: str = gj.field("name")
    type: int = gj.field("type")
    url: str = gj.field("url", optional=True)
    created_at: int = gj.field("created_at")
    timestamps = gj.field("timestamps", optional=True)
    application_id: str = gj.field("application_id", optional=True)
    details: str = gj.field("details", optional=True)
    state: str = gj.field("state", optional=True)
    emoji = gj.field("emoji", optional=True)
    party = gj.field("party", optional=True)
    assets = gj.field("assets", optional=True)
    secrets = gj.field("secrets", optional=True)
    instance: bool = gj.field("instance", optional=True)
    flags: int = gj.field("flags", optional=True)
    buttons = gj.field("buttons", optional=True)


class UpdateStatusData(gj.Struct):
    since: int = gj.field("since")
    activities: list = gj.field("activities")
    status: Literal["online", "idle", "dnd", "invisible"] = gj.field("status")
    afk: bool = gj.field("afk")


class Event(gj.Struct):
    __partial = True  # pylint: disable=unused-private-member
    operation: int = gj.field("op")
    sequence: int = gj.field("s", optional=True)
    type: str = gj.field("t", optional=True)
    raw_data: str = gj.field("d", raw_json=True)


class Intents(IntEnum):
    # fmt: off
    GUILDS                          =   (1 << 0) # noqa: E221, E222
    GUILD_MEMBERS                   =   (1 << 1) # noqa: E221, E222
    GUILD_BANS                      =   (1 << 2) # noqa: E221, E222
    GUILD_EMOJIS_AND_STICKERS       =   (1 << 3) # noqa: E221, E222
    GUILD_INTEGRATIONS              =   (1 << 4) # noqa: E221, E222
    GUILD_WEBHOOKS                  =   (1 << 5) # noqa: E221, E222
    GUILD_INVITES                   =   (1 << 6) # noqa: E221, E222
    GUILD_VOICE_STATES              =   (1 << 7) # noqa: E221, E222
    GUILD_PRESENCES                 =   (1 << 8) # noqa: E221, E222
    GUILD_MESSAGES                  =   (1 << 9) # noqa: E221, E222
    GUILD_MESSAGE_REACTIONS         =   (1 << 10) # noqa: E221, E222
    GUILD_MESSAGE_TYPING            =   (1 << 11) # noqa: E221, E222
    DIRECT_MESSAGES                 =   (1 << 12) # noqa: E221, E222
    DIRECT_MESSAGE_REACTIONS        =   (1 << 13) # noqa: E221, E222
    DIRECT_MESSAGE_TYPING           =   (1 << 14) # noqa: E221, E222
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


class Hello(gj.Struct):
    heartbeat_interval: int = gj.field("heartbeat_interval")
    trace: str = gj.field("_trace", raw_json=True)


class Ready(gj.Struct):
    version = gj.field("v")
    user: User = gj.field("user", json_object=User)
    guilds = gj.field("guilds")
    session_id = gj.field("session_id")
    shard = gj.field("shard")
    application = gj.field("application")


class Resumed(gj.Struct):
    pass


class Reconnect(gj.Struct):
    pass


class InvalidSession(gj.Struct):
    pass


class ChannelCreate(gj.Struct):
    pass


class ChannelDelete(gj.Struct):
    pass


class ChannelPinsUpdate(gj.Struct):
    pass


class ChannelUpdate(gj.Struct):
    pass


class ThreadCreate(gj.Struct):
    pass


class ThreadDelete(gj.Struct):
    pass


class ThreadListSync(gj.Struct):
    pass


class ThreadMembersUpdate(gj.Struct):
    pass


class ThreadMemberUpdate(gj.Struct):
    pass


class ThreadUpdate(gj.Struct):
    pass


class GuildCreate(gj.Struct):
    pass


class GuildDelete(gj.Struct):
    pass


class GuildUpdate(gj.Struct):
    pass


class GuildBanAdd(gj.Struct):
    pass


class GuildBanRemove(gj.Struct):
    pass


class GuildEmojisUpdate(gj.Struct):
    pass


class GuildStickersUpdate(gj.Struct):
    pass


class GuildIntegrationsUpdate(gj.Struct):
    pass


class GuildMemberAdd(gj.Struct):
    pass


class GuildMemberRemove(gj.Struct):
    pass


class GuildMemberUpdate(gj.Struct):
    pass


class GuildMembersChunk(gj.Struct):
    pass


class GuildRoleCreate(gj.Struct):
    pass


class GuildRoleDelete(gj.Struct):
    pass


class GuildRoleUpdate(gj.Struct):
    pass


class IntegrationCreate(gj.Struct):
    pass


class IntegrationDelete(gj.Struct):
    pass


class IntegrationUpdate(gj.Struct):
    pass


class InteractionCreate(gj.Struct):
    pass


class InviteCreate(gj.Struct):
    pass


class InviteDelete(gj.Struct):
    pass


class MessageCreate(gj.Struct):
    pass


class MessageDelete(gj.Struct):
    pass


class MessageUpdate(gj.Struct):
    pass


class MessageDeleteBulk(gj.Struct):
    pass


class MessageReactionAdd(gj.Struct):
    pass


class MessageReactionRemove(gj.Struct):
    pass


class MessageReactionRemoveAll(gj.Struct):
    pass


class MessageReactionRemoveEmoji(gj.Struct):
    pass


class PresenceUpdate(gj.Struct):
    pass


class StageInstanceCreate(gj.Struct):
    pass


class StageInstanceDelete(gj.Struct):
    pass


class StageInstanceUpdate(gj.Struct):
    pass


class TypingStart(gj.Struct):
    pass


class UserUpdate(gj.Struct):
    pass


class VoiceServerUpdate(gj.Struct):
    pass


class VoiceStateUpdate(gj.Struct):
    pass


class WebhooksUpdate(gj.Struct):
    pass
