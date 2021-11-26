from __future__ import annotations

__all__ = ("Shard", "WSSession")

import asyncio
from typing import TYPE_CHECKING, Optional

import aiohttp
import go_json

from .event import EventSession
from .structs import Event, Hello
from .utils import WSClosedError

if TYPE_CHECKING:
    from .discpyth import Session

ZLIB_SUFFIX = b"\x00\x00\xff\xff"


class Shard:  # pylint: disable=too-many-instance-attributes
    __slots__ = {
        "buffer",
        "inflator",
        "identify",
        "seq",
        "ses_id",
        "ws_conn",
        "ses",
        "lock",
        "hbt_task",
        "sid",
        "last_heartbeat_ack",
        "last_heartbeat_sent",
    }

    def __init__(  # pylint: disable=too-many-arguments;
        self,
        buffer: bytearray,
        inflator,
        sequence: int,
        session_id: str,
        identify,
        session: Session,
        lock: asyncio.Lock,
    ):
        self.buffer: bytearray = buffer  # type: ignore
        self.inflator = inflator
        self.identify = identify  # type: ignore
        self.seq: int = sequence  # type: ignore
        self.ses_id: str = session_id  # type: ignore
        self.ws_conn: aiohttp.ClientWebSocketResponse = None  # type: ignore
        self.ses = session
        self.lock = lock
        self.hbt_task: asyncio.Future = None  # type: ignore
        self.sid = self.identify.shard[0]

    async def connect(self):
        try:
            await self.open()
        except WSClosedError as wsc:
            if wsc.rmsg != "":
                self.ses.log.error(wsc.rmsg, __name__)

    async def open(self):

        self.ses.log.info(
            (
                f"Shard {self.sid} is attempting to connect"
                f" to discord gateway @ {self.ses._gateway.url}"  # pylint: disable=protected-access
            ),
            __name__,
        )
        self.ws_conn = await self.ses._client.ws_connect(  # pylint: disable=protected-access
            self.ses._gateway.url  # pylint: disable=protected-access
        )

        eve = await self._on_event()
        assert isinstance(eve, Event)

        hello: Hello = go_json.loads(eve.raw_data, Hello)

        self.ses.log.info(
            f"Shard {self.sid} is now sending Identify Payload", __name__
        )
        await self._send_payload(2, self.identify)

        eve = await self._on_event()
        assert isinstance(eve, Event)

        asyncio.create_task(
            self._heartbeat_task((hello.heartbeat_interval / 1000)),
            name=f"DiscPyth - Shard {self.sid} Heartbeat Task",
        )

        while True:
            try:
                await self._on_event()
            except WSClosedError as wsc:
                if wsc.rmsg != "":
                    self.ses.log.error(wsc.rmsg, __name__)
                else:
                    break

    async def _on_event(self) -> Optional[Event]:
        recv: aiohttp.WSMessage = await self.ws_conn.receive()

        if recv.type in (aiohttp.WSMsgType.BINARY, aiohttp.WSMsgType.TEXT):
            return await self._received_payload(recv.data)
        if recv.type in (
            aiohttp.WSMsgType.CLOSING,
            aiohttp.WSMsgType.CLOSE,
            aiohttp.WSMsgType.CLOSED,
        ):
            raise WSClosedError(recv.data, recv.extra)
        if recv.type is aiohttp.WSMsgType.ERROR:
            raise recv.data
        return None

    async def _received_payload(self, payload) -> Optional[Event]:
        # pylint: disable=too-many-return-statements
        if isinstance(payload, bytes):
            self.buffer.extend(payload)
            if len(payload) < 4 or payload[-4:] != ZLIB_SUFFIX:
                return None
            payload = self.inflator.decompress(self.buffer)
            self.buffer = bytearray()
            payload = payload.decode("utf-8")  # type: ignore

        payload: Event = go_json.loads(payload, Event)  # type: ignore
        self.seq = payload.seq

        self.ses.log.spam(
            "Event{ "
            + (
                f"operation: {payload.operation},"
                f" type: {payload.type},"
                f" seq: {payload.seq},"
                f" raw_data: {(payload.raw_data[:10] + '...' + payload.raw_data[-10:] if len(payload.raw_data) > 20 else payload.raw_data)}"
            )
            + " }",
            __name__,
        )

        if payload.operation == 0:
            self.ses.log.info(
                f"Shard {self.sid} gateway event - {payload.type}", __name__
            )
            await self.ses._handle(  # pylint: disable=protected-access
                payload.type, payload.raw_data
            )
            return payload

        if payload.operation == 1:
            await self._send_payload(1, self.seq)
            return payload

        if payload.operation == 7:
            await self.close(code=aiohttp.WSCloseCode.SERVICE_RESTART)
            await self.reconnect()
            return payload

        if payload.operation == 9:
            await self._send_payload(2, self.identify)
            return payload

        if payload.operation == 11:
            self.ses.log.info(
                f"Shard {self.sid} has received Heartbeat ACK", __name__
            )
            return payload

        return payload  # just in-case something goes brrrr

    async def _heartbeat_task(self, interval):
        while True:
            await self._send_payload(1, self.seq)
            await asyncio.sleep(interval)

    async def _send_payload(self, operation, data):
        async with self.lock:
            event = Event()
            event.operation = operation
            event.raw_data = data  # Not really "raw" data
            raw_payload = go_json.dumps(event)

            await self.ws_conn.send_str(raw_payload)

    async def close(self, code=aiohttp.WSCloseCode.OK):
        if self.hbt_task is not None:
            self.hbt_task.cancel()
            self.hbt_task = None

        if self.ws_conn is not None:
            await self.ws_conn.close(code=code)
            self.ws_conn = None

    async def reconnect(self):
        if self.ws_conn is not None:
            self.ses.log.warn(
                f"Shard {self.sid} is already open, no need to reopen!",
                __name__,
            )
        else:
            await self.open()


class WSSession(EventSession):
    async def _open_ws(self):

        for shard_id, shard in self._ws_conn.items():
            if shard.ws_conn is not None:
                self.log.warn(f"Shard {shard_id} already open!", __name__)
                continue

            asyncio.create_task(shard.connect())

    async def close_ws(self):
        if self._ws_conn is not None:
            for _, shard in self._ws_conn.items():
                await shard.close()
