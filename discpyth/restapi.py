from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING

import aiohttp

from .endpoints import Endpoints

if TYPE_CHECKING:
    from .discpyth import Session


class RESTSession:
    async def request(self: Session, method, endpoint, headers={}):
        headers.update(**{"User-Agent":self.user_agent})
        
        if self._client is None:
            self._client = aiohttp.ClientSession()

        async with self._client.request(method, endpoint, headers=headers) as response:
            print(await response.text("utf-8"))

    async def get_gateway(self: Session):
        await self.request("GET", Endpoints.ENDPOINT_GATEWAY)

    async def get_gateway_bot(self: Session):
        await self.request(
            "GET", 
            Endpoints.ENDPOINT_GATEWAY_BOT, 
            headers={"Authorization":f"Bot {self._token}"})