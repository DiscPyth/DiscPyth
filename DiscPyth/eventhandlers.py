import inspect
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Optional

from . import _Session
from .structs import *


class EventTypes:
    __slots__ = (
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
    )

    class EventHandlerWrap:
        __slots__ = ("_type",)

        class EventHandler:
            __slots__ = ("_type", "_func")

            def __init__(self):
                self._type = ""

            @property
            def type(self):
                return self._type

            async def __call__(self, s, d):
                await self._func(s, d)

        def __init__(self, typ: str):
            self._type = typ

        def __call__(self):
            evh = self.EventHandler()
            evh._type = self._type
            return evh

    def __init__(self):
        # fmt: off
        self.CHANNEL_CREATE                         = self.EventHandlerWrap("CHANNEL_CREATE")
        self.CHANNEL_DELETE                         = self.EventHandlerWrap("CHANNEL_DELETE")
        self.CHANNEL_PINS_UPDATE                    = self.EventHandlerWrap("CHANNEL_PINS_UPDATE")
        self.CHANNEL_UPDATE                         = self.EventHandlerWrap("CHANNEL_UPDATE")
        self.__CONNECT__                            = self.EventHandlerWrap("__CONNECT__")
        self.__DISCONNECT__                         = self.EventHandlerWrap("__DISCONNECT__")
        self.__EVENT__                              = self.EventHandlerWrap("__EVENT__")
        self.GUILD_BAN_ADD                          = self.EventHandlerWrap("GUILD_BAN_ADD")
        self.GUILD_BAN_REMOVE                       = self.EventHandlerWrap("GUILD_BAN_REMOVE")
        self.GUILD_CREATE                           = self.EventHandlerWrap("GUILD_CREATE")
        self.GUILD_DELETE                           = self.EventHandlerWrap("GUILD_DELETE")
        self.GUILD_EMOJIS_UPDATE                    = self.EventHandlerWrap("GUILD_EMOJIS_UPDATE")
        self.GUILD_INTEGRATIONS_UPDATE              = self.EventHandlerWrap("GUILD_INTEGRATIONS_UPDATE")
        self.GUILD_MEMBER_ADD                       = self.EventHandlerWrap("GUILD_MEMBER_ADD")
        self.GUILD_MEMBER_REMOVE                    = self.EventHandlerWrap("GUILD_MEMBER_REMOVE")
        self.GUILD_MEMBER_UPDATE                    = self.EventHandlerWrap("GUILD_MEMBER_UPDATE")
        self.GUILD_MEMBERS_CHUNK                    = self.EventHandlerWrap("GUILD_MEMBERS_CHUNK")
        self.GUILD_ROLE_CREATE                      = self.EventHandlerWrap("GUILD_ROLE_CREATE")
        self.GUILD_ROLE_DELETE                      = self.EventHandlerWrap("GUILD_ROLE_DELETE")
        self.GUILD_ROLE_UPDATE                      = self.EventHandlerWrap("GUILD_ROLE_UPDATE")
        self.GUILD_STICKERS_UPDATE                  = self.EventHandlerWrap("GUILD_STICKERS_UPDATE")
        self.GUILD_UPDATE                           = self.EventHandlerWrap("GUILD_UPDATE")
        self.INTEGRATION_CREATE                     = self.EventHandlerWrap("INTEGRATION_CREATE")
        self.INTEGRATION_DELETE                     = self.EventHandlerWrap("INTEGRATION_DELETE")
        self.INTEGRATION_UPDATE                     = self.EventHandlerWrap("INTEGRATION_UPDATE")
        self.INTERACTION_CREATE                     = self.EventHandlerWrap("INTERACTION_CREATE")
        self.INVITE_CREATE                          = self.EventHandlerWrap("INVITE_CREATE")
        self.INVITE_DELETE                          = self.EventHandlerWrap("INVITE_DELETE")
        self.MESSAGE_CREATE                         = self.EventHandlerWrap("MESSAGE_CREATE")
        self.MESSAGE_DELETE                         = self.EventHandlerWrap("MESSAGE_DELETE")
        self.MESSAGE_DELETE_BULK                    = self.EventHandlerWrap("MESSAGE_DELETE_BULK")
        self.MESSAGE_REACTION_ADD                   = self.EventHandlerWrap("MESSAGE_REACTION_ADD")
        self.MESSAGE_REACTION_REMOVE                = self.EventHandlerWrap("MESSAGE_REACTION_REMOVE")
        self.MESSAGE_REACTION_REMOVE_ALL            = self.EventHandlerWrap("MESSAGE_REACTION_REMOVE_ALL")
        self.MESSAGE_REACTION_REMOVE_EMOJI          = self.EventHandlerWrap("MESSAGE_REACTION_REMOVE_EMOJI")
        self.MESSAGE_UPDATE                         = self.EventHandlerWrap("MESSAGE_UPDATE")
        self.PRESENCE_UPDATE                        = self.EventHandlerWrap("PRESENCE_UPDATE")
        self.__RATE_LIMIT__                         = self.EventHandlerWrap("__RATE_LIMIT__")
        self.READY                                  = self.EventHandlerWrap("READY")
        self.RESUMED                                = self.EventHandlerWrap("RESUMED")
        self.STAGE_INSTANCE_CREATE                  = self.EventHandlerWrap("STAGE_INSTANCE_CREATE")
        self.STAGE_INSTANCE_DELETE                  = self.EventHandlerWrap("STAGE_INSTANCE_DELETE")
        self.STAGE_INSTANCE_UPDATE                  = self.EventHandlerWrap("STAGE_INSTANCE_UPDATE")
        self.TYPING_START                           = self.EventHandlerWrap("TYPING_START")
        self.THREAD_CREATE                          = self.EventHandlerWrap("THREAD_CREATE")
        self.THREAD_DELETE                          = self.EventHandlerWrap("THREAD_DELETE")
        self.THREAD_LIST_SYNC                       = self.EventHandlerWrap("THREAD_LIST_SYNC")
        self.THREAD_MEMBER_UPDATE                   = self.EventHandlerWrap("THREAD_MEMBER_UPDATE")
        self.THREAD_MEMBERS_UPDATE                  = self.EventHandlerWrap("THREAD_MEMBERS_UPDATE")
        self.THREAD_UPDATE                          = self.EventHandlerWrap("THREAD_UPDATE")
        self.USER_UPDATE                            = self.EventHandlerWrap("USER_UPDATE")
        self.VOICE_SERVER_UPDATE                    = self.EventHandlerWrap("VOICE_SERVER_UPDATE")
        self.VOICE_STATE_UPDATE                     = self.EventHandlerWrap("VOICE_STATE_UPDATE")
        self.WEBHOOKS_UPDATE                        = self.EventHandlerWrap("WEBHOOKS_UPDATE")
        # fmt: on


def _handler_for_interface(
    func: Callable[[Any, Any], Coroutine[Any, Any, Any]]
) -> Optional[Callable[[Any, Any], Coroutine[Any, Any, Any]]]:
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

    if param_values[1].annotation == Ready:
        return func
