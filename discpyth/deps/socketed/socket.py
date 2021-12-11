"""This file contains the anyio and curio implementation of
`discpyth.socketed.proto.ProtoManager`. You may take reference from this
file to see the implementation specifics to implment it in other frameworks.
"""

from __future__ import annotations

from typing import Optional, Tuple, Union
from socket import SHUT_WR

try:
    import anyio
    from anyio import connect_tcp
    from anyio.streams.tls import TLSStream
except ImportError:
    ANY_IO_AVAILABLE = False
else:
    ANY_IO_AVAILABLE = True

try:
    from curio import open_connection  # type: ignore
    from curio.io import Socket  # type: ignore
except ImportError:
    CURIO_AVAILABLE = False
else:
    CURIO_AVAILABLE = True

from wsproto.events import BytesMessage, TextMessage

from .errors import ConnectionClosed
from .proto import ProtoManager
from .types import _MISSING
from .types import Message as MessageType
from .types import Ping as PingType

__all__ = ("AnyIOWebSocketManager", "CurIOWebSocketManager")


class BaseWSManager:

    _proto: ProtoManager
    _socket: Union[TLSStream, Socket]

    def __init__(self) -> None:
        self._recreate()

    def _recreate(self) -> None:
        self._proto = ProtoManager()

    async def connect(self, url):
        raise NotImplementedError()

    async def receive(self) -> MessageType:
        raise NotImplementedError()

    async def send(self, msg: Union[str, bytes]) -> None:
        raise NotImplementedError()

    async def close(self, code=1001) -> None:
        raise NotImplementedError()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()


class AnyIOWebSocketManager(BaseWSManager):

    _socket: TLSStream

    def __init__(self) -> None:
        if not ANY_IO_AVAILABLE:
            raise RuntimeError("anyio is not available")

        super().__init__()

    async def connect(self, url) -> AnyIOWebSocketManager:
        """Connect to a websocket server at `url`."""
        conn_payload = self._proto.connect(url)
        self._socket = await connect_tcp(
            *self._proto.destination,
            tls=True,
            tls_standard_compatible=False,
        )
        await self._socket.send(conn_payload)
        return self

    async def receive(self) -> MessageType:
        """Receive messages from the websocket server wrapped in a
        `discpyth.socketed.types.Message` instance.
        """
        msg: Tuple[MessageType, Optional[PingType]] = self._proto.receive(await self._socket.receive())

        while (msg[0].type is _MISSING):
            msg = self._proto.receive(await self._socket.receive())

            if isinstance(msg[1], PingType):
                await self._socket.send(msg[1].data)  # type: ignore

        return msg[0]

    async def send(self, msg: Union[str, bytes]) -> None:
        """Send a message to the websocket server."""
        if isinstance(msg, str):
            msg = TextMessage(msg)  # type: ignore
            await self._socket.send(self._proto.send(msg))  # type: ignore
            return None

        if isinstance(msg, bytes):
            msg = BytesMessage(msg)  # type: ignore
            await self._socket.send(self._proto.send(msg))  # type: ignore
            return None

        raise TypeError(f"msg must be str or bytes, got {type(msg)}")

    async def close(self, code=1001) -> None:
        """Gracefully close the websocket connection."""
        if not self._proto.closing:
            close_payload = self._proto.close(code)
            try:
                await self._socket.send(close_payload)
                try:
                    while True:
                        self._proto.receive(await self._socket.receive())
                except anyio.EndOfStream:
                    pass
                except ConnectionClosed as conn_closed:
                    if conn_closed.data is not None:
                        await self._socket.send(conn_closed.data)
            finally:
                await self._socket.aclose()


class CurIOWebSocketManager(BaseWSManager):

    _socket: Socket

    def __init__(self) -> None:
        if not CURIO_AVAILABLE:
            raise RuntimeError("curio is not available")

        super().__init__()

    async def connect(self, url) -> CurIOWebSocketManager:
        """Connect to a websocket server at `url`."""
        conn_payload = self._proto.connect(url)
        self._socket = await open_connection(
            *self._proto.destination, ssl=True
        )
        await self._socket.__aenter__()
        await self._socket.sendall(conn_payload)
        return self

    async def receive(self) -> MessageType:
        """Receive messages from the websocket server wrapped in a
        `discpyth.socketed.types.Message` instance.
        """
        msg: Tuple[MessageType, Optional[PingType]] = self._proto.receive(await self._socket.recv(65536))

        while (msg[0].type is _MISSING):
            msg = self._proto.receive(await self._socket.recv(65536))

            if isinstance(msg[1], PingType):
                await self._socket.send(msg[1].data)  # type: ignore

        return msg[0]

    async def send(self, msg: Union[str, bytes]) -> None:
        """Send a message to the websocket server."""
        if isinstance(msg, str):
            msg = TextMessage(msg)  # type: ignore
            await self._socket.sendall(self._proto.send(msg))  # type: ignore
            return None

        if isinstance(msg, bytes):
            msg = BytesMessage(msg)  # type: ignore
            await self._socket.sendall(self._proto.send(msg))  # type: ignore
            return None

        raise TypeError(f"msg must be str or bytes, got {type(msg)}")

    async def close(self, code=1001) -> None:
        """Gracefully close the websocket connection."""
        if not self._proto.closing:
            close_payload = self._proto.close(code)
            try:
                await self._socket.send(close_payload)
                try:
                    while True:
                        self._proto.receive(await self._socket.recv(65536))  # type: ignore
                except ConnectionClosed as conn_closed:
                    if conn_closed.data is not None:
                        await self._socket.send(conn_closed.data)
            finally:
                await self._socket.shutdown(SHUT_WR)
                # Since curio is very similar to the normal socket module
                # or I should say, its just the normal socket module with
                # async support, so I'm gonna pull a copy-paste move and
                # trust Bluenix on this one.
                recv = None
                while recv != b"":
                    recv = await self._socket.recv(65536)
                await self._socket.close()  # type: ignore
