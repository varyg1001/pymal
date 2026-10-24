"""
Client for MyAnimeList's official API v2 (https://myanimelist.net/apiconfig).

MyAnimeList's website login is protected by a captcha, so everything that needs an
account goes through the official API and its OAuth2 flow (authorization code
with PKCE) instead.
"""

__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

import json
import os
import secrets
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib import parse

from pymal import exceptions, global_functions


__all__ = ["ApiClient", "Credentials", "default_token_file"]

API_URL = "https://api.myanimelist.net/v2"
AUTHORIZE_URL = "https://myanimelist.net/v1/oauth2/authorize"
TOKEN_URL = "https://myanimelist.net/v1/oauth2/token"

# Refresh the access token this many seconds before it really expires.
_EXPIRY_MARGIN = 60


def default_token_file(username: str) -> Path:
    """
    :return: where the tokens of ``username`` are saved: ``~/.config/pymal/<username>.json``
    """
    config_home = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return config_home / "pymal" / f"{parse.quote(username, safe='')}.json"


@dataclass
class Credentials:
    """
    :ivar client_id: the client id of your MAL API app.
    :ivar client_secret: the client secret, only for apps of the "web" type.
    :ivar access_token: empty when only the client id is known (public data only).
    :ivar refresh_token: used to get a new access token when it expires.
    :ivar expires_at: unix time the access token expires; ``0`` if unknown.
    :ivar session_id: the ``MALSESSIONID`` cookie, see :mod:`pymal.web_session`.
    :ivar user_agent: the ``User-Agent`` to use with the session; the one of its browser.
    """

    client_id: str = ""
    client_secret: str = ""
    access_token: str = ""
    refresh_token: str = ""
    expires_at: float = 0.0
    session_id: str = ""
    user_agent: str = ""


