"""Offline tests for the OAuth/API layer, the account lists and MyAnime/MyManga."""

import inspect
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib import parse

from pymal import account, exceptions, mal_api
from pymal.account_objects import my_anime, my_manga


def answer(status=200, body=None):
    sock = MagicMock()
    sock.status_code = status
    sock.content = b"" if body is None else json.dumps(body).encode()
    sock.text = "" if body is None else json.dumps(body)
    sock.json.return_value = body
    return sock


class FakeMal:
    """Replaces the HTTP layer; answers are queued per (method, path start)."""

    def __init__(self):
        self.calls = []
        self.routes = []

    def add(self, method, path, *answers):
        self.routes.append([method, path, list(answers)])

    def __call__(self, url, data=None, headers=None, method=None, **_unused):
        method = method or ("POST" if data is not None else "GET")
        self.calls.append((method, url, data, dict(headers or {})))
        for route in self.routes:
            path = parse.urlsplit(url).path
            # "/" only matches the home page, not every url
            if route[0] == method and (
                path == route[1] or (route[1] != "/" and path.startswith(route[1]))
            ):
                chosen = route[2].pop(0) if len(route[2]) > 1 else route[2][0]
                return chosen(url, data) if inspect.isfunction(chosen) else chosen
        raise AssertionError(f"unexpected call {method} {url}")

    def calls_to(self, method):
        return [c for c in self.calls if c[0] == method]


class ApiTestCase(unittest.TestCase):
    counter = 0

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.mal = FakeMal()
        patcher = patch("pymal.global_functions._connect", self.mal)
        patcher.start()
        self.addCleanup(patcher.stop)
        ApiTestCase.counter += 1
        self.name = (
            f"apitest{os.getpid()}x{ApiTestCase.counter}"  # accounts are singletons
        )
        self.token_file = str(Path(self.tmp.name) / "token.json")

    def make_account(self, access_token="tok", refresh_token="", client_id="cid"):
        acc = account.Account(self.name, token_file=self.token_file)
        acc.login(client_id, access_token, refresh_token)
        return acc


class TestAccountPages(unittest.TestCase):
    def test_user_id_from_message_button(self):
        from pymal import account

        acc = account.Account("TestUserId")
        html = '<a id="message" data-ga-click-param="uid:4242"></a>'
        with patch.object(acc, "connect", return_value=html):
            self.assertEqual(acc.user_id, 4242)

    def test_friends_parse(self):
        import bs4

        from pymal.account_objects import account_friends

        html = (
            '<div id="contentWrapper"><div class="boxlist-container friend">'
            '<div class="boxlist col-3"><div class="title">'
            '<a href="https://myanimelist.net/profile/FriendA">FriendA</a></div></div>'
            '<div class="boxlist col-3"><div class="title">'
            '<a href="https://myanimelist.net/profile/FriendB">FriendB</a></div></div>'
            "</div></div>"
        )
        wrapper = bs4.BeautifulSoup(html, "lxml").find(id="contentWrapper")
        friends = account_friends.AccountFriends(
            MagicMock(_main_profile_url="u", username="o")
        )
        with patch(
            "pymal.global_functions.get_content_wrapper_div", return_value=wrapper
        ):
            friends.reload()
        self.assertEqual({a.username for a in friends}, {"FriendA", "FriendB"})


