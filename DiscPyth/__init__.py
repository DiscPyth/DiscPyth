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

__author__ = "arHSM"
__version__ = "0.1.0"

import asyncio
import aiohttp


class _Session_Manager:
    pass


class _Session:
    _loop: asyncio.AbstractEventLoop = None

    Token: str = ""

    # Sharding
    ShardID: int = 0
    ShardCount: int = 1

    # Max number of REST API retries
    MaxRestRetries: int = 3

    # Managed state object, updated internally with events when
    # StateEnabled is true.
    # State

    # The http client used for REST requests and WSs
    Client: aiohttp.ClientSession = None

    # The user agent used for REST APIs
    UserAgent: str = f"DiscordBot (https://github.com/DiscPyth/DiscPyth, {__version__}) by {__author__}"

    # Stores the last HeartbeatAck that was received (in UTC)
    LastHeartbeatAck: float = 0.0

    # Stores the last Heartbeat sent (in UTC)
    LastHeartbeatSent: float = 0.0

    # used to deal with rate limits
    # Ratelimiter

    # Event handlers
    handlers: None = None
    onceHandlers: None = None

    # The websocket connection.
    wsConn: aiohttp.ClientWebSocketResponse = None

    # sequence tracks the current gateway api websocket sequence number
    sequence: int = None

    # stores sessions current Discord Gateway
    gateway: str = ""

    # stores session ID of current Gateway connection
    sessionID: str = ""

    # Logger
    log = lambda lvl, msg: None

    # Tasks
    listening: asyncio.Future = None
    heartbeat: asyncio.Future = None
    opened: asyncio.Future = None


from .discpyth import new, new_sharded

__all__ = ("new", "new_sharded")