class ApiClient:
    """
    Talks to the API for one account and keeps its tokens fresh.

    :param username: the MAL username; only used to pick the default token file.
    :param token_file: where to load and save the tokens.
    """

    def __init__(self, username: str, token_file: str | os.PathLike | None = None):
        self.username = username
        self.token_file = Path(token_file) if token_file else default_token_file(username)
        self.credentials: Credentials | None = None
        self.load()

    @property
    def has_client_id(self) -> bool:
        """True when public API calls are possible."""
        return self.credentials is not None and bool(self.credentials.client_id)

    @property
    def session_id(self) -> str:
        """The ``MALSESSIONID`` cookie, or an empty string."""
        return self.credentials.session_id if self.credentials else ""

    @property
    def user_agent(self) -> str:
        return self.credentials.user_agent if self.credentials else ""

    def set_session(self, session_id: str, user_agent: str = "") -> None:
        if self.credentials is None:
            self.credentials = Credentials()
        self.credentials.session_id = session_id
        self.credentials.user_agent = user_agent

    @property
    def is_auth(self) -> bool:
        """True when there is an access token, so the account's own list can be edited."""
        return self.credentials is not None and bool(self.credentials.access_token)

    # -- token storage --------------------------------------------------------

    def load(self) -> None:
        """Load the saved tokens, if the token file exists and is readable."""
        try:
            data = json.loads(self.token_file.read_text(encoding="utf-8"))
            self.credentials = Credentials(**data)
        except (OSError, ValueError, TypeError):
            self.credentials = None

    def save(self) -> None:
        """Save the tokens to the token file (readable by the owner only)."""
        if self.credentials is None:
            return
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.token_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(asdict(self.credentials), f, indent=2)

    def set_credentials(
        self,
        client_id: str,
        access_token: str = "",
        refresh_token: str = "",
        client_secret: str = "",
        expires_at: float = 0.0,
    ) -> None:
        self.credentials = Credentials(
            client_id,
            client_secret,
            access_token,
            refresh_token,
            expires_at,
            self.session_id,
            self.user_agent,
        )

    # -- OAuth2 ---------------------------------------------------------------

    @staticmethod
    def authorization_url(
        client_id: str, redirect_uri: str | None = None
    ) -> tuple[str, str, str]:
        """
        :return: ``(url, code_verifier, state)``; open the url in a browser, and keep
            the verifier for :meth:`exchange_code`.
        """
        # MAL only supports the "plain" PKCE method: the challenge is the verifier.
        code_verifier = secrets.token_urlsafe(96)
        state = secrets.token_urlsafe(16)
        query = {
            "response_type": "code",
            "client_id": client_id,
            "code_challenge": code_verifier,
            "code_challenge_method": "plain",
            "state": state,
            # always show the login screen, so the account of the browser isn't used silently
            "force_logout": "true",
        }
        if redirect_uri:
            query["redirect_uri"] = redirect_uri
        return f"{AUTHORIZE_URL}?{parse.urlencode(query)}", code_verifier, state

    def exchange_code(
        self,
        client_id: str,
        code: str,
        code_verifier: str,
        client_secret: str = "",
        redirect_uri: str | None = None,
    ) -> None:
        """Trade the code from the redirect for tokens, and save them."""
        form = {
            "client_id": client_id,
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": code_verifier,
        }
        if client_secret:
            form["client_secret"] = client_secret
        if redirect_uri:
            form["redirect_uri"] = redirect_uri
        session = (self.session_id, self.user_agent)
        self.credentials = Credentials(
            client_id, client_secret, session_id=session[0], user_agent=session[1]
        )
        self._store_token(self._token_request(form))

    def forget(self) -> None:
        """Drop the tokens, in memory and the saved file."""
        self.credentials = None
        self.token_file.unlink(missing_ok=True)

    def refresh(self) -> None:
        """Get a new access token with the refresh token, and save it."""
        creds = self.credentials
        if creds is None or not creds.refresh_token:
            raise exceptions.UnauthenticatedAccountError(self.username)
        form = {
            "client_id": creds.client_id,
            "grant_type": "refresh_token",
            "refresh_token": creds.refresh_token,
        }
        if creds.client_secret:
            form["client_secret"] = creds.client_secret
        self._store_token(self._token_request(form))

    def _token_request(self, form: dict) -> dict:
        sock = global_functions._connect(
            TOKEN_URL,
            data=parse.urlencode(form),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if sock.status_code != 200:
            raise exceptions.MyAnimeListApiError(
                f"MAL refused the token request (HTTP {sock.status_code}): "
                f"{sock.text.strip()[:200]}",
                sock.status_code,
            )
        return sock.json()

    def _store_token(self, token: dict) -> None:
        creds = self.credentials
        creds.access_token = token["access_token"]
        creds.refresh_token = token.get("refresh_token", creds.refresh_token)
        expires_in = token.get("expires_in")
        creds.expires_at = time.time() + float(expires_in) if expires_in else 0.0
        self.save()

    # -- requests -------------------------------------------------------------

    def _headers(self) -> dict:
        creds = self.credentials
        if creds is None or not creds.client_id:
            raise exceptions.UnauthenticatedAccountError(self.username)
        if creds.access_token:
            expired = creds.expires_at and creds.expires_at - _EXPIRY_MARGIN < time.time()
            if expired and creds.refresh_token:
                self.refresh()
            return {"Authorization": f"Bearer {creds.access_token}"}
        return {"X-MAL-CLIENT-ID": creds.client_id}

    def request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        data: dict | None = None,
    ):
        """
        Call the API.

        :param method: ``GET``, ``PUT`` or ``DELETE``.
        :param path: for example ``/anime/1``; a full url (a ``paging.next``) works too.
        :param params: the query string.
        :param data: the form body.
        :return: the decoded JSON, or ``None`` when the answer has no body.
        :raises exceptions.UnauthenticatedAccountError: when there are no credentials.
        :raises exceptions.MyAnimeListApiError: when the API answers with an error.
        :raises exceptions.SiteUnavailableError: when MAL can't be reached.
        """
        url = path if path.startswith("http") else API_URL + path
        if params:
            url += ("&" if "?" in url else "?") + parse.urlencode(params)
        body = parse.urlencode(data) if data is not None else None

        for attempt in range(2):
            headers = self._headers()
            if body is not None:
                headers["Content-Type"] = "application/x-www-form-urlencoded"
            sock = global_functions._connect(
                url, data=body, headers=headers, method=method
            )
            # An access token can be revoked before it expires: refresh once and retry.
            can_refresh = self.credentials.access_token and self.credentials.refresh_token
            if sock.status_code == 401 and attempt == 0 and can_refresh:
                self.refresh()
                continue
            break

        if sock.status_code >= 400:
            raise exceptions.MyAnimeListApiError(
                f"{method} {path} failed (HTTP {sock.status_code}): {sock.text.strip()[:200]}",
                sock.status_code,
            )
        return sock.json() if sock.content else None

    def pages(self, path: str, params: dict | None = None):
        """Iterate over every item of a paged API answer (``{"data": [...], "paging": {...}}``)."""
        page = self.request("GET", path, params)
        while page:
            yield from page.get("data", [])
            next_url = page.get("paging", {}).get("next")
            page = self.request("GET", next_url) if next_url else None
