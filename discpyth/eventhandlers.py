from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional, Set, Tuple

import go_json as gj  # type: ignore

# fmt: off
from .structs import ( # isort: skip
    Ready,
    Resumed,
    Reconnect,
    InvalidSession,

    ChannelCreate,
    ChannelDelete,
    ChannelPinsUpdate,
    ChannelUpdate,

    ThreadCreate,
    ThreadDelete,
    ThreadListSync,
    ThreadMembersUpdate,
    ThreadMemberUpdate,
    ThreadUpdate,

    GuildCreate,
    GuildDelete,
    GuildUpdate,

    GuildBanAdd,
    GuildBanRemove,

    GuildEmojisUpdate,
    GuildStickersUpdate,

    GuildIntegrationsUpdate,

    GuildMemberAdd,
    GuildMemberRemove,
    GuildMemberUpdate,

    GuildMembersChunk,

    GuildRoleCreate,
    GuildRoleDelete,
    GuildRoleUpdate,

    IntegrationCreate,
    IntegrationDelete,
    IntegrationUpdate,

    InteractionCreate,

    InviteCreate,
    InviteDelete,

    MessageCreate,
    MessageDelete,
    MessageUpdate,

    MessageDeleteBulk,
    MessageReactionAdd,
    MessageReactionRemove,
    MessageReactionRemoveAll,
    MessageReactionRemoveEmoji,

    PresenceUpdate,

    StageInstanceCreate,
    StageInstanceDelete,
    StageInstanceUpdate,

    TypingStart,

    UserUpdate,

    VoiceServerUpdate,
    VoiceStateUpdate,

    WebhooksUpdate,
)
# fmt: on

if TYPE_CHECKING:
    from .discpyth import Session


