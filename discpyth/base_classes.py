"""
This file contains the BaseSession class,
which is a important base classe and is used multiple times across the
module.
"""
from __future__ import annotations

__all__ = ("BaseSession",)

from typing import TYPE_CHECKING, Dict, Sequence, Set, TypedDict, Union

from . import __author__, __url__, __version__  # pylint: disable=cyclic-import

if TYPE_CHECKING:
    import aiohttp

    from .eventhandlers import EventHandler
    from .structs import GetGatewayBot
    from .utils import Logging
    from .wsapi import Shard


class ShardConfig(TypedDict):
    ids: Union[Sequence[int], int]
    count: int
    auto: bool


class BaseSession:  # pylint: disable=too-many-instance-attributes
    __slots__: Set[str] = {
        # Rest retries on failure
        "max_rest_retries",
        # aiohttp ClientSession instance
        "_client",
        # Token to be used
        "token",
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
        "shard_config",
        "intents",
        # This is 100% hell
        "_ws_conn",
    }

    def __init__(self):
        self.max_rest_retries: int = 3
        self._client: aiohttp.ClientSession = None
        self.token: str = ""
        self.user_agent: str = (
            f"DiscordBot ({__url__}, {__version__}) by {__author__}"
        )
        self._handlers: EventHandler = None
        self._once_handlers: EventHandler = None
        self.sync_events: bool = False
        self._gateway: GetGatewayBot = ""
        self.log: Logging = None
        self.shard_config: ShardConfig = {}
        self.intents: int = 0
        self._ws_conn: Dict[int, Shard] = None
