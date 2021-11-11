"""
## DiscPyth
`DiscPyth` is an unofficial python wrapper for the official Discord API.
It is mainly inspired from `discordgo` (https://github.com/bwmarrin/discordgo) which is another wonderful wrapper for the Discord API in GO.

```py
import discpyth

# create a new session
ses = discpyth.Session.new("YOUR_TOKEN_HERE")
# Set your required intents
ses.set_intents(513)

# Create an Event callback
@ses.add_handler(discpyth.Ready)
# You can also use typehints
# @ses.add_handler
# async def bot_is_online(s, r: discpyth.Ready):
async def bot_is_online(s, r):
    print(f"{r.user.tag} is now online!")

try:
    # Open the connection to Discord
    ses.open()
except KeyboardInterrupt:
    # Close the connection to Discord
    ses.close()
```

---------------------------------
MIT License

Copyright (c) 2021 DiscPyth, arHSM

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

__author__ = "arHSM"
__version__ = "0.1.0"

import zlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import asyncio
    from logging import Logger

    import aiohttp

    from .eventhandlers import EventHandler
    from .structs import Identify


class _Session:
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    __slots__ = (
        "_loop",
        "identify",
        "max_rest_retries",
        "client",
        "user_agent",
        "last_heartbeat_ack",
        "last_heartbeat_sent",
        "_handlers",
        "_once_handlers",
        "_sync_events",
        "_event_types",
        "_register_event_providers",
        "_ws_conn",
        "_sequence",
        "_gateway",
        "_session_id",
        "_buffer",
        "_inflator",
        "_log",
        "_trim_logs",
        "_heartbeat",
        "_open_task",
        "_ws_lock",
    )

    def __init__(self):
        self._loop: asyncio.AbstractEventLoop = None

        self.identify: Identify = None

        # Max number of REST API retries
        self.max_rest_retries: int = 3

        # The http client used for REST requests and WSs
        self.client: aiohttp.ClientSession = None

        # The user agent used for REST APIs
        self.user_agent: str = f"DiscordBot (https://github.com/DiscPyth/DiscPyth, {__version__}) by {__author__}"

        # Stores the last HeartbeatAck that was received (in UTC)
        self.last_heartbeat_ack: float = 0.0

        # Stores the last Heartbeat sent (in UTC)
        self.last_heartbeat_sent: float = 0.0

        # Event handlers
        self._handlers: EventHandler = None
        self._once_handlers: EventHandler = None
        self._sync_events: bool = False

        # The websocket connection.
        self._ws_conn: aiohttp.ClientWebSocketResponse = None

        # sequence tracks the current gateway api websocket sequence number
        self._sequence: int = None

        # stores sessions current Discord Gateway
        self._gateway: str = ""

        # stores session ID of current Gateway connection
        self._session_id: str = ""

        # for decompressing gateway messages
        self._buffer: bytearray = bytearray()
        self._inflator: zlib.decompressobj = zlib.decompressobj()

        # Logger
        self._log: Logger.log = lambda lvl, msg: None
        self._trim_logs = True

        # Tasks
        self._heartbeat: asyncio.Future = None
        self._open_task: asyncio.Future = None

        # Locks
        self._ws_lock: asyncio.Lock = None


from .discpyth import (  # pylint: disable=wrong-import-position,cyclic-import # noqa: E402
    Session,
)
from .structs import *  # pylint: disable=wrong-import-position # noqa: E402, F401, F403

__all__ = ("Session",)
