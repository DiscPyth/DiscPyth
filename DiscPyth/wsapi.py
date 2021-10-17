import zlib
import time
import asyncio
import aiohttp
import sys
from . import _Session
from .ext import gopyjson as gpj
from .types import EVENT, IDENTIFY, IDENTIFY_PROPERTIES

ZLIB_SUFFIX = b'\x00\x00\xff\xff'

# Monkey Patched exception creator 😋
def new_error(name:str, output=None) -> Exception:
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

class WS_Session(_Session):
    def __init__(self):
        self._buffer = bytearray()
        self._inflator = zlib.decompressobj()
    async def _open(self):
        if self.Client is None:
            self.Client = aiohttp.ClientSession()

        if self._wsConn is not None:
            raise ErrWSAlreadyOpen
        if self._gateway == "":
            self._gateway = "wss://gateway.discord.gg/?v=9&encoding=json"
        self._wsConn = await self.Client.ws_connect(self._gateway)
        await self._on_event()

        self._loop.create_task(self._t_listening())

    async def _on_event(self):
        ws_resp = await self._wsConn.receive()
        if ws_resp.type in (aiohttp.WSMsgType.BINARY, aiohttp.WSMsgType.TEXT):
            msg = self._decode_message(ws_resp.data)
            self._log(10, f"Received Payload from Discord\nOperation Code : {msg.Operation}, Sequence : {msg.Sequence}, Event Type : {msg.Type}, Raw Data : {msg.Raw_Data}")
            if msg.Operation == 1:
                await self._send_payload(1, self._sequence)
                return msg
            if msg.Operation == 7:
                await self._close_w_code(aiohttp.WSCloseCode.SERVICE_RESTART)
                await self._reconnect()
            if msg.Operation == 9:
                if msg.Raw_Data == "true":
                    pass
                else:
                    pass
            if msg.Operation == 10:
                return msg
            if msg.Operation == 11:
                self.LastHeartbeatAck = time.time()
                return msg
            if msg.Operation != 0:
                print(f"Recieved unknown Operation Code {msg.Operation}")
                return msg
        if ws_resp.type in (aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSE):
            raise ErrWSClosed
        if ws_resp.type in (aiohttp.WSMsgType.ERROR,):
            # "Actually not frame but a flag 
            # indicating that websocket was received an error."
            # https://docs.aiohttp.org/en/stable/websocket_utilities.html#aiohttp.WSMsgType.ERROR
            raise ws_resp.data

    def _decode_message(self, msg):
        if type(msg) is bytes:
            self._buffer.extend(msg)
            if len(msg) < 4 or msg[-4:] != ZLIB_SUFFIX:
                return
            msg = self._inflator.decompress(self._buffer)
            msg = msg.decode('utf-8')
            self._buffer = bytearray()

        return gpj.loads(msg, EVENT())

    async def _send_payload(self, op, data):
        e = EVENT
        e.Operation = op
        e.Raw_Data = data
        raw_payload = gpj.dumps(e)
        await self._wsConn.send_str(raw_payload)

    async def _t_listening(self):
        while True:
            await self._on_event()

    async def _t_heartbeat(self, delay):
        while True:
            await self._send_payload(1, self._sequence)
            await asyncio.sleep(delay)

    async def _close_w_code(self, code=None):
        if self._opened is not None:
            self._opened.cancel()

        if self._wsConn is not None:
            if code is not None:
                await self._wsConn.close(code=code)
            else:
                await self._wsConn.close()

    async def _reconnect(self):
        try:
            self._opened = self._loop.create_task(self._open())
        except ErrWSAlreadyOpen:
            pass