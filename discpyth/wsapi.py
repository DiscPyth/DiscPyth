import asyncio
import time
from typing import Optional

import aiohttp
import go_json as gj # type: ignore

from . import _Session
from .structs import Event, Hello
from .utils import new_error

__all__ = ("WsSession",)

ZLIB_SUFFIX = b"\x00\x00\xff\xff"


ErrWSAlreadyOpen = new_error("ErrWSAlreadyOpen", "WebSocket already open!")
ErrWSNotFound = new_error("ErrWSNotFound", "WebSocket not yet opened!")
# For handling the while loop
ErrWSClosed = new_error("ErrWSClosed", "WebSocket is closed!")
# Dynamic errors
ErrWS = new_error("ErrWS")

class Resume(gj.Struct):
    token = gj.field("token")
    session_id = gj.field("session_id")
    sequence = gj.field("seq")


class WsSession(_Session):  # pylint: disable=too-many-instance-attributes;
    async def _open(self) -> None:
        if self.client is None:

            self.client = aiohttp.ClientSession()
        if self._ws_conn is not None:
            raise ErrWSAlreadyOpen
        if self._gateway == "":
            # TODO: Implement a way to get the gateway from the API
            self._gateway = "wss://gateway.discord.gg/?v=9&encoding=json"
        self._ws_conn = await self.client.ws_connect(self._gateway)
        e = await self._on_event()  # pylint: disable=invalid-name

        if e.operation != 10:
            raise ErrWS(
                f"Shard {self.identify.shard[0]} expected Operation Code 10, instead got {e.operation}"
            )

        self._log(
            20,
            f"Shard {self.identify.shard[0]} has received Hello Payload!",
        )

        h = gj.loads(e.raw_data, Hello)  # pylint: disable=invalid-name
        self.last_heartbeat_ack = time.time()

        if self._session_id == "" and self._sequence is None:
            await self._send_payload(2, self.identify)
        else:
            resm = Resume(
                token=self._token,
                session_id=self._session_id,
                seq=self._sequence,
            )
            await self._send_payload(6, resm)

        e = await self._on_event()  # pylint: disable=invalid-name

        if e.type not in ("READY", "RESUMED"):
            self._log(
                30,
                f'Shard {self.identify.shard[0]} expected "READY" or "RESUMED" event instead got "{e.type}"',
            )
        else:
            self._log(20, f'Shard {self.identify.shard[0]} has received "{e.type}"')

        self._log(20, f"Heartbeat Interval is {h.heartbeat_interval} milliseconds")

        self._heartbeat = self._loop.create_task(
            self._t_heartbeat((h.heartbeat_interval / 1000))
        )

        while True:
            try:
                await self._on_event()
            except ErrWSClosed:
                break

    async def _on_event(self) -> Event:
        r = await self._ws_conn.receive()  # pylint: disable=invalid-name
        if r.type in (aiohttp.WSMsgType.BINARY, aiohttp.WSMsgType.TEXT):
            msg = gj.loads(r.data, Event)
            self._log(
                10,
                f"Operation : {msg.operation}, Sequence : {msg.sequence}, Type : {msg.type}, Data : {msg.raw_data if msg.raw_data == 'null' or len(msg.raw_data) <= 20 else (msg.raw_data if not self._trim_logs else msg.raw_data[:10]+'...(Showing first and last 10 chars)...'+msg.raw_data[-10:]) }",
            )
            if msg.operation == 1:
                self._log(
                    20,
                    f"Shard {self.identify.shard[0]} received Operation Code 1 responding with a heartbeat...",
                )
                await self._send_payload(1, self._sequence)
                return msg
            if msg.operation == 7:
                self._log(
                    20,
                    f"Shard {self.identify.shard[0]} is reopening connection in response to Operation Code 7",
                )
                await self._close_w_code(aiohttp.WSCloseCode.SERVICE_RESTART)
                await self._reconnect()
            if msg.operation == 9:
                if msg.raw_data == "true":
                    self._log(
                        20,
                        f"Session for Shard {self.identify.shard[0]} has been invalidated, but is resumeable, resuming....",
                    )
                    resm = Resume(
                        token=self._token,
                        session_id=self._session_id,
                        seq=self._sequence,
                    )
                    await self._send_payload(6, resm)
                else:
                    self._log(
                        20,
                        f"Session for Shard {self.identify.shard[0]} has been invalidated, amd is not resumeable, identifying....",
                    )
                    await self._send_payload(2, self.identify)
            if msg.operation == 10:
                return msg
            if msg.operation == 11:
                self._log(
                    20,
                    f"Shard {self.identify.shard[0]} has received Heartbeat Acknowledgement!",
                )
                self.last_heartbeat_ack = time.time()
                self._log(20, f"Heartbeat latency is {self.heartbeat_latency}.")
                return msg
            if msg.operation != 0:
                self._log(
                    20,
                    f"Shard {self.identify.shard[0]} has received an unknown Operation Code {msg.operation}",
                )
                return msg

            self._log(
                20,
                f'Shard {self.identify.shard[0]} Gateway event - "{msg.type}"',
            )
            return msg

        if r.type in (
            aiohttp.WSMsgType.CLOSED,
            aiohttp.WSMsgType.CLOSING,
            aiohttp.WSMsgType.CLOSE,
        ):
            raise ErrWSClosed
        if r.type is aiohttp.WSMsgType.ERROR:
            raise r.data

    def _decode_payload(self, payload) -> Optional[Event]:
        if isinstance(payload, bytes):
            self._buffer.extend(payload)  # type: ignore
            if len(payload) < 4 or payload[-4:] != b"\x00\x00\xff\xff":
                return None

            payload = self._inflator.decompress(self._buffer)  # type: ignore
            payload = payload.decompress("utf-8")
            self._buffer = bytearray()

        return gj.loads(payload, Event)

    async def _send_payload(self, op, data) -> None:  # pylint: disable=invalid-name;
        e = Event()  # pylint: disable=invalid-name
        e.operation = op
        e.raw_data = data
        raw_payload = gj.dumps(e)
        await self._ws_conn.send_str(raw_payload)

    async def _t_heartbeat(self, delay) -> None:
        while True:
            last = self.last_heartbeat_ack
            self.last_heartbeat_sent = time.time()
            await self._send_payload(1, self._sequence)
            if (time.time() - last) > (delay * 5):
                self._log(
                    40,
                    f"Haven't received a Heartbeat Acknowledgement in {time.time()-last}, reconnecting...",
                )
                await self._close_w_code()
                await self._reconnect()
            await asyncio.sleep(delay)

    @property
    def heartbeat_latency(self) -> float:
        return self.last_heartbeat_ack - self.last_heartbeat_sent

    async def _close_w_code(self, code=None) -> None:

        if self._heartbeat is not None:
            self._heartbeat.cancel()

        if self._open_task is not None:
            self._open_task.cancel()

        if self._ws_conn is not None:
            if code is not None:
                await self._ws_conn.close(code=code)
            else:
                await self._ws_conn.close()

    async def _reconnect(self) -> None:
        async def _wrapped_open():
            await self._open()
        try:
            self._open_task = self._loop.create_task(_wrapped_open())
            await self._open_task
        except ErrWSAlreadyOpen:
            self._log(
                30,
                f"Shard {self.identify.shard[0]} already open, no need to reconnect!",
            )
            return
