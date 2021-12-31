from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Sequence, Union

if TYPE_CHECKING:
    from logging import Logger

    from httpx import AsyncClient

    from .state import State
    from .wsapi import AnyIOShard, CurioShard


class BaseSession:

    __slots__ = {
        "token",
        "intents",
        "state",
        "user_agent",
        "max_rest_retries",
        "logger",
        "_backend",
        "_gateway",
        "_client",
        "_shards",
        "_shard_id",
        "_shard_count",
    }

    token: str
    intents: int
    state: State
    user_agent: str
    max_rest_retries: int
    logger: Logger
    _backend: str
    _gateway: None
    _client: AsyncClient
    _shards: Dict[int, Union[AnyIOShard, CurioShard]]
    _shard_id: Union[int, Sequence[int]]
    _shard_count: int
