"""Error related to the websocket reside here."""

from typing import Optional, List, Tuple

from wsproto.events import RejectConnection

__all__ = ("ConnectionClosed", "ConnectionRejected")


class ConnectionClosed(Exception):
    """Rasied when the connection to the WebSocket is closed.

    Attributes:
        `data (Optional[bytes])`: The Pong paylod to send to the websocket.
    """

    def __init__(self, data: Optional[bytes]) -> None:
        super().__init__()

        self.data = data


class ConnectionRejected(Exception):
    """Rasied when the connection to the WebSocket is rejected by the peer.

    Attributes:
        `code (int)`: The status code of the rejection.
        `headers (List[Tuple[bytes, bytes]])`: The headers of the rejection.
        `body (bytes)`: The body of the rejection.
    """

    code: int
    headers: List[Tuple[bytes, bytes]]
    body: bytes

    def __init__(self, event: RejectConnection, body) -> None:
        super().__init__(
            f"WebSocket connection was rejected code: {event.status_code}, body: {body}"
        )

        self.code = event.status_code
        self.headers = event.headers
        self.body = body
