"""This file contatins the base class for handling `wsproto`.
You may use this class to create your own socket handler.
Or use the anyio implementation in `discpyth.socketed.socket`.
"""

from typing import Optional, Tuple, Union
from urllib.parse import ParseResult, urlparse

from wsproto import ConnectionType, WSConnection
from wsproto.connection import ConnectionState
from wsproto.events import (
    BytesMessage,
    CloseConnection,
    Event,
    Ping,
    RejectConnection,
    RejectData,
    Request,
    TextMessage,
)

from .errors import ConnectionClosed, ConnectionRejected
from .types import _MISSING
from .types import Message as MessageType
from .types import Ping as PingType

__all__ = ("ProtoManager",)


ZLIB_SUFFIX = b"\x00\x00\xff\xff"


class ProtoManager:
    """ProtoManager wraps around `wsproto`'s functions and methods to
    simplify handling of connection/closing/events.

    If you wish to use something other than anyio you may use this class
    instead of `WebSocketManager`.

    Attributes:
        `destination (Tuple[str, int])`: A tuple contatining the host
        and port of the websocket connection.
        `closing (bool)`: A boolean indicating if the connection is
        closing or not.
        `url (ParseResult)`: PardeResult named tuple returned by
        urllib.parse.urlparse, contains the data for connecting to the websocket.
        `_proto (wsproto.WSConnection)`: The `wsproto` WebSocket constructor.
        `_text_buffer (str)`: Buffer for text messages.
        `_bytes_buffer (bytes)`: Buffer for bytes messages.

    Methods:
        `connect () -> bytes`: Returns the network data to be sent to
        the websocket to connect to `url`.
        `send (Event) -> bytes`: Returns the network data of `msg` to
        send to the websocket.
        `receive (Optional[bytes]) -> Tuple[MessageType, Optional[PingType]]`:
        Returns a tuple of `discpyth.socketed.types.Message` and optionally
        `discpyth.socketed.types.Ping`.
        `close (Optional[int]) -> bytes`: Returns the close event network data.
        `recreate () -> None`: Resets all buffers and resets the `wsproto`
        WebSocket constructor.
    """

    url: ParseResult
    _proto: WSConnection

    _text_buffer: str
    _bytes_buffer: bytes

    def __init__(self) -> None:
        self.recreate()

    @property
    def destination(self) -> Tuple[str, int]:
        """Returns a tuple contatining the host and port of the websocket connection."""
        return self.url.netloc, 443 if self.url.scheme == "wss" else 80

    @property
    def closing(self) -> bool:
        """Returns a bool indication whether the connection is closing or not."""
        return self._proto.state in {
            ConnectionState.CLOSED,
            ConnectionState.LOCAL_CLOSING,
            ConnectionState.REMOTE_CLOSING,
        }

    def send(self, msg: Event) -> bytes:
        """Returns the network data of `msg` to send to the websocket.

        Parameters:
            `msg (Event)`: The Event to send to the websocket.

        Raises:
            `wsproto.utilities.LocalProtocolError`: If the passed event is not of the correct type.

        Returns:
            `bytes`: The network data of `msg`.
        """
        return self._proto.send(msg)

    def recreate(self) -> None:
        """Reset all buffers and reset the `wsproto` WebSocket constructor."""
        self._proto = WSConnection(ConnectionType.CLIENT)
        self._text_buffer = ""
        self._bytes_buffer = b""

    def connect(self, url: Union[str, ParseResult]) -> bytes:
        """Returns the network data to be sent to the websocket to connect to `url`.

        Parameters:
            `url (Union[str, ParseResult])`: The url to connect to.

        Returns:
            `bytes`: The network data to be sent to the websocket to connect to `url`.
        """
        if isinstance(url, str):
            url = urlparse(url)
        self.url = url
        return self._proto.send(
            Request(
                self.url.netloc,
                f"{self.url.path}{'?'+self.url.query if self.url.query else ''}",
            )
        )

    def close(self, code: int = 1001) -> bytes:
        """Returns the close event network data.

        Parameters:
            `code (int)`: The code to send to the websocket.

        Returns:
            `bytes`: The network data of the close event.
        """
        return self._proto.send(CloseConnection(code))

    def receive(self, data: Optional[bytes]) -> Tuple[MessageType, Optional[PingType]]:
        """Returns a tuple of `discpyth.socketed.types.Message` and
        optionally `discpyth.socketed.types.Ping`.

        You should make sure to check if the ping payload exists and
        send the data to the socket accordingly, the data to be sent
        is the `discpyth.socketed.types.Ping.data` attribute.

        Parameters:
            `data (Optional[bytes])`: The data received from the websocket.

        Raises:
            `discpyth.socketed.errors.ConnectionClosed`: If the connection is closed.
            `discpyth.socketed.errors.ConnectionRejected`: If the connection is rejected.

        Returns:
            `Tuple[MessageType, Optional[PingType]]`: A tuple of `discpyth.socketed.types.Message`
            and optionally `discpyth.socketed.types.Ping`.
        """
        if data is not None and len(data) == 0:
            data = None

        self._proto.receive_data(data)

        reject_data = b""
        reject_event = None
        to_return = None

        for event in self._proto.events():
            if isinstance(event, Ping):
                to_return = PingType(self._proto.send(event.response()))
                continue
            elif isinstance(event, RejectConnection):
                reject_event = event
                if event.has_body:
                    continue
                else:
                    raise ConnectionRejected(reject_event, None)
            if isinstance(event, RejectData):
                reject_data += event.data
                if not event.body_finished:
                    continue
                else:
                    raise ConnectionRejected(reject_event, reject_data)  # type: ignore
            elif isinstance(event, CloseConnection):
                if self._proto.state == ConnectionState.CLOSED:
                    raise ConnectionClosed(None)
                else:
                    raise ConnectionClosed(
                        self._proto.send(event.response()),
                        code=event.code,
                        reason=event.reason,
                    )
            elif isinstance(event, TextMessage):
                self._text_buffer += event.data
                if not event.message_finished:
                    continue
                payload = MessageType(self._text_buffer, "str")
                self._text_buffer = ""
                return payload, to_return
            elif isinstance(event, BytesMessage):
                self._bytes_buffer += event.data
                if not event.message_finished:
                    continue
                payload = MessageType(self._bytes_buffer, "bytes")
                self._bytes_buffer = b""
                return payload, to_return
            else:
                continue

        return MessageType(None, _MISSING), to_return
