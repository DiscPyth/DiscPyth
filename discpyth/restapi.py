from __future__ import annotations

__all__ = ("RESTSession",)

from . import fur_json

from .base_classes import BaseSession
from .endpoints import Endpoints
from .structs import GetGateway, GetGatewayBot


class RESTSession(BaseSession):
    async def request(  # pylint: disable=dangerous-default-value
        self, method, endpoint, *, headers={}
    ):
        headers.update(**{"User-Agent": self.user_agent})

        async with self._client.request(
            method, endpoint, headers=headers
        ) as response:
            return await response.text("utf-8")

    async def get_gateway(self) -> GetGateway:
        resp = await self.request("GET", Endpoints.ENDPOINT_GATEWAY)

        return fur_json.loads(resp, GetGateway)

    async def get_gateway_bot(self) -> GetGatewayBot:
        resp = await self.request(
            "GET",
            Endpoints.ENDPOINT_GATEWAY_BOT,
            headers={"Authorization": f"Bot {self.token}"},
        )

        return fur_json.loads(resp, GetGatewayBot)

    async def get_channel_message(self, channel_id, message_id):
        resp = await self.request(
            "GET",
            Endpoints.ENDPOINT_GET_CHANNEL_MESSAGE.format(
                channel_id=channel_id, message_id=message_id
            ),
            headers={"Authorization": f"Bot {self.token}"},
        )

        return resp
