from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Coroutine

from . import _Session
from .eventhandlers import _handler_for_interface


class Event_Session(_Session):
    def add_event_handler(self, func: Callable[[Any, Any], Coroutine[Any, Any, Any]]):
        eh = _handler_for_interface(func)
        if eh is None:
            return

        self._add_handler(eh)

    def _add_handler(self, eh):
        if self._handlers is None:
            self._handlers = dict()

        self._handlers[eh.type].append(eh)

    def _register_event_provider(self, eh):
        if eh.type in self._register_event_providers:
            return
        self._register_event_providers[eh.type] = eh

    async def handle(self, t, d):
        for eh in self._handlers[t]:
            await eh(self, d)
