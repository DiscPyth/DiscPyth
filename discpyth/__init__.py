__url__ = "https://github.com/DiscPyth/DiscPyth"
__version__ = "0.1.0b2"
__author__ = "arHSM <hanseungmin.ar@gmail.com>"

__all__ = ("Session",)

from . import structs
from .discpyth import Session  # noqa: F401
from .structs import *  # noqa: F401, F403

__all__ += structs.__all__  # type: ignore
