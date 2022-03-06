from __future__ import annotations

from typing import TYPE_CHECKING
from httpx import AsyncClient

from ..constants import __version__, __repo_url__
from .ratelimiter import BucketManager, Route

if TYPE_CHECKING:
    from ..disc import Disc


class _HTTPClient:
    disc: Disc
    http: AsyncClient
    bucket_manager: BucketManager

    def __init__(self, disc: Disc) -> None:
        self.disc = disc
        self.http = AsyncClient(
            http2=True,
            headers={
                "Authorization": f"Bot {self.disc.token}",
                "User-Agent": f"DiscordBot ({__repo_url__}, {__version__})",
            },
        )

        self.bucket_manager = BucketManager()

    async def __aenter__(self) -> None:
        return

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self._http.aclose()

    async def request(self, route: Route) -> dict:

        bucket = self.bucket_manager.get(route.bucket_id)
        method = route.method
        url = route.url

        if not self.bucket_manager.is_global:
            await self.bucket_manager.wait()

        async with bucket:
            for tries in range(self.disc.max_rest_retries):
                ...
