import logging

from . import __author__, __url__, __version__
from .deps.socketed.socket import ANY_IO_AVAILABLE, CURIO_AVAILABLE
from .utils import WrappedLogger
from .wsapi import WSSession

if ANY_IO_AVAILABLE:
    from anyio import run as anyio_run

if CURIO_AVAILABLE:
    from curio import run as curio_run

__all__ = ("Session", "new")


class _AnyIOSession(WSSession):
    def open(self):
        def wrapped_open():
            pass

        if self._backend == "asyncio":
            anyio_run(wrapped_open, backend="asyncio")
        elif self._backend == "trio":
            anyio_run(wrapped_open, backend="trio")


class _CurIOSession(WSSession):
    def open(self):
        def wrapped_open():
            pass

        curio_run(wrapped_open)


class Session(_AnyIOSession, _CurIOSession):
    def __init__(self):
        # Handle inheritance in _post_init
        pass

    def _post_init(self):
        if self._backend in {"asyncio", "trio"}:
            _AnyIOSession.__init__(self)
        elif self._backend in {"curio"}:
            _CurIOSession.__init__(self)
        else:
            # Can't put your trust in users, you need to have a fallback
            # if someone messes with private attributes.
            raise RuntimeError(
                (
                    "Uh oh! this isn't supposed to happen, make sure your"
                    " session was created using `new`. If you used `new`"
                    " and you are seeing this then please discuss this"
                    " issue @ https://discord.gg/8RATdNBs6n"
                )
            )

    def open(self):
        raise NotImplementedError()


# This function is just to align the library with DiscordGo's model
# the same behavior can be achieved with `Session.__init__`` but
# we are gonna stick to discordgo's paradigm
#
# dont quote me with this:
# There should be one-- and preferably only one --obvious way to do it.
#
def new(token, intents, **config):
    """Create a new Session instance.

    Arguments:
        `token (str)`: Your Discord Bot token.
        `intents (int)`: The intents you want to use.

    Keyword Arguments:
        `config`:
            `max_rest_retries (int)`: The maximum number of times to
            retry a REST request.
            `shard_count (int)`: The number of shards to use.
            `shard_id (Union[int, Sequence[int]])`: The shard ID or
            sequence of shard IDs to use.
            `backend (str)`: The async backend to use.
            `log (bool)`: Whether to log to stdout.
            `log_level (int)`: The log level to use.
            `to_file (bool)`: Whether to log to a file.
    """
    # pylint: disable=protected-access
    session = Session()
    session.token = token
    session.intents = intents
    session.user_agent = (
        f"DiscordBot ({__url__}, {__version__}) by {__author__}"
    )
    session.max_rest_retries = config.get("max_rest_retries", 5)
    if config.get("log", False):
        logger = logging.getLogger("discpyth")
        logger.setLevel(10)

        log_level = config.get("log_level", logging.WARNING)
        formatter = logging.Formatter(
            "[%(name)s] | [%(asctime)s] | [%(levelname)s] : %(message)s"
        )
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(log_level)
        logger.addHandler(stream_handler)

        if config.get("to_file", False):
            file_handler = logging.FileHandler("discpyth.log")
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            logger.addHandler(file_handler)

        session.logger = WrappedLogger(logger)

    session._shard_count = config.get("shard_count", 1)
    session._shard_id = config.get("shard_id", 1)
    backend = config.get("backend", "asyncio")

    if backend in {"asyncio", "trio", "curio"}:
        if backend == "curio" and not CURIO_AVAILABLE:
            raise RuntimeError(
                (
                    "curio event loop backend is not available."
                    " Please install curio."
                )
            )
        elif not ANY_IO_AVAILABLE:
            raise RuntimeError(
                (
                    "asyncio or trio event loop backend is not available."
                    " Please install anyio."
                )
            )
    else:
        raise LookupError(
            (
                "Event loop backend must be one of asyncio, trio, curio."
                f" Invalid backend: {backend}"
            )
        )

    session._backend = backend
    session._post_init()

    return session
