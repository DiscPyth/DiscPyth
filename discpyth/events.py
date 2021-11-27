from typing_extensions import Annotated
from .fur_json import Struct

class Event(Struct):
    operation: Annotated[int, {"name": "op"}]
    sequence: Annotated[int, {"name": "s"}]
    type: Annotated[str, {"name": "t"}]
    raw_data: Annotated[str, {"name": "d", "raw": True}]

class Hello(Struct)