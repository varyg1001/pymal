"""Offline tests for connection failure handling in global_functions._connect."""

import unittest
from unittest.mock import MagicMock, patch

import niquests

from pymal import exceptions, global_functions


def response(status: int) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status
    return mock


@patch("pymal.global_functions.time.sleep")
class TestConnectUnavailable(unittest.TestCase):
    URL = "https://myanimelist.net/anime/1"

    def test_retries_connection_error_then_succeeds(self, _sleep):
        session = MagicMock()
        session.request.side_effect = [
            niquests.exceptions.ConnectionError("down"),
            response(200),
        ]
        sock = global_functions._connect(self.URL, session=session)
        self.assertEqual(sock.status_code, 200)
        self.assertEqual(session.request.call_count, 2)

    def test_raises_after_retries_on_503(self, _sleep):
        session = MagicMock()
        session.request.return_value = response(503)
        with self.assertRaises(exceptions.SiteUnavailableError) as ctx:
            global_functions._connect(self.URL, session=session)
        self.assertIn("503", str(ctx.exception))
        self.assertEqual(session.request.call_count, global_functions.consts.RETRY_NUMBER)

    def test_raises_on_persistent_timeout(self, _sleep):
        session = MagicMock()
        session.request.side_effect = niquests.exceptions.ReadTimeout("slow")
        with self.assertRaises(exceptions.SiteUnavailableError):
            global_functions._connect(self.URL, session=session)

    def test_404_is_returned_not_retried(self, _sleep):
        session = MagicMock()
        session.request.return_value = response(404)
        sock = global_functions._connect(self.URL, session=session)
        self.assertEqual(sock.status_code, 404)
        self.assertEqual(session.request.call_count, 1)

    def test_put_is_retried_on_server_error(self, _sleep):
        session = MagicMock()
        session.request.side_effect = [response(503), response(200)]
        sock = global_functions._connect(
            self.URL, data="x=1", method="PUT", session=session
        )
        self.assertEqual(sock.status_code, 200)
        self.assertEqual(session.request.call_args.args[0], "PUT")

    def test_post_not_retried_on_server_error(self, _sleep):
        session = MagicMock()
        session.request.return_value = response(500)
        with self.assertRaises(exceptions.SiteUnavailableError):
            global_functions._connect(self.URL, data="x=1", session=session)
        self.assertEqual(session.request.call_count, 1)

    def test_post_retried_on_connection_error(self, _sleep):
        session = MagicMock()
        session.request.side_effect = [
            niquests.exceptions.ConnectionError("down"),
            response(200),
        ]
        global_functions._connect(self.URL, data="x=1", session=session)
        self.assertEqual(session.request.call_count, 2)


class TestFetchPublicListJson(unittest.TestCase):
    def test_follows_pages_until_empty(self):
        pages = [[{"anime_id": i} for i in range(300)], [{"anime_id": 300}], []]
        responses = []
        for page in pages:
            r = response(200)
            r.json.return_value = page
            responses.append(r)
        with patch("pymal.global_functions._connect", side_effect=responses) as connect:
            items = global_functions.fetch_public_list_json(
                "https://x/load.json?status=1"
            )
        self.assertEqual(len(items), 301)
        self.assertTrue(connect.call_args_list[1].args[0].endswith("&offset=300"))

    def test_unreadable_list_is_empty(self):
        with patch("pymal.global_functions._connect", return_value=response(400)):
            self.assertEqual(
                global_functions.fetch_public_list_json("https://x?status=1"), []
            )

    def test_site_unavailable_propagates(self):
        with (
            patch(
                "pymal.global_functions._connect",
                side_effect=exceptions.SiteUnavailableError("u", "HTTP 503"),
            ),
            self.assertRaises(exceptions.SiteUnavailableError),
        ):
            global_functions.fetch_public_list_json("https://x?status=1")


class TestReloadedSetOps(unittest.TestCase):
    def setUp(self):
        from pymal.types.ReloadedSet import ReloadedSet

        class Fixed(ReloadedSet):
            @property
            def _values(self):
                return frozenset({1, 2, 3})

        self.s = Fixed()

    def test_ops(self):
        self.assertEqual(self.s & {2, 3, 4}, frozenset({2, 3}))
        self.assertEqual(self.s - {2}, frozenset({1, 3}))
        self.assertEqual(self.s ^ {3, 4}, frozenset({1, 2, 4}))
        self.assertEqual(self.s | {9}, frozenset({1, 2, 3, 9}))
        self.assertEqual(self.s.intersection({1, 2}, {2, 5}), frozenset({2}))


class TestMakeCounter(unittest.TestCase):
    def test_values(self):
        self.assertEqual(global_functions.make_counter("1,100"), 1100)
        self.assertEqual(global_functions.make_counter("26"), 26)
        self.assertEqual(global_functions.make_counter("Unknown"), float("inf"))
        self.assertEqual(global_functions.make_counter("?"), float("inf"))


class TestSearchRanking(unittest.TestCase):
    def prefix_answer(self, ids):
        sock = response(200)
        sock.json.return_value = {
            "categories": [
                {"type": "anime", "items": [{"id": i, "name": f"T{i}"} for i in ids]}
            ]
        }
        return sock

    def test_results_keep_the_order_of_mal(self):
        from pymal.searches.search_animes_provider import SearchAnimesProvider

        ids = [52991, 59978, 5114, 1, 21, 16498, 7, 8, 9, 10, 11]
        with patch(
            "pymal.global_functions._connect", return_value=self.prefix_answer(ids)
        ):
            results = SearchAnimesProvider().search("frieren")
        self.assertEqual([a.id for a in results], ids)
        self.assertEqual([a.id for a in list(results)[:3]], ids[:3])
        self.assertIsInstance(results, frozenset)
        self.assertEqual(len(results), len(ids))
        self.assertIn(5114, results)

    def test_outage_is_not_hidden_by_the_fallback(self):
        from pymal.searches.search_animes_provider import SearchAnimesProvider

        with (
            patch(
                "pymal.global_functions._connect",
                side_effect=exceptions.SiteUnavailableError("u", "down"),
            ) as connect,
            self.assertRaises(exceptions.SiteUnavailableError),
        ):
            SearchAnimesProvider().search("frieren")
        self.assertEqual(
            connect.call_count, 1
        )  # no second attempt through the old search
