"""
This file contains the BaseSession class and the BaseShard class,
both are important base classes and are used multiple times across the
module.
"""
from __future__ import annotations

import asyncio
import zlib
from typing import TYPE_CHECKING, Dict, List, Union

from . import __author__, __version__
from .utils import DummyLogging, Logging

if TYPE_CHECKING:
    import aiohttp

    from .discpyth import Session
    from .wsapi import Shard


class BaseShard:
    __slots__ = {
        # The WebSocket Connection
        "_conn",
        # The Session instance controlling the shard
        "_ses",
        # ByteArray for decompressing
        "_buffer",
        # zlib.decompressobj instance
        "_inflator",
        # Identify payload to send
        "_identify",
    }

    def __init__(self, session: Session):

        self._ses: Session = session

        # bytearray object to pass into self._inflator.decompress()
        self._buffer: bytearray = bytearray()

        # zlib doesn't expose zlib.Decompress so no type hints
        # (visible anger)
        self._inflator = zlib.decompressobj()


class BaseSession:  # pylint: disable=too-many-instance-attributes
    __slots__ = {
        # Event loop
        "_loop",
        # Rest retries on failure
        "max_rest_retries",
        # aiohttp ClientSession instance
        "_client",
        # Token to be used
        "_token",
        # Rest User-Agent, doesnt have a "_" prefix to indicate that it
        # allow modification by users, in thw following format
        # "DiscordBot (link, version) extra_data"
        "user_agent",
        # Event handlers
        "_handlers",
        "_once_handlers",
        # If True then do "await callback()"
        # if False (default) then create it as a task
        # in the running loop
        "sync_events",
        # Gateway URL for shards to connect
        "_gateway",
        # Gateway imtents to use
        "_intents",
        # Logger instance
        "_log",
        # Shard count to use to connect to Discord Gateway
        "shard_count",
        # This  an be a list or an integer,
        # if its a list like `[5, 10]` then we will lauch shard 5
        # to shard 10 or if its an int like 0 then we will launch
        # shard 0
        "shard_id",
        # A dictionary containing all the launched shards
        "_shards",
    }

    def __init__(self, **options):
        # The user may pass in their own loop, not really recommended
        # `asyncio.get_event_loop()` is deprecated so not recommended to
        # mess with loops
        self._loop: asyncio.AbstractEventLoop = options.get("loop", None)

        self.max_rest_retries: int = options.get("rest_retries", 3)
        # ClientSession should be initialized in a coroutine
        self._client: aiohttp.ClientSession = None

        self._token: str = options.get("token", "")

        self.user_agent: str = options.get(
            "useragent",
            (
                "DiscordBot (https://github.com/DiscPyth/DiscPyth,"
                f" {__version__}) by {__author__}"
            ),
        )

        # This \/ is really dumb but hey it exists, lmao
        self.sync_events: bool = options.get("sync_events", False)

        self._gateway: str = ""

        self._intents: int = options.get("intents", 513)

        if options.get("log", False):
            name = options.get("name", "DiscPyth")
            self._log: Logging = Logging(
                name,
                log_level=options.get("level", 30),
                to_file=options.get("to_file", False),
                file=name + ".log",
            )
        else:
            # Just a place holder, but might add some functionality to
            # it in future
            self._log: DummyLogging = DummyLogging()

        self.shard_count: int = options.get("shard_count", 1)
        self.shard_id: Union[List[int], int] = options.get("shard_id", 0)

        self._shards: Dict[int, Shard] = {}