class TestOAuth(ApiTestCase):
    def test_authorization_url(self):
        url, verifier, state = mal_api.ApiClient.authorization_url("cid", "http://x/cb")
        query = parse.parse_qs(parse.urlsplit(url).query)
        self.assertEqual(query["client_id"], ["cid"])
        self.assertEqual(query["code_challenge"], [verifier])
        self.assertEqual(query["code_challenge_method"], ["plain"])
        self.assertEqual(query["state"], [state])
        self.assertEqual(query["force_logout"], ["true"])
        self.assertEqual(query["redirect_uri"], ["http://x/cb"])
        self.assertTrue(43 <= len(verifier) <= 128)

    def test_exchange_code_saves_tokens_privately(self):
        self.mal.add(
            "POST",
            "/v1/oauth2/token",
            answer(200, {"access_token": "A", "refresh_token": "R", "expires_in": 3600}),
        )
        client = mal_api.ApiClient("u", self.token_file)
        client.exchange_code("cid", "the-code", "ver", "sec")
        form = dict(parse.parse_qsl(self.mal.calls[0][2]))
        self.assertEqual(form["grant_type"], "authorization_code")
        self.assertEqual(form["code"], "the-code")
        self.assertEqual(form["code_verifier"], "ver")
        self.assertEqual(form["client_secret"], "sec")
        saved = json.loads(Path(self.token_file).read_text())
        self.assertEqual((saved["access_token"], saved["refresh_token"]), ("A", "R"))
        self.assertEqual(stat.S_IMODE(Path(self.token_file).stat().st_mode), 0o600)
        # a new client picks the saved tokens up
        self.assertTrue(mal_api.ApiClient("u", self.token_file).is_auth)

    def test_refused_code(self):
        self.mal.add("POST", "/v1/oauth2/token", answer(400, {"error": "invalid_grant"}))
        client = mal_api.ApiClient("u", self.token_file)
        with self.assertRaises(exceptions.MyAnimeListApiError) as ctx:
            client.exchange_code("cid", "bad", "ver")
        self.assertEqual(ctx.exception.status_code, 400)

    def test_authorize_reads_pasted_redirect(self):
        self.mal.add(
            "POST",
            "/v1/oauth2/token",
            answer(200, {"access_token": "A", "refresh_token": "R"}),
        )
        self.mal.add("GET", "/v2/users/@me", answer(200, {"name": self.name.upper()}))
        acc = account.Account(self.name, token_file=self.token_file)

        def paste(prompt):
            url = prompt.split("  ")[1].split("\n")[0]
            state = parse.parse_qs(parse.urlsplit(url).query)["state"][0]
            return f"http://localhost/cb?code=XYZ&state={state}"

        with patch("builtins.input", paste), patch("webbrowser.open"):
            acc.authorize("cid")
        self.assertTrue(acc.is_auth)
        self.assertEqual(dict(parse.parse_qsl(self.mal.calls[0][2]))["code"], "XYZ")

    def test_authorize_rejects_another_user(self):
        self.mal.add(
            "POST",
            "/v1/oauth2/token",
            answer(200, {"access_token": "A", "refresh_token": "R"}),
        )
        self.mal.add("GET", "/v2/users/@me", answer(200, {"name": "somebody_else"}))
        acc = account.Account(self.name, token_file=self.token_file)
        with (
            patch("builtins.input", return_value="the-code"),
            patch("webbrowser.open"),
            self.assertRaises(exceptions.UnauthenticatedAccountError),
        ):
            acc.authorize("cid")
        self.assertFalse(acc.is_auth)
        self.assertFalse(Path(self.token_file).exists())

    def test_authorize_rejects_wrong_state(self):
        acc = account.Account(self.name, token_file=self.token_file)
        with (
            patch("builtins.input", return_value="http://l/cb?code=X&state=evil"),
            patch("webbrowser.open"),
            self.assertRaises(ValueError),
        ):
            acc.authorize("cid")


