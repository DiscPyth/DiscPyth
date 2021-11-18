import asyncio
from typing import TYPE_CHECKING

import go_json  # type: ignore

if TYPE_CHECKING:
    from .discpyth import Session


class EventHandler:
    __slots__ = {"d_struct", "callbacks"}

    def __init__(self, dstruct):

        self.d_struct = dstruct
        self.callbacks = set()

    async def handle(  # pylint: disable=used-before-assignment
        self, ses: Session, data: str
    ):
        data = go_json.loads(data, self.d_struct)
        for callback in self.callbacks:
            if ses.sync_events:
                await callback(ses, data)
            else:
                asyncio.create_task(
                    callback,
                    name=f"DiscPyth - '{self.d_struct.__name__}' callback '{callback.__name__}'",
                )
