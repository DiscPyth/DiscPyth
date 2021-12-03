"""All the types returned by `discpyth.socketed.proto.ProtoManager.receive`."""

__all__ = ("Payload", "Ping", "Message")


from typing import Type, Union


class Payload:
    """Base class for websocket payloads.

    Attributes:
        `data (Union[str, bytes, None])`: The payload data.
    """

    def __init__(self, data: Union[str, bytes, None]):
        self.data = data

    def __repr__(self):
        return f"<{__name__}.{self.__class__.__name__} data: {self.data}>"


class Ping(Payload):
    """A ping payload, used to mark a ping payload so that the handler
    can send a Pong as a response.

    Attributes:
        `data (wsproto.events.Pong)`: The data to send in response to Ping.
    """

    def __init__(self, to_send: bytes):
        super().__init__(to_send)


class _MISSING:
    def __repr__(self) -> str:
        return "..."


class Message(Payload):
    """Message payload, used to wrap websocket messages.
    Use the type attribute to determine the type of the message.
    i.e `str` or `bytes`

    Attributes:
        `data (Union[str, bytes, None])`: The data of the message.
        `type (str)`: The type of the message.
    """

    def __init__(
        self, data: Union[bytes, str, None], _type: Union[str, Type[_MISSING]]
    ):
        super().__init__(data)
        self.type = _type

    def __repr__(self):
        return f"<{__name__}.Message data: {self.data}, type: {self.type}>"
