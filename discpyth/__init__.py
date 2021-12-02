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
DiscPyth is licensed under the MIT license.

MIT License

Copyright (c) 2021 DiscPyth and arHSM

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

__url__ = "https://github.com/DiscPyth/DiscPyth"
__version__ = "0.1.0b2"
__author__ = "arHSM <hanseungmin.ar@gmail.com>"

__all__ = ()
