class RequestError(Exception):
    """Base class for all errors"""
    pass


class TimeoutError(RequestError):
    """Raised if the request has timed out"""
    pass


class NetworkError(RequestError):
    """Raised if there is an issue with the network
    (i.e. requests.ConnectionError)
    """
    pass


class StatusError(RequestError):
    """Exceptions for status code different from 200"""
    pass


class UnexpectedError(StatusError):
    """Raised if the error was not caught"""
    pass


class BadRequest(StatusError):
    """Raised when status code 400 is returned.
    Typically when at least one search parameter was not provided
    """
    pass


class NotFoundError(StatusError):
    """Raised if the player/clan is not found"""
    pass


class ServerError(StatusError):
    """Raised if the API service is having issues"""
    pass


class Unauthorized(StatusError):
    """Raised if you passed an invalid token."""
    pass


class NotTrackedError(StatusError):
    """Raised if the requested clan is not tracked (RoyaleAPI)"""
    pass


class RateLimitError(StatusError):
    """Raised if rate limit is hit"""
    pass