class TestRequests(ApiTestCase):
    def test_bearer_token_header(self):
        acc = self.make_account()
        self.mal.add("GET", "/v2/users/@me", answer(200, {"name": "x"}))
        self.assertEqual(acc.api("GET", "/users/@me"), {"name": "x"})
        self.assertEqual(self.mal.calls[0][3]["Authorization"], "Bearer tok")

    def test_client_id_only(self):
        acc = self.make_account(access_token="")
        self.mal.add("GET", "/v2/anime/1", answer(200, {"id": 1}))
        acc.api("GET", "/anime/1")
        self.assertEqual(self.mal.calls[0][3], {"X-MAL-CLIENT-ID": "cid"})
        self.assertFalse(acc.is_auth)

    def test_no_credentials(self):
        acc = account.Account(self.name, token_file=self.token_file)
        with self.assertRaises(exceptions.UnauthenticatedAccountError):
            acc.api("GET", "/users/@me")

    def test_expired_token_is_refreshed_first(self):
        acc = self.make_account(refresh_token="R")
        acc._Account__api.credentials.expires_at = 1.0
        self.mal.add("POST", "/v1/oauth2/token", answer(200, {"access_token": "NEW"}))
        self.mal.add("GET", "/v2/x", answer(200, {}))
        acc.api("GET", "/x")
        self.assertEqual(self.mal.calls[-1][3]["Authorization"], "Bearer NEW")

    def test_401_refreshes_and_retries_once(self):
        acc = self.make_account(refresh_token="R")
        self.mal.add(
            "GET",
            "/v2/x",
            answer(401, {"error": "invalid_token"}),
            answer(200, {"ok": 1}),
        )
        self.mal.add("POST", "/v1/oauth2/token", answer(200, {"access_token": "NEW"}))
        self.assertEqual(acc.api("GET", "/x"), {"ok": 1})
        self.assertEqual(len(self.mal.calls_to("GET")), 2)

    def test_error_status(self):
        acc = self.make_account()
        self.mal.add("GET", "/v2/anime/0", answer(404, {"error": "not_found"}))
        with self.assertRaises(exceptions.MyAnimeListApiError) as ctx:
            acc.api("GET", "/anime/0")
        self.assertEqual(ctx.exception.status_code, 404)

    def test_pages_follow_next(self):
        acc = self.make_account()
        self.mal.add(
            "GET",
            "/v2/first",
            answer(
                200,
                {
                    "data": [1, 2],
                    "paging": {"next": "https://api.myanimelist.net/v2/second"},
                },
            ),
        )
        self.mal.add("GET", "/v2/second", answer(200, {"data": [3], "paging": {}}))
        self.assertEqual(list(acc.api_pages("/first")), [1, 2, 3])


def list_item(mal_id, status, **extra):
    return {
        "node": {"id": mal_id, "title": f"T{mal_id}"},
        "list_status": {"status": status, **extra},
    }


class TestApiHelpers(ApiTestCase):
    def test_me(self):
        acc = self.make_account()
        self.mal.add(
            "GET", "/v2/users/@me", answer(200, {"name": "x", "anime_statistics": {}})
        )
        self.assertEqual(acc.me()["name"], "x")
        self.assertIn("fields=anime_statistics", self.mal.calls[0][1])

    def test_me_needs_a_token(self):
        acc = self.make_account(access_token="")
        with self.assertRaises(exceptions.UnauthenticatedAccountError):
            acc.me()

    def test_ranking_and_limit(self):
        acc = self.make_account(access_token="")
        nodes = [{"node": {"id": i}} for i in (5, 6, 7)]
        self.mal.add(
            "GET", "/v2/anime/ranking", answer(200, {"data": nodes, "paging": {}})
        )
        animes = acc.anime_ranking("airing", limit=2)
        self.assertEqual([a.id for a in animes], [5, 6])
        self.assertIn("ranking_type=airing", self.mal.calls[0][1])

    def test_suggestions(self):
        acc = self.make_account()
        self.mal.add(
            "GET",
            "/v2/anime/suggestions",
            answer(200, {"data": [{"node": {"id": 9}}], "paging": {}}),
        )
        self.assertEqual([a.id for a in acc.suggestions()], [9])


