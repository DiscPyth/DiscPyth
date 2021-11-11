import inspect

from go_json import is_struct_class  # type: ignore

from . import _Session  # pylint: disable=cyclic-import


class Event(_Session):
    async def _handle(self, event, data):
        if self._handlers is not None:
            await self._handlers._handle_event(  # pylint: disable=protected-access
                self, event, data
            )
        if self._once_handlers is not None:
            await self._once_handlers._handle_event(  # pylint: disable=protected-access
                self, event, data
            )
            self._once_handlers = None

    def add_handler(self, func):
        if inspect.isclass(func):
            if is_struct_class(func):  # pylint: disable=no-else-return

                def wrapped(func_):
                    if self._handlers is not None:
                        self._log(
                            *self._handlers._add_event_callback(  # pylint: disable=protected-access
                                func_, event=func
                            )
                        )
                    return func_

                return wrapped
            else:
                raise AttributeError(
                    "The passed Event is not a go_json struct, read the stacktrace to find out where you specified the wrong event!"
                )
        if self._handlers is not None:
            self._log(
                *self._handlers._add_event_callback(  # pylint: disable=protected-access
                    func
                )
            )
        return func

    def add_once_handler(self, func):
        if inspect.isclass(func):
            if is_struct_class(func):  # pylint: disable=no-else-return

                def wrapped(func_):
                    if self._once_handlers is not None:
                        self._log(
                            *self._once_handlers._add_event_callback(  # pylint: disable=protected-access
                                func_, event=func
                            )
                        )
                    return func_

                return wrapped
            else:
                raise AttributeError(
                    "The passed Event is not a go_json struct, read the stacktrace to find out where you specified the wrong event!"
                )
        if self._once_handlers is not None:
            self._log(
                *self._once_handlers._add_event_callback(  # pylint: disable=protected-access
                    func
                )
            )
        return func
