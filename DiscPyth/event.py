from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Coroutine

from . import _Session
from .eventhandlers import _handler_for_interface

if TYPE_CHECKING:
    from .eventhandlers import EventHandler


class Event_Session(_Session):
    def add_handler(
        self, event: str, func: Callable[[Any, Any], Coroutine[Any, Any, Any]]
    ):
        eh = _handler_for_interface(event, func)
        if eh is None:
            return

        self._add_event_handler(eh)

    def _add_event_handler(self, eh: EventHandler):
        if self._handlers is None:
            self._handlers = dict()

        try:
            self._handlers[eh.event].append(eh)
        except KeyError:
            self._handlers[eh.event] = [eh]

    async def handle(self, t, d):
        try:
            for eh in self._handlers[t]:
                await eh(self, d)
        except KeyError:
            return
