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
    pass


def detect_and_raise_error(response: Response):

    if response.status_code == 400:
        raise BadRequest(response)
