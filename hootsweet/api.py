"""
HootSweet Client
================

This module provides a client, HootSweet, to interact with the Hootsuite REST 1.0
API.

"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple

from hootsweet.constants import MessageState, Reviewer
from hootsweet.exceptions import (
    InvalidLanguage,
    InvalidTimezone,
    detect_and_raise_error,
)
from hootsweet.locale import is_valid_language, is_valid_timezone
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

HOOTSUITE_BASE_URL = "https://platform.hootsuite.com"
HOOTSUITE_AUTHORIZATION_URL = "%s/oauth2/auth" % HOOTSUITE_BASE_URL
HOOTSUITE_TOKEN_URL = "%s/oauth2/token" % HOOTSUITE_BASE_URL
API_VERSION = "v1"
API_URL = "%s/%s" % (HOOTSUITE_BASE_URL, API_VERSION)
ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

log = logging.getLogger(__name__)


def default_refresh_cb(token: Dict):
    return token


class HootSweet:
    """A client for interacting with the Hootsuite REST API.

    Args:
        client_id (str): A Hootsuite client id.
        client_secret (str): A Hootsuite client secret.
        token (Dict): A token dictionary containing the `access_token`,
            `refresh_token`, `expires_on` and `expires_in` keys.
        redirect_uri (str): The callback uri registered with Hootsuite.
        scope (str): The OAuth2 scope.
        refresh_cb (callable): A function to be called when a token is refreshed.

    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token: Dict = None,
        redirect_uri: str = None,
        scope: str = "offline",
        refresh_cb=None,
        **kwargs,
    ):
        self.client_id, self.client_secret = client_id, client_secret
        token = token or {}

        self.refresh_cb = refresh_cb
        if self.refresh_cb is None:
            self.refresh_cb = default_refresh_cb

        self.scope = scope
        self.session = OAuth2Session(
            client_id,
            token=token,
            redirect_uri=redirect_uri,
            auto_refresh_url=HOOTSUITE_TOKEN_URL,
            scope=self.scope,
            token_updater=self.refresh_cb,
        )
        self.timeout = kwargs.get("timeout", None)

    def __getattr__(self, name):
        # Proxies any attributes from HootSweet to OAuth2Session
        return getattr(self.session, name)

    def authorization_url(self, state: str = None, **kwargs) -> Tuple[str, str]:
        """Get a Hootsuite authorization url.

        Args:
            state (str): An opaque value used by the client to maintain
                state between the request and callback.

        """
        return self.session.authorization_url(HOOTSUITE_AUTHORIZATION_URL, state=state)

    def fetch_token(self, code: str) -> Dict[str, Any]:
        """Fetch a Hootsuite OAuth2 token.

        Args:
            code (str): The authorization code obtained from Hootsuite.

        """
        return self.session.fetch_token(
            HOOTSUITE_TOKEN_URL,
            client_secret=self.client_secret,
            code=code,
            scope=self.scope,
        )

    def refresh_token(self) -> Dict[str, Any]:
        """ Refresh the OAuth2 token and call token updater."""
        log.debug("Refreshing access token.")
        token = {}
        if self.refresh_cb:
            token = self.session.refresh_token(
                HOOTSUITE_TOKEN_URL,
                auth=HTTPBasicAuth(self.client_id, self.client_secret),
            )
            log.debug("Calling refresh callback %s." % self.refresh_cb.__name__)
            self.refresh_cb(token)
        return token

    def _make_request(self, resource, *args, **kwargs) -> Dict[str, Any]:
        url = "%s/%s" % (API_URL, resource)

        if self.timeout is not None and "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout

        expires_in = self.token.get("expires_in", 0)
        if expires_in <= 0:
            self.refresh_token()

        method = kwargs.pop("method", "POST" if "data" in kwargs else "GET")
        response = self.request(method, url, *args, **kwargs)

        if response.status_code == 401:
            self.refresh_token()
            response = self.request(method, url, *args, **kwargs)

        if not response.status_code == 200:
            raise detect_and_raise_error(response)
        else:
            if method == "DELETE":
                return {}
            else:
                return response.json()["data"]

    def get_me(self) -> Dict:
        """ Retrieve the currently authenticated member."""
        resource = "me"
        return self._make_request(resource)

    def get_me_organizations(self) -> Dict:
        """ Retrieve the organizations that the authenticated member is in."""
        resource = "me/organizations"
        return self._make_request(resource)

    def get_me_social_profiles(self) -> Dict:
        """Retrieve the social media profiles that the authenticated user has
        basic usage permissions on.

        """
        resource = "me/socialProfiles"
        return self._make_request(resource)

    def get_social_profiles(self) -> Dict:
        """Retrieve the social profiles that the authenticated user has access to.

        """
        resource = "socialProfiles"
        return self._make_request(resource)

    def get_social_profile(self, profile_id: int) -> Dict:
        """Retrieve a social profile.

        Args:
            profile_id (int): The social profile id.

        """
        resource = "socialProfiles/%s" % profile_id
        return self._make_request(resource)

    def get_social_profile_teams(self, profile_id: int) -> List:
        """ Retrieve a list of team IDs with access to a social profile.

        Args:
            profile_id (int): The social profile id.

        """
        resource = "socialProfiles/%s/teams" % profile_id
        return self._make_request(resource)

    def get_member(self, member_id: str) -> Dict[str, Any]:
        """Retrieve a member.

        Args:
            member_id (str): The Hootsuite member id.

        """
        resource = "members/%s" % member_id
        return self._make_request(resource)

    def create_member(
        self,
        full_name: str,
        email: str,
        organization_ids: List[int],
        company_name: str = None,
        bio: str = None,
        timezone: str = "Europe/London",
        language: str = "en",
    ) -> Dict[str, Any]:
        """Create a member in a Hootsuite organization.

        Args:
            full_name (str): The member’s name.
            email (str): The member’s email.
            organization_ids (List[int]): The organizations the member should be
                added to.
            company_name (str): The member’s company name.
            bio (str): The member’s bio.
            timezone (str): The member's time zone. Defaults to "Europe/London"
            language (str): The member’s language. Defaults to "en"

        """
        resource = "members"
        if not is_valid_language(language):
            raise InvalidLanguage("%s is not a valid language." % language)

        if not is_valid_timezone(timezone):
            raise InvalidTimezone("%s is not a valid timezone." % timezone)

        data = {
            "fullName": full_name,
            "email": email,
            "organizationIds": organization_ids,
            "timezone": timezone,
            "language": language,
        }

        if company_name:
            data["companyName"] = company_name

        if bio:
            data["bio"] = bio

        return self._make_request(resource, data=data)

    def get_member_organizations(self, member_id: str) -> List[Dict[str, Any]]:
        """Retrieve the organizations that the member is in.

        Args:
            member_id (str): A Hootsuite member id.

        """
        resource = "members/%s/organizations" % member_id
        return self._make_request(resource)

    def schedule_message(
        self, text: str, social_profile_ids: List[str], send_time: datetime, **kwargs
    ):
        """Schedule a message to send on one or more social profiles.

        Args:
            text (str): The text of the message.
            social_profile_ids (List[str]): A list of ids of social profiles that
                will publish the message.
            send_time (datetime): Time to send the message in UTC time.

        """
        resource = "messages"
        assert isinstance(send_time, datetime), "send_time must be a datetime"

        # assume send_time in UTC time
        send_time_str = send_time.strftime(ISO_FORMAT)
        data = {
            "text": text,
            "socialProfileIds": social_profile_ids,
            "scheduledSendTime": send_time_str,
            "emailNotification": False,
        }
        data.update(kwargs)
        json_ = json.dumps(data)
        return self._make_request(resource, method="POST", data=json_)

    def get_outbound_messages(
        self,
        start_time: datetime,
        end_time: datetime,
        state: MessageState = None,
        social_profile_ids: List[int] = None,
        limit: int = 50,
        include_unscheduled_review_messages: bool = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """Retrieve a list of outbound messages.

        Args:
            start_time (datetime): The start date range of the messages returned.
            end_time (datetime): The end date range of the messages returned.
            state (MessageState): The state of the messages returned.
            social_profile_ids (List[int]): The ids of social profiles of the
                messages returned.
            limit (int): Maximum number of messages to be returned. Defaults to 50.
            include_unscheduled_review_messages(bool): Flag to retrieve unscheduled
                (Send Now) review messages on top of scheduled ones retrieved from
                time range query.

        """

        resource = "messages"
        params = {}

        assert isinstance(start_time, datetime), "start_time must be a datetime"
        params["startTime"] = start_time.strftime(ISO_FORMAT)

        assert isinstance(end_time, datetime), "end_time must be a datetime"
        params["endTime"] = end_time.strftime(ISO_FORMAT)

        params["limit"] = limit

        if state is not None:
            params["state"] = state.name

        if social_profile_ids is not None:
            params["socialProfileIds"] = social_profile_ids

        if include_unscheduled_review_messages is not None:
            params["includeUnscheduledReviewMsgs"] = include_unscheduled_review_messages

        return self._make_request(resource, params=params)

    def get_message(self, message_id: str) -> Dict[str, Any]:
        """ Retrieve a message.

        Args:
            message_id (str): The Hootsuite message id.

        """
        resource = "messages/%s" % message_id
        return self._make_request(resource)

    def delete_message(self, message_id: str) -> Dict[str, Any]:
        """Delete a message.

        Args:
            message_id (str): The Hootsuite message id.
        """
        resource = "messages/%s" % message_id
        return self._make_request(resource, method="DELETE")

    def approve_message(
        self, message_id: str, sequence_number: int, reviewer_type: Reviewer
    ):
        """Approve a message.

        Args:
            message_id (str): A Hootsuite message id.
            sequence_number (int): The sequence number of the message.
            reviewer_type (Reviewer): The actor that will be approving he message.

        """
        resource = "messages/%s/approve" % message_id
        data = {"sequenceNumber": sequence_number, "reviewerType": reviewer_type.name}
        json_ = json.dumps(data)
        return self._make_request(resource, method="POST", data=json_)

    def reject_message(
        self,
        message_id: str,
        reason: str,
        sequence: int,
        reviewer_type: Reviewer = None,
        **kwargs,
    ):
        """Reject a message.

        Args:
            message_id (str): The Hootsuite message id.
            reason (str): The rejection reason.
            sequence (int): The sequence number of the message.
            reviewer_type (Reviewer): The actor that will be rejecting the message.

        """
        resource = "messages/%s/reject" % message_id
        data = {"reason": reason, "sequenceNumber": sequence}

        if reviewer_type is not None:
            data["reviewerType"] = reviewer_type.name
        return self._make_request(resource, method="POST", data=data)

    def get_message_review_history(self, message_id: str) -> Dict:
        """ Get a messages prescreening review history.

        Args:
            message_id (str): The Hootsuite message id.
        """
        resource = "messages/%s/history" % message_id
        return self._make_request(resource)
