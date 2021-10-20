import asyncio
import sys
import time
import zlib

import aiohttp

from . import _Session
from .ext import gopyjson as gpj
from .structs import (EVENT, HELLO, IDENTIFY, IDENTIFY_PROPERTIES, RESUME,
                      new_type)

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
        if self.Client is None:

            self.Client = aiohttp.ClientSession()
        if self._wsConn is not None:
            raise ErrWSAlreadyOpen
        if self._gateway == "":
            self._gateway = "wss://gateway.discord.gg/?v=9&encoding=json"
        self._wsConn = await self.Client.ws_connect(self._gateway)
        e = await self._on_event()

        if e.Operation != 10:
            raise ErrWS(
                f"Shard {self.Identify.Shard[0]} expected Operation Code 10, instead got {e.Operation}"
            )
        else:
            self._log(20, f"Shard {self.Identify.Shard[0]} has received Hello Payload!")

        h = gpj.loads(e.RawData, HELLO())
        self.LastHeartbeatAck = time.time()

        if self._sessionID == "" and self._sequence is None:
            await self._send_payload(2, self.Identify)
        else:
            await self._send_payload(6, self._resume)

        e = await self._on_event()

        if e.Type not in ("READY", "RESUMED"):
            self._log(
                30,
                f'Shard {self.Identify.Shard[0]} expected "READY" or "RESUMED" event instead got "{e.Type}"',
            )
        else:
            self._log(20, f'Shard {self.Identify.Shard[0]} has received "{e.Type}"')

        self._log(20, f"Heartbeat Interval is {h.HeartbeatInterval} milliseconds")

        self._heartbeat = self._loop.create_task(
            self._t_heartbeat((h.HeartbeatInterval / 1000))
        )

        while True:
            try:
                await self._on_event()
            except ErrWSClosed:
                pass
                break

    async def _on_event(self):
        r = await self._wsConn.receive()
        if r.type in (aiohttp.WSMsgType.BINARY, aiohttp.WSMsgType.TEXT):
            msg = gpj.loads(r.data, EVENT())
            self._log(
                10,
                f"Operation : {msg.Operation}, Sequence : {msg.Sequence}, Type : {msg.Type}, Data : {msg.RawData}",
            )
            if msg.Operation == 1:
                self._log(
                    20,
                    f"Shard {self.Identify.Shard[0]} received Operation Code 1 responding with a heartbeat...",
                )
                await self._send_payload(1, self._sequence)
                return msg
            if msg.Operation == 7:
                self._log(
                    20,
                    f"Shard {self.Identify.Shard[0]} is reopening connection in response to Operation Code 7",
                )
                await self._close_w_code(aiohttp.WSCloseCode.SERVICE_RESTART)
                await self._reconnect()
            if msg.Operation == 9:
                if msg.RawData == "true":
                    self._log(
                        20,
                        f"Session for Shard {self.Identify.Shard[0]} has been invalidated, but is resumeable, resuming....",
                    )
                    await self._send_payload(6, self._resume)
                else:
                    self._log(
                        20,
                        f"Session for Shard {self.Identify.Shard[0]} has been invalidated, amd is not resumeable, identifying....",
                    )
                    await self._send_payload(2, self.Identify)
            if msg.Operation == 10:
                return msg
            if msg.Operation == 11:
                self._log(
                    20,
                    f"Shard {self.Identify.Shard[0]} has received Heartbeat Acknowledgement!",
                )
                self.LastHeartbeatAck = time.time()
                self._log(20, f"Heartbeat latency is {self.heartbeat_latency}.")
                return msg
            if msg.Operation == 0:
                self._log(
                    20, f'Shard {self.Identify.Shard[0]} Gateway event - "{msg.Type}"'
                )
                return msg
            else:
                self._log(
                    20,
                    f"Shard {self.Identify.Shard[0]} has received an unknown Operation Code {msg.Operation}",
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

        return gpj.loads(payload, EVENT())

    async def _send_payload(self, op, data):
        e = EVENT()
        e.Operation = op
        e.RawData = data
        raw_payload = gpj.dumps(e)
        await self._wsConn.send_str(raw_payload)

    async def _t_heartbeat(self, delay):
        while True:
            last = self.LastHeartbeatAck
            self.LastHeartbeatSent = time.time()
            await self._send_payload(1, self._sequence)
            if (time.time()-last) > (delay*5):
                self._log(40, f"Haven't received a Heartbeat Acknowledgement in {time.time()-last}, reconnecting...")
                await self._close_w_code()
                await self._reconnect()
            await asyncio.sleep(delay)

    @property
    def heartbeat_latency(self):
        return self.LastHeartbeatAck-self.LastHeartbeatSent

    @property
    def _resume(self):
        r = RESUME()
        r.Token = self.Identify.Token
        r.SessionID = self._sessionID
        r.Sequence = self._sequence
        return r

    async def _close_w_code(self, code=None):

        if self._heartbeat is not None:
            self._heartbeat.cancel()

        if self._wsConn is not None:
            if code is not None:
                await self._wsConn.close(code=code)
            else:
                await self._wsConn.close()

    async def _reconnect(self):
        try:
            self._opened = self._loop.create_task(self._open())
        except ErrWSAlreadyOpen:
            self._log(
                30,
                f"Shard {self.Identify.Shard[0]} already open, no need to reconnect!",
            )
            pass
