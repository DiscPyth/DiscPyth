import asyncio
import sys
import time
import zlib
from typing import Literal

import aiohttp

from . import _Session
from .ext import gopyjson as gpj
from .structs import Event, Hello

__all__ = ("WS_Session",)

ZLIB_SUFFIX = b"\x00\x00\xff\xff"

# Monkey Patched exception creator 😋
def new_error(name: str, output=None) -> Exception:
    # Class Cell so super() doesnt throw an error,
    # could have just done Exception.__init__
    # but whatever 🙄
    # https://stackoverflow.com/questions/43778914/python3-using-super-in-eq-methods-raises-runtimeerror-super-class/43779009#43779009
    __class__ = Exception

    def replacedinit(self):
        super().__init__(output)

    # Quick way to create a class
    err = type(str(name), (Exception,), dict())
    if output is not None:
        # Replace __init__ if output is defined,
        # better than new_error("Error")("Output")
        # instead new_error("Error", "Output")
        setattr(err, "__init__", replacedinit)
    return err


ErrWSAlreadyOpen = new_error("ErrWSAlreadyOpen", "WebSocket already open!")
ErrWSNotFound = new_error("ErrWSNotFound", "WebSocket not yet opened!")
# For handling the while loop
ErrWSClosed = new_error("ErrWSClosed", "WebSocket is closed!")
# Dynamic errors
ErrWS = new_error("ErrWS")


class WS_Session(_Session):
    async def _open(self):
        if self.client is None:

            self.client = aiohttp.ClientSession()
        if self._ws_conn is not None:
            raise ErrWSAlreadyOpen
        if self._gateway == "":
            self._gateway = "wss://gateway.discord.gg/?v=8&encoding=json"
        self._ws_conn = await self.client.ws_connect(self._gateway)
        e = await self._on_event()

        if e.operation != 10:
            raise ErrWS(
                f"Shard {self.identify.shard[0]} expected Operation Code 10, instead got {e.operation}"
            )
        else:
            self._log(20, f"Shard {self.identify.shard[0]} has received Hello Payload!")

        h = gpj.loads(e.raw_data, Hello())
        self.last_heartbeat_ack = time.time()

        if self._session_id == "" and self._sequence is None:
            await self._send_payload(2, self.identify)
        # else:
        # await self._send_payload(6, self._resume)

        e = await self._on_event()

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
                pass
                break

    async def _on_event(self):
        r = await self._ws_conn.receive()
        if r.type in (aiohttp.WSMsgType.BINARY, aiohttp.WSMsgType.TEXT):
            msg = gpj.loads(r.data, Event())
            self._log(
                10,
                f"Operation : {msg.operation}, Sequence : {msg.sequence}, Type : {msg.type}, Data : {msg.raw_data}",
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
                    # await self._send_payload(6, self._resume)
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
                self.LastHeartbeatAck = time.time()
                self._log(20, f"Heartbeat latency is {self.heartbeat_latency}.")
                return msg
            if msg.operation != 0:
                self._log(
                    20,
                    f"Shard {self.identify.shard[0]} has received an unknown Operation Code {msg.operation}",
                )
                return msg

            self._log(
                20, f'Shard {self.identify.shard[0]} Gateway event - "{msg.type}"'
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

    def _decode_payload(self, payload):
        if type(payload) is bytes:
            self._buffer.extend(payload)
            if len(payload) < 4 or payload[-4:] != b"\x00\x00\xff\xff":
                return

            payload = self._inflator.decompress(self._buffer)
            payload = payload.decompress("utf-8")
            self._buffer = bytearray()

        return gpj.loads(payload, Event())

    async def _send_payload(self, op, data):
        e = Event()
        e.operation = op
        e.raw_data = data
        raw_payload = gpj.dumps(e)
        await self._ws_conn.send_str(raw_payload)

    async def _t_heartbeat(self, delay):
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
    def heartbeat_latency(self):
        return self.last_heartbeat_ack - self.last_heartbeat_sent

    async def _close_w_code(self, code=None):

        if self._heartbeat is not None:
            self._heartbeat.cancel()

        if self._ws_conn is not None:
            if code is not None:
                await self._ws_conn.close(code=code)
            else:
                await self._ws_conn.close()

    async def _reconnect(self):
        try:
            self._opened = self._loop.run_until_complete(self._open())
        except ErrWSAlreadyOpen:
            self._log(
                30,
                f"Shard {self.identify.shard[0]} already open, no need to reconnect!",
            )
            pass
