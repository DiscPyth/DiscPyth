from __future__ import annotations

__all__ = ("Session",)

import asyncio
import os
import signal
import sys
import zlib
from collections.abc import Sequence as SequenceType
from contextlib import asynccontextmanager

import aiohttp

from .base_classes import ShardConfig
from .endpoints import Endpoints
from .eventhandlers import EventHandler
from .structs import Identify, IdentifyProperties
from .utils import Logging
from .wsapi import Shard, WSSession


def create_shard(sid, scount, self):
    return Shard(
        buffer=bytearray(),
        inflator=zlib.decompressobj(),
        sequence=0,
        session_id="",
        identify=Identify(
            token=str(self.token),
            properties=IdentifyProperties(
                **{
                    "$os": sys.platform,
                    "$browser": "DiscPyth",
                    "$device": "DiscPyth",
                }
            ),
            compress=False,
            large_threshold=250,
            shard=[sid, scount],
            intents=int(self.intents),
        ),
        session=self,
        lock=asyncio.Lock(),
    )


class Session(WSSession):  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=dangerous-default-value
        self,
        token,
        intents,
        /,
        *,
        shard_config: ShardConfig = {
            "ids": 0,
            "count": 1,
            "auto": False,
        },
        **options,
    ) -> None:
        WSSession.__init__(self)

        # shard_id can either be an int or a tuple
        # int   -> Launch a single shard
        # tuple -> Launch shards in range(*shard_id)

        # Since we are using a for loop with range() below, we need to
        # convert it into a tuple which will be
        # (shard_id, (shard_id + 1))
        shard_id = shard_config.get("ids", 0)
        shard_count = shard_config.get("count", 1)
        if isinstance(shard_id, int) and 0 <= shard_id < shard_count:
            # Shard id will never be equal to shard count, it will be at
            # max => (shard_count - 1) `range()` kinda handles this for us
            # and it also cannot be less than 0.
            shard_config["ids"] = (shard_id, (shard_id + 1))
        if isinstance(shard_id, SequenceType):
            if (
                len(shard_id) >= 2
                and shard_id[-1] <= shard_count
                and shard_id[0] >= 0
            ):
                # If the user wants to launch multiple shards then they can
                # pass shard_id as a tuple, but we need to make sure that
                # min is not less than 0 and max is not more than
                # shard_count.
                shard_config["ids"] = tuple(shard_id)
            else:
                raise IndexError(
                    "Sequence of Shard IDs must be of length 2 or more"
                )

        # Shards should be "created" during `open()`, because if we
        # create the dictionary in `__init__()` we cannot make a call to
        # /gateway/bot and we would have to then overwrite the dict in
        # `open()` if auto is set to True hence we just save the
        # configuration in `__init__`
        self.intents = intents
        self.shard_config = shard_config
        self.max_rest_retries = options.get("max_rest_retries", 3)
        self.user_agent: str = options.get("user_agent", self.user_agent)
        self.token = str(token)
        if options.get("log", False):
            self.log = Logging(
                options.get("name", "DiscPyth"),
                log_level=options.get("log_level", 30),
                to_file=options.get("to_file", False),
                file=options.get("name", "DiscPyth") + ".log",
            )
        else:
            self.log = Logging("", 0, False, "", "")

        self._handlers = EventHandler(intents, False)
        self._once_handlers = EventHandler(intents, True)

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
                "Received open command, opening connection(s) to discord gateway",
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
                if self._client is None:
                    self._client = aiohttp.ClientSession()
                self._gateway = await self.get_gateway_bot()
                self._gateway.url = (
                    self._gateway.url
                    + "?v="
                    + Endpoints.API_VERSION
                    + "&encoding=json"
                )

                if self.shard_config["auto"]:
                    self._ws_conn = {
                        s: create_shard(s, self._gateway.shards, self)
                        for s in range(*self._gateway.shards)
                    }
                else:
                    self._ws_conn = {
                        s: create_shard(s, self.shard_config["count"], self)
                        for s in (
                            range(*self.shard_config["ids"])
                            if len(self.shard_config["ids"]) == 2
                            else self.shard_config["ids"]
                        )
                    }
                # Open all shards
                await self._open_ws()
                await asyncio.Event().wait()

        try:
            # Since get_event_loop is deprecated I dont really want to
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
