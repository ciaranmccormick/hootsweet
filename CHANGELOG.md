### Future

- Added method to get outbound messages
- Added method to reject messages
- Added method to get message review history

### 0.5.1

- Bug fix for issue [#11](https://github.com/ciaranmccormick/hootsweet/issues/11)

### 0.5.0

- Improvements to refresh token callback

### 0.4.0

- Added /messages POST endpoint
- Added /messages/{id}/approve
- Added /messages GET
- Added /messages DELETE

### 0.3.0

- Added OAuth2 workflow for authorization
- Added script to obtain access token

### 0.2.0

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
