from __future__ import annotations
from . import _Session
from .wsapi import WS_Session
from .types import IDENTIFY, IDENTIFY_PROPERTIES
import sys
import logging
import asyncio


class Session(WS_Session, _Session):
    def __init__(self):
        WS_Session.__init__(self)
        _Session.__init__(self)

    @classmethod
    def new(
        cls,
        token: str,
        shard_id: int = 0,
        shard_count: int = 1,
        log: bool = False,
        level: int = 30,
        to_file: bool = False,
        log_name: str = "",
    ) -> Session:
        s = cls()

        s._loop = asyncio.get_event_loop()

        if log:
            if level not in (10,20,30,40,50):
                level = 30
            logger = logging.getLogger(f"DiscPyth_{log_name}")
            logger.setLevel(10)
            formatter = logging.Formatter(
                "[%(name)s] | [%(asctime)s] | [%(levelname)s] : %(message)s"
            )
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(level)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)
            if to_file:
                file_handler = logging.FileHandler(
                    f"DiscPyth_{log_name}", mode="a", encoding="utf-8"
                )
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
        s.Identify.Compress = True
        s.Identify.Large = 250
        s.Identify.Shard = [shard_id, shard_count]

        return s
