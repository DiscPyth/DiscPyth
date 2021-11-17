from typing import Dict, Union
import asyncio
from contextlib import contextmanager

from .base_classes import BaseSession
from .restapi import RESTSession

class Session(RESTSession, BaseSession):
    def __init__(self, **options):
        BaseSession.__init__(self, **options)
        RESTSession.__init__(self)

    
    @contextmanager
    def get_loop(self):
        loop: asyncio.AbstractEventLoop = asyncio.events._get_running_loop()
        try:
            if loop is not None:
                yield loop
            else:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                yield loop
        finally:
            try:
                asyncio.runners._cancel_all_tasks(loop)
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.run_until_complete(loop.shutdown_default_executor())
            finally:
                asyncio.set_event_loop(None)
                loop.close()

    def open(self):
        async def wrapped_open():
            self._loop = asyncio.get_running_loop()
            try:
                await self.get_gateway_bot()
                await asyncio.sleep(15)
            except KeyboardInterrupt:
                self.close()

        asyncio.run(wrapped_open())

    def close(self):
        if self._client is not None:
            self._loop.run_until_complete(self._client.close())


def new(token, intents, shard_id=0, shard_count=1, **options) -> Session:
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
        # If a user passes in the wrong thing then the program will
        # crash, hence don't mess with loops unless you know what you
        # are doing.
        loop=options.get("loop", None),
        **log_options,
    )
    return cls
