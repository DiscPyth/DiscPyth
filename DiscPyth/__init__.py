"""
## DiscPyth
`DiscPyth` is an unofficial python wrapper for the official Discord API.
It is mainly inspired from `discordgo` (https://github.com/bwmarrin/discordgo) which is another wonderful wrapper for the Discord API in GO.

```py
from DiscPyth import new

def main():
    # create a new session
    dpth = new("YOUR_TOKEN_HERE")
    # open connection to discord
    dpth.open()
# run
main()
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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import asyncio
    from logging import Logger
    import zlib

    import aiohttp

    from .structs import IDENTIFY


class _Session_Manager:
    pass


class _Session:
    __slots__ = (
        "_loop",
        "Identify",
        "MaxRestRetries",
        "Client",
        "UserAgent",
        "LastHeartbeatAck",
        "LastHeartbeatSent",
        "_handlers",
        "_onceHandlers",
        "_wsConn",
        "_sequence",
        "_gateway",
        "_sessionID",
        "_buffer",
        "_inflator",
        "_log",
        "_heartbeat",
    )

    def __init__(self):
        self._loop: asyncio.AbstractEventLoop = None

        self.Identify: IDENTIFY = None

        # Max number of REST API retries
        self.MaxRestRetries: int = 3

        # The http client used for REST requests and WSs
        self.Client: aiohttp.ClientSession = None

        # The user agent used for REST APIs
        self.UserAgent: str = f"DiscordBot (https://github.com/DiscPyth/DiscPyth, {__version__}) by {__author__}"

        # Stores the last HeartbeatAck that was received (in UTC)
        self.LastHeartbeatAck: float = 0.0

        # Stores the last Heartbeat sent (in UTC)
        self.LastHeartbeatSent: float = 0.0

        # Event handlers
        self._handlers: None = None
        self._onceHandlers: None = None

        # The websocket connection.
        self._wsConn: aiohttp.ClientWebSocketResponse = None

        # sequence tracks the current gateway api websocket sequence number
        self._sequence: int = None

        # stores sessions current Discord Gateway
        self._gateway: str = ""

        # stores session ID of current Gateway connection
        self._sessionID: str = ""

        # for decompressing gateway messages
        self._buffer: bytearray = None
        self._inflator: zlib.decompressobj = None

        # Logger
        self._log: Logger.log = lambda lvl, msg: None

        # Tasks
        self._heartbeat: asyncio.Future = None


from .discpyth import Session
from .structs import Intents

__all__ = ("Session",)