class EventHandler:  # pylint: disable=too-many-instance-attributes;
    _EVENTS = {
        "READY": Ready,
        "RESUMED": Resumed,
        "RECONNECT": Reconnect,
        "INVALID_SESSION": InvalidSession,
        "CHANNEL_CREATE": ChannelCreate,
        "CHANNEL_DELETE": ChannelDelete,
        "CHANNEL_PINS_UPDATE": ChannelPinsUpdate,
        "CHANNEL_UPDATE": ChannelUpdate,
        "THREAD_CREATE": ThreadCreate,
        "THREAD_DELETE": ThreadDelete,
        "THREAD_LIST_SYNC": ThreadListSync,
        "THREAD_MEMBERS_UPDATE": ThreadMembersUpdate,
        "THREAD_MEMBER_UPDATE": ThreadMemberUpdate,
        "THREAD_UPDATE": ThreadUpdate,
        "GUILD_CREATE": GuildCreate,
        "GUILD_DELETE": GuildDelete,
        "GUILD_UPDATE": GuildUpdate,
        "GUILD_BAN_ADD": GuildBanAdd,
        "GUILD_BAN_REMOVE": GuildBanRemove,
        "GUILD_EMOJIS_UPDATE": GuildEmojisUpdate,
        "GUILD_STICKERS_UPDATE": GuildStickersUpdate,
        "GUILD_INTEGRATIONS_UPDATE": GuildIntegrationsUpdate,
        "GUILD_MEMBER_ADD": GuildMemberAdd,
        "GUILD_MEMBER_REMOVE": GuildMemberRemove,
        "GUILD_MEMBER_UPDATE": GuildMemberUpdate,
        "GUILD_MEMBERS_CHUNK": GuildMembersChunk,
        "GUILD_ROLE_CREATE": GuildRoleCreate,
        "GUILD_ROLE_DELETE": GuildRoleDelete,
        "GUILD_ROLE_UPDATE": GuildRoleUpdate,
        "INTEGRATION_CREATE": IntegrationCreate,
        "INTEGRATION_DELETE": IntegrationDelete,
        "INTEGRATION_UPDATE": IntegrationUpdate,
        "INTERACTION_CREATE": InteractionCreate,
        "INVITE_CREATE": InviteCreate,
        "INVITE_DELETE": InviteDelete,
        "MESSAGE_CREATE": MessageCreate,
        "MESSAGE_DELETE": MessageDelete,
        "MESSAGE_UPDATE": MessageUpdate,
        "MESSAGE_DELETE_BULK": MessageDeleteBulk,
        "MESSAGE_REACTION_ADD": MessageReactionAdd,
        "MESSAGE_REACTION_REMOVE": MessageReactionRemove,
        "MESSAGE_REACTION_REMOVE_ALL": MessageReactionRemoveAll,
        "MESSAGE_REACTION_REMOVE_EMOJI": MessageReactionRemoveEmoji,
        "PRESENCE_UPDATE": PresenceUpdate,
        "STAGE_INSTANCE_CREATE": StageInstanceCreate,
        "STAGE_INSTANCE_DELETE": StageInstanceDelete,
        "STAGE_INSTANCE_UPDATE": StageInstanceUpdate,
        "TYPING_START": TypingStart,
        "USER_UPDATE": UserUpdate,
        "VOICE_SERVER_UPDATE": VoiceServerUpdate,
        "VOICE_STATE_UPDATE": VoiceStateUpdate,
        "WEBHOOKS_UPDATE": WebhooksUpdate,
    }
    __slots__ = {
        "ready",
        "resumed",
        "reconnect",
        "invalid_session",
        "channel_create",
        "channel_delete",
        "channel_pins_update",
        "channel_update",
        "thread_create",
        "thread_delete",
        "thread_list_sync",
        "thread_members_update",
        "thread_member_update",
        "thread_update",
        "guild_create",
        "guild_delete",
        "guild_update",
        "guild_ban_add",
        "guild_ban_remove",
        "guild_emojis_update",
        "guild_stickers_update",
        "guild_integrations_update",
        "guild_member_add",
        "guild_member_remove",
        "guild_member_update",
        "guild_members_chunk",
        "guild_role_create",
        "guild_role_delete",
        "guild_role_update",
        "integration_create",
        "integration_delete",
        "integration_update",
        "interaction_create",
        "invite_create",
        "invite_delete",
        "message_create",
        "message_delete",
        "message_update",
        "message_delete_bulk",
        "message_reaction_add",
        "message_reaction_remove",
        "message_reaction_remove_all",
        "message_reaction_remove_emoji",
        "presence_update",
        "stage_instance_create",
        "stage_instance_delete",
        "stage_instance_update",
        "typing_start",
        "user_update",
        "voice_server_update",
        "voice_state_update",
        "webhooks_update",
    }

    def __init__(self):  # pylint: disable=too-many-statements;
        self.ready: Set[Callable[[Session, Ready], Awaitable[None]]] = set()
        self.resumed: Set[Callable[[Session, Resumed], Awaitable[None]]] = set()
        self.reconnect: Set[Callable[[Session, Reconnect], Awaitable[None]]] = set()
        self.invalid_session: Set[
            Callable[[Session, InvalidSession], Awaitable[None]]
        ] = set()

        self.channel_create: Set[
            Callable[[Session, ChannelCreate], Awaitable[None]]
        ] = set()
        self.channel_delete: Set[
            Callable[[Session, ChannelDelete], Awaitable[None]]
        ] = set()
        self.channel_pins_update: Set[
            Callable[[Session, ChannelPinsUpdate], Awaitable[None]]
        ] = set()
        self.channel_update: Set[
            Callable[[Session, ChannelUpdate], Awaitable[None]]
        ] = set()

        self.thread_create: Set[
            Callable[[Session, ThreadCreate], Awaitable[None]]
        ] = set()
        self.thread_delete: Set[
            Callable[[Session, ThreadDelete], Awaitable[None]]
        ] = set()
        self.thread_list_sync: Set[
            Callable[[Session, ThreadListSync], Awaitable[None]]
        ] = set()
        self.thread_members_update: Set[
            Callable[[Session, ThreadMembersUpdate], Awaitable[None]]
        ] = set()
        self.thread_member_update: Set[
            Callable[[Session, ThreadMemberUpdate], Awaitable[None]]
        ] = set()
        self.thread_update: Set[
            Callable[[Session, ThreadUpdate], Awaitable[None]]
        ] = set()

        self.guild_create: Set[
            Callable[[Session, GuildCreate], Awaitable[None]]
        ] = set()
        self.guild_delete: Set[
            Callable[[Session, GuildDelete], Awaitable[None]]
        ] = set()
        self.guild_update: Set[
            Callable[[Session, GuildUpdate], Awaitable[None]]
        ] = set()

        self.guild_ban_add: Set[
            Callable[[Session, GuildBanAdd], Awaitable[None]]
        ] = set()
        self.guild_ban_remove: Set[
            Callable[[Session, GuildBanRemove], Awaitable[None]]
        ] = set()

        self.guild_emojis_update: Set[
            Callable[[Session, GuildEmojisUpdate], Awaitable[None]]
        ] = set()
        self.guild_stickers_update: Set[
            Callable[[Session, GuildStickersUpdate], Awaitable[None]]
        ] = set()

        self.guild_integrations_update: Set[
            Callable[[Session, GuildIntegrationsUpdate], Awaitable[None]]
        ] = set()

        self.guild_member_add: Set[
            Callable[[Session, GuildMemberAdd], Awaitable[None]]
        ] = set()
        self.guild_member_remove: Set[
            Callable[[Session, GuildMemberRemove], Awaitable[None]]
        ] = set()
        self.guild_member_update: Set[
            Callable[[Session, GuildMemberUpdate], Awaitable[None]]
        ] = set()

        self.guild_members_chunk: Set[
            Callable[[Session, GuildMembersChunk], Awaitable[None]]
        ] = set()

        self.guild_role_create: Set[
            Callable[[Session, GuildRoleCreate], Awaitable[None]]
        ] = set()
        self.guild_role_delete: Set[
            Callable[[Session, GuildRoleDelete], Awaitable[None]]
        ] = set()
        self.guild_role_update: Set[
            Callable[[Session, GuildRoleUpdate], Awaitable[None]]
        ] = set()

        self.integration_create: Set[
            Callable[[Session, IntegrationCreate], Awaitable[None]]
        ] = set()
        self.integration_delete: Set[
            Callable[[Session, IntegrationDelete], Awaitable[None]]
        ] = set()
        self.integration_update: Set[
            Callable[[Session, IntegrationUpdate], Awaitable[None]]
        ] = set()

        self.interaction_create: Set[
            Callable[[Session, InteractionCreate], Awaitable[None]]
        ] = set()

        self.invite_create: Set[
            Callable[[Session, InviteCreate], Awaitable[None]]
        ] = set()
        self.invite_delete: Set[
            Callable[[Session, InviteDelete], Awaitable[None]]
        ] = set()

        self.message_create: Set[
            Callable[[Session, MessageCreate], Awaitable[None]]
        ] = set()
        self.message_delete: Set[
            Callable[[Session, MessageDelete], Awaitable[None]]
        ] = set()
        self.message_update: Set[
            Callable[[Session, MessageUpdate], Awaitable[None]]
        ] = set()

        self.message_delete_bulk: Set[
            Callable[[Session, MessageDeleteBulk], Awaitable[None]]
        ] = set()
        self.message_reaction_add: Set[
            Callable[[Session, MessageReactionAdd], Awaitable[None]]
        ] = set()
        self.message_reaction_remove: Set[
            Callable[[Session, MessageReactionRemove], Awaitable[None]]
        ] = set()
        self.message_reaction_remove_all: Set[
            Callable[[Session, MessageReactionRemoveAll], Awaitable[None]]
        ] = set()
        self.message_reaction_remove_emoji: Set[
            Callable[[Session, MessageReactionRemoveEmoji], Awaitable[None]]
        ] = set()

        self.presence_update: Set[
            Callable[[Session, PresenceUpdate], Awaitable[None]]
        ] = set()

        self.stage_instance_create: Set[
            Callable[[Session, StageInstanceCreate], Awaitable[None]]
        ] = set()
        self.stage_instance_delete: Set[
            Callable[[Session, StageInstanceDelete], Awaitable[None]]
        ] = set()
        self.stage_instance_update: Set[
            Callable[[Session, StageInstanceUpdate], Awaitable[None]]
        ] = set()

        self.typing_start: Set[
            Callable[[Session, TypingStart], Awaitable[None]]
        ] = set()

        self.user_update: Set[Callable[[Session, UserUpdate], Awaitable[None]]] = set()

        self.voice_server_update: Set[
            Callable[[Session, VoiceServerUpdate], Awaitable[None]]
        ] = set()
        self.voice_state_update: Set[
            Callable[[Session, VoiceStateUpdate], Awaitable[None]]
        ] = set()

        self.webhooks_update: Set[
            Callable[[Session, WebhooksUpdate], Awaitable[None]]
        ] = set()

    async def _handle_event(self, session: Session, event, data) -> None:
        data = gj.loads(data, self._EVENTS.get(event, None))
        event = getattr(self, event.lower(), set())
        for callback in event:
            if session.sync_events:  # pylint: disable=protected-access
                await callback(session, data)
            else:
                session._loop.create_task(  # pylint: disable=protected-access
                    callback(session, data)
                )

    def _add_event_callback(  # pylint: disable=too-many-return-statements,too-many-branches,too-many-statements;
        self,
        func: Callable[[Session, Any], Awaitable[None]],
        event=None,
    ) -> Optional[Tuple[int, str]]:
        if not inspect.iscoroutinefunction(func):
            return (
                30,
                f"Event callback must be coroutines, skipping {func.__name__} since its not a coroutine...",
            )
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        if len(params) != 2:
            return (
                30,
                f"Event Callbacks should only have 2 arguments, skipping {func.__name__} since it has {'less' if len(params) < 2 else 'more'} that required arguments...",
            )
        if params[1].annotation is inspect._empty and event is None:  # type: ignore # pylint: disable=protected-access
            return (
                30,
                f"Event not defined, skipping {func.__name__} since it has no event defined...",
            )

        if params[1].annotation is Ready or event is Ready:
            self.ready.add(func)
            return 10, f"{func.__name__} has been added to 'READY' event callbacks."
        if params[1].annotation is Resumed or event is Resumed:
            self.resumed.add(func)
            return 10, f"{func.__name__} has been added to 'RESUMED' event callbacks."
        if params[1].annotation is Reconnect or event is Reconnect:
            self.reconnect.add(func)
            return 10, f"{func.__name__} has been added to 'RECONNECT' event callbacks."
        if params[1].annotation is InvalidSession or event is InvalidSession:
            self.invalid_session.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'INVALID_SESSION' event callbacks.",
            )
        if params[1].annotation is ChannelCreate or event is ChannelCreate:
            self.channel_create.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'CHANNEL_CREATE' event callbacks.",
            )
        if params[1].annotation is ChannelDelete or event is ChannelDelete:
            self.channel_delete.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'CHANNEL_DELETE' event callbacks.",
            )
        if params[1].annotation is ChannelPinsUpdate or event is ChannelPinsUpdate:
            self.channel_pins_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'CHANNEL_PINS_UPDATE' event callbacks.",
            )
        if params[1].annotation is ChannelUpdate or event is ChannelUpdate:
            self.channel_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'CHANNEL_UPDATE' event callbacks.",
            )
        if params[1].annotation is ThreadCreate or event is ThreadCreate:
            self.thread_create.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'THREAD_CREATE' event callbacks.",
            )
        if params[1].annotation is ThreadDelete or event is ThreadDelete:
            self.thread_delete.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'THREAD_DELETE' event callbacks.",
            )
        if params[1].annotation is ThreadListSync or event is ThreadListSync:
            self.thread_list_sync.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'THREAD_LIST_SYNC' event callbacks.",
            )
        if params[1].annotation is ThreadMembersUpdate or event is ThreadMembersUpdate:
            self.thread_members_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'THREAD_MEMBERS_UPDATE' event callbacks.",
            )
        if params[1].annotation is ThreadMemberUpdate or event is ThreadMemberUpdate:
            self.thread_member_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'THREAD_MEMBER_UPDATE' event callbacks.",
            )
        if params[1].annotation is ThreadUpdate or event is ThreadUpdate:
            self.thread_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'THREAD_UPDATE' event callbacks.",
            )
        if params[1].annotation is GuildCreate or event is GuildCreate:
            self.guild_create.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'GUILD_CREATE' event callbacks.",
            )
        if params[1].annotation is GuildDelete or event is GuildDelete:
            self.guild_delete.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'GUILD_DELETE' event callbacks.",
            )
        if params[1].annotation is GuildUpdate or event is GuildUpdate:
            self.guild_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'GUILD_UPDATE' event callbacks.",
            )
        if params[1].annotation is GuildBanAdd or event is GuildBanAdd:
            self.guild_ban_add.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'GUILD_BAN_ADD' event callbacks.",
            )
        if params[1].annotation is GuildBanRemove or event is GuildBanRemove:
            self.guild_ban_remove.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'GUILD_BAN_REMOVE' event callbacks.",
            )
        if params[1].annotation is GuildEmojisUpdate or event is GuildEmojisUpdate:
            self.guild_emojis_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'GUILD_EMOJIS_UPDATE' event callbacks.",
            )
        if params[1].annotation is GuildStickersUpdate or event is GuildStickersUpdate:
            self.guild_stickers_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'GUILD_STICKERS_UPDATE' event callbacks.",
            )
        if (
            params[1].annotation is GuildIntegrationsUpdate
            or event is GuildIntegrationsUpdate
        ):
            self.guild_integrations_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'GUILD_INTEGRATIONS_UPDATE' event callbacks.",
            )
        if params[1].annotation is GuildMemberAdd or event is GuildMemberAdd:
            self.guild_member_add.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'GUILD_MEMBER_ADD' event callbacks.",
            )
        if params[1].annotation is GuildMemberRemove or event is GuildMemberRemove:
            self.guild_member_remove.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'GUILD_MEMBER_REMOVE' event callbacks.",
            )
        if params[1].annotation is GuildMemberUpdate or event is GuildMemberUpdate:
            self.guild_member_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'GUILD_MEMBER_UPDATE' event callbacks.",
            )
        if params[1].annotation is GuildMembersChunk or event is GuildMembersChunk:
            self.guild_members_chunk.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'GUILD_MEMBERS_CHUNK' event callbacks.",
            )
        if params[1].annotation is GuildRoleCreate or event is GuildRoleCreate:
            self.guild_role_create.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'GUILD_ROLE_CREATE' event callbacks.",
            )
        if params[1].annotation is GuildRoleDelete or event is GuildRoleDelete:
            self.guild_role_delete.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'GUILD_ROLE_DELETE' event callbacks.",
            )
        if params[1].annotation is GuildRoleUpdate or event is GuildRoleUpdate:
            self.guild_role_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'GUILD_ROLE_UPDATE' event callbacks.",
            )
        if params[1].annotation is IntegrationCreate or event is IntegrationCreate:
            self.integration_create.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'INTEGRATION_CREATE' event callbacks.",
            )
        if params[1].annotation is IntegrationDelete or event is IntegrationDelete:
            self.integration_delete.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'INTEGRATION_DELETE' event callbacks.",
            )
        if params[1].annotation is IntegrationUpdate or event is IntegrationUpdate:
            self.integration_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'INTEGRATION_UPDATE' event callbacks.",
            )
        if params[1].annotation is InteractionCreate or event is InteractionCreate:
            self.interaction_create.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'INTERACTION_CREATE' event callbacks.",
            )
        if params[1].annotation is InviteCreate or event is InviteCreate:
            self.invite_create.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'INVITE_CREATE' event callbacks.",
            )
        if params[1].annotation is InviteDelete or event is InviteDelete:
            self.invite_delete.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'INVITE_DELETE' event callbacks.",
            )
        if params[1].annotation is MessageCreate or event is MessageCreate:
            self.message_create.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'MESSAGE_CREATE' event callbacks.",
            )
        if params[1].annotation is MessageDelete or event is MessageDelete:
            self.message_delete.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'MESSAGE_DELETE' event callbacks.",
            )
        if params[1].annotation is MessageUpdate or event is MessageUpdate:
            self.message_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'MESSAGE_UPDATE' event callbacks.",
            )
        if params[1].annotation is MessageDeleteBulk or event is MessageDeleteBulk:
            self.message_delete_bulk.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'MESSAGE_DELETE_BULK' event callbacks.",
            )
        if params[1].annotation is MessageReactionAdd or event is MessageReactionAdd:
            self.message_reaction_add.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'MESSAGE_REACTION_ADD' event callbacks.",
            )
        if (
            params[1].annotation is MessageReactionRemove
            or event is MessageReactionRemove
        ):
            self.message_reaction_remove.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'MESSAGE_REACTION_REMOVE' event callbacks.",
            )
        if (
            params[1].annotation is MessageReactionRemoveAll
            or event is MessageReactionRemoveAll
        ):
            self.message_reaction_remove_all.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'MESSAGE_REACTION_REMOVE_ALL' event callbacks.",
            )
        if (
            params[1].annotation is MessageReactionRemoveEmoji
            or event is MessageReactionRemoveEmoji
        ):
            self.message_reaction_remove_emoji.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'MESSAGE_REACTION_REMOVE_EMOJI' event callbacks.",
            )
        if params[1].annotation is PresenceUpdate or event is PresenceUpdate:
            self.presence_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'PRESENCE_UPDATE' event callbacks.",
            )
        if params[1].annotation is StageInstanceCreate or event is StageInstanceCreate:
            self.stage_instance_create.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'STAGE_INSTANCE_CREATE' event callbacks.",
            )
        if params[1].annotation is StageInstanceDelete or event is StageInstanceDelete:
            self.stage_instance_delete.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'STAGE_INSTANCE_DELETE' event callbacks.",
            )
        if params[1].annotation is StageInstanceUpdate or event is StageInstanceUpdate:
            self.stage_instance_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'STAGE_INSTANCE_UPDATE' event callbacks.",
            )
        if params[1].annotation is TypingStart or event is TypingStart:
            self.typing_start.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'TYPING_START' event callbacks.",
            )
        if params[1].annotation is UserUpdate or event is UserUpdate:
            self.user_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'USER_UPDATE' event callbacks.",
            )
        if params[1].annotation is VoiceServerUpdate or event is VoiceServerUpdate:
            self.voice_server_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'VOICE_SERVER_UPDATE' event callbacks.",
            )
        if params[1].annotation is VoiceStateUpdate or event is VoiceStateUpdate:
            self.voice_state_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'VOICE_STATE_UPDATE' event callbacks.",
            )
        if params[1].annotation is WebhooksUpdate or event is WebhooksUpdate:
            self.webhooks_update.add(func)
            return (
                10,
                f"{func.__name__} has been added to 'WEBHOOKS_UPDATE' event callbacks.",
            )

        # This happens when you are too lazy to do a proper check with 50+ events in your decorator
        return (
            30,
            "Something is not right 😕\nMake sure you passed in the right Event or didn't mess up somewhere...",
        )
