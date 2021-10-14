from . import _Session
from .types import gateway
from .ext import gopyjson as gpj
import zlib
from aiohttp import WSCloseCode, WSMsgType
import asyncio
import time
import sys


class ErrWSAlreadyOpen(Exception):
    def __init__(self, sid):
        self.sid = sid
        super().__init__(f"WebSocket already open for shard {sid}!")


class WSClosed(Exception):
    pass


class WSError(Exception):
    pass


class WS_Session(_Session):
    def __init__(self):
        self.ZLIB_SUFFIX = b"\x00\x00\xff\xff"
        self.buffer = bytearray()
        self.inflator = zlib.decompressobj()

    async def _open(self):
        if self.wsConn is not None:
            raise ErrWSAlreadyOpen(self.ShardID) from None

        if self.gateway == "":
            # TODO: replace with a REST request to /gateway
            self.gateway = (
                "wss://gateway.discord.gg/?v=9&encoding=json&compress=zlib-stream"
            )

        self.wsConn = await self.Client.ws_connect(self.gateway)

        e = await self._on_event()
        if e.operation != 10:
            raise WSError(f"Expected Operation Code 10 but received {e.operation}.")

        h = gpj.loads(e.raw_data, gateway.Hello())
        self.LastHeartbeatAck = time.time()

        if self.sessionID == "" and self.sequence is None:
            await self.wsConn.send_str(self._create_payload(2, self._identify))

        e = await self._on_event()

        self.heartbeat = self._loop.create_task(self._heartbeat((h.heartbeat)/1000))
        self.listening = self._loop.create_task(self._listening())

    async def _on_event(self):
        msg = await self.wsConn.receive()
        if msg.type in (WSMsgType.BINARY, WSMsgType.TEXT):
            msg = self._decompress_message(msg.data)
            self.sequence = msg.seq
            print(
                f"""Received Payload from Discord
\tOperation Code : {msg.operation},
\tSequence : {msg.seq},
\tEvent : {msg.type},
\tRaw Data : {msg.raw_data},"""
            )
            if msg.operation == 1:
                print("Gateway requested for a heartbeat sending one...")
                await self.wsConn.send_str(self._create_payload(1, self.sequence))
                return msg
            if msg.operation == 7:
                print("Reconnecting...")
                await self._close(code=WSCloseCode.SERVICE_RESTART)
                await self._reconnect()
                return msg
            if msg.operation == 9:
                print("Invalid Session, checking if Resumeable else Identifying...")
                # "The inner d key is a boolean that indicates
                # whether the session may be resumable. See Connecting
                # and Resuming for more information."
                # https://discord.com/developers/docs/topics/gateway#invalid-session
                if msg.raw_data == "false":
                    await self.wsConn.send_str(self._create_payload(2, self._identify))
                else:
                    await self.wsConn.send_str(self._create_payload(6, self._resume))
                return msg
            if msg.operation == 10:
                # Handled by _open()
                return msg
            if msg.operation == 11:
                print("Heartbeat Ack received!")
                self.LastHeartbeatAck = time.time()
                return msg
            if msg.operation != 0:
                print(f"Received unknown Operation Code {msg.operation}")
                return msg
        if msg.type in (WSMsgType.CLOSED, WSMsgType.CLOSING, WSMsgType.CLOSE):
            raise WSClosed()

        return

    def _decompress_message(self, msg) -> gateway.Event:
        if type(msg) is bytes:
            self.buffer.extend(msg)
            if len(msg) < 4 or msg[-4:] != self.ZLIB_SUFFIX:
                return
            msg = self.inflator.decompress(self.buffer)
            msg = msg.decode("utf-8")
            self.buffer = bytearray()
        msg = gpj.loads(msg, gateway.Event())
        return msg

    def update_status_complex():
        status = {}

    @property
    def _identify(self):
        identify = gateway.Identify()
        identify.token = self.Token
        identify.compress = True
        identify.large = 250
        identify.shard = [self.ShardID, self.ShardCount]
        identify.intents = 513
        properties = gateway.IdentifyProperties()
        properties.os = sys.platform
        properties.browser = "DiscPyth"
        properties.device = "DiscPyth"
        identify.properties = properties
        return identify

    @property
    def _resume(self):
        resume = gateway.Resume()
        resume.seq = self.sequence
        resume.ses_id = self.sessionID
        resume.token = self.Token
        return resume

    async def _heartbeat(self, delay):
        while True:
            await self.wsConn.send_str(self._create_payload(1, self.sequence))
            await asyncio.sleep(delay)

    async def _listening(self):
        while True:
            try:
                await self._on_event()
            except WSClosed:
                raise

    def _create_payload(self, op, data):
        e = gateway.Event()
        e.operation = op
        e.raw_data = data
        return gpj.dumps(e)

    async def _close(self, code=None):
        if self.opened is not None:
            self.opened.cancel()
            self.opened = None
        if self.listening is not None:
            self.listening.cancel()
            self.listening = None
        if self.heartbeat is not None:
            self.heartbeat.cancel()
        if self.wsConn is not None:
            if code is not None:
                await self.wsConn.close(code=code)
            else:
                await self.wsConn.close()
            self.wsConn = None

    async def _reconnect(self):
        try:
            await self._open()
        except ErrWSAlreadyOpen as e:
            print(f"WebSocket already open for shard id {e.sid} no need to reopen!")
