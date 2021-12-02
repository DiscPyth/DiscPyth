"""This file contains the anyio implementation of
`discpyth.socketed.proto.ProtoManager`. You may take reference from this
file to see the implementation specifics to implment it in other frameworks.
"""

from __future__ import annotations

from typing import Union, Tuple, Optional

import anyio
from anyio import connect_tcp
from anyio.streams.tls import TLSStream
from wsproto.events import BytesMessage, Event, TextMessage

from .errors import ConnectionClosed
from .proto import ProtoManager
from .types import _MISSING
from .types import Message as MessageType
from .types import Ping as PingType

__all__ = ("WebSocketManager",)


class WebSocketManager:
    """`anyio` implementation of `discpyth.socketed.proto.ProtoManager`.

    Attributes:
        `_socket (TLSStream)`: The underlying socket.
        `_proto (ProtoManager)`: The `discpyth.socketed.proto.ProtoManager`
        instance.

    Methods:
        `connect(url: str) -> WebSocketManager`: Connect to a websocket server.
        `receive() -> MessageType`: Receive messages from the websocket server
        wrapped in a `discpyth.socketed.types.Message` instance.
        `send(msg: Union[str, bytes]) -> None`: Send a message to the websocket server.
        `close(code: int) -> None`: Gracefully close the websocket connection.
    """

    _proto: ProtoManager
    _socket: TLSStream

    def __init__(self) -> None:
        self._recreate()

    def _recreate(self):
        """Create a new `discpyth.socketed.proto.ProtoManager` instance."""
        self._proto = ProtoManager()

    async def connect(self, url: str) -> WebSocketManager:
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
        msg: Tuple[MessageType, Optional[PingType]] = None  # type: ignore

        while msg is None or msg[0].type is _MISSING:  # pylint: disable=unsubscriptable-object
            msg = self._proto.receive(await self._socket.receive())

        if isinstance(msg[1], PingType):
            await self._socket.send(msg[1].data)  # type: ignore

        return msg[0]

    async def _send(self, msg: Event) -> None:
        await self._socket.send(self._proto.send(msg))

    async def send(self, msg: Union[str, bytes]) -> None:
        """Send a message to the websocket server."""
        if isinstance(msg, str):
            msg = TextMessage(msg)  # type: ignore
            await self._send(msg)  # type: ignore
            return None

        if isinstance(msg, bytes):
            msg = BytesMessage(msg)  # type: ignore
            await self._send(msg)  # type: ignore
            return None

        raise TypeError(f"msg must be str or bytes, got {type(msg)}")

    async def close(self, code=1001) -> None:
        """Gracefully close the websocket connection."""
        try:
            await self._socket.send(self._proto.close(code))
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
