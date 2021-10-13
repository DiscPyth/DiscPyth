import zlib
from aiohttp import WSCloseCode
import sys
import time
from . import _Session
from .types import gateway
from .ext import gopyjson as gpj


class ErrWSAlreadyOpen(Exception):
    """Raised when a user tries to open an already opened WebSocket connection for a particular Session."""

    def __init__(self, sid) -> None:
        super().__init__(
            f"WebSocket connection already open for shard {sid} no need to reopen"
        )


class ErrWSNotFound(Exception):
    """Raised when a user performs a WebSocket action but the WebSocket is not yet opened."""

    def __init__(self) -> None:
        super().__init__("WebSocket connection connection not found")


class WS_Session(_Session):
    async def _open(self):

        # This wont be triggered unless the user tries
        # to open the session again at that time we need to raise an
        # error if not then the user may use this multiple times (who knows)
        # and idk what will the side effects be
        if self.wsConn is not None:
            raise ErrWSAlreadyOpen(self.session.ShardID)

        if self.gateway == "":
            # TODO: Replace with a REST handler request to "/gateway"
            self.gateway = (
                "wss://gateway.discord.gg/?v=9&encoding=json&compress=zlib-stream"
            )

        self.wsConn = await self.Client.ws_connect(self.gateway)

        e = await self._on_event()

    async def _on_event(self) -> gateway.Event:
        recv = await self.wsConn.receive()
        msg = self._decode_message(recv.data)

        print(
            f"Received Payload from Discord\n\tOperation Code : {msg.operation}\n\tSequence : {msg.seq}\n\tEvent Type : {msg.type}\n\tRaw Data (d) : {msg.raw_data}"
        )

        # "The gateway may request a heartbeat from the
        # client in some situations by sending an
        # Opcode 1 Heartbeat. When this occurs, the
        # client should immediately send an Opcode 1 Heartbeat
        # without waiting the remainder of the current interval."
        # https://discord.com/developers/docs/topics/gateway#heartbeating
        if msg.operation == 1:
            await self._send_as_json(self._create_payload(1, self.session.sequence))

            return msg

        # "The reconnect event is dispatched when a client
        # should reconnect to the gateway (and resume their
        # existing session, if they have one). This event usually
        # occurs during deploys to migrate sessions gracefully
        # off old hosts."
        # https://discord.com/developers/docs/topics/gateway#resuming
        if msg.operation == 7:
            await self._close(code=WSCloseCode.SERVICE_RESTART)
            await self._reconnect()

            return msg

        if msg.operation == 9:
            # "The inner d key is a boolean that indicates
            # whether the session may be resumable. See
            # Connecting and Resuming for more information."
            # https://discord.com/developers/docs/topics/gateway#invalid-session
            if msg.raw_data == "true":
                self._identify()
            else:
                # TODO: replace with resume
                self._identify()

            return msg

        if msg.operation == 10:
            # Handled by open()
            return msg

        if msg.operation == 11:

            self.LastHeartbeatAck = time.time()

    def _decode_message(self, msg) -> gateway.Event:

        buffer = bytearray()
        inflator = zlib.decompressobj()

        e = gateway.Event()

        if type(msg) is bytes:
            buffer.extend(msg)

            # Afaik if its compressed and doesn't end with the
            # ZLIB suffix its invalid so we return none
            # and any action done with NoneType will raise an error
            if len(msg) < 4 or msg[-4:] != b"\x00\x00\xff\xff":
                return

            rmsg = inflator.decompress(buffer)
            buffer = bytearray()
            # Decode here since a str is already decoded
            # maybe not but it just throws an error
            # (Turns out this is actually bystes so we decode this
            # but we cannot decode str, silly me)
            rmsg = rmsg.decode("utf-8")

        # returning here accounts for both
        # compressed and non-compressed
        # hence we dont have to do 2 returns
        return gpj.loads(rmsg, e)

    async def _identify(self):
        ident = gateway.Identify()
        ident.token = self.session.Token
        ident.compress = True
        ident.large = 250
        ident.shard = [self.ShardID, self.ShardCount]
        ident.properties = gateway.IdentifyProperties()
        ident.properties.os = sys.platform
        ident.properties.browser = "DiscPyth"
        ident.properties.device = "DiscPyth"

        await self._send_as_json(self._create_payload(2, ident))

    def _create_payload(self, op, data):
        e = gateway.Event()
        e.operation = op
        e.raw_data = data

        return e

    async def _send_as_json(self, msg):
        await self.session.wsConn.send_str(gpj.dumps(msg))

    async def _close(self, code=None):

        if self.wsConn is not None:

            # default close is 1000 so we dont need to specify
            # that but we need to check if we have a code specified
            if code is not None:
                await self.wsConn.close(code)
            else:
                await self.wsConn.close()

        else:
            raise ErrWSNotFound() from None

    async def _reconnect(self):
        try:
            await self._open()
        except ErrWSAlreadyOpen:
            print("WebSocket already open, no need to reconnect!")
