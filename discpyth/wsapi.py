import time
import zlib
from typing import TYPE_CHECKING, Set, Union

from .deps.socketed import (
    AnyIOWebSocketManager,
    ConnectionClosed,
    CurIOWebSocketManager,
)
from .deps.socketed.socket import ANY_IO_AVAILABLE, CURIO_AVAILABLE
from .event import EventSession

if ANY_IO_AVAILABLE:
    from anyio import Lock as Anyio_Lock
    from anyio import create_lock as Anyio_create_lock

if CURIO_AVAILABLE:
    from curio import Lock as Curio_Lock

    # from curio import Task as Curio_Task

if TYPE_CHECKING:
    from .discpyth import Session

ZLIB_SUFFIX = b"\x00\x00\xff\xff"


class BaseShard:
    __slots__ = {
        "buffer",
        "inflator",
        "identify",
        "seq",
        "ses_id",
        "ws_conn",
        "ses",
        "lock",
        "sid",
        "last_heartbeat_ack",
        "last_heartbeat_sent",
    }

    buffer: bytearray
    seq: int
    ses_id: str
    ws_conn: Union[AnyIOWebSocketManager, CurIOWebSocketManager]
    lock: Union[Anyio_Lock, Curio_Lock]
    sid: int
    ses: Session  # pylint: disable=used-before-assignment
    last_heartbeat_ack: float
    last_heartbeat_sent: float

    def __init__(self, identify):
        self.buffer = bytearray()
        self.inflator = zlib.decompressobj()
        self.seq = 0
        self.ses_id = ""
        self.identify = identify
        self.last_heartbeat_ack = time.time()
        self.last_heartbeat_sent = time.time()


class AnyIOShard(BaseShard):

    __slots__: Set[str] = set()

    lock: Anyio_Lock

    def __init__(self, identify):
        super().__init__(identify)
        self.lock = Anyio_create_lock()

    async def connect(self):
        try:
            await self.open()
        except ConnectionClosed as conn_closed:
            await self.close()
            self.ses.logger.error(conn_closed)

    async def open(self):
        if self.ws_conn is not None:
            self.ses.logger.warning(f"{self.sid} is already connected!")
            return

    async def close(self):
        pass


# Curio TBD


class WSSession(EventSession):

    __slots__: Set[str] = set()
