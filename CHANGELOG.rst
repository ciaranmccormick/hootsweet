#########
Changelog
#########

-----
0.7.1
-----

- Added messages with media section to readme


-----
0.7.0
-----

- Fixed bug releating to scheduling messages with media attached.

-----
0.6.6
-----

- Added method to create media url
- Added method to get media url status

-----
0.6.5
-----

### 0.6.0

- Added method to get outbound messages
- Added method to reject messages
- Added method to get message review history

-----
0.5.1
-----

- Bug fix for issue `#11 <https://github.com/ciaranmccormick/hootsweet/issues/11>`_

-----
0.5.0
-----

- Improvements to refresh token callback

-----
0.4.0
-----

- Added /messages POST endpoint
- Added /messages/{id}/approve
- Added /messages GET
- Added /messages DELETE

-----
0.3.0
-----

- Added OAuth2 workflow for authorization
- Added script to obtain access token

-----
0.2.0
-----

- Added basic API access authorizing using an access token
- Endpoints available are;

  - /me
  - /me/organizations
  - /me/socialProfiles
  - /socialProfiles
  - /socialProfiles/{profile}
  - /socialProfiles/{profile}/teams

- Added HTTP exception handling
- Added initial tests
