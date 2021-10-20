from __future__ import annotations

import asyncio
import logging
import sys
import zlib
from typing import Literal

from . import _Session
from .structs import IDENTIFY, IDENTIFY_PROPERTIES, Intents
from .wsapi import WS_Session


class Session(WS_Session, _Session):
    def __init__(self):
        WS_Session.__init__(self)
        _Session.__init__(self)

    def open(self):
        self._loop.run_until_complete(self._open())

    def set_intents(self, intents):
        if isinstance(intents, Intents):
            self._log(20, f"Setting intents - {intents}...")
            self.Identify.Intents = intents
        elif isinstance(intents, int):
            self._log(20, f"Setting intents - {intents}...")
            self._log(30, f"You have entered your intents directly, you are advised to use {Intents} instead of specifying it directly!\nIf you know what you are doing then you can safely ignore this warning.")
            self.Identify.Intents = intents

    def close(self):
        self._log(20, f"Woosh, received close command!\nclean closing shard {self.Identify.Shard[0]}...")

        self._loop.run_until_complete(self._close_w_code())

        # We can only rely on this to know if we 
        # have multiple ws connections or not
        if self.Identify.Shard[1] == 1:
            self._loop.run_until_complete(self.Client.close())

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
        trim_logs: bool = True
    ) -> Session:
        s = cls()

        s._loop = asyncio.get_event_loop()
        s._buffer = bytearray()
        s._inflator = zlib.decompressobj()

        if log:
            if level not in (10, 20, 30, 40, 50):
                level = 30
            if log_name != "":
                log_name = "_"+log_name
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

        s.Identify = IDENTIFY()
        properties = IDENTIFY_PROPERTIES()
        properties.os = sys.platform
        properties.browser = "DiscPyth"
        properties.device = "DiscPyth"
        s.Identify.Token = token.strip()
        s.Identify.Properties = properties
        s.Identify.Compress = False
        s.Identify.Large = 250
        s.Identify.Shard = [shard_id, shard_count]

        return s
