__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

import os
from pathlib import Path
from urllib import request

import singleton_factory

from pymal import exceptions, global_functions, mal_api, web_session
from pymal.consts import HOST_NAME
from pymal.decorators import load


__all__ = ["Account"]


class Account(metaclass=singleton_factory.SingletonFactory):
    """
    Object that keeps all the account data in MAL.

    MAL's website login has a captcha, so the account's own list is reached through
    the official API (https://myanimelist.net/apiconfig): call :meth:`authorize` once
    (it saves the tokens), or :meth:`login` with tokens you already have.
    Public data of any account works without logging in.
    """

    def __init__(self, username: str, *, token_file: str | None = None):
        """
        :param username: The account username.
        :type username: str
        :param token_file: where the API tokens are saved and loaded from;
            by default ``~/.config/pymal/<username>.json``. Tokens saved by an
            earlier :meth:`authorize` are loaded automatically.
        :type token_file: str or None
        """
        from pymal.account_objects import account_animes, account_mangas

        self.__username = username
        self.connect = global_functions.connect
        self.__user_id = None
        self.__api = mal_api.ApiClient(username, token_file)

        self._main_profile_url = request.urljoin(HOST_NAME, f"profile/{self.username:s}")

        self.__animes = account_animes.AccountAnimes(self)
        self.__mangas = account_mangas.AccountMangas(self)
        self.__friends = None
        self.__image_url = ""

        self._is_loaded = False

    @property
    def username(self) -> str:
        """

        :returns: the user name.
        :rtype: str
        """
        return self.__username

    @property
    def user_id(self) -> int:
        """
        :returns: the user id. If unknown loading it.
        :rtype: int
        """
        if self.__user_id is None:
            import re

            ret = self.connect(self._main_profile_url)
            # The message button carries the id: data-ga-click-param="uid:<id>"
            match = re.search(r"uid:(\d+)", ret) or re.search(
                r'name="profileMemId"[^>]*value="(\d+)"', ret
            )
            if match is None:
                raise exceptions.FailedToParseError(f"user id of {self.username}")
            self.__user_id = int(match.group(1))
        return self.__user_id

    @property
    def mangas(self):
        """
        :returns: list of account's mangas.
        :rtype: :class:`account_objects.account_mangas.AccountMangas`
        """
        return self.__mangas

    @property
    def animes(self):
        """
        :returns: list of account's animes.
        :rtype: :class:`account_objects.account_animes.AccountAnimes`
        """
        return self.__animes

    @property
    def friends(self) -> set:
        """
        :returns: list of account's friends.
        :rtype: :class:`account_objects.account_friends.AccountFriends`
        """
        from pymal.account_objects import account_friends

        if self.__friends is None:
            self.__friends = account_friends.AccountFriends(self)
        return self.__friends

    def search(self, search_line: str, is_anime: bool = True) -> map:
        """
        Searching like regular search but switching all the object in "my" lists to the "my" objects.

        :param search_line: the search line.
        :type search_line: str
        :param is_anime: True is searching for anime, False for manga.
        :type is_anime: bool
        :returns: searched objects
        :rtype: map
        """
        from pymal import searches

        if is_anime:
            results = searches.search_animes(search_line)
            account_object_list = self.animes
        else:
            results = searches.search_mangas(search_line)
            account_object_list = self.mangas

        def get_object(result):
            if result not in account_object_list:
                return result
            # if account_object_list was set:
            #     return account_object_list.intersection([result]).pop()
            return list(filter(lambda x: x == result, account_object_list))[0]

        return map(get_object, results)

    def authorize(
        self,
        client_id: str,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
        open_browser: bool = True,
    ) -> None:
        """
        Log in through MAL's OAuth2 page; asks for input, so run it in a terminal.
        You need an API app (https://myanimelist.net/apiconfig) first. The tokens are
        saved, so this is needed only once; they are refreshed automatically.

        It shows a link (and opens it); allow the app, and paste the address your browser
        was redirected to (or just its ``code`` value).

        :param client_id: the client id of your API app.
        :param client_secret: the client secret; only for apps of the "web" type.
        :param redirect_uri: only needed if the app has several redirect urls.
        :param open_browser: open the link in the default browser.
        :exception exceptions.MyAnimeListApiError: when MAL refuses the code.
        """
        import webbrowser
        from urllib import parse

        url, verifier, state = self.__api.authorization_url(client_id, redirect_uri)
        if open_browser:
            webbrowser.open(url)
        pasted = input(
            f"Open this link and allow the app:\n\n  {url}\n\n"
            "Then paste the address you were redirected to (or its code): "
        ).strip()

        query = parse.parse_qs(parse.urlsplit(pasted).query)
        code = query["code"][0] if "code" in query else pasted
        if "state" in query and query["state"][0] != state:
            raise ValueError("The state doesn't match; start again.")
        self.__api.exchange_code(
            client_id, code, verifier, client_secret or "", redirect_uri
        )
        # The browser may have been logged in as somebody else: don't keep their tokens.
        name = self.api("GET", "/users/@me").get("name", "")
        if name.lower() != self.username.lower():
            self.__api.forget()
            raise exceptions.UnauthenticatedAccountError(
                f"You logged in as '{name}', not '{self.username}'. Log out of MAL "
                "in the browser (or use that username) and try again."
            )

    def login(
        self,
        client_id: str,
        access_token: str = "",
        refresh_token: str = "",
        client_secret: str = "",
        save: bool = False,
    ) -> None:
        """
        Use API credentials you already have, instead of :meth:`authorize`.
        With only a ``client_id``, public data (like another user's public list) is
        readable; editing a list needs an ``access_token``.

        :param save: also save them to the token file.
        """
        self.__api.set_credentials(client_id, access_token, refresh_token, client_secret)
        if save:
            self.__api.save()

    def login_with_cookie(
        self, session_id: "str | dict", save: bool = False, user_agent: str = ""
    ) -> None:
        """
        Experimental, see :mod:`pymal.web_session`: use the website session of a browser
        where you are logged in, instead of the official API (which is preferred).
        Log in in your browser, copy the value of the ``MALSESSIONID`` cookie
        (developer tools, Storage/Application, Cookies), and pass it here.
        Only the status, score and progress of list entries can be read and changed
        this way. It is used only when there is no API client id.

        :param session_id: the value of the ``MALSESSIONID`` cookie; or the path of a cookie
            export of your browser (``cookies.txt``, Netscape format; only the login
            cookies are read from it); or a dict of cookies, ``{"MALSESSIONID": "..."}``;
            or the whole ``Cookie`` header of a request that the browser sent to
            myanimelist.net (``name=value; name2=value2; ...``). pymal adds the
            ``is_logged_in=1`` flag cookie that MAL also wants.
        :param save: also save it to the token file (readable by the owner only).
        :param user_agent: the ``User-Agent`` of that browser, if MAL ties the session to it;
            a recent Chrome one (``consts.BROWSER_USER_AGENT``) by default.
        """
        if isinstance(session_id, os.PathLike) or (
            isinstance(session_id, str)
            and len(session_id) < 4096
            and Path(session_id).is_file()
        ):
            session_id = web_session.cookie_header_from_file(session_id)
        if isinstance(session_id, dict):
            session_id = "; ".join(
                f"{name}={value}" for name, value in session_id.items()
            )
        self.__api.set_session(session_id.strip(), user_agent.strip())
        if save:
            self.__api.save()

    @property
    def web(self) -> "web_session.WebSession | None":
        """
        :returns: the website session, if :meth:`login_with_cookie` was used.
        """
        session_id = self.__api.session_id
        if not session_id:
            return None
        return web_session.WebSession(session_id, self.username, self.__api.user_agent)

    def api(
        self, method: str, path: str, params: dict | None = None, data: dict | None = None
    ):
        """
        Call MAL's API v2 as this account, for example ``account.api("GET", "/users/@me")``.

        :return: the decoded JSON answer.
        :exception exceptions.UnauthenticatedAccountError: when not logged in.
        :exception exceptions.MyAnimeListApiError: when the API answers with an error.
        """
        return self.__api.request(method, path, params, data)

    def api_pages(self, path: str, params: dict | None = None):
        """Like :meth:`api` for a paged answer: iterates over all the items."""
        return self.__api.pages(path, params)

    def me(self, fields: str = "anime_statistics") -> dict:
        """
        :param fields: comma separated extra fields, for example
            ``"anime_statistics,birthday,location"``.
        :return: the profile of the logged in user (``id``, ``name``, ``joined_at``, ...).
        :exception exceptions.UnauthenticatedAccountError: when there is no access token.
        """
        if not self.is_auth:
            raise exceptions.UnauthenticatedAccountError(self.username)
        return self.api("GET", "/users/@me", {"fields": fields})

    def suggestions(self, limit: int = 100) -> list:
        """
        :return: the animes MAL suggests to the logged in user.
        :rtype: list of :class:`anime.Anime`
        :exception exceptions.UnauthenticatedAccountError: when there is no access token.
        """
        if not self.is_auth:
            raise exceptions.UnauthenticatedAccountError(self.username)
        return self.__anime_nodes("/anime/suggestions", limit)

    def anime_ranking(self, ranking_type: str = "all", limit: int = 100) -> list:
        """
        :param ranking_type: ``all``, ``airing``, ``upcoming``, ``tv``, ``ova``, ``movie``,
            ``special``, ``bypopularity`` or ``favorite``.
        :return: the top animes of that ranking, best first.
        :rtype: list of :class:`anime.Anime`
        """
        return self.__anime_nodes("/anime/ranking", limit, {"ranking_type": ranking_type})

    def __anime_nodes(self, path: str, limit: int, params: dict | None = None) -> list:
        import itertools

        from pymal import anime

        params = {"limit": min(limit, 100), **(params or {})}
        items = itertools.islice(self.api_pages(path, params), limit)
        return [anime.Anime(item["node"]["id"]) for item in items]

    @property
    def has_session(self) -> bool:
        """
        :returns: True if there is a website session cookie.
        :rtype: bool
        """
        return bool(self.__api.session_id)

    @property
    def has_api_access(self) -> bool:
        """
        :returns: True if there is at least a client id, so the API can be used.
        :rtype: bool
        """
        return self.__api.has_client_id

    @property
    @load
    def image_url(self):
        """
        :return: path for the image of the avatar of the account.
        :rtype: str
        """
        return self.__image_url

    def get_image(self):
        """
        :return: image of the account's avatar
        :rtype: :class:`PIL.Image.Image`
        """
        import io

        from PIL import Image

        sock = global_functions._connect(self.image_url)
        data = io.BytesIO(sock.content)
        return Image.open(data)

    def reload(self):
        """
        reloading account image (all the other things are already lazy load!
        """
        div = global_functions.get_content_wrapper_div(
            self._main_profile_url, self.connect
        )
        img = div.select_one("div.user-image img")
        if img is None:
            raise exceptions.FailedToParseError("profile avatar wasn't found")
        self.__image_url = img.get("data-src") or img.get("src") or ""

    @property
    def is_auth(self) -> bool:
        """
        :returns: True if there is an access token (able to edit the list).
        :rtype: bool
        """
        return self.__api.is_auth

    def __repr__(self):
        return f"<Account username: {self.username:s}>"

    def __hash__(self):
        import hashlib

        hash_md5 = hashlib.md5()
        hash_md5.update(self.username.encode())
        return int(hash_md5.hexdigest(), 16)

    def __format__(self, format_spec):
        return str(self).__format__(format_spec)
