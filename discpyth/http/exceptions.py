class HTTPException(Exception):
    """
    Base class for all HTTP exceptions.
    """

    code: int
    message: str

    def __init__(self, code: int, message: str) -> None:
        super().__init__(f"{code} {message}")
        self.code = code
        self.message = message


class Forbidden(HTTPException):
    """
    403 Forbidden
    """

    def __init__(self, endpoint: str) -> None:
        super().__init__(403, f"Forbidden: {endpoint}")


class NotFound(HTTPException):
    """
    404 Not Found
    """

    def __init__(self, endpoint: str) -> None:
        super().__init__(404, f"Not Found: {endpoint}")


class ServerError(HTTPException):
    """
    500 Server Error
    """

    def __init__(self, endpoint: str) -> None:
        super().__init__(500, f"Server Error: {endpoint}")
