from unittest.mock import Mock, patch

import pytest
from hootsweet.api import HootSweet
from requests import Response

ENDPOINT_TEST_CASES = [
    ("get_me", "https://platform.hootsuite.com/v1/me", ()),
    ("get_me_organizations", "https://platform.hootsuite.com/v1/me/organizations", ()),
    (
        "get_me_social_profiles",
        "https://platform.hootsuite.com/v1/me/socialProfiles",
        (),
    ),
    ("get_social_profiles", "https://platform.hootsuite.com/v1/socialProfiles", ()),
    (
        "get_social_profile",
        "https://platform.hootsuite.com/v1/socialProfiles/1234",
        ("1234",),
    ),
    (
        "get_social_profile_teams",
        "https://platform.hootsuite.com/v1/socialProfiles/1234/teams",
        ("1234",),
    ),
]


@pytest.mark.parametrize("func,expected_url,args", ENDPOINT_TEST_CASES)
@patch("hootsweet.api.OAuth2Session", autospec=True)
def test_endpoint_urls(mock_session, func, args, expected_url):
    response = Mock(status_code=200, spec=Response)
    mock_session.return_value.request.return_value = response
    data = {"data": {}}
    response.json.return_value = data
    token = {"access_token": "token"}
    hoot_suite = HootSweet("client_id", "client_secret", token=token)
    actual = getattr(hoot_suite, func)(*args)
    mock_session.return_value.request.assert_called_once_with("GET", expected_url)
    assert actual == data["data"]
