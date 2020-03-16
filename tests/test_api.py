from unittest.mock import Mock, call, patch

import pytest
from hootsweet.api import (
    HOOTSUITE_TOKEN_URL,
    HootSweet,
    HTTPBasicAuth,
    default_refresh_cb,
)
from hootsweet.exceptions import InvalidLanguage, InvalidTimezone
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
    ("get_member", "https://platform.hootsuite.com/v1/members/1234", ("1234",)),
    (
        "get_member_organizations",
        "https://platform.hootsuite.com/v1/members/1234/organizations",
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


@patch("hootsweet.api.OAuth2Session", autospec=True)
def test_create_member_endpoint_urls(mock_session):
    response = Mock(status_code=200, spec=Response)
    mock_session.return_value.request.return_value = response
    data = {"data": {}}
    response.json.return_value = data

    token = {"access_token": "token"}
    hoot_suite = HootSweet("client_id", "client_secret", token=token)

    args = ("Joe Bloggs", "joe.bloggs@email.com", ["1234"])
    with pytest.raises(InvalidLanguage):
        hoot_suite.create_member(*args, language="rr")

    with pytest.raises(InvalidTimezone):
        hoot_suite.create_member(*args, timezone="Mars/Europa")

    assert mock_session.return_value.request.call_count == 0

    hoot_suite.create_member(*args)

    expected_url = "https://platform.hootsuite.com/v1/members"
    expected_data = {
        "fullName": "Joe Bloggs",
        "email": "joe.bloggs@email.com",
        "organizationIds": ["1234"],
        "language": "en",
        "timezone": "Europe/London",
    }
    mock_session.return_value.request.assert_called_once_with(
        "POST", expected_url, data=expected_data
    )
    mock_session.return_value.request.reset_mock()
    hoot_suite.create_member(*args, bio="a bio", company_name="ACompany")
    expected_data["bio"] = "a bio"
    expected_data["companyName"] = "ACompany"
    mock_session.return_value.request.assert_called_once_with(
        "POST", expected_url, data=expected_data
    )


def test_default_refresh_cb():
    expected = {"access_token": "access_token", "refresh_token": "refresh_token"}
    actual = default_refresh_cb(expected)
    assert expected == actual


@patch("hootsweet.api.default_refresh_cb", autospec=True)
@patch("hootsweet.api.OAuth2Session", autospec=True)
def test_refresh_token(mock_session, mock_refresh_cb):
    attrs = [
        {"status_code": c, "json.return_value": {"data": {}}} for c in [401, 200, 200]
    ]
    responses = [Mock(spec=Response, **attr) for attr in attrs]
    mock_session.return_value.request.side_effect = responses

    token = {"access_token": "access_token", "refresh_token": "refresh_token"}
    hoot_suite = HootSweet("client_id", "client_secret", token=token)

    expected_url = "https://platform.hootsuite.com/v1/me"
    hoot_suite.get_me()

    calls = [call("GET", expected_url), call("GET", expected_url)]
    assert mock_session.return_value.request.mock_calls == calls
    mock_session.return_value.refresh_token.assert_called_once_with(
        HOOTSUITE_TOKEN_URL, auth=HTTPBasicAuth("client_id", "client_secret")
    )
    mock_refresh_cb.assert_called_once()
