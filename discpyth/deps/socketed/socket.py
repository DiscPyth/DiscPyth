"""This file contains the anyio and curio implementation of
`discpyth.socketed.proto.ProtoManager`. You may take reference from this
file to see the implementation specifics to implment it in other frameworks.
"""

from __future__ import annotations

from typing import Literal, Optional, Tuple, Union

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

__all__ = ("WebSocketManager",)


class WebSocketManager:
    """`anyio`/`curio` implementation of `discpyth.socketed.proto.ProtoManager`.

    Parameters:
        `backend (Literal["asyncio", "trio", "curio"])`: The async
        backend to use. must be one of `'asyncio'`, `'trio'`, `'curio'`.

    Attributes:
        `_socket (Union[TLSStream, Socket])`: The underlying socket.
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
    _socket: Union[TLSStream, Socket]
    _backend: str

    def __init__(self, backend: Literal["asyncio", "trio", "curio"]) -> None:
        if backend not in {"asyncio", "trio", "curio"}:
            raise ValueError(
                f"backend must be one of 'asyncio', 'trio', 'curio', got {backend}"
            )

        if backend in {"asyncio", "trio"} and not ANY_IO_AVAILABLE:
            raise RuntimeError(
                f"{backend} backend requires anyio to be installed"
            )

        if backend == "curio" and not CURIO_AVAILABLE:
            raise RuntimeError(
                f"{backend} backend requires curio to be installed"
            )

        self._backend = "anyio" if backend in {"asyncio", "trio"} else "curio"

        self._recreate()

    def _recreate(self):
        """Create a new `discpyth.socketed.proto.ProtoManager` instance."""
        self._proto = ProtoManager()

    async def connect(self, url: str) -> WebSocketManager:
        """Connect to a websocket server at `url`."""
        conn_payload = self._proto.connect(url)
        if self._backend == "anyio":
            self._socket = await connect_tcp(
                *self._proto.destination,
                tls=True,
                tls_standard_compatible=False,
            )
            await self._socket.send(conn_payload)
        else:
            self._socket = await open_connection(
                *self._proto.destination, ssl=True
            )
            self._socket._socket.__enter__()
            await self._socket.sendall(conn_payload)
        return self

    async def receive(self) -> MessageType:
        """Receive messages from the websocket server wrapped in a
        `discpyth.socketed.types.Message` instance.
        """
        msg: Tuple[MessageType, Optional[PingType]] = None  # type: ignore

        while (
            msg is None
            or msg[0].type  # pylint: disable=unsubscriptable-object
            is _MISSING
        ):
            msg = (
                self._proto.receive(await self._socket.receive())
                if self._backend == "anyio"
                else self._proto.receive(await self._socket.recv(65536))  # type: ignore
            )

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
            if self._backend == "anyio":
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
            else:
                try:
                    await self._socket.send(close_payload)
                    try:
                        while True:
                            self._proto.receive(await self._socket.recv(65536))  # type: ignore
                    except ConnectionClosed as conn_closed:
                        if conn_closed.data is not None:
                            await self._socket.send(conn_closed.data)
                finally:
                    await self._socket.close()  # type: ignore

    async def __aenter__(self) -> WebSocketManager:
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()
