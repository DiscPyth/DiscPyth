from __future__ import annotations

try:
    from anyio import run as any_run
except ImportError:
    ANYIO_AVAILABLE = False
else:
    ANYIO_AVAILABLE = True

try:
    from curio import run as cur_run
except ImportError:
    CURIO_AVAILABLE = False
else:
    CURIO_AVAILABLE = True

from .api.http import _HTTPClient
from .errors import BackendNotFoundError, BackendUnavailableError, BadTokenError
from .constants import BACKEND

if not ANYIO_AVAILABLE and not CURIO_AVAILABLE:
    raise RuntimeError("anyio or curio is required to run DiscPyth!")


class Disc:
    token: str
    shards: int
    should_reconnect_on_error: bool
    max_rest_retries: int

    voice_connections: dict[str, None]
    _http: _HTTPClient
    _backend: str
    __run: any_run | cur_run

    def __init__(
        self, token: str, max_rest_retries: int = 3, backend: str = "asyncio"
    ) -> None:
        if backend not in {"asyncio", "trio", "curio"}:
            raise BackendNotFoundError(backend)

        if backend in {"asyncio", "trio"}:
            if not ANYIO_AVAILABLE:
                raise BackendUnavailableError("anyio")
            self._backend = "anyio"
            BACKEND = "anyio"
            self.__run = any_run
        else:
            if not CURIO_AVAILABLE:
                raise BackendUnavailableError("curio")
            self._backend = "curio"
            BACKEND = "curio"
            self.__run = cur_run

        if token == "":
            raise BadTokenError()

        self.max_rest_retries = max_rest_retries

    async def astart(self) -> None:
        async with _HTTPClient(self) as self._http:
            ...

    def start(self) -> None:
        if self._backend in {"asyncio", "trio"}:
            return self.__run(self.astart, backend=self._backend)
        return
