"""
Live tests against a real MAL account through the official API.
Read-only unless MAL_TEST_WRITE=1 (see tests/constants_for_testing.py).
"""

import unittest

import pytest

from pymal import anime, manga
from pymal.account_objects import my_anime, my_manga
from tests.constants_for_testing import (
    ACCOUNT_TEST_WRITE,
    ADD_ANIME_ID,
    ADD_MANGA_ID,
    make_account,
)


class LiveListsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.account = make_account()

    def test_is_auth(self):
        self.assertTrue(self.account.is_auth or self.account.has_session)

    def test_anime_list(self):
        self.assertGreater(len(self.account.animes), 0)
        entry = next(iter(self.account.animes))
        self.assertIsInstance(entry, my_anime.MyAnime)
        self.assertIn(entry.my_status, (1, 2, 3, 4, 6))
        self.assertIsInstance(entry.my_score, int)
        self.assertIsInstance(entry.my_tags, frozenset)
        self.assertIn(entry.id, self.account.animes)

    def test_manga_list(self):
        if not len(self.account.mangas):
            self.skipTest("the account has no manga")
        entry = next(iter(self.account.mangas))
        self.assertIsInstance(entry, my_manga.MyManga)
        self.assertIsInstance(entry.my_completed_chapters, int)

    def test_entry_reload(self):
        entry = next(iter(self.account.animes))
        entry.my_reload()
        self.assertTrue(entry.in_list)

    def test_set_operations(self):
        animes = self.account.animes
        self.assertEqual(animes & animes, frozenset(animes))
        self.assertEqual(animes - animes, frozenset())

    def test_api_user(self):
        if not self.account.is_auth:
            self.skipTest("needs an API access token")
        self.assertEqual(
            self.account.api("GET", "/users/@me")["name"], self.account.username
        )


@pytest.mark.skipif(
    not ACCOUNT_TEST_WRITE, reason="set MAL_TEST_WRITE=1 to modify the list"
)
class LiveWriteTestCase(unittest.TestCase):
    """Adds, changes and removes one anime and one manga that must not be in the list."""

    @classmethod
    def setUpClass(cls):
        cls.account = make_account()

    def check(self, obj, cls):
        entry = obj.add(self.account)
        self.assertIsInstance(entry, cls)
        self.addCleanup(lambda: entry.in_list and entry.delete())
        self.assertTrue(entry.in_list)
        entry.my_score = 7
        if self.account.has_api_access:  # the website session only does score/progress
            entry.my_comments = "pymal test"
            entry.my_tags = {"pymal-test"}
        entry.update()
        entry.my_reload()
        self.assertEqual(entry.my_score, 7)
        if self.account.has_api_access:
            self.assertEqual(entry.my_comments, "pymal test")
            self.assertEqual(entry.my_tags, frozenset({"pymal-test"}))
        entry.delete()
        entry.my_reload()
        self.assertFalse(entry.in_list)

    def test_anime(self):
        self.check(anime.Anime(ADD_ANIME_ID), my_anime.MyAnime)

    def test_manga(self):
        self.check(manga.Manga(ADD_MANGA_ID), my_manga.MyManga)
