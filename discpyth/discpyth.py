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
    def __init__(self) -> None:
        WSSession.__init__(self)

    def open(self):
        async def wrapped_open():
            print("henlo")

        anyio_run(wrapped_open, backend=self._backend)


class _CurIOSession(WSSession):
    def __init__(self) -> None:
        WSSession.__init__(self)

    def open(self):
        async def wrapped_open():
            pass

        curio_run(wrapped_open)


_BACKEND_DICT = {
    "asyncio": _AnyIOSession,
    "trio": _AnyIOSession,
    "curio": _CurIOSession,
}


class Session(_AnyIOSession, _CurIOSession):
    def __init__(self):
        # Handle inheritance in _post_init
        # pylint: disable=super-init-not-called
        pass


# This function is just to align the library with DiscordGo's model
# the same behavior can be achieved with `Session.__init__`` but
# we are gonna stick to discordgo's paradigm
#
# dont quote me with this:
# There should be one-- and preferably only one --obvious way to do it.
#
def new(token, intents, **config):
    # pylint: disable=protected-access
    session = Session()
    session.token = token
    session.intents = intents
    session.user_agent = f"DiscordBot ({__url__}, {__version__}) by {__author__}"
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
                ("curio event loop backend is not available." " Please install curio.")
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

    # This will never be None
    _BACKEND_DICT.get(session._backend).__init__(session)

    return session
