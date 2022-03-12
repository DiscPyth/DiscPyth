from __future__ import annotations
from binascii import hexlify

from enum import IntEnum
from mimetypes import guess_type
from os import SEEK_END, fstat, urandom
from typing import TYPE_CHECKING, Any, AsyncIterable, AsyncIterable, AsyncIterator
from urllib.parse import urlencode, urlparse, urlunparse
from ..utils import dumps

if TYPE_CHECKING:
    from urllib.parse import ParseResult
    from typing_extensions import Self


CHUNK_SIZE = 64 * 1024


def to_bytes(value: str | bytes) -> bytes:
    return value.encode("utf-8") if isinstance(value, str) else value


def create_headers(
    headers: dict[str | bytes, str | bytes]
) -> list[tuple[bytes, bytes]]:
    headrs = []
    for key, value in headers.items():
        key, value = to_bytes(key), to_bytes(value)
        headrs.append((key.lower(), value))
    return headrs


def get_file_length(file: Any) -> int:
    try:
        filedescriptor = file.fileno()
        length = fstat(filedescriptor).st_size
    except (AttributeError, OSError):
        try:
            pos = file.tell()
            length = file.seek(0, SEEK_END)
            file.seek(pos)
        except (AttributeError, OSError):
            length = 0

    return length


class Stream:
    def __init__(self, data: bytes):
        self.data = data

    async def __aiter__(self) -> AsyncIterator[bytes]:
        yield self.data


class MultiPartStream:
    def __init__(
        self,
        data: dict[str | bytes, str | bytes],
        files: dict[str, tuple[str | bytes, bytes | AsyncIterable]],
        headers: dict[str, str] | None = None,
    ):
        self.data = data
        self.files = files
        self.encode_headers = headers or {}
        self.boundary = hexlify(urandom(16))

        self.length, self.rendered_headers = self.render_headers()

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Content-Type": f"multipart/form-data; boundary={self.boundary.decode('utf-8')}",
            "Content-Length": str(self.length),
        }

    def render_headers(self) -> tuple[int, dict[str | bytes, str | bytes]]:
        headers = {}
        length = 0
        boundary_len = len(self.boundary) + 4
        for key, value in self.data.items():
            length += len(value) + 2 + boundary_len
            headers[key] = b""
            headers[key] += (
                b'Content-Disposition: form-data; name="' + to_bytes(key) + b'"\r\n'
            )
            extra_headers = self.encode_headers.get(key, {})
            for extra_key, extra_value in extra_headers.items():
                headers[key] += (
                    to_bytes(extra_key) + b": " + to_bytes(extra_value) + b"\r\n"
                )

        for name, (filename, content) in self.files.items():
            if isinstance(content, AsyncIterable):
                length += get_file_length(content) + 2 + boundary_len
            else:
                length += len(content) + 2 + boundary_len

            headers[name] = b""
            headers[name] += (
                b'Content-Disposition: form-data; name="' + to_bytes(name) + b'"'
            )
            if filename:
                headers[name] += b'; filename="' + to_bytes(filename) + b'"'
            headers[name] += b"\r\n"
            headers[name] += (
                b"Content-Type: "
                + to_bytes(guess_type(filename)[0] or "application/octet-stream")
                + b"\r\n"
            )
            extra_headers = self.encode_headers.get(key, {})
            for extra_key, extra_value in extra_headers.items():
                headers[name] += (
                    to_bytes(extra_key) + b": " + to_bytes(extra_value) + b"\r\n"
                )

        length += len(b"\r\n".join(headers.values())) + boundary_len + 4

        return length, headers

    async def __aiter__(self) -> AsyncIterator[bytes]:
        data = self.data
        files = self.files
        boundary = self.boundary

        for key, value in data.items():
            yield b"--" + boundary + b"\r\n" + (
                # Headers
                self.rendered_headers[key]
                + b"\r\n"
                # Body
                + to_bytes(value)
            ) + b"\r\n"

        for name, (_, content) in files.items():
            yield b"--" + boundary + b"\r\n" + self.rendered_headers[name] + b"\r\n"
            if isinstance(content, AsyncIterable):
                if hasattr(content, "seek"):
                    await content.seek(0)

                chunk = await content.read(CHUNK_SIZE)
                while chunk:
                    yield to_bytes(chunk)
                    chunk = await content.read(CHUNK_SIZE)
                else:
                    yield b"\r\n"

        yield b"--" + boundary + b"--\r\n"


class ContentType(IntEnum):
    NONE = 0  # No content
    CONTENT = 1  # No type header
    TEXT = 2  # `text/plain`
    JSON = 3  # `application/json`
    MULTIPART = 4  # `multipart/form-data`
    URL_ENCODED = 5  # `application/x-www-form-urlencoded`