class TestAccountLists(ApiTestCase):
    def test_anime_list_from_api(self):
        acc = self.make_account()
        self.mal.add(
            "GET",
            "/v2/users/",
            answer(
                200,
                {
                    "data": [
                        list_item(1, "watching", score=8, num_episodes_watched=5),
                        list_item(2, "completed", score=10),
                        list_item(3, "plan_to_watch"),
                        list_item(4, "something_new"),
                    ],
                    "paging": {},
                },
            ),
        )
        animes = acc.animes
        self.assertEqual({a.id for a in animes.watching}, {1})
        self.assertEqual({a.id for a in animes.completed}, {2})
        self.assertEqual({a.id for a in animes.plan_to_watch}, {3})
        self.assertEqual(len(animes), 3)
        self.assertIn(2, animes)
        # the entries are filled from the list, without more requests
        entry = next(iter(animes.watching))
        self.assertEqual(
            (entry.my_score, entry.my_completed_episodes, entry.my_status), (8, 5, 1)
        )
        self.assertEqual(len(self.mal.calls), 1)
        self.assertIn("limit=1000", self.mal.calls[0][1])

    def test_manga_list_from_api(self):
        acc = self.make_account()
        self.mal.add(
            "GET",
            "/v2/users/",
            answer(
                200,
                {
                    "data": [list_item(7, "reading", num_chapters_read=3)],
                    "paging": {},
                },
            ),
        )
        entry = next(iter(acc.mangas.reading))
        self.assertIsInstance(entry, my_manga.MyManga)
        self.assertEqual(entry.my_completed_chapters, 3)

    def test_public_list_without_credentials(self):
        acc = account.Account(self.name, token_file=self.token_file)
        self.assertFalse(acc.has_api_access)
        with patch(
            "pymal.global_functions.fetch_public_list_json",
            side_effect=lambda url: [{"anime_id": 9}] if url.endswith("status=2") else [],
        ):
            self.assertEqual({a.id for a in acc.animes.completed}, {9})
        self.assertEqual(self.mal.calls, [])


