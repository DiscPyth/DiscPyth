from __future__ import annotations

from ssl import create_default_context
from typing import TYPE_CHECKING
from urllib.parse import urlparse
from weakref import WeakValueDictionary

from anyio import BrokenResourceError, EndOfStream, Event, Lock, connect_tcp, sleep
from anyio.streams.tls import TLSStream
from certifi import where
from h2.config import H2Configuration
from h2.connection import H2Connection

from ...utils import exponential_backoff
from ...http.base import BaseHTTPClient, ConnectionState

if TYPE_CHECKING:
    from ssl import SSLContext
    from types import TracebackType

    from typing_extensions import Self


def create_ssl_context() -> SSLContext:
    context = create_default_context(
        cafile=where(),
    )
    context.set_alpn_protocols(["h2"])
    return context


class Bucket:
    lock: Lock

    def __init__(self, lock: Lock) -> None:
        self.lock = lock
        self.deferred = False

    async def __aenter__(self) -> Lock:
        await self.lock.acquire()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.deferred:
            return
        await self.release()

    def defer(self) -> None:
        if not self.deferred:
            self.deferred = True

    async def release(self) -> None:
        self.lock.release()


class BucketManager:
    buckets: dict[str, Bucket]
    global_limiter: Event

    def __init__(self: Self) -> None:
        self.global_limiter = None
        self.buckets = WeakValueDictionary()

    def get(self, key: str) -> Bucket:
        try:
            bucket = self.buckets[key]
        except KeyError:
            bucket = self.buckets[key] = Bucket(Lock())
        return bucket

    async def clear_global(self: Self) -> None:
        self.global_limiter.set()

    def is_global(self: Self) -> bool:
        if self.global_limiter is None:
            return False
        return self.global_limiter.is_set()

    async def wait_global(self: Self) -> None:
        await self.global_limiter.wait()

    async def set_global(self: Self) -> None:
        self.global_limiter = Event()


class HTTPClient(BaseHTTPClient):
    socket: TLSStream
    state_lock: Lock
    bucket_manager: BucketManager
    connect_lock: Lock
    read_lock: Lock

    def __init__(
        self: Self,
        max_reconnect_retries: int = 3,
        max_request_retries: int = 3,
        default_headers: list[tuple[bytes, bytes]] | None = None,
    ) -> None:
        BaseHTTPClient.__init__(
            self,
            max_reconnect_retries=max_reconnect_retries,
            max_request_retries=max_request_retries,
            default_headers=default_headers,
        )
        self.state_lock = Lock()
        self.bucket_manager = BucketManager()
        self.connect_lock = Lock()
        self.read_lock = Lock()

    @property
    def port(self: Self) -> int:
        return 443

    async def connect(self: Self, url: str) -> Self:
        if self.connection_initialized:
            return

        self.url = urlparse(url)
        self.server_name = self.url.netloc.encode("ascii")
        server_name = self.url.netloc
        self.connection = None

        retries = self.max_reconnect_retries

        back_off = exponential_backoff(2, 0)

        ssl_context = create_ssl_context()

        async with self.connect_lock:
            while True:
                try:
                    self.socket = await connect_tcp(
                        server_name,
                        self.port,
                        tls=True,
                        ssl_context=ssl_context,
                    )
                except (OSError, TimeoutError, BrokenResourceError):
                    if retries == 0:
                        raise
                    retries -= 1
                    back_off = exponential_backoff(2, back_off)
                    await sleep(back_off)
                else:
                    self.connection_initialized = True
                    break

        assert isinstance(self.socket, TLSStream)

        self.connection = H2Connection(
            config=H2Configuration(validate_inbound_headers=False)
        )
        self.connection.initiate_connection()
        await self._stream_send(self.connection.data_to_send())
        return self

    async def _stream_recv(self: Self, max_bytes: int) -> bytes:
        try:
            read = await self.socket.receive(max_bytes)
        except EndOfStream:
            read = b""
        return read

    async def _stream_send(self: Self, data: bytes) -> None:
        await self.socket.send(data)

    async def aclose(self: Self) -> None:
        if self.connection_initialized:
            self.connection.close_connection()
            await self._stream_send(self.connection.data_to_send())
            self.state = ConnectionState.CLOSED
