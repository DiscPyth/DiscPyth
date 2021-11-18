__all__ = ("Shard", "ShardManager")

import aiohttp
import go_json

from .endpoints import Endpoints
from .structs import Event

ZLIB_SUFFIX = b"\x00\x00\xff\xff"


class Shard:
    # pylint: disable=no-member
    async def _open_ws(self, sid):

        if self._gateway == "":
            getg = await self.get_gateway()
            self._gateway = getg.url

        if self._ws_conn.get(sid) is not None:
            self._log.warn("Shard {sid} is already open")
            return

        self._ws_conn[
            sid
        ]: aiohtttp.ClientWebSocketResponse = await self._client.ws_connect(
            self._gateway
        )

        while True:
            await self._on_event(sid)

    async def _on_event(self, sid):
        recv: aiohttp.WSMessage = await self._ws_conn[sid].receive()

        if recv.type in (aiohttp.WSMsgType.BINARY, aiohttp.WSMsgType.TEXT):
            await self._msg_received(recv.data, sid)
        if recv.type in (
            aiohttp.WSMsgType.CLOSING,
            aiohttp.WSMsgType.CLOSE,
            aiohttp.WSMsgType.CLOSED,
        ):
            self._log.error(
                f"{recv.data}{' - '+recv.extra if recv.extra != '' else ''}"
            )
        if recv.type is aiohttp.WSMsgType.ERROR:
            raise recv.data

    async def _msg_received(self, msg, sid):
        if isinstance(msg, bytes):
            self._buffer[sid].extend(msg)
            if len(msg) < 4 or msg[-4:] != ZLIB_SUFFIX:
                return
            msg = self._inflator[sid].decompress(self._buffer[sid])
            self._buffer[sid] = bytearray()
            msg = msg.decode("utf-8")

        msg = go_json.loads(msg, Event)


class ShardManager:
    pass
