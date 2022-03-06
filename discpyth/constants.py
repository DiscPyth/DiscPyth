__all__ = (
    "T",
    "LOGGER_FORMAT",
    "BACKEND",
    "__repo_url__",
    "__author__",
    "__title__",
    "__version__",
    "__license__",
    "__copyright__",
)

from typing import TypeVar

__repo_url__ = "https://github.com/DiscPyth"
__author__ = "한승민"
__title__ = "DiscPyth"
__version__ = "0.1.0"
__license__ = "Apache 2.0"
__copyright__ = "Copyright 2020 한승민"

T = TypeVar("T")

BACKEND = "anyio"

LOGGER_FORMAT = "[{name}] [%(levelname)s] [{asctime}] [{module}:{lineno}] | {message}"
