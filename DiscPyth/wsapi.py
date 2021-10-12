import zlib
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


class WS_Session:
    def __init__(self, session: _Session) -> None:
        # This is already defined in Session
        # idk why I'm redefining it tho this doesn't 
        # cause any problems if you know any potential 
        # dangers of doing this then immediately 
        # create a pr!
        self.session: _Session = session

        self.buffer = bytearray()
        self.inflator = zlib.decompressobj()
        self.ZLIB_SUFFUIX = b'\x00\x00\xff\xff'

    async def _open(self):

        # This wont be triggered unless the user tries
        # to open the session again at that time we need to raise an
        # error if not then the user may use this multiple times (who knows)
        # and idk what will the side effects be
        if self.session.wsConn is not None:
            raise ErrWSAlreadyOpen(self.session.ShardID)

        if self.session.gateway == "":
            # TODO: Replace with a REST handler request to "/gateway"
            self.session.gateway == "wss://gateway.discord.gg/?v=9&encoding=json&compress=zlib-stream"

        self.session.wsConn = await self.session.Client.ws_connect("wss://gateway.discord.gg/?v=9&encoding=json")

        e = await self._on_event()
        
    async def _on_event(self) -> gateway.Event:
        recv = await self.session.wsConn.receive()
        msg = self._decode_message(recv.data)

        print(f"Received Payload from Discord\n\tOperation Code : {msg.operation}\n\tSequence : {msg.seq}\n\tEvent Type : {msg.type}\n\tRaw Data (d) : {msg.raw_data}")

    def _decode_message(self, msg) -> gateway.Event:

        e = gateway.Event()

        if type(msg) is bytes:
            self.buffer.extend(msg)

            # Afaik if its compressed and doesn't end with the
            # ZLIB suffix its invalid so we return none
            # and any action done with NoneType will raise an error
            if len(msg) < 4 or msg[-4:] != ZLIB_SUFFIX:
                return

            msg = inflator.decompress(buffer)
            buffer = bytearray()
            # Decode here since a str is already decoded 
            # maybe not but it just throws an error
            msg = msg.decode('utf-8')

        # returning here accounts for both
        # compressed and non-compressed
        # hence we dont have to do 2 returns    
        return gpj.loads(msg, e)

    def _create_payload(self, op, data):
        e = gateway.Event()
        e.operation = op
        e.raw_data = data

        return e

    async def _send_as_json(self, msg):

        await self.session.wsConn.send_str(gpj.dumps(msg))

    async def _close(self, code=None):

        if self.session.wsConn is not None:

            # default close is 1000 so we dont need to specify
            # that but we need to check if we have a code specified
            if code is not None:
                await self.session.wsConn.close(code)
            else:
                await self.session.wsConn.close()

        else:
            raise ErrWSNotFound()

    async def _reconnect(self):
        try:
            await self._open()
        except ErrWSAlreadyOpen:
            print("WebSocket already open, no need to reconnect!")