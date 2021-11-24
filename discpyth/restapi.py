from __future__ import annotations

__all__ = ("RESTSession",)

import aiohttp
import go_json  # type: ignore

from .base_classes import BaseSession
from .endpoints import Endpoints
from .structs import GetGateway, GetGatewayBot


class RESTSession(BaseSession):
    # pylint: disable=no-member

    async def request(  # pylint: disable=dangerous-default-value
        self, method, endpoint, *, headers={}
    ):
        headers.update(**{"User-Agent": self.user_agent})

        if (  # pylint: disable=access-member-before-definition
            self._client is None
        ):
            self._client: aiohttp.ClientSession = (  # pylint: disable=attribute-defined-outside-init
                aiohttp.ClientSession()
            )

        async with self._client.request(
            method, endpoint, headers=headers
        ) as response:
            return await response.text("utf-8")

    async def get_gateway(self) -> GetGateway:
        resp = await self.request("GET", Endpoints.ENDPOINT_GATEWAY)

        return go_json.loads(resp, GetGateway)

    async def get_gateway_bot(self) -> GetGatewayBot:
        resp = await self.request(
            "GET",
            Endpoints.ENDPOINT_GATEWAY_BOT,
            headers={"Authorization": f"Bot {self._token}"},  # type: ignore
        )

        return go_json.loads(resp, GetGatewayBot)