class TestMyEntry(ApiTestCase):
    def entry(self, status=None, mal_id=11):
        acc = self.make_account()
        self.mal.routes.clear()
        self.mal.add(
            "GET",
            f"/v2/anime/{mal_id}",
            answer(
                200,
                {"id": mal_id, "my_list_status": status} if status else {"id": mal_id},
            ),
        )
        return my_anime.MyAnime(mal_id, acc)

    def test_reload_reads_the_list_status(self):
        entry = self.entry(
            {
                "status": "on_hold",
                "score": 7,
                "num_episodes_watched": 4,
                "is_rewatching": True,
                "start_date": "2024-03-05",
                "finish_date": "2024-04",
                "priority": 2,
                "num_times_rewatched": 1,
                "rewatch_value": 3,
                "tags": ["a", "b"],
                "comments": "nice",
            }
        )
        self.assertTrue(entry.in_list)
        self.assertEqual(entry.my_status, 3)
        self.assertEqual(entry.my_score, 7)
        self.assertEqual(entry.my_completed_episodes, 4)
        self.assertIs(entry.my_is_rewatching, True)
        self.assertEqual(entry.my_start_date, "20240305")
        self.assertEqual(entry.my_end_date, "20240400")
        self.assertEqual(entry.my_priority, 2)
        self.assertEqual(entry.my_tags, frozenset({"a", "b"}))
        self.assertEqual(entry.my_comments, "nice")
        self.assertIn("my_list_status", self.mal.calls[0][1])

    def test_update_sends_changes(self):
        entry = self.entry({"status": "watching", "score": 5, "start_date": "2024-01-02"})
        entry.my_score = 9
        entry.my_tags = {"z", "a"}
        entry.my_is_rewatching = True
        entry.my_completed_episodes = 12
        self.mal.add(
            "PUT",
            "/v2/anime/11/my_list_status",
            answer(200, {"status": "watching", "score": 9}),
        )
        entry.update()
        method, url, data, _ = self.mal.calls_to("PUT")[0]
        form = dict(parse.parse_qsl(data))
        self.assertEqual(form["status"], "watching")
        self.assertEqual(form["score"], "9")
        self.assertEqual(form["tags"], "a,z")
        self.assertEqual(form["is_rewatching"], "true")
        self.assertEqual(form["num_watched_episodes"], "12")
        self.assertEqual(form["start_date"], "2024-01-02")
        self.assertNotIn("finish_date", form)  # unset dates are not sent

    def test_update_failure(self):
        entry = self.entry({"status": "watching"})
        self.mal.add("PUT", "/v2/anime/11/my_list_status", answer(400, {"error": "bad"}))
        with self.assertRaises(exceptions.MyAnimeListApiUpdateError):
            entry.update()

    def test_delete(self):
        entry = self.entry({"status": "watching"})
        self.mal.add("DELETE", "/v2/anime/11/my_list_status", answer(200))
        entry.delete()
        self.assertFalse(entry.in_list)

    def test_delete_failure(self):
        entry = self.entry({"status": "watching"})
        self.mal.add("DELETE", "/v2/anime/11/my_list_status", answer(404, {"error": "x"}))
        with self.assertRaises(exceptions.MyAnimeListApiDeleteError):
            entry.delete()

    def test_add_creates_as_plan_to_watch(self):
        entry = self.entry(None)
        self.mal.add(
            "PUT", "/v2/anime/11/my_list_status", answer(200, {"status": "plan_to_watch"})
        )
        result = entry.add(entry._account)
        self.assertIs(result, entry)
        self.assertEqual(
            dict(parse.parse_qsl(self.mal.calls_to("PUT")[0][2]))["status"],
            "plan_to_watch",
        )
        self.assertTrue(entry.in_list)

    def test_add_does_not_overwrite_an_existing_entry(self):
        entry = self.entry({"status": "completed", "score": 10})
        entry.add(entry._account)
        self.assertEqual(self.mal.calls_to("PUT"), [])

    def test_validation(self):
        entry = self.entry({"status": "watching"})
        for name, value in (
            ("my_status", 5),
            ("my_score", 11),
            ("my_priority", 3),
            ("my_rewatch_value", 6),
            ("my_completed_episodes", -1),
            ("my_start_date", "2024-01-01"),
            ("my_is_rewatching", "yes"),
        ):
            with self.subTest(name), self.assertRaises(ValueError):
                setattr(entry, name, value)

    def test_manga_form(self):
        acc = self.make_account()
        self.mal.add(
            "GET",
            "/v2/manga/5",
            answer(200, {"id": 5, "my_list_status": {"status": "reading"}}),
        )
        entry = my_manga.MyManga(5, acc)
        entry.my_completed_chapters = 10
        entry.my_completed_volumes = 2
        entry.my_is_rereading = False
        self.mal.add(
            "PUT", "/v2/manga/5/my_list_status", answer(200, {"status": "reading"})
        )
        entry.update()
        form = dict(parse.parse_qsl(self.mal.calls_to("PUT")[0][2]))
        self.assertEqual(form["num_chapters_read"], "10")
        self.assertEqual(form["num_volumes_read"], "2")
        self.assertEqual(form["is_rereading"], "false")
        self.assertEqual(form["status"], "reading")

    def test_accounts_do_not_share_entries(self):
        a = self.make_account()
        other = account.Account(self.name + "other", token_file=self.token_file + "2")
        other.login("cid", "tok")
        self.assertIsNot(my_anime.MyAnime(11, a), my_anime.MyAnime(11, other))
        self.assertIs(my_anime.MyAnime(11, a), my_anime.MyAnime(11, a))

    def test_eq_with_id_and_anime(self):
        entry = self.entry({"status": "watching"})
        self.assertEqual(entry, 11)
        self.assertIn(11, [entry])


def page(text="", status=200):
    sock = MagicMock()
    sock.status_code = status
    sock.text = text
    sock.content = text.encode()
    return sock


