from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Any, AsyncIterable
from urllib.parse import urlparse

from anyio import sleep
from h2.events import DataReceived, ResponseReceived, StreamEnded
from h2.exceptions import NoAvailableStreamIDError, ProtocolError

from ..utils import loads
from .exceptions import Forbidden, HTTPException, NotFound, ServerError
from .types import Request, create_headers

if TYPE_CHECKING:
    from types import TracebackType
    from urllib.parse import ParseResult

    from h2.connection import H2Connection
    from h2.events import Event as BaseEvent
    from typing_extensions import Self


class ConnectionState(IntEnum):
    INIT = 0
    CONNECTED = 1
    CLOSED = 2


class BaseHTTPClient:
    url: ParseResult
    server_name: bytes
    connection: H2Connection
    state: int
    max_reconnect_retries: int
    max_request_retries: int
    connection_initialized: bool
    out_of_stream_ids: bool
    connection_fail: bool
    connection_error: BaseEvent
    write_error: Exception
    default_headers: dict[bytes, bytes]

    socket: Any
    state_lock: Any
    bucket_manager: Any
    connect_lock: Any
    read_lock: Any

    def __init__(
        self: Self,
        max_reconnect_retries: int = 3,
        max_request_retries: int = 3,
        default_headers: dict[bytes, bytes] | None = None,
    ) -> None:
        self.url = None
        self.server_name = None
        self.connection = None
        self.socket = None
        self.state = ConnectionState.INIT
        self.max_reconnect_retries = max_reconnect_retries
        self.max_request_retries = max_request_retries
        self.connection_initialized = False
        self.out_of_stream_ids = False
        self.connection_fail = False
        self.connection_error = None
        self.write_error = None
        self.default_headers = default_headers or {}

    async def connect(self: Self, url: str) -> Self:
        raise NotImplementedError()

    async def _stream_recv(self: Self, max_bytes: int) -> bytes:
        raise NotImplementedError()

    async def _stream_send(self: Self, data: bytes) -> None:
        raise NotImplementedError()

    async def aclose(self: Self) -> None:
        raise NotImplementedError()

    async def send(
        self: Self,
        request: Request,
    ) -> bytes:
        if not self.connection_initialized:
            raise RuntimeError("Please connect first")

        method = request.method
        url = request.url
        if url.netloc.encode("ascii") != self.server_name:
            raise ValueError("Invalid URL")

        path = url._replace(scheme="", netloc="").geturl() or "/"

        async with self.state_lock:
            if self.state not in (ConnectionState.INIT, ConnectionState.CONNECTED):
                raise RuntimeError(
                    "Cannot send request from an already closed connection"
                )

        try:
            stream_id = self.connection.get_next_available_stream_id()
        except NoAvailableStreamIDError:
            self.out_of_stream_ids = True
            raise

        try:
            req_headers, req_body = await request.read()
            headers = (
                [
                    (b":method", method),
                    (b":authority", self.server_name),
                    (b":scheme", "https"),
                    (b":path", path),
                ]
                + create_headers(req_headers)
                + create_headers(self.default_headers)
            )
            end_stream = request.end_stream

            bucket = self.bucket_manager.get(request.bucket_id)
            if self.bucket_manager.is_global():
                self.bucket_manager.wait_global()

            for _ in range(self.max_request_retries):
                await self._send_headers(headers, end_stream, stream_id, bucket)
                if not end_stream:
                    await self._send_body(stream_id, req_body, bucket)

                _, response_headers, body = await self._receive_events(bucket)
                return body
        except Exception:
            raise

    async def _send_headers(
        self,
        headers: list[tuple[bytes, bytes]],
        end_stream: bool,
        stream_id: int,
        bucket,
    ) -> None:
        self.connection.send_headers(stream_id, headers, end_stream=end_stream)
        self.connection.increment_flow_control_window(2**24, stream_id=stream_id)

        await self._write_to_socket(bucket)

    async def _send_body(
        self, stream_id: int, stream: AsyncIterable[bytes], bucket
    ) -> None:
        async for data in stream:
            while data:
                max_fl0w = await self._wait_for_max_flow(stream_id, bucket)
                chunk_size = min(len(data), max_fl0w)
                chunk, data = data[:chunk_size], data[chunk_size:]
                self.connection.send_data(stream_id, chunk)

                await self._write_to_socket(bucket)

        self.connection.end_stream(stream_id)
        await self._write_to_socket(bucket)

    async def _write_to_socket(self, bucket) -> None:
        async with bucket:
            to_send = self.connection.data_to_send()
            if self.write_error is not None:
                raise self.write_error

            try:
                await self._stream_send(to_send)
            except Exception as exc:
                self.write_error = exc
                self.connection_fail = True
                raise

    async def _wait_for_max_flow(self: Self, stream_id: int, bucket) -> int:
        local_flow = self.connection.local_flow_control_window(stream_id)
        max_frame_size = self.connection.max_outbound_frame_size
        max_fl0w = min(local_flow, max_frame_size)
        while max_fl0w == 0:
            await self._receive_events(bucket)
            local_flow = self.connection.local_flow_control_window(stream_id)
            max_frame_size = self.connection.max_outbound_frame_size
            max_fl0w = min(local_flow, max_frame_size)
        return max_fl0w

    async def _receive_events(
        self, bucket
    ) -> tuple[list[BaseEvent], dict[bytes, bytes], bytes]:
        events_list = []
        headers = None
        body = b""
        response_stream_ended = False

        async with self.read_lock:
            if self.connection_error is not None:  # pragma: nocover
                raise ProtocolError(self.connection_error)
            while not response_stream_ended:
                data = await self._stream_recv(65536)
                if not data:
                    break
                events = self.connection.receive_data(data)
                for event in events:
                    event_stream_id = getattr(event, "stream_id", 0)
                    if hasattr(event, "error_code") and event_stream_id == 0:
                        self.connection_error = event
                        raise ProtocolError(event)

                    events_list.append(event)
                    if isinstance(event, ResponseReceived):
                        headers = event.headers

                    if isinstance(event, DataReceived):
                        self.connection.acknowledge_received_data(
                            event.flow_controlled_length, event.stream_id
                        )
                        body += event.data

                    if isinstance(event, StreamEnded):
                        response_stream_ended = True
                        break

            await self._write_to_socket(bucket)

        headers = dict(headers)

        return events_list, headers, body

    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.aclose()
