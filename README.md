## HootSweet

A python API for the HootSuite REST API.

### Installation

```shell
pip install hootsweet
```

### Usage

```python
from hootsweet import HootSweet

client_id = "Your-HootSuite-Client-ID"
client_secret = "Your-HootSuite-Client-Secret"
redirect_uri = "http://redirect.uri/"

def handle_refresh(token):
    # callback function to save token to a database or file
    save_token_to_db(token)

client = HootSweet(client_id, client_secret, redirect_uri=redirect_uri, refresh_cb=handle_refresh)

# Step 1 get authorization url from HootSuite
url, state = client.authorization_url()

# Step 2 go to url above and get OAuth2 code
token = client.fetch_token(code)

# client.token now contains your authentication token
# Step 3 (optional) refresh token periodically, this automatically calls handle_refresh
token = client.refresh_token()

# retrieve data from https://platform.hootsuite.com/v1/me
me = client.get_me()

# retrieve authenticated members organizations https://platform.hootsuite.com/v1/me/organizations
organizations = client.get_me_organizations()
```
