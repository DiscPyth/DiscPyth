from __future__ import annotations

import asyncio
import logging
import sys
from typing import Literal

from . import _Session  # pylint: disable=cyclic-import
from .structs import Identify, IdentifyProperties, Intents
from .wsapi import WsSession  # pylint: disable=cyclic-import


class Session(WsSession, _Session):
    def __init__(self):
        WsSession.__init__(self)
        _Session.__init__(self)

    def open(self) -> None:
        self._log(
            20,
            f"Woosh, received open command!\nOpening shard {self.identify.shard[0]}...",
        )
        async def _wrapped_open():
            await self._open()
        self._open_task = self._loop.create_task(_wrapped_open())
        self._loop.run_until_complete(self._open_task)

    def set_intents(self, intents) -> None:
        if isinstance(intents, (Intents, int)):
            self._log(20, f"Setting intents - {intents}...")
            self.identify.intents = intents
        else:
            self._log(
                30,
                f"Invalid type of intents, expected {Intents} or {int} instead got {type(intents)}!\nUsing 0 as intents",
            )

    def close(self) -> None:
        self._log(
            20,
            f"Woosh, received close command!\nClean closing shard {self.identify.shard[0]}...",
        )

        self._loop.run_until_complete(self._close_w_code())

        # We can only rely on this to know if we
        # have multiple ws connections or not
        if self.identify.shard[1] == 1:
            self._loop.run_until_complete(self.client.close())

    def stop(self):
        self._loop.stop()

    @classmethod
    def new(  # pylint: disable=too-many-arguments, too-many-branches;
        cls,
        token: str,
        shard_id: int = 0,
        shard_count: int = 1,
        log: bool = False,
        level: Literal[10, 20, 30, 40, 50] = 30,
        to_file: bool = False,
        log_name: str = "",
        trim_logs: bool = True,
    ) -> Session:
        s_instance = cls()

        s_instance._loop = asyncio.get_event_loop()

        if log:
            if isinstance(level, str):
                if level == "debug":
                    level = 10
                elif level == "info":
                    level = 20
                elif level in ("warning", "warn"):
                    level = 30
                elif level == "error":
                    level = 40
                elif level == "critical":
                    level = 50
                else:
                    level = 30
            if isinstance(level, int):
                if level not in (10, 20, 30, 40, 50):
                    level = 30
            if log_name != "":
                log_name = "_" + log_name
            logger = logging.getLogger(f"DiscPyth{log_name}")
            logger.setLevel(10)
            formatter = logging.Formatter(
                "[%(name)s] | [%(asctime)s] | [%(levelname)s] : %(message)s"
            )
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(level)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)
            if to_file:
                file_handler = logging.FileHandler(f"DiscPyth{log_name}")
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

            s_instance._log = logger.log
        if not trim_logs:
            s_instance._trim_logs = False
        s_instance.identify = Identify()
        properties = IdentifyProperties()
        properties.os = sys.platform
        properties.browser = "DiscPyth"
        properties.device = "DiscPyth"
        s_instance.identify.token = token.strip()
        s_instance.identify.properties = properties
        s_instance.identify.compress = False
        s_instance.identify.large_threshold = 250
        s_instance.identify.shard = [shard_id, shard_count]

        s_instance._ws_lock = asyncio.Lock()

        return s_instance
