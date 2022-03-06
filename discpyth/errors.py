class BackendNotFoundError(Exception):
    """Raised when a backend is not found."""

    def __init__(self, backend: str) -> None:
        super().__init__(
            f"Backend '{backend}' not found!"
            " Allowed backends are 'asyncio', 'trio', 'curio'."
        )


class BackendUnavailableError(Exception):
    """Raised when a backend is not available."""

    def __init__(self, backend: str) -> None:
        super().__init__(f"Backend '{backend}' is unavailable!")


class BadTokenError(Exception):
    """Raised when the `token` provided is invalid."""

    def __init__(self) -> None:
        super().__init__("Invalid token provided")
