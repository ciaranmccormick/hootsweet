import logging
from typing import Any, Dict, List, Tuple

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

log = logging.getLogger(__name__)


def default_refresh_cb(token: Dict):
    return token


class HootSweet:
    def __init__(
        self,
        client_id,
        client_secret,
        token=None,
        redirect_uri=None,
        scope=None,
        refresh_cb=None,
        **kwargs,
    ):
        self.client_id, self.client_secret = client_id, client_secret
        token = token or {}

        if refresh_cb is None:
            self.refresh_cb = default_refresh_cb

        self.scope = scope or "offline"
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

    def authorization_url(self, state=None, **kwargs) -> Tuple[str, str]:
        return self.session.authorization_url(HOOTSUITE_AUTHORIZATION_URL, state=state)

    def fetch_token(self, code) -> Dict[str, Any]:
        return self.session.fetch_token(
            HOOTSUITE_TOKEN_URL,
            client_secret=self.client_secret,
            code=code,
            scope=self.scope,
        )

    def refresh_token(self) -> Dict[str, Any]:
        """ Refreshes OAuth2 token and calls updater."""
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

        method = kwargs.get("method", "POST" if "data" in kwargs else "GET")
        response = self.request(method, url, *args, **kwargs)

        # Extra check if expires_at missing
        if response.status_code == 401:
            self.refresh_token()
            response = self.request(method, url, *args, **kwargs)

        if not response.status_code == 200:
            raise detect_and_raise_error(response)
        else:
            return response.json()["data"]

    def get_me(self) -> Dict:
        """ Retrieves authenticated member"""
        resource = "me"
        return self._make_request(resource)

    def get_me_organizations(self) -> Dict:
        """ Retrieves the organizations that the authenticated member is in."""
        resource = "me/organizations"
        return self._make_request(resource)

    def get_me_social_profiles(self) -> Dict:
        """ Retrieves the social media profiles that the authenticated user has
        BASIC_USAGE permissions on."""
        resource = "me/socialProfiles"
        return self._make_request(resource)

    def get_social_profiles(self) -> Dict:
        """ Retrieves the social profiles that the authenticated user has access to."""
        resource = "socialProfiles"
        return self._make_request(resource)

    def get_social_profile(self, profile_id: int) -> Dict:
        """Retrieve a social profile.

        Requires BASIC_USAGE permission on the social profile.
        """
        resource = "socialProfiles/%s" % profile_id
        return self._make_request(resource)

    def get_social_profile_teams(self, profile_id: int) -> Dict:
        """Retrieves a list of team IDs with access to a social profile.

        Requires BASIC_USAGE permission on the social profile or
        ORG_MANAGE_SOCIAL_PROFILE permission on the organization that owns the
        social profile.
        """
        resource = "socialProfiles/%s/teams" % profile_id
        return self._make_request(resource)

    def get_member(self, member_id: str) -> Dict[str, Any]:
        """Retrieves a member."""
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
        """Creates a member in a Hootsuite organization. Requires organization manage
        members permission.

        Args:
            full_name: The member’s name.
            email: The member’s email.
            organization_ids: The organizations the member should be added to.
            company_name: The member’s company name.
            bio: The member’s bio.
            timezone: The member's time zone. If not provided it will default to
                'America/Vancouver'. Valid values are defined at
                http://php.net/manual/en/timezones.php.
            language: The member’s language.
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
        """Retrieves the organizations that the member is in."""
        resource = "members/%s/organizations" % member_id
        return self._make_request(resource)
