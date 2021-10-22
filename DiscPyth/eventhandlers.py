import inspect
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Literal

from . import _Session


class EventHandler:
    def __init__(self, event, func: Callable[[Any, Any], Coroutine[Any, Any, Any]]):
        self._event = event
        self._func = func

    @property
    def event(self):
        return self._event

    async def __call__(self, s, ed):
        await self._func(s, ed)


_EVENT_TYPES = [
    "CHANNEL_CREATE",
    "CHANNEL_DELETE",
    "CHANNEL_PINS_UPDATE",
    "CHANNEL_UPDATE",
    "__CONNECT__",
    "__DISCONNECT__",
    "__EVENT__",
    "GUILD_BAN_ADD",
    "GUILD_BAN_REMOVE",
    "GUILD_CREATE",
    "GUILD_DELETE",
    "GUILD_EMOJIS_UPDATE",
    "GUILD_INTEGRATIONS_UPDATE",
    "GUILD_MEMBER_ADD",
    "GUILD_MEMBER_REMOVE",
    "GUILD_MEMBER_UPDATE",
    "GUILD_MEMBERS_CHUNK",
    "GUILD_ROLE_CREATE",
    "GUILD_ROLE_DELETE",
    "GUILD_ROLE_UPDATE",
    "GUILD_STICKERS_UPDATE",
    "GUILD_UPDATE",
    "INTEGRATION_CREATE",
    "INTEGRATION_DELETE",
    "INTEGRATION_UPDATE",
    "INTERACTION_CREATE",
    "INVITE_CREATE",
    "INVITE_DELETE",
    "MESSAGE_CREATE",
    "MESSAGE_DELETE",
    "MESSAGE_DELETE_BULK",
    "MESSAGE_REACTION_ADD",
    "MESSAGE_REACTION_REMOVE",
    "MESSAGE_REACTION_REMOVE_ALL",
    "MESSAGE_REACTION_REMOVE_EMOJI",
    "MESSAGE_UPDATE",
    "PRESENCE_UPDATE",
    "__RATE_LIMIT__",
    "READY",
    "RESUMED",
    "STAGE_INSTANCE_CREATE",
    "STAGE_INSTANCE_DELETE",
    "STAGE_INSTANCE_UPDATE",
    "TYPING_START",
    "THREAD_CREATE",
    "THREAD_DELETE",
    "THREAD_LIST_SYNC",
    "THREAD_MEMBER_UPDATE",
    "THREAD_MEMBERS_UPDATE",
    "THREAD_UPDATE",
    "USER_UPDATE",
    "VOICE_SERVER_UPDATE",
    "VOICE_STATE_UPDATE",
    "WEBHOOKS_UPDATE",
]


def _handler_for_interface(
    event: str, func: Callable[[Any, Any], Coroutine[Any, Any, Any]]
) -> Literal[None, Callable[[Any, Any], Coroutine[Any, Any, Any]]]:
    signature = inspect.signature(func)
    params = signature.parameters
    param_values = list(params.values())
    if not inspect.iscoroutinefunction(func):
        print(f"Specified function/method is not a coroutine! Ignoring {func.__name__}")
        return None
    if not len(params) == 2:
        print(
            f"There must be 2 arguments specified, but got {'more' if len(params)>2 else 'fewer'} than 2! Ignoring {func.__name__}."
        )
        return None
    if not param_values[0].kind in (0, 1) or not param_values[1].kind in (0, 1):
        print(
            f"Expected arguments to be [(POSITIONAL or POSITIONAL_OR_KEYWORD), (POSITIONAL or POSITIONAL_OR_KEYWORD)] instead got [{param_values[0].kind}, {param_values[1].kind}]! Ignoring {func.__name__}"
        )
        return None

    if event.upper().replace(" ", "_") in _EVENT_TYPES:
        evh = EventHandler(event.upper().replace(" ", "_"), func)
        return evh
    else:
        print(f"Invalid event type! Ignoring {func.__name__}")
        return None
