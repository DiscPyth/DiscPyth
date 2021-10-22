from __future__ import annotations

import asyncio
import logging
import sys
import zlib
from typing import TYPE_CHECKING, Literal

from . import _Session
from .event import Event_Session
from .structs import Identify, IdentifyProperties, Intents
from .wsapi import WS_Session


class Session(WS_Session, Event_Session, _Session):
    def __init__(self):
        Event_Session.__init__(self)
        WS_Session.__init__(self)
        _Session.__init__(self)

    def open(self):
        self._loop.run_until_complete(self._open())

    def set_intents(self, intents):
        if isinstance(intents, Intents) or isinstance(intents, int):
            self._log(20, f"Setting intents - {intents}...")
            self.identify.intents = intents
        else:
            self._log(
                30,
                f"Invalid type of intents, expected {Intents} or {int} instead got {type(intents)}!\nUsing 0 as intents",
            )

    def close(self):
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
    def new(
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
        s = cls()

        s._loop = asyncio.get_event_loop()
        s._buffer = bytearray()
        s._inflator = zlib.decompressobj()

        if log:
            if level not in (10, 20, 30, 40, 50):
                level = 30
            if log_name != "":
                log_name = "_" + log_name
            logger = logging.getLogger(f"DiscPyth{log_name}")
            logger.setLevel(10)
            formatter = logging.Formatter(
                f"[%(name)s] | [%(asctime)s] | [%(levelname)s] : %(message)s"
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

            s._log = logger.log
        if not trim_logs:
            self._trim_logs = False
        s.identify = Identify()
        properties = IdentifyProperties()
        properties.os = sys.platform
        properties.browser = "DiscPyth"
        properties.device = "DiscPyth"
        s.identify.token = token.strip()
        s.identify.properties = properties
        s.identify.compress = False
        s.identify.large_threshold = 250
        s.identify.shard = [shard_id, shard_count]

        return s
