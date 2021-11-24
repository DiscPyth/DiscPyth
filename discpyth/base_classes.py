"""
This file contains the BaseSession class and the BaseShard class,
both are important base classes and are used multiple times across the
module.
"""
from __future__ import annotations

__all__ = ("BaseSession",)

from typing import TYPE_CHECKING, Dict, Set

from . import __author__, __url__, __version__  # pylint: disable=cyclic-import

if TYPE_CHECKING:
    import aiohttp

    from .utils import Logging
    from .wsapi import Shard


class BaseSession:  # pylint: disable=too-many-instance-attributes
    __slots__: Set[str] = {
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
        # Logger instance
        "log",
        # This is 100% hell
        "_ws_conn",
    }

    def __init__(self):
        self.max_rest_retries: int = 3
        self._client: aiohttp.ClientSession = None
        self._token: str = ""
        self.user_agent: str = (
            f"DiscordBot ({__url__}, {__version__}) by {__author__}"
        )
        self._handlers = None
        self._once_handlers = None
        self.sync_events: bool = False
        self._gateway: str = ""
        self.log: Logging = None
        self._ws_conn: Dict[int, Shard] = None