class Encoder:
    __slots__ = {"type", "data", "files", "multipart_headers", "_end_stream", "_data"}

    type: ContentType
    data: str | bytes | dict | None
    files: dict[str, tuple[str, str | bytes | AsyncIterable, str]]
    multipart_headers: dict[str | bytes, str | bytes]

    def __init__(
        self: Self,
        content_type: ContentType,
        data: str | bytes | dict | Any | None,
        files: dict[str | bytes, tuple[str | bytes, bytes | AsyncIterable]] = None,
        multipart_headers: dict[str, str] = None,
    ) -> None:
        self.type = content_type
        self.data = data
        self.files = files or {}
        self.multipart_headers = multipart_headers or {}
        self._end_stream = True if content_type == ContentType.NONE else False

    @property
    def end_stream(self: Self) -> bool:
        return self._end_stream

    async def encode(self: Self) -> tuple[dict[bytes, bytes], AsyncIterable[bytes]]:
        # already encoded, no need to go through the process again
        if hasattr(self, "_data"):
            return self._data

        # Ugly if/else tree
        if self.type == ContentType.NONE:
            return self.encode_none()  # type: ignore
        elif self.type == ContentType.CONTENT:
            return await self.encode_content()
        elif self.type == ContentType.TEXT:
            return self.encode_text()
        elif self.type == ContentType.JSON:
            return self.encode_json()
        elif self.type == ContentType.MULTIPART:
            return await self.encode_multipart()
        elif self.type == ContentType.URL_ENCODED:
            return self.encode_urlencoded()

        raise ValueError(f"Unknown content type: {self.type}")

    def encode_none(self: Self) -> tuple[dict[bytes, bytes], None]:
        return {}, None

    async def encode_content(
        self: Self,
    ) -> tuple[dict[bytes, bytes], AsyncIterable[bytes]]:
        content = self.data

        if isinstance(content, (bytes, str)):
            body = to_bytes(content)
            length = str(len(body)).encode("utf-8")
            headers = {b"content-length": length} if body else {}
            return headers, Stream(body)

        # file or file-like object
        elif isinstance(content, AsyncIterable):
            body = b""
            async for chunk in content:
                try:
                    body += chunk
                except TypeError:
                    # Raised when not using `rb` mode for opening the file
                    # or the iterator did not return `bytes`
                    body += chunk.encode("utf-8")

            return {b"transfer-encoding": b"chunked"}, Stream(body)

    def encode_text(self: Self) -> tuple[dict[bytes, bytes], AsyncIterable[bytes]]:
        text = self.data
        return (
            {
                b"content-type": b"text/plain",
                b"content-length": str(len(text)).encode("utf-8"),
            },
            Stream(to_bytes(text)),
        )

    def encode_json(self: Self) -> tuple[dict[bytes, bytes], bytes]:
        body = dumps(self.data)
        return (
            {
                b"content-type": b"application/json",
                b"content-length": str(len(body)).encode("utf-8"),
            },
            Stream(body),
        )

    async def encode_multipart(
        self: Self,
    ) -> tuple[dict[bytes, bytes], AsyncIterable[bytes]]:
        stream = MultiPartStream(
            self.data,
            self.files,
            self.multipart_headers,
        )
        return stream.headers, stream

    def encode_urlencoded(
        self: Self,
    ) -> tuple[dict[bytes, bytes], AsyncIterable[bytes]]:
        data = []
        for key, value in data.items():
            if isinstance(value, (list, tuple, set)):
                for item in value:
                    if item is True:
                        item = "true"
                    elif item is False:
                        item = "false"
                    elif item is None:
                        item = ""
                    else:
                        item = str(item)
                    data.append((key, item))
            else:
                if value is True:
                    value = "true"
                elif value is False:
                    value = "false"
                elif value is None:
                    value = ""
                value = str(value)
                data.append((key, value))

        body = urlencode(data, doseq=True).encode("utf-8")
        return (
            {
                b"content-type": b"application/x-www-form-urlencoded",
                b"content-length": str(len(body)).encode("utf-8"),
            },
            Stream(body),
        )


class Request:
    method: bytes
    url: ParseResult
    headers: dict[str | bytes, str | bytes]
    multipart_headers: dict[str | bytes, str | bytes]
    encoder: Encoder

    def __init__(
        self: Self,
        method: str | bytes,
        url: str,
        *,
        content_type: ContentType = ContentType.NONE,
        data: str | bytes | dict | Any | None = None,
        files: dict[str | bytes, tuple[str | bytes, bytes | AsyncIterable]] = None,
        headers: dict[str | bytes, str | bytes] | None = None,
        multipart_headers: dict[str | bytes, str | bytes] = None,
    ) -> None:
        self.method = to_bytes(method.upper())
        self.url = urlparse(url)
        self.headers = headers or {}
        self.encoder = Encoder(content_type, data, files, multipart_headers)

    @property
    def bucket_id(self: Self) -> str:
        return urlunparse(
            (self.url.scheme, self.url.netloc, self.url.path, None, None, None)
        )

    @property
    def end_stream(self: Self) -> bool:
        return self.encoder.end_stream

    async def read(self: Self) -> tuple[dict[bytes, bytes], bytes]:
        return await self.encoder.encode()
