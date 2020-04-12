==========
Hootsweet
==========

.. image:: https://img.shields.io/pypi/v/hootsweet
    :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/hootsweet
    :alt: PyPI Versions

.. image:: https://img.shields.io/pypi/format/hootsweet
    :alt: PyPi Format

.. image:: https://requires.io/github/ciaranmccormick/hootsweet/requirements.svg?branch=develop
    :target: https://requires.io/github/ciaranmccormick/hootsweet/requirements/?branch=develop
    :alt: Requirements Status

.. image:: https://readthedocs.org/projects/hootsweet/badge/?version=latest
    :target: https://hootsweet.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

A python API for the HootSuite REST API.

------------
Installation
------------

.. code-block:: shell

    pip install hootsweet

-----
Usage
-----

.. code-block:: python

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


Messages
=========

.. code-block:: python

    token = {
    "access_token": "e9a90a81-xf2d-dgh3-cfsd-23jhvn76",
    "token_Type": "Bearer",
    "expires_in": 2592000,
    "refresh_token": "82d82cf4-76gf-gfds-nt3k-lzpo12jg",
    "scope": "offline"
    }

    client = HootSweet("client_id", "client_secret", token=token)

    # Schedule a message
    text = "A message"
    social_profile_ids = ["1234", "12345"]
    send_time = datetime(2020, 1, 1, 12, 40, 15)
    message = client.schedule_message(text=text, social_profile_ids=social_profile_ids,  send_time=send_time)

    # Get message
    message = client.get_message(message_id="98765")

    # Delete message
    client.delete_message(message_id="98765")