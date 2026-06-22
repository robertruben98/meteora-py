"""Exception hierarchy for the Meteora client."""

from __future__ import annotations


class MeteoraError(Exception):
    """Base class for all errors raised by this library.

    Catch this to handle any failure originating from ``meteora`` (currently
    just :class:`MeteoraAPIError`). Network-level failures from the underlying
    ``httpx`` client propagate as ``httpx`` exceptions and are not wrapped.
    """


class MeteoraAPIError(MeteoraError):
    """Raised when the Meteora DLMM Data API returns an error response.

    The API signals errors with a non-2xx HTTP status. The body, when present,
    is surfaced in :attr:`message`; otherwise it falls back to ``"HTTP <status>"``.

    Attributes:
        message: The error message text, falling back to ``"HTTP <status>"``.
        status_code: The HTTP status code of the response.

    Example::

        from meteora import MeteoraClient, MeteoraAPIError

        with MeteoraClient() as client:
            try:
                client.get_pool("not-a-real-address")
            except MeteoraAPIError as exc:
                print(exc.status_code, exc.message)
    """

    def __init__(self, *, message: str, status_code: int) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(f"[HTTP {status_code}] {message}")
