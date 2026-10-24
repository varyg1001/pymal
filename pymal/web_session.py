"""
Experimental: use the website session of a browser (the ``MALSESSIONID`` cookie).

MyAnimeList's login page has a captcha that only a person in a browser can pass, so
pymal can't log in with a password. A person can log in in their own browser and give
pymal the cookie of that session; pymal then reads and edits the list through the
website's own endpoints. Those aren't documented or versioned, and they fall under
MAL's website Terms of Use, so this can break at any time. Prefer the official API
(:mod:`pymal.mal_api`) when you can.
"""

__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

import json
import re
from pathlib import Path

from pymal import consts, exceptions, global_functions


__all__ = ["WebSession", "cookie_header_from_file"]

# The cookies the website needs to treat a request as logged in.
_LOGIN_COOKIES = ("MALSESSIONID", "MALHLOGSESSID", "is_logged_in")


def cookie_header_from_file(path) -> str:
    """
    Read a browser's cookie export (the Netscape ``cookies.txt`` format, made by
    extensions like "Get cookies.txt") and build the ``Cookie`` header from the
    login cookies of myanimelist.net. Nothing else is kept from the file.

    :raises ValueError: when the file has no ``MALSESSIONID`` cookie.
    """
    cookies = {}
    for line in Path(path).read_text(errors="ignore").splitlines():
        line = line.strip().removeprefix("#HttpOnly_")
        parts = line.split("\t")
        if (
            line
            and not line.startswith("#")
            and len(parts) >= 7
            and parts[0].lstrip(".").endswith("myanimelist.net")
            and parts[5] in _LOGIN_COOKIES
        ):
            cookies[parts[5]] = parts[6]
    if "MALSESSIONID" not in cookies:
        raise ValueError(f"No MALSESSIONID cookie for myanimelist.net in {path}")
    return "; ".join(f"{name}={value}" for name, value in cookies.items())


class WebSession:
    """
    :param session_id: the value of the ``MALSESSIONID`` cookie of a logged in browser.
    :param username: only used in error messages.
    :param user_agent: the ``User-Agent`` of that browser; a recent Chrome one by default.
    """

    def __init__(self, session_id: str, username: str = "", user_agent: str = ""):
        session_id = session_id.strip().strip("'\"")
        # A bare cookie value, "MALSESSIONID=value", or a whole Cookie header are all fine.
        if ";" not in session_id and "=" in session_id:
            session_id = session_id.removeprefix("MALSESSIONID=")
        self.session_id = session_id
        self.user_agent = user_agent or consts.BROWSER_USER_AGENT
        self.username = username
        self._csrf_token = ""

    def _headers(self, extra: dict | None = None) -> dict:
        cookie = (
            self.session_id
            if "=" in self.session_id
            else f"MALSESSIONID={self.session_id}"
        )
        # The website only sees a browser as logged in with this flag cookie as well.
        if "is_logged_in=" not in cookie:
            cookie += "; is_logged_in=1"
        headers = {"Cookie": cookie, **(extra or {})}
        headers["User-Agent"] = self.user_agent
        return headers

    def _expired(self, sock) -> exceptions.UnauthenticatedAccountError:
        return exceptions.UnauthenticatedAccountError(
            f"MAL refused the session of '{self.username}' (HTTP {sock.status_code}: "
            f"{sock.text.strip()[:150]}). The MALSESSIONID cookie is probably expired or "
            "not the cookie of a logged in browser. Log in in the browser again and use "
            "the new cookie."
        )

    @property
    def csrf_token(self) -> str:
        """The token the website wants with every change; every page carries one."""
        if not self._csrf_token:
            sock = global_functions._connect(
                consts.HOST_NAME + "/", headers=self._headers()
            )
            match = re.search(r"<meta name=.csrf_token. content=.([^'\"]+)", sock.text)
            if sock.status_code != 200 or match is None:
                raise self._expired(sock)
            # A visitor who isn't logged in gets the page with a "Login" link.
            if 'id="malLogin"' in sock.text:
                raise exceptions.UnauthenticatedAccountError(
                    f"MAL doesn't see the MALSESSIONID cookie as logged in ('{self.username}'). "
                    "Copy the value of the cookie again from a browser where you are logged in "
                    "(only the value, not 'MALSESSIONID=')."
                )
            self._csrf_token = match.group(1)
        return self._csrf_token

    def list_items(self, kind: str, username: str) -> list:
        """
        :param kind: ``anime`` or ``manga``.
        :return: every entry (dicts) of the whole list of ``username``, private or not.
        """
        items = []
        while True:
            url = f"{consts.HOST_NAME}/{kind}list/{username}/load.json?status=7&offset={len(items)}"
            sock = global_functions._connect(url, headers=self._headers())
            if sock.status_code != 200:
                raise self._expired(sock)
            page = sock.json()
            if not isinstance(page, list) or not page:
                return items
            items.extend(page)

    def _ajax_headers(self) -> dict:
        # What the website's own scripts (jQuery) send; without X-Requested-With the
        # website answers with a whole web page instead of JSON.
        return self._headers(
            {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Origin": consts.HOST_NAME,
                "Referer": consts.HOST_NAME + "/",
            }
        )

    def post_json(self, path: str, payload: dict):
        """
        POST like the website's scripts do: the JSON text, with the csrf token inside it,
        as the body. The website answers with JSON.

        :raises exceptions.MyAnimeListApiError: when it doesn't (wrong address, changed format).
        """
        body = json.dumps({**payload, "csrf_token": self.csrf_token})
        sock = global_functions._connect(
            consts.HOST_NAME + path,
            data=body,
            headers=self._ajax_headers(),
            method="POST",
        )
        self._check(path, sock)
        try:
            sock.json()
        except ValueError:
            raise exceptions.MyAnimeListApiError(
                f"POST {path} didn't answer with JSON but with a web page "
                f"(HTTP {sock.status_code}); the website's format may have changed.",
                sock.status_code,
            ) from None
        return sock

    def post_form(self, path: str):
        """POST only the csrf token as a form (what delete wants); returns the response."""
        sock = global_functions._connect(
            consts.HOST_NAME + path,
            data=f"csrf_token={self.csrf_token}",
            headers=self._ajax_headers(),
            method="POST",
        )
        self._check(path, sock)
        return sock

    def _check(self, path: str, sock) -> None:
        if sock.status_code in (401, 403):
            raise self._expired(sock)
        try:
            body = sock.json()
        except ValueError:
            body = None
        errors = (
            body.get("errors") or body.get("error") if isinstance(body, dict) else None
        )
        if errors:
            raise exceptions.MyAnimeListApiError(
                f"POST {path} was refused: {str(errors)[:200]}", sock.status_code
            )
        if sock.status_code >= 400:
            raise exceptions.MyAnimeListApiError(
                f"POST {path} failed (HTTP {sock.status_code}): {sock.text.strip()[:200]}",
                sock.status_code,
            )
