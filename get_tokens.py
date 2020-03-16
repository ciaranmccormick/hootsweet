import argparse
import threading
import webbrowser
from os import environ
from pprint import pprint
from urllib.parse import urlparse

import cherrypy
from hootsweet import HootSweet
from hootsweet.exceptions import HootSuiteException
from oauthlib.oauth2.rfc6749.errors import InvalidClientError, InvalidGrantError

SUCCESS_HTML = """
        <h1>You can now access the HootSuite API.<h1>
        </br><h3>Please close this window</h3>"""

FAILURE_HTML = """
    <h1>Authorization unsuccessful - {error}</h1>
    <p>{error_description}</p>
    <p>{error_hint}</p>"""


class HootSuiteServer:
    def __init__(
        self, client_id, client_secret, redirect_uri="http://localhost:8000/",
    ):
        self.client = HootSweet(client_id, client_secret, redirect_uri=redirect_uri)

    def authorize(self):
        url, _ = self.client.authorization_url()

        # Navigate to the authorization url
        threading.Timer(1, webbrowser.open, args=(url,)).start()

        # Create a endpoint that matches the redirect uri
        urlparams = urlparse(self.client.redirect_uri)
        cherrypy.config.update(
            {
                "server.socket_host": urlparams.hostname,
                "server.socket_port": urlparams.port,
                "log.screen": False,
            }
        )
        cherrypy.quickstart(self, urlparams.path)

    @cherrypy.expose
    def index(self, state, code=None, error=None, **kwargs):
        error_html = None
        if code:
            try:
                self.client.fetch_token(code=code)
            except InvalidGrantError:
                error_html = FAILURE_HTML.format(
                    error="invalid_grant",
                    error_description="The supplied 'code' is invalid.",
                    error_hint="Make sure that the authorization 'code' supplied is correct.",
                )
            except InvalidClientError:
                error_html = FAILURE_HTML.format(
                    error="invalid_client",
                    error_description="Client authentication failed.",
                    error_hint="Client secret could be incorrect.",
                )
        else:
            error_html = FAILURE_HTML.format(error=error, **kwargs)

        self._exit_cherry_py()
        return error_html or SUCCESS_HTML

    def _exit_cherry_py(self):
        if cherrypy.engine.state == cherrypy.engine.states.STARTED:
            threading.Timer(1, cherrypy.engine.exit).start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve HootSuite tokens.")
    parser.add_argument("--client_id")
    parser.add_argument("--client_secret")
    parser.add_argument("--redirect_uri")
    args = parser.parse_args()

    try:
        client_id = args.client_id or environ["HOOTSUITE_CLIENT_ID"]
        client_secret = args.client_secret or environ["HOOTSUITE_CLIENT_SECRET"]
    except KeyError as exc:
        k = exc.args[0]
        pretty_k = "_".join(k.lower().split("_")[1:])
        print("Please either set %s or pass --%s to this command." % (k, pretty_k))
        exit()
    redirect_uri = args.redirect_uri or environ.get("HOOTSUITE_REDIRECT_URI")
    server = HootSuiteServer(client_id, client_secret, redirect_uri)
    server.authorize()

    try:
        profile = server.client.get_me()
    except HootSuiteException as exc:
        print(exc.args)
        exit()

    print(
        "You can successfully access the HootSuite API for the user {}\n.".format(
            profile["fullName"]
        )
    )
    print("TOKEN\n=======")
    print("token = ", end="")
    pprint(server.client.token)
