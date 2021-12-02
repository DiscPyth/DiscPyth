"""Socketed is a modified version of discord-gateway.
discord-gateway is a Sans-I/O implementation of the Discord gateway/websocket.

Socketed changes the way how data is handled in discord-gateway and provides,
a simplified interface for interacting with websockets using anyio.

Copyrights: Bluenix2 <bluenixdev@gmail.com>

discord-gateway is licensed under the MIT License. And can be foud at:
https://github.com/Bluenix2/discord-gateway
"""

from .errors import *  # noqa: F403, F401
from .proto import *  # noqa: F403, F401
from .socket import *  # noqa: F403, F401
from .types import *  # noqa: F403, F401
