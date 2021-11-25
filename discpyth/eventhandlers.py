from __future__ import annotations

import asyncio
import inspect
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, Set, Tuple

from go_json import S, loads

from .structs import Events

if TYPE_CHECKING:
    from .discpyth import Session


class EventDispatcher:
    __slots__ = {"callbacks", "struct"}

    def __init__(self, struct: S) -> None:
        self.struct = struct
        self.callbacks: Set[
            Callable[[Session, S], Coroutine[Any, Any, None]]
        ] = set()

    def __iadd__(
        self, callback: Callable[[Session, S], Coroutine[Any, Any, None]]
    ) -> EventDispatcher:
        self.callbacks.add(callback)
        return self

    async def __call__(self, ses: Session, data: str):
        data = loads(data, self.struct)
        for callback in self.callbacks:
            if ses.sync_events:
                await callback(ses, data)  # type: ignore
            else:
                asyncio.create_task(callback(ses, data), name="DiscPyth")  # type: ignore


class EventHandler:
    __slots__ = {"event_dispatchers", "is_once"}

    def __init__(self, intents, once):
        self.event_dispatchers: Dict[str, EventDispatcher] = {}
        self.event_dispatchers.update(
            **{
                name: EventDispatcher(event_struct)
                for name, event_struct in Events.NON_INTENT_BASED_EVENTS.value.items()
            }
        )
        for intent, event_struct_t in Events.INTENT_BASED_EVENTS.value.items():
            if intents & intent:
                self.event_dispatchers.update(
                    **{
                        event_struct.__dict__["__name__"]: EventDispatcher(
                            event_struct
                        )
                        for event_struct in event_struct_t
                    }
                )

        # I'm definitely a ONCE, lol... if you don't get the reference
        # then ignore this comment
        self.is_once = once

    def __add__(
        self,
        func: Callable[[Session, S], Coroutine[Any, Any, None]],
        event=None,
    ) -> Tuple[int, str]:

        coro_msg = (
            "Expected a coroutine, {0} is not a coroutine. Skipping..."
        ).format

        args_len_msg = (
            "Event callbacks must only have 2 arguments,"
            " nothing more nothing less! {0} has"
            " {1} than 2 arguments. Skipping..."
        ).format

        arg_typ_msg = (
            "Argument types should only be POSITIONAL_ONLY"
            "or POSTION_OR_KEYWORD, {0} has invalid argument types."
            " Skipping..."
        ).format

        not_good_msg = (
            f"One of the following error occured while adding {func.__name__}"
            "\nPassed event is not a class."
            "\nPassed event is not registered."
            "\n(Rare case, something went wrong.)"
            "\nYou may discuss this issue @ https://discord.gg/8RATdNBs6n"
        )

        success_msg = "{0} successfully added to {1} callbacks!".format

        if not inspect.iscoroutinefunction(func):
            return 40, coro_msg(func.__name__)

        sig = inspect.signature(func)
        params = list(sig.parameters.values())

        if len(params) != 2:
            return 40, args_len_msg(
                func.__name__, ("less" if len(params) < 2 else "more")
            )

        if params[0].kind not in (0, 1) or params[1].kind not in (0, 1):
            return 40, arg_typ_msg(func.__name__)

        # Type annotations take priority over passed event class
        if (
            inspect.isclass(params[1].annotation)
            and params[1].annotation.__dict__["__name__"]
            in self.event_dispatchers
        ):
            self.event_dispatchers[
                params[1].annotation.__dict__["__name__"]
            ] += func
            return 20, success_msg(
                func.__name__, params[1].annotation.__name__
            )
        if inspect.isclass(event) and event.__name__ in self.event_dispatchers:
            self.event_dispatchers[event.__name__] += func
            return 20, success_msg(func.__name__, event.__name__)

        # This will not happen 90% of the time
        return 40, not_good_msg

    async def __call__(self, event: str, session: Session, data: str):
        try:
            await self.event_dispatchers[event](session, data)
        except KeyError:
            if not self.is_once:
                session.log.warn(
                    f"Event not registered or unknown! {self.is_once}",
                    __name__,
                )
        finally:
            if self.is_once:
                try:
                    del self.event_dispatchers[event]
                except KeyError:
                    pass
