"""DiscPyth is a Discord API wrapper in Python, built based off of the
very awesome DiscordGo library by bwmarrin.

DiscordGo is a simple and easy to use library for interacting with the
Discord API. The fact that DIscPyth is basically a DiscordGo clone
in Python makes it easy to get started with and its pretty simple to
understand.

Example:

```py
import discpyth

# Create a session with your bot token and the intents you need
session = discpyth.Session(
    "MTA1NjgxMzYxMzA2ODE2NTIy.MTUxNDI2ODAwLjA=.cPW6VQMVp8pdbfUm8FHHWR9+UCpYpIgyhytMpZj9xG8=",
    513
)

@session.add_handler
# Create a new event callback
# You can even use type annotataions
# async def bot_is_ready(ses, ready: discpyth.Ready):
async def bot_is_ready(ses, ready):
    print("Bot is ready!")

session.open()
```

bwmarrin    - https://github.com/bwmarrin/
discordgo   - https://github.com/bwmarrin/discordgo

-------------------------------------------
DiscordPyth is licensed under the BSD 3-Clause License.

BSD 3-Clause License

Copyright (c) 2021, DiscPyth and arHSM
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""
__url__ = "https://github.com/DiscPyth/DiscPyth"
__version__ = "0.1.0b2"
__author__ = "arHSM <hanseungmin.ar@gmail.com>"

from .discpyth import Session, new  # noqa: F401
