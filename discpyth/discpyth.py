from __future__ import annotations

__all__ = ("Session", "new")

import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Union

from .base_classes import BaseSession
from .restapi import RESTSession
from .wsapi import Shard, ShardManager


class Session(ShardManager, Shard, RESTSession, BaseSession):
    def __init__(self, **options):
        BaseSession.__init__(self, **options)
        RESTSession.__init__(self)
        if self.shard_count == 1:
            Shard.__init__(self)
        elif self.shard_count > 1:
            ShardManager.__init__(self)

    @asynccontextmanager
    async def _openmanager(self):
        try:
            yield None
        finally:
            await self.close()

    def open(self):
        async def wrapped_open():
            async with self._openmanager():
                await self._open_ws(self.shard_id)

        try:
            asyncio.run(wrapped_open())
        except KeyboardInterrupt:
            pass

    async def close(self):

        if self._client is not None:
            await self._client.close()
            self._client = None  # type: ignore

    def __getitem__(self, key: int) -> Union[Session, Shard]:
        if not isinstance(key, int):
            # TODO: Think about an appropriate message
            raise TypeError("")

        # TODO: Think of  out of range and under range shards
        # error messasge
        if key > (self.shard_count - 1):
            raise IndexError("")
        if key < 0:
            raise IndexError("")

        if self._shards is not None:
            return self._shards[key]

        return self


def new(token, intents, /, *, shard_id=0, shard_count=1, **options) -> Session:
    shard_count = int(shard_count)
    intents = int(intents)
    token = str(token)

    if isinstance(shard_id, (list, int)):
        if isinstance(shard_id, list):
            if len(shard_id) != 2:
                raise IndexError(
                    (
                        "To launch multiple shards the format"
                        " should be '[start, end]'. Expected length of 2, got"
                        f" {len(shard_id)}"
                    )
                )
            if shard_id[1] > shard_count:
                raise ValueError(
                    "End of Shards to launch is more than Shard ID"
                )
        if isinstance(shard_id, int) and shard_id > shard_count:
            raise ValueError("End of Shards to launch is more than Shard ID")

    log_options: Dict[str, Union[int, str, bool]] = {}
    if options.get("log", False):
        log_options.update(
            log=True,
            name=str(options.get("name", "DiscPyth")),
            level=int(options.get("level", 30)),
            to_file=bool(options.get("to_file", False)),
        )

    cls = Session(
        token=token,
        intents=intents,
        shard_count=shard_count,
        shard_id=shard_id,
        rest_retries=int(options.get("rest_retries", 3)),
        **log_options,
    )
    return cls
