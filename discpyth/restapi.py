from typing import Optional

from .endpoints import ENDPOINT_GATEWAY, ENDPOINT_GATEWAY_BOT
from .session import BaseSession


class RestSession(BaseSession):

    __slots__ = set()

    async def request(
        self, method: str, endpoint: str, headers: Optional[dict] = None
    ):
        pass

    async def get_gateway(self):
        pass

    async def get_gateway_bot(self):
        pass
