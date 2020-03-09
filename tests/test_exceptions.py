from unittest.mock import Mock

import pytest
from hootsweet.exceptions import (
    BadRequest,
    Forbidden,
    NotFound,
    ServerError,
    TooManyRequests,
    Unauthorized,
    detect_and_raise_error,
)
from requests import Response


@pytest.mark.parametrize(
    "status_code,exception",
    [
        (400, BadRequest),
        (401, Unauthorized),
        (403, Forbidden),
        (404, NotFound),
        (429, TooManyRequests),
        (500, ServerError),
    ],
)
def test_bad_request(status_code, exception):
    errors = {
        "errors": [
            {
                "code": 1234,
                "message": "An Error has occurred.",
                "id": "f7d32670-4e6a-48c0-a2a7-87803536a712",
                "resource": {"type": "socialProfile", "id": "7534653235"},
            }
        ]
    }
    mock_response = Mock(status_code=status_code, spec=Response)
    mock_response.json.return_value = errors

    with pytest.raises(exception):
        detect_and_raise_error(mock_response)


def test_hoot_suit_exception():
    status_code = 400
    errors = {
        "errors": [
            {
                "code": 1234,
                "message": "An Error has occurred.",
                "id": "f7d32670-4e6a-48c0-a2a7-87803536a712",
                "resource": {"type": "socialProfile", "id": "7534653235"},
            }
        ]
    }
    mock_response = Mock(status_code=status_code, spec=Response)
    mock_response.json.return_value = errors
    with pytest.raises(BadRequest) as exc:
        detect_and_raise_error(mock_response)
    assert str(exc.value) == "1234 - An Error has occurred."


def test_hoot_suit_exception_no_error():
    status_code = 430
    mock_response = Mock(status_code=status_code, spec=Response)
    mock_response.content = b"An Error has occurred."
    mock_response.json.return_value = {}
    with pytest.raises(BadRequest) as exc:
        detect_and_raise_error(mock_response)
    assert str(exc.value) == "430 - An Error has occurred."
