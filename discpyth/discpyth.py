from __future__ import annotations

__all__ = ("Session",)

import asyncio
import os
import signal
import sys
import zlib
from collections.abc import Sequence as SequenceType
from contextlib import asynccontextmanager
from typing import Sequence, Tuple, Union

from .structs import Identify, IdentifyProperties
from .utils import Logging
from .wsapi import Shard, WSSession


class Session(WSSession):
    def __init__(
        self,
        token,
        intents,
        /,
        *,
        shard_id: Union[Sequence[int], int] = 0,
        shard_count=1,
        **options,
    ) -> None:
        WSSession.__init__(self)
        # If anything fails in the code below, this will make sure things
        # don't go haywire since its just gonna launch Shard 0 which will
        # receive all the events for us, but I still need to do some
        # confirmation regarding shards
        shard_range: Tuple[int, int] = (0, 1)

        # shard_id can either be an int or a tuple
        # int   -> Launch a single shard
        # tuple -> Launch shards in range(*shard_id)

        # Since we are using a for loop with range() below, we need to
        # convert it into a tuple which will be
        # (shard_id, (shard_id + 1))
        if isinstance(shard_id, int) and 0 <= shard_id <= shard_count:
            # Shard id will never be equal to shard count, it will be at
            # max => (shard_count - 1) `range()` kinda handles this for us
            # and it also cannot be less than 0.
            shard_range = (shard_id, (shard_id + 1))
        if (
            isinstance(shard_id, SequenceType)
            and len(shard_id) == 2
            and shard_id[1] <= shard_count
            and shard_id[0] >= 0
        ):
            # If the user wants to launch multiple shards then they can
            # pass shard_id as a tuple, but we need to make sure that
            # min is not less than 0 and max is not more than
            # shard_count.
            shard_range = tuple(shard_id)  # type: ignore

        self.max_rest_retries = options.get("max_rest_retries", 3)
        self.user_agent: str = options.get("user_agent", self.user_agent)
        self._token = str(token)
        self._ws_conn = {
            s: Shard(
                buffer=bytearray(),
                inflator=zlib.decompressobj(),
                sequence=0,
                session_id="",
                identify=Identify(
                    token=str(token),
                    properties=IdentifyProperties(
                        **{
                            "$os": sys.platform,
                            "$browser": "DiscPyth",
                            "$device": "DiscPyth",
                        }
                    ),
                    compress=False,
                    large_threshold=250,
                    shard=[s, shard_count],
                    intents=int(intents),
                ),
                session=self,
                lock=asyncio.Lock(),
            )
            for s in range(*shard_range)
        }
        if options.get("log", False):
            self.log = Logging(
                options.get("name", "DiscPyth"),
                log_level=options.get("log_level", 30),
                to_file=options.get("to_file", False),
                file=options.get("name", "DiscPyth") + ".log",
            )
        else:
            self.log = Logging("", 0, False, "", "")

    @asynccontextmanager
    async def _openmanager(self):
        try:
            # we don't have anything to do in __aenter__
            # so just yeild nothing
            yield None
        finally:
            # But we do need to close our connections, so __aexit__ is
            # what we will focus on here
            await self.close()

    def _handle_sigterm(self, *args):  # pylint: disable=no-self-use;
        # Too lazy to create another class derived from something like
        # SystemExit, but doesn't matter both are subclasses of
        # BaseException and as long as we can execute our clean close
        # code we don't have to worry about it being KeyboardInterrupt.
        raise KeyboardInterrupt("Triggered by sig TERM.")

    def open(self):
        async def wrapped_open():
            self.log.info(
                f"Received open command, opening {len(self._ws_conn)} connection(s) to discord gateway",
                __name__,
            )
            # Might be helpful
            self.log.info(f"Current Process ID is {os.getpid()}", __name__)
            # Handle sig TERM, is it necessary(?)
            signal.signal(signal.SIGTERM, self._handle_sigterm)
            # Credits to graingert#9275 (172270232499388416) for the
            # idea of context managers, or I was about to work with some
            # hacky-ish event loop code.
            async with self._openmanager():
                # Open all shards
                await self._open_ws()

        try:
            # Since get_event_loop is deprecated i dont really want to
            # mess with loop creation so context manager + asyncio.run
            # works both ways, forwards compatible and backwards
            # compatible with python versions. Yay!
            asyncio.run(wrapped_open())
        except KeyboardInterrupt:
            # Ofc we gotta suppress the long sig INT traceback 'cus we
            # cannot catch it while to loop is running but thanks to the
            # context manager all the shards are closed properly so we
            # can safely suppress this.
            pass

    async def close(self):

        self.log.info(
            "Recieved close command, clean closing ALL shards.", __name__
        )

        # Close all the WebSocket connections.
        await self.close_ws()

        # Then finally close the aiohttp ClientSession thingy, dont
        # quite remember what it is... (trust me, I'm a good dev...
        # forgetting some names won't break your bot, I ~~promise~~.)
        if self._client is not None:
            await self._client.close()
            self._client = None  # type: ignore
