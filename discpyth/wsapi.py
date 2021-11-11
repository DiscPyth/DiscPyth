import asyncio
import time

import aiohttp
import go_json as gj  # type: ignore

from . import _Session  # pylint: disable=cyclic-import
from .structs import Activity, Event, Hello
from .utils import new_error

__all__ = ("WsSession",)

ZLIB_SUFFIX = b"\x00\x00\xff\xff"


ErrWSAlreadyOpen: Exception = new_error("ErrWSAlreadyOpen", "WebSocket already open!")
ErrWSNotFound: Exception = new_error("ErrWSNotFound", "WebSocket not yet opened!")
# For handling the while loop
ErrWSClosed: Exception = new_error("ErrWSClosed")
# Dynamic errors
ErrWS: Exception = new_error("ErrWS")


class Resume(gj.Struct):
    token = gj.field("token")
    session_id = gj.field("session_id")
    sequence = gj.field("seq")


class UpdateStatusData(gj.Struct):
    __partial = True  # pylint: disable=unused-private-member
    idle_since: int = gj.field("since")
    activities: list = gj.field("activities")
    afk: bool = gj.field("afk")
    status: str = gj.field("status")


class WsSession(_Session):  # pylint: disable=too-many-instance-attributes;
    async def _open(self) -> None:
        if self.client is None:

            self.client: aiohttp.ClientSession = aiohttp.ClientSession()
        if self._ws_conn is not None:
            raise ErrWSAlreadyOpen
        if self._gateway == "":
            # TODO: Implement a way to get the gateway from the API # pylint: disable=fixme
            self._gateway: str = (
                "wss://gateway.discord.gg/?v=9&encoding=json&compress=zlib-stream"
            )
        self._ws_conn: aiohttp.ClientWebSocketResponse = await self.client.ws_connect(
            self._gateway
        )
        e = await self._on_event()  # pylint: disable=invalid-name

        if e.operation != 10:
            raise ErrWS(  # type: ignore
                f"Shard {self.identify.shard[0]} expected Operation Code 10, instead got {e.operation}"
            )

        self._log(  # type: ignore
            20,
            f"Shard {self.identify.shard[0]} has received Hello Payload!",
        )

        h = gj.loads(e.raw_data, Hello)  # pylint: disable=invalid-name
        self.last_heartbeat_ack = time.time()

        if self._session_id == "" and self._sequence is None:
            await self._send_payload(2, self.identify)
        else:
            resm = Resume(
                token=self.identify.token,
                session_id=self._session_id,
                seq=self._sequence,
            )
            await self._send_payload(6, resm)

        e = await self._on_event()  # pylint: disable=invalid-name

        if e.type not in ("READY", "RESUMED"):
            self._log(  # type: ignore
                30,
                f'Shard {self.identify.shard[0]} expected "READY" or "RESUMED" event instead got "{e.type}"',
            )
        else:
            self._log(20, f'Shard {self.identify.shard[0]} has received "{e.type}"')  # type: ignore

        self._log(20, f"Heartbeat Interval is {h.heartbeat_interval} milliseconds")  # type: ignore

        self._heartbeat = self._loop.create_task(
            self._t_heartbeat((h.heartbeat_interval / 1000))
        )

        while True:
            try:
                await self._on_event()
            except ErrWSClosed as wsc:  # type: ignore
                if wsc.msg != "":  # pylint: disable=no-else-raise,no-member
                    raise
                else:
                    break

    async def _on_event(self) -> Event:
        r = await self._ws_conn.receive()  # pylint: disable=invalid-name
        if r.type in (aiohttp.WSMsgType.BINARY, aiohttp.WSMsgType.TEXT):
            msg = self._decode_payload(r.data)
            self._log(  # type: ignore
                10,
                f"Operation : {msg.operation}, Sequence : {msg.sequence}, Type : {msg.type}, Data : {msg.raw_data if msg.raw_data == 'null' or len(msg.raw_data) <= 20 else (msg.raw_data if not self._trim_logs else msg.raw_data[:10]+'...(Showing first and last 10 chars)...'+msg.raw_data[-10:]) }",
            )
            if msg.operation == 1:
                self._log(  # type: ignore
                    20,
                    f"Shard {self.identify.shard[0]} received Operation Code 1 responding with a heartbeat...",
                )
                await self._send_payload(1, self._sequence)
                return msg
            if msg.operation == 7:
                self._log(  # type: ignore
                    20,
                    f"Shard {self.identify.shard[0]} is reopening connection in response to Operation Code 7",
                )
                await self._close_w_code(aiohttp.WSCloseCode.SERVICE_RESTART)
                await self._reconnect()
            if msg.operation == 9:
                if msg.raw_data == "true":
                    self._log(  # type: ignore
                        20,
                        f"Session for Shard {self.identify.shard[0]} has been invalidated, but is resumeable, resuming....",
                    )
                    resm = Resume(
                        token=self.identify.token,
                        session_id=self._session_id,
                        seq=self._sequence,
                    )
                    await self._send_payload(6, resm)
                else:
                    self._log(  # type: ignore
                        20,
                        f"Session for Shard {self.identify.shard[0]} has been invalidated, amd is not resumeable, identifying....",
                    )
                    await self._send_payload(2, self.identify)
            if msg.operation == 10:
                return msg
            if msg.operation == 11:
                self._log(  # type: ignore
                    20,
                    f"Shard {self.identify.shard[0]} has received Heartbeat Acknowledgement!",
                )
                self.last_heartbeat_ack: float = time.time()  # type: ignore
                self._log(10, f"Heartbeat latency is {self.heartbeat_latency}.")  # type: ignore
                return msg
            if msg.operation != 0:
                self._log(  # type: ignore
                    20,
                    f"Shard {self.identify.shard[0]} has received an unknown Operation Code {msg.operation}",
                )
                return msg

            self._log(  # type: ignore
                20,
                f'Shard {self.identify.shard[0]} Gateway event - "{msg.type}"',
            )
            await self._handle(msg.type, msg.raw_data)  # type: ignore # pylint: disable=no-member
            return msg

        if r.type in (
            aiohttp.WSMsgType.CLOSED,
            aiohttp.WSMsgType.CLOSING,
            aiohttp.WSMsgType.CLOSE,
        ):
            raise ErrWSClosed(f"{r.data}{' - '+r.extra if r.extra != '' else ''}")  # type: ignore
        if r.type is aiohttp.WSMsgType.ERROR:
            raise r.data

        return None  # type: ignore

    def _decode_payload(self, payload) -> Event:
        if isinstance(payload, bytes):
            self._buffer.extend(payload)  # type: ignore
            if len(payload) < 4 or payload[-4:] != b"\x00\x00\xff\xff":
                return None  # type: ignore

            payload = self._inflator.decompress(self._buffer)  # type: ignore
            payload = payload.decode("utf-8")
            self._buffer = bytearray()

        return gj.loads(payload, Event)

    async def _send_payload(self, op, data) -> None:  # pylint: disable=invalid-name;
        async with self._ws_lock:  # pylint: disable=not-async-context-manager
            e = Event()  # pylint: disable=invalid-name
            e.operation = op
            e.raw_data = data
            raw_payload = gj.dumps(e)
            await self._ws_conn.send_str(raw_payload)

    async def _t_heartbeat(self, delay) -> None:
        while True:
            last: float = self.last_heartbeat_ack  # type: ignore
            self.last_heartbeat_sent: float = time.time()
            await self._send_payload(1, self._sequence)
            if (time.time() - last) > (delay * 5):
                self._log(  # type: ignore
                    30,
                    f"Haven't received a Heartbeat Acknowledgement in {time.time()-last}, reconnecting...",
                )
                await self._close_w_code()
                await self._reconnect()
            await asyncio.sleep(delay)

    @property
    def heartbeat_latency(self) -> float:
        return self.last_heartbeat_ack - self.last_heartbeat_sent  # type: ignore

    def new_update_status_data(  # pylint: disable=too-many-arguments,no-self-use;
        self, status: str, idle: int, activity_type, name: str, url: str
    ):
        if status not in ("online", "dnd", "idle", "invisible"):
            status = "online"
        if name != "":
            act = [Activity(name=name, type=activity_type, url=url)]
        return UpdateStatusData(sinc=idle, status=status, afk=False, activities=act)

    async def update_status_comple(self, usd):
        await self._send_payload(3, usd)

    async def _close_w_code(self, code=None) -> None:

        if self._heartbeat is not None:  # type: ignore
            self._heartbeat.cancel()  # type: ignore

        if self._open_task is not None:
            self._open_task.cancel()

        if self._ws_conn is not None:
            if code is not None:
                await self._ws_conn.close(code=code)
            else:
                await self._ws_conn.close()
            self._ws_conn = None  # type: ignore

    async def _reconnect(self) -> None:
        async def _wrapped_open():
            await self._open()

        try:
            self._open_task = self._loop.create_task(_wrapped_open())
            await self._open_task
        except ErrWSAlreadyOpen:  # type: ignore
            self._log(  # type: ignore
                30,
                f"Shard {self.identify.shard[0]} already open, no need to reconnect!",
            )
            return
