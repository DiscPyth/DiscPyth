import asyncio
import aiohttp
from .wsapi import WS_Session
from . import _Session, _Session_Manager


class SessionManager:
    pass


class Session(WS_Session):
    def __init__(self, session: _Session) -> None:

        # explicitly defining class because
        # (uhh i dont remember but its important!)
        WS_Session.__init__(self, session)
        self.session: _Session = session

    def open(self):

        # I think async is a pretty confusing concept and
        # as of what I've seen most bot creators
        # are new and they don't understand certain concepts
        # so we will just wrap this function
        async def inner_open():

            # aiohttp ClientSession must be initialized in a async def method/function
            # hence we set it here instead of new()
            # Creating a ClientSession per session
            # is not good for performance but in this instance
            # this is just a single session, in sharding
            # we can modify the results from new to
            # use the same ClientSession hence we need to check if its none or not
            if self.session.Client is None:
                self.session.Client = aiohttp.ClientSession()

            # Open the actual ws connection (./wsapi.py)
            await self._open()

        # Create inner_open() as a task
        # my testing shows run_until_complete doesn't work here
        tsk = self.session._loop.create_task(inner_open())
        try:

            # Now run the loop
            self.session._loop.run_forever()

        # For now this is KeyboardInterrupt but later we prob will change it
        except KeyboardInterrupt:

            # Trigger close on Exception
            self.close()

            # We close our loop here because we dont know if our user has
            # ended their entire session or just a shard
            # if we close our seesion in wsapi.WS_Session.close() then
            # even closing a shard will end the loop
            self.session._loop.close()

    def close(self):

        # since close is not a coro we need to use
        # run_until_complete to run the coro in (./wsapi.py)

        # Why this isnt a coro is the same reason as open()
        # users might want to close their sesion on a command from discord and
        # as stated in open() this is much more newbie friendly

        self.session._loop.run_until_complete(self._close())

        # Since we dont know if a shard has closed or the entire thing
        # we need to check if shard count is 1, since 1 shard means just a
        # single ws connection and we can safetly close our ClientSession without
        # worrying about killing all the other ws connections
        # if a user manually launches shards 
        # then its not a problem unless they modify the Session returned by
        # new() to share the same ClientSession and keep the shard count at 1
        if self.session.ShardCount == 1:
            self.session._loop.run_until_complete(self.session.Client.close())


def new(token, /, *, shard_id=0, shard_count=1, **options) -> Session:
    """
    ### Creates a new `Session` and returns it.

    Positional Arguments:
        `token` - Your bot token, this is some sensitive stuff make sure to keep it perfectly hidden.
    Keyword Arguments:
        `shard_id` - Useful when launching a single shard or manually creating instances of `Session` to launch multiple shards, max shard id is (shard_count-1) if you specify `shard_id` to be the same as `shard_count` or more than it you wont be able to create a session.
        `shard_count` - Max number of shards required when `shard_id` is specified.
    Misc:
        `log` - Needs to be `log` from the `logging` module: `import logging`, `new("YOUR_TOKEN_HERE", log=logging.log)`

    Raises:
        `ValueError` - When `shard_id` is more than or equal to`shard_count`
    """
    s = _Session()

    # Set the event loop or get it from options
    s._loop = options.get("__loop", asyncio.get_event_loop())

    # Get the logger or set an empty lamba function
    s.log = options.get("logger", (lambda lvl, msg: None))

    # Set the token
    s.Token = token

    if shard_id >= shard_count:
        raise ValueError(
            "Shard ID must be 1 less than Shard Count, this error usually occurs if you try to launch shards yourself use `new_sharded`, \nif you did not manually launch shards and you see this error then create an issue @ https://github.com/DiscPyth/DiscPyth"
        )

    # Set current session shard id
    s.ShardID = shard_id

    # Set the total shard count, going to be same
    # across all session instances.. probs unless
    # the user does some stuff after creating the session
    s.ShardCount = shard_count

    # Other stuff is predefined or needs to be set in open() method

    return Session(s)


def new_sharded(token, /, *, shard_id=0, shard_count=1, **options) -> SessionManager:
    pass
