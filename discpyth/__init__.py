__url__ = "https://github.com/DiscPyth/DiscPyth"
__version__ = "0.1.0b2"
__author__ = "arHSM <hanseungmin.ar@gmail.com>"

from .structs import __all__ as st_all

__all__ = ("Session",) + st_all

from .discpyth import Session  # noqa: F401
from .structs import *  # noqa: F401, F403
