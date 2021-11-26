import inspect

from .restapi import RESTSession


class EventSession(RESTSession):
    def add_handler(self, func):
        # A wrapped function so that users can call `add_handler` with
        # parens or or without parens
        def wrapped_handler(func_):
            if self._handlers is not None:
                logparms = self._handlers + func_
                self.log.log(*logparms, __name__)
            return func_

        if inspect.isclass(func):
            return wrapped_handler

        return wrapped_handler(func)

    def add_once_handler(self, func):
        # Same as `add_handler` just replace `_handlers` -> `_once_handlers`

        def wrapped_handler(func_):
            if self._once_handlers is not None:
                logparms = self._once_handlers + func_
                self.log.log(*logparms, __name__)
            return func_

        if inspect.isclass(func):
            return wrapped_handler

        return wrapped_handler(func)

    async def _handle(self, event: str, data: str):
        # TODO: add internal callbacks for state and other stuff
        await self._handlers(event, self, data)  # type: ignore # pylint: disable=not-callable
        await self._once_handlers(event, self, data)  # type: ignore # pylint: disable=not-callable
