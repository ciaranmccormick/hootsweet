import datetime
import json
from unittest.mock import Mock, PropertyMock, call, patch

import pytest
from hootsweet.api import (
    HOOTSUITE_TOKEN_URL,
    ISO_FORMAT,
    HootSweet,
    HTTPBasicAuth,
    default_refresh_cb,
)
from hootsweet.constants import Reviewer
from hootsweet.exceptions import InvalidLanguage, InvalidTimezone
from requests import Response
from requests_oauthlib import OAuth2Session

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
    ("get_message", "https://platform.hootsuite.com/v1/messages/1234", ("1234",)),
]

DELETE_ENDPOINTS = [
    ("delete_message", "https://platform.hootsuite.com/v1/messages/1234", ("1234",)),
]

test_token = {
    "access_token": "access_token",
    "refresh_token": "refresh_token",
    "expires_in": 10,
}


@pytest.mark.parametrize("func,expected_url,args", DELETE_ENDPOINTS)
@patch("hootsweet.api.OAuth2Session", spec=OAuth2Session, token=test_token)
def test_endpoint_urls(mock_session, func, args, expected_url):
    response = Mock(status_code=200, spec=Response)
    mock_session.return_value.request.return_value = response
    data = {"data": {}}
    response.json.return_value = data
    hoot_suite = HootSweet("client_id", "client_secret", token=test_token)
    actual = getattr(hoot_suite, func)(*args)
    mock_session.return_value.request.assert_called_once_with("DELETE", expected_url)
    assert actual == data["data"]


@pytest.mark.parametrize("func,expected_url,args", ENDPOINT_TEST_CASES)
@patch("hootsweet.api.OAuth2Session", spec=OAuth2Session, token=test_token)
def test_delete_endpoint_urls(mock_session, func, args, expected_url):
    response = Mock(status_code=200, spec=Response)
    mock_session.return_value.request.return_value = response
    data = {"data": {}}
    response.json.return_value = data
    token = {"access_token": "token"}
    hoot_suite = HootSweet("client_id", "client_secret", token=token)
    actual = getattr(hoot_suite, func)(*args)
    mock_session.return_value.request.assert_called_once_with("GET", expected_url)
    assert actual == data["data"]


@patch("hootsweet.api.OAuth2Session", spec=OAuth2Session, token=test_token)
def test_schedule_message(mock_session):
    response = Mock(status_code=200, spec=Response)
    mock_session.return_value.request.return_value = response
    data = {"data": {}}
    response.json.return_value = data
    hoot_suite = HootSweet("client_id", "client_secret", token=test_token)
    text = "An example message."
    ids_ = ["1234", "12345"]
    send_time = datetime.datetime(2020, 1, 1, 13, 10, 14)
    hoot_suite.schedule_message(text, ids_, send_time=send_time)
    expected_json = json.dumps(
        {
            "text": text,
            "socialProfileIds": ids_,
            "scheduledSendTime": send_time.strftime(ISO_FORMAT),
            "emailNotification": False,
        }
    )
    expected_url = "https://platform.hootsuite.com/v1/messages"
    mock_session.return_value.request.assert_called_once_with(
        "POST", expected_url, data=expected_json
    )


@patch("hootsweet.api.OAuth2Session", spec=OAuth2Session, token=test_token)
def test_approve_message(mock_session):
    response = Mock(status_code=200, spec=Response)
    mock_session.return_value.request.return_value = response
    data = {"data": {}}
    response.json.return_value = data
    hoot_suite = HootSweet("client_id", "client_secret", token=test_token)

    message_id = "1234"
    sequence = 11
    reviewer_type = Reviewer.EXTERNAL

    hoot_suite.approve_message(
        message_id=message_id, sequence_number=sequence, reviewer_type=Reviewer.EXTERNAL
    )
    expected_json = json.dumps(
        {"sequenceNumber": sequence, "reviewerType": reviewer_type.name}
    )
    expected_url = "https://platform.hootsuite.com/v1/messages/%s/approve" % message_id
    mock_session.return_value.request.assert_called_once_with(
        "POST", expected_url, data=expected_json
    )


@patch("hootsweet.api.OAuth2Session", spec=OAuth2Session, token=test_token)
def test_create_member_endpoint_urls(mock_session):
    response = Mock(status_code=200, spec=Response)
    mock_session.return_value.request.return_value = response
    mock_session.return_value.token = {"expires_in": 10}
    data = {"data": {}}
    response.json.return_value = data

    hoot_suite = HootSweet("client_id", "client_secret", token=test_token)

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
@patch("hootsweet.api.OAuth2Session", spec=OAuth2Session, token=test_token)
def test_refresh_token(mock_session, mock_refresh_cb):
    attrs = [
        {"status_code": c, "json.return_value": {"data": {}}} for c in [401, 200, 200]
    ]
    responses = [Mock(spec=Response, **attr) for attr in attrs]
    mock_session.return_value.request.side_effect = responses

    hoot_suite = HootSweet("client_id", "client_secret", token=test_token)

    expected_url = "https://platform.hootsuite.com/v1/me"
    hoot_suite.get_me()

    calls = [call("GET", expected_url), call("GET", expected_url)]
    assert mock_session.return_value.request.mock_calls == calls
    mock_session.return_value.refresh_token.assert_called_once_with(
        HOOTSUITE_TOKEN_URL, auth=HTTPBasicAuth("client_id", "client_secret")
    )
    mock_refresh_cb.assert_called_once()


@patch("hootsweet.api.OAuth2Session", autospec=True)
def test_negative_expires_in(mock_session):
    attrs = [{"status_code": c, "json.return_value": {"data": {}}} for c in [200, 200]]
    responses = [Mock(spec=Response, **attr) for attr in attrs]
    mock_session.return_value.request.side_effect = responses
    mock_session.return_value.token = {"expires_in": -10}

    mock_refresh_cb = Mock(__name__="refresh_cb")
    hoot_suite = HootSweet(
        "client_id", "client_secret", token=test_token, refresh_cb=mock_refresh_cb
    )

    hoot_suite.get_me()

    mock_session.return_value.refresh_token.assert_called_once_with(
        HOOTSUITE_TOKEN_URL, auth=HTTPBasicAuth("client_id", "client_secret")
    )
    mock_refresh_cb.assert_called_once()