CSRF_PAGE = "<html><head><meta name='csrf_token' content='CSRF123'></head></html>"


class TestWebSession(ApiTestCase):
    """The experimental website-session (MALSESSIONID cookie) route."""

    def make_web_account(self, anime_items=(), manga_items=()):
        """An account with a cookie, and a website that has these list entries."""
        acc = account.Account(self.name, token_file=self.token_file)
        acc.login_with_cookie("  SESSION1  ")
        self.web_lists = {"anime": list(anime_items), "manga": list(manga_items)}
        self.mal.add("GET", "/", page(CSRF_PAGE))
        for kind in ("anime", "manga"):
            self.mal.add("GET", f"/{kind}list/", self.list_page(kind))
        return acc

    def list_page(self, kind):
        def respond(url, _data):
            offset = int(dict(parse.parse_qsl(parse.urlsplit(url).query))["offset"])
            return answer(200, self.web_lists[kind][offset:])

        return respond

    def website_writes(self, path, apply):
        """POST `path` answers JSON and applies the change to the fake website."""

        def respond(_url, data):
            apply(json.loads(data))
            return answer(200, {})

        self.mal.add("POST", path, respond)

    def test_cookie_is_sent_and_saved(self):
        acc = account.Account(self.name, token_file=self.token_file)
        acc.login_with_cookie("SESSION1", save=True)
        self.assertTrue(acc.has_session)
        self.assertFalse(acc.has_api_access)
        self.assertEqual(
            json.loads(Path(self.token_file).read_text())["session_id"], "SESSION1"
        )
        self.mal.add("GET", "/animelist/", answer(200, []))
        acc.animes.reload()
        self.assertEqual(
            self.mal.calls[0][3]["Cookie"], "MALSESSIONID=SESSION1; is_logged_in=1"
        )

    def test_private_list_from_the_website(self):
        acc = self.make_web_account(
            [
                {"anime_id": 1, "status": 1, "score": 8, "num_watched_episodes": 5},
                {"anime_id": 2, "status": 2, "score": 10, "num_watched_episodes": 12},
                {"anime_id": 3, "status": 7},
            ]
        )
        self.assertEqual({a.id for a in acc.animes.watching}, {1})
        entry = next(iter(acc.animes.watching))
        self.assertEqual(
            (entry.my_score, entry.my_completed_episodes, entry.my_status), (8, 5, 1)
        )
        self.assertEqual(len(acc.animes), 2)
        self.assertIn("status=7", self.mal.calls[1][1])

    def test_edit_existing_entry(self):
        acc = self.make_web_account(
            [{"anime_id": 7, "status": 1, "score": 3, "num_watched_episodes": 2}]
        )

        def apply(payload):
            self.web_lists["anime"][0].update(
                score=payload["score"],
                num_watched_episodes=payload["num_watched_episodes"],
            )

        self.website_writes("/ownlist/anime/edit.json", apply)
        entry = my_anime.MyAnime(7, acc)
        entry.my_score = 9
        entry.my_completed_episodes = 4
        entry.update()
        _, _, data, headers = self.mal.calls_to("POST")[0]
        self.assertEqual(
            json.loads(data),
            {
                "anime_id": 7,
                "status": 1,
                "score": 9,
                "num_watched_episodes": 4,
                "csrf_token": "CSRF123",
            },
        )
        # like the website's own scripts: JSON text in a form-typed body, as an ajax call
        self.assertTrue(
            headers["Content-Type"].startswith("application/x-www-form-urlencoded")
        )
        self.assertEqual(headers["X-Requested-With"], "XMLHttpRequest")
        self.assertEqual(
            (entry.my_score, entry.my_completed_episodes), (9, 4)
        )  # read back

    def test_add_new_entry(self):
        acc = self.make_web_account()

        def apply(payload):
            self.web_lists["anime"].append(
                {"anime_id": payload["anime_id"], "status": payload["status"], "score": 0}
            )

        self.website_writes("/ownlist/anime/add.json", apply)
        entry = my_anime.MyAnime(8, acc)
        entry.add(acc)
        payload = json.loads(self.mal.calls_to("POST")[0][2])
        self.assertEqual((payload["anime_id"], payload["status"]), (8, 6))
        self.assertTrue(entry.in_list)

    def test_write_that_did_not_happen_is_an_error(self):
        acc = self.make_web_account()
        self.website_writes("/ownlist/anime/add.json", lambda _payload: None)
        with self.assertRaises(exceptions.MyAnimeListApiError):
            my_anime.MyAnime(8, acc).add(acc)

    def test_a_web_page_instead_of_json_is_an_error(self):
        acc = self.make_web_account()
        html = page("<html>not json</html>")
        html.json.side_effect = ValueError("no json")
        self.mal.add("POST", "/ownlist/anime/add.json", html)
        with self.assertRaises(exceptions.MyAnimeListApiAddError) as ctx:
            my_anime.MyAnime(8, acc).add(acc)
        self.assertIn("web page", str(ctx.exception))

    def test_manga_fields(self):
        acc = self.make_web_account(
            manga_items=[
                {
                    "manga_id": 5,
                    "status": 1,
                    "num_read_chapters": 3,
                    "num_read_volumes": 1,
                }
            ]
        )

        def apply(payload):
            self.web_lists["manga"][0]["num_read_chapters"] = payload["num_read_chapters"]

        self.website_writes("/ownlist/manga/edit.json", apply)
        entry = my_manga.MyManga(5, acc)
        self.assertEqual(
            (entry.my_completed_chapters, entry.my_completed_volumes), (3, 1)
        )
        entry.my_completed_chapters = 4
        entry.update()
        payload = json.loads(self.mal.calls_to("POST")[0][2])
        self.assertEqual(
            (
                payload["manga_id"],
                payload["num_read_chapters"],
                payload["num_read_volumes"],
            ),
            (5, 4, 1),
        )
        self.assertEqual(entry.my_completed_chapters, 4)

    def test_delete(self):
        acc = self.make_web_account([{"anime_id": 9, "status": 2}])

        def respond(_url, _data):
            self.web_lists["anime"].clear()
            return page("")

        self.mal.add("POST", "/ownlist/anime/9/delete", respond)
        entry = my_anime.MyAnime(9, acc)
        self.assertTrue(entry.in_list)
        entry.delete()
        self.assertEqual(self.mal.calls_to("POST")[0][2], "csrf_token=CSRF123")
        self.assertFalse(entry.in_list)

    def test_delete_that_did_not_happen_is_an_error(self):
        acc = self.make_web_account([{"anime_id": 9, "status": 2}])
        self.mal.add("POST", "/ownlist/anime/9/delete", page(""))
        with self.assertRaises(exceptions.MyAnimeListApiDeleteError):
            my_anime.MyAnime(9, acc).delete()

    def test_whole_cookie_header_and_user_agent(self):
        acc = account.Account(self.name, token_file=self.token_file)
        acc.login_with_cookie("a=1; MALSESSIONID=XYZ; b=2", user_agent="Mozilla/5.0 Test")
        self.mal.add("GET", "/", page(CSRF_PAGE))
        self.assertEqual(acc.web.csrf_token, "CSRF123")
        _, _, _, headers = self.mal.calls[0]
        self.assertEqual(headers["Cookie"], "a=1; MALSESSIONID=XYZ; b=2; is_logged_in=1")
        self.assertEqual(headers["User-Agent"], "Mozilla/5.0 Test")

    def test_login_flag_cookie_is_added(self):
        acc = account.Account(self.name, token_file=self.token_file)
        acc.login_with_cookie("SESSION1")
        self.mal.add("GET", "/", page(CSRF_PAGE))
        _ = acc.web.csrf_token
        self.assertEqual(
            self.mal.calls[0][3]["Cookie"], "MALSESSIONID=SESSION1; is_logged_in=1"
        )

    def test_cookie_export_file(self):
        export = Path(self.tmp.name) / "cookies.txt"
        export.write_text(
            "# Netscape HTTP Cookie File\n"
            "#HttpOnly_.myanimelist.net\tTRUE\t/\tTRUE\t0\tMALHLOGSESSID\tH1\n"
            "myanimelist.net\tFALSE\t/\tTRUE\t0\tMALSESSIONID\tS1\n"
            ".myanimelist.net\tTRUE\t/\tFALSE\t0\tis_logged_in\t1\n"
            ".myanimelist.net\tTRUE\t/\tFALSE\t0\teuconsent-v2\tTRACKING\n"
            ".example.com\tTRUE\t/\tFALSE\t0\tMALSESSIONID\tOTHER\n"
        )
        acc = account.Account(self.name, token_file=self.token_file)
        acc.login_with_cookie(export)
        self.mal.add("GET", "/", page(CSRF_PAGE))
        _ = acc.web.csrf_token
        cookie = self.mal.calls[0][3]["Cookie"]
        self.assertEqual(cookie, "MALHLOGSESSID=H1; MALSESSIONID=S1; is_logged_in=1")
        self.assertNotIn("TRACKING", cookie)

    def test_cookie_export_without_a_session(self):
        export = Path(self.tmp.name) / "empty.txt"
        export.write_text("# Netscape HTTP Cookie File\n")
        acc = account.Account(self.name, token_file=self.token_file)
        with self.assertRaises(ValueError):
            acc.login_with_cookie(export)

    def test_cookies_as_a_dict(self):
        acc = account.Account(self.name, token_file=self.token_file)
        acc.login_with_cookie({"MALSESSIONID": "A", "MALHLOGSESSID": "B"})
        self.mal.add("GET", "/", page(CSRF_PAGE))
        _ = acc.web.csrf_token
        self.assertEqual(
            self.mal.calls[0][3]["Cookie"],
            "MALSESSIONID=A; MALHLOGSESSID=B; is_logged_in=1",
        )

    def test_default_user_agent_is_a_browser_one(self):
        acc = account.Account(self.name, token_file=self.token_file)
        acc.login_with_cookie("SESSION1")
        self.mal.add("GET", "/", page(CSRF_PAGE))
        _ = acc.web.csrf_token
        self.assertIn("Chrome/", self.mal.calls[0][3]["User-Agent"])

    def test_cookie_that_is_not_logged_in(self):
        acc = account.Account(self.name, token_file=self.token_file)
        acc.login_with_cookie("MALSESSIONID=WRONG")
        self.mal.add(
            "GET",
            "/",
            page(CSRF_PAGE.replace("</head>", '</head><a id="malLogin">Login</a>')),
        )
        with self.assertRaises(exceptions.UnauthenticatedAccountError) as ctx:
            _ = acc.web.csrf_token
        self.assertIn("logged in", str(ctx.exception))
        self.assertEqual(
            self.mal.calls[0][3]["Cookie"], "MALSESSIONID=WRONG; is_logged_in=1"
        )

    def test_expired_session(self):
        acc = account.Account(self.name, token_file=self.token_file)
        acc.login_with_cookie("OLD")
        self.mal.add("GET", "/animelist/", answer(400, {"error": "x"}))
        with self.assertRaises(exceptions.UnauthenticatedAccountError) as ctx:
            acc.animes.reload()
        self.assertIn("expired", str(ctx.exception))

    def test_api_wins_when_both_are_set(self):
        acc = self.make_account()
        acc.login_with_cookie("SESSION1")
        self.mal.add("GET", "/v2/users/", answer(200, {"data": [], "paging": {}}))
        acc.animes.reload()
        self.assertIn("api.myanimelist.net", self.mal.calls[0][1])


if __name__ == "__main__":
    unittest.main()
