from requests import Response


class HootSuiteException(Exception):
    def __init__(self, response, *args, **kwargs):
        try:
            errors = response.json()["errors"]
            message = "{code} - {message}".format(**errors)
        except Exception:
            if hasattr(response, "status_code") and response.status_code == 401:
                message = response.content.decode("utf-8")
            else:
                message = response
        super().__init__(message, *args, **kwargs)


class BadRequest(HootSuiteException):
    """400"""

    pass


class Unauthorized(HootSuiteException):
    """401"""

    pass


class Forbidden(HootSuiteException):
    """403"""

    pass


class NotFound(HootSuiteException):
    """404"""

    pass


class TooManyRequests(HootSuiteException):
    """429"""

    pass


class ServerError(HootSuiteException):
    """500"""

    pass


def detect_and_raise_error(response: Response):
    status_code = response.status_code
    if status_code == 400:
        raise BadRequest(response)
    elif status_code == 401:
        raise Unauthorized(response)
    elif status_code == 403:
        raise Forbidden(response)
    elif status_code == 404:
        raise NotFound(response)
    elif status_code == 429:
        raise TooManyRequests(response)
    elif status_code >= 500:
        raise ServerError(response)
    elif status_code >= 400:
        raise BadRequest(Response)
