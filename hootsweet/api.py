from typing import Dict

from hootsweet.exceptions import detect_and_raise_error
from requests import request

HOOTSUITE_BASE_URL = "https://platform.hootsuite.com"
API_VERSION = "v1"
API_URL = "%s/%s" % (HOOTSUITE_BASE_URL, API_VERSION)


class HootSweet:
    def __init__(self, access_token=None, **kwargs):
        self._access_token = access_token

    def _make_request(self, resource, *args, **kwargs) -> Dict:
        url = "%s/%s" % (API_URL, resource)

        method = kwargs.get("method", "POST" if "data" in kwargs else "GET")
        headers = kwargs.get("headers", {})
        headers.update({"Authorization": "Bearer %s" % self._access_token})
        kwargs["headers"] = headers
        response = request(method, url, *args, **kwargs)

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
